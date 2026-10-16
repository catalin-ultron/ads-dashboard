# D23 Payment Management (Textura-class)

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D23.01 | Project setup and payment structure | ERPNext Project + Purchase Order + Payment Terms Template | partial | Project has customer/sales_order/billed totals; no prime→sub→sub-tier contract tree, no SOV per contract |
| D23.02 | Draws (billing periods) | ERPNext Payment Schedule (closest) | none | No draw entity or draw lifecycle; schedule rows are per-invoice installments only |
| D23.03 | Subcontractor invoices / pay requests | ERPNext Purchase Invoice + status_updater over-billing check | partial | Amount-based invoice lines validated against PO with allowance %; no % complete × scheduled value, no stored materials |
| D23.04 | Retention (retainage) | ERPNext Tax Withholding (threshold engine), Payment Entry deductions, Odoo withholding hook | none | No retainage anywhere (grep "retention/retainage" hits only stock sample retention); threshold/withheld-ledger pattern is reusable |
| D23.05 | Lien waivers | ERPNext Purchase Invoice on_hold, Odoo payment_state=blocked | none | Hold primitives exist; no waiver document, forms, amounts or signer |
| D23.06 | Compliance documents | ERPNext Supplier hold, Lower Deduction Certificate, Bank Guarantee, Supplier Scorecard | partial | Validity-dated certificates and supplier-level payment blocks; no COI/W-9/licence register with automatic hold |
| D23.07 | Review and approval routing | frappe Workflow on Purchase Invoice; Odoo PO two-step approval; Odoo account.move review_state | partial | Role-gated state machine with conditions; no approved-vs-requested amounts per line, no reject-to-sub portal loop |
| D23.08 | Owner/GC pay application (G702/G703) | none | none | No AIA aggregation; ERPNext Sales Invoice could carry result lines only |
| D23.09 | Electronic payments and disbursement | ERPNext Payment Entry / Payment Request / Payment Order; Odoo account.payment | partial | Allocation to invoices, payment orders to bank, trusted-bank-account guard; no joint checks, no ACH/NACHA file generation in sources read |
| D23.10 | Change orders in payment management | frappe amend (amended_from) | none | No CO entity in payments; amendment creates a new document name with suffix, no SOV revision versioning |
| D23.11 | Signatures and audit | frappe Version + Comment | partial | Field-level diff audit and timeline; no e-signature |
| D23.12 | ERP/accounting integration | ERPNext Payment Ledger Entry, GL, Odoo account.move/partial reconcile | partial | These are the ERP side (AP, outstanding, payment status); no connector to external ERPs |
| D23.13 | Platform usage fees | none | none | No fee schedule by contract value |

## Storage model

### ERPNext (Frappe doctypes; field lists from `<doctype>.json`)

**Payment Entry** (`erpnext/erpnext/accounts/doctype/payment_entry/payment_entry.json`), submittable, naming `ACC-PAY-.YYYY.-`.
- `payment_type` Select(Receive | Pay | Internal Transfer), `posting_date`, `company`, `party_type` Link(DocType) + `party` Dynamic Link, `paid_from`/`paid_to` Link(Account), `paid_amount`, `received_amount`, `source_exchange_rate`, `target_exchange_rate`, `base_*` mirrors.
- `references` Table(Payment Entry Reference) 1:N, `deductions` Table(Payment Entry Deduction) 1:N, `taxes` Table(Advance Taxes and Charges), `tax_withholding_entries` Table(Tax Withholding Entry).
- Derived: `total_allocated_amount`, `unallocated_amount`, `difference_amount`; `project` Link(Project); `payment_order` Link + `payment_order_status` Select(Initiated | Payment Ordered); `bank_account`, `party_bank_account`; `status` Select(Draft | Submitted | Cancelled); `apply_tds`, `tax_withholding_category`, `ignore_tax_withholding_threshold`.

**Payment Entry Reference** (child): `reference_doctype`* + `reference_name`* (Dynamic Link to Purchase Invoice / Purchase Order / Journal Entry / Payment Entry for suppliers, `payment_entry.py:753`), `due_date`, `bill_no`, `total_amount`, `outstanding_amount`, `allocated_amount`, `exchange_rate`, `payment_term` Link(Payment Term), `payment_term_outstanding`, `payment_request` Link, `payment_request_outstanding`, `exchange_gain_loss`, `advance_voucher_type/no`.

**Payment Entry Deduction** (child): `account`*, `cost_center`*, `amount`*, `is_exchange_gain_loss`, `dunning`. Generic channel for amounts withheld from a payment (the only place a retainage deduction could be booked today).

**Payment Request** (`.../payment_request/payment_request.json`), submittable: `payment_request_type` Select(Outward | Inward)*, `reference_doctype` + `reference_name` (the invoice/order), `grand_total`*, `outstanding_amount`, `party_type/party`, `bank_account`, `payment_gateway_account`, `payment_order` Link, `status` Select(Draft | Requested | Initiated | Partially Paid | Payment Ordered | Paid | Failed | Cancelled), `payment_reference` Table(Payment Reference: `payment_term`, `due_date`, `amount`, `payment_schedule` Link).

**Payment Order** (`.../payment_order/payment_order.json`), submittable, naming `PMO-`: `company_bank_account`*, `payment_order_type` Select(Payment Request | Payment Entry)*, `party` Link(Supplier), `references` Table(Payment Order Reference: `reference_doctype/name`*, `amount`*, `supplier`, `payment_request`, `bank_account`*, `mode_of_payment`, `payment_reference`).

**Payment Terms Template / Payment Term / Payment Schedule**
- Template detail rows (`payment_terms_template_detail.json`): `payment_term`, `invoice_portion`* (percent), `due_date_based_on`* Select(Day(s) after invoice date | Day(s) after the end of the invoice month | Month(s) after the end of the invoice month), `credit_days`, `credit_months`, `discount_type` (Percentage | Amount), `discount`, `discount_validity_based_on`, `discount_validity`. Template flag `allocate_payment_based_on_payment_terms`.
- Payment Schedule (child of invoice/order, `payment_schedule.json`): `payment_term`, `due_date`*, `invoice_portion`, `payment_amount`*, `paid_amount`, `outstanding`, `discounted_amount`, `discount_date`, `base_*` mirrors. This is the per-invoice installment ledger updated by payments.

**Purchase Invoice** (subcontractor invoice analog; fields filtered from `purchase_invoice.json`): `supplier`, `bill_no`, `bill_date`, `due_date`, `project`, `on_hold` Check, `release_date` Date, `hold_comment`, `outstanding_amount`, `total_advance`, `advances` Table(Purchase Invoice Advance: `reference_type/name`, `reference_row`, `advance_amount`, `allocated_amount`, `exchange_gain_loss`), `payment_schedule` Table, `write_off_amount`, `apply_tds`, `tax_withholding_entries`, `per_received`, `status` Select(Draft | Return | Debit Note Issued | Submitted | Paid | Partly Paid | Unpaid | Overdue | Cancelled | Internal Transfer).

**Supplier** (`erpnext/erpnext/buying/doctype/supplier/supplier.json`): `on_hold`, `hold_type` Select(All | Invoices | Payments), `release_date`, `tax_id`, `tax_withholding_category`, `default_bank_account`.

**Tax Withholding** (closest structural analog to retainage)
- Category (`tax_withholding_category.json`): `rates` Table*, `accounts` Table*, `tax_on_excess_amount`, `round_off_tax_amount`, `tax_deduction_basis` (Gross Total | Net Total)*, `disable_cumulative_threshold`, `disable_transaction_threshold`.
- Rate row: `tax_withholding_rate`*, `single_threshold`, `cumulative_threshold`, `from_date`*, `to_date`*, `tax_withholding_group`.
- Tax Withholding Entry (child of invoice/payment/journal; `tax_withholding_entry.json`): `party_type/party`, `tax_id`, `tax_withholding_category`, `tax_rate`, `taxable_amount`, `withholding_amount`, `taxable_doctype/name/date` (where the base arose), `withholding_doctype/name/date` (where the amount was actually withheld), `status` Select(Settled | Under Withheld | Over Withheld | Duplicate | Cancelled), `under_withheld_reason` (Threshold Exemption | Lower Deduction Certificate), `lower_deduction_certificate` Link. The split between "taxable" and "withholding" voucher is a held-vs-released ledger pattern directly reusable for retention held/released.

**Lower Deduction Certificate** (`erpnext/erpnext/regional/doctype/lower_deduction_certificate/lower_deduction_certificate.json`): `certificate_no`*, `supplier`*, `valid_from`*, `valid_upto`*, `rate`*, `certificate_limit`*, `tax_withholding_category`*, `company`*. A validity-dated, amount-capped compliance document per supplier.

**Bank Guarantee** (`erpnext/erpnext/accounts/doctype/bank_guarantee/bank_guarantee.json`), submittable, naming `ACC-BG-.YYYY.-.#####`: `bg_type` (Receiving | Providing)*, `reference_doctype/docname`, `customer`/`supplier`, `project`, `amount`*, `start_date`*, `validity` Int, `end_date`, `bank`, `bank_guarantee_number`, `margin_money`, `charges`. Usable as the bond record of D23.06.

**Payment Ledger Entry** (`payment_ledger_entry.json`): `posting_date`, `account_type` (Receivable | Payable), `account`, `party_type/party`, `voucher_type/no`, `against_voucher_type/no`, `amount`, `amount_in_account_currency`, `delinked`, `project`, `due_date`, `voucher_detail_no`. Outstanding of any invoice = sum over rows with `against_voucher = invoice`. **Advance Payment Ledger Entry** tracks advances against orders (`voucher_*`, `against_voucher_*`, `amount`, `event`, `delinked`).

**Project** (`erpnext/erpnext/projects/doctype/project/project.json`): `customer`, `sales_order`, `percent_complete_method` (Manual | Task Completion | Task Progress | Task Weight), `percent_complete`, `estimated_costing`, `total_billable_amount`, `total_billed_amount`, `total_purchase_cost`, `per_gross_margin`.

### Odoo account

- **account.payment** (`odoo/addons/account/models/account_payment.py:37`): `state` Selection(draft | paid | reconciled | canceled | rejected), computed+stored; `is_reconciled`, `is_matched` (matched to bank statement), `is_sent`; `move_id` (journal entry), `outstanding_account_id`, `destination_account_id`, `partner_bank_id`, `payment_method_line_id`.
- **account.move** (invoice/bill): `payment_state` (`account_move.py:619`) Selection(not_paid | in_payment | paid | partial | reversed | blocked | invoicing_legacy) (`account_move.py:51`), `amount_residual` (`:578`), `matched_payment_ids` (`:217`), `origin_payment_id` (`:210`), `invoice_payment_term_id` (`:415`), `review_state` (todo | reviewed | supervised | anomaly) (`:60`, `:320`).
- **account.partial.reconcile** (`odoo/addons/account/models/account_partial_reconcile.py:17-66`): `debit_move_id`, `credit_move_id`, `amount`, `full_reconcile_id`, `max_date`. N:M join between invoice lines and payment lines; residuals derive from it.
- **account.payment.term / .line** (`account_payment_term.py:9`, `:274`): term has `early_discount`, `discount_percentage`, `discount_days`, `early_pay_discount_computation`; line has `value` (percent | fixed), `value_amount`, `delay_type` (days_after | days_after_end_of_month | days_after_end_of_next_month | days_end_of_month_on_the), `nb_days`, `days_next_month`.
- **res.partner.bank** `allow_out_payment` (`res_partner_bank.py:36`): bank account must be validated before outbound payment.

Sources disagree on the payment model: ERPNext stores allocation on the payment (Payment Entry Reference rows with `allocated_amount`) and derives invoice outstanding from Payment Ledger Entry; Odoo stores allocation as account.partial.reconcile between move lines and derives `payment_state` from those.

## Algorithms and logic

**ERPNext payment schedule generation** (`erpnext/erpnext/accounts/services/payment_schedule.py:18-117`)
1. Skip for POS sales invoices and opening entries.
2. Base date = `bill_date` or `posting_date`; total = rounded/grand total minus `write_off_amount` (invoices) minus `total_advance` (with currency conversion branch).
3. If no schedule: copy from linked order when `automatically_fetch_payment_terms` and the order has terms; else expand the template; else one row (100%, due = due_date).
4. For each row with `invoice_portion`: `payment_amount = grand_total × portion / 100`, `outstanding = payment_amount`.
- Due date (`payment_schedule.py:425`): `+credit_days`; end of month `+credit_days`; or end of month after `+credit_months`. Clamped to never precede posting date (`:420`). Discount date is computed the same way (`:437`).
- Template invariant: portions must sum to 100.00 (`payment_terms_template.py:33-39`).

**Odoo payment term distribution** (`odoo/addons/account/models/account_payment_term.py:169-266`): iterate lines; `percent` lines take `round(total × value/100)`, `fixed` lines take `value_amount` converted by rate; **the last line always takes the residual** regardless of type. Early discount only applies to single-line 100% terms; the discounted balance excludes or includes tax depending on `early_pay_discount_computation`. Due dates come from `_get_due_date` (`:303`).

**ERPNext payment allocation and balancing** (`erpnext/erpnext/accounts/doctype/payment_entry/payment_entry.py`)
- Auto-allocation `allocate_amount_to_references` (`:1660`): paid amount minus deductions; positive and negative outstanding totals are computed; allocate to positive outstanding until paid amount is exhausted (supplier Pay / customer Receive).
- `set_total_allocated_amount` (`:1081`): sum of `allocated_amount` (abs).
- `set_unallocated_amount` (`:1098`): Pay case: `unallocated = (base_received − non-FX deductions − base_total_allocated − included_taxes) / target_exchange_rate` when allocations fall short.
- `set_difference_amount` (`:1201`): Pay case `difference = base_paid − (base_allocated + base_unallocated) − included_taxes − Σdeductions`. **Invariant**: `on_submit` throws unless `difference_amount == 0` (`:203-205`).
- Over-allocation guard (`:374-395`): non-customer/supplier parties: `allocated ≤ outstanding` (and symmetric for negatives). Customer/supplier: re-fetch latest outstanding by voucher and payment term (`:432`), and when the template has term-based allocation enabled, each reference row must name a payment term.
- Payment schedule update on submit (`:826-917`): group allocations by (term, invoice); `paid_amount += allocated − discount`, `outstanding −= allocated`; throws if allocated > term outstanding; reversal on cancel.
- Reference validation (`:686-751`): reference party must equal payment party; party account must match the invoice's `credit_to`; **a Purchase Invoice with `on_hold` cannot be referenced** (`:742`); referenced docs must be submitted.
- Submit sequence (`:203-213`): withholding on_submit → update payment requests → update schedule → GL entries → update outstanding (Payment Ledger) → dunnings → status.

**Invoice outstanding** (`erpnext/erpnext/accounts/utils.py:2213-2257`): for invoice doctypes, query Payment Ledger outstanding for (voucher, party, account) and write `outstanding_amount`; advance doctypes recompute `total_advance_paid` instead.

**Advance allocation to an invoice** (`erpnext/erpnext/accounts/services/advances.py:27-60`): fetch open advance Payment/Journal Entries for the party; greedily `allocated = min(invoice_total − already_allocated, advance.amount)`; on submit `update_against_document_in_jv` (`controllers/accounts_controller.py:1224`) relinks/splits the advance voucher rows to the invoice.

**Over-billing against order** (`erpnext/erpnext/controllers/status_updater.py:492-541`): `overflow% = (billed − ordered)/ordered × 100`; allowance from Item `over_billing_allowance` else Accounts Settings global (`:852-916`); if `overflow% − allowance > 0.01` and user lacks `role_allowed_to_over_bill`, throw with `max_allowed = ordered × (100+allowance)/100`. This is the only "validate against remaining balance" logic for D23.03.

**Payment hold checks**
- Invoice: `invoice_is_blocked = on_hold and (no release_date or release_date > today)` (`purchase_invoice.py:261-262`); release date must be in the future (`:395`); `block_invoice`/`unblock_invoice`/`change_release_date` set fields via db_set (`:918-948`); `before_save` clears `release_date` when not on hold (`:257`).
- Supplier: `is_blocked_for(hold_type)` = `on_hold and hold_type in (All, hold_type) and (no release_date or today < release_date)` (`buying/doctype/supplier/supplier.py:104-110`). Scope per doctype (`controllers/accounts_controller.py:164-190`): PO/PI → "Invoices"; Purchase Receipt/Supplier Quotation/RFQ → "All"; Payment Entry to Supplier → "Payments"; bank/cash credit Journal Entry also checked. Payment Entry `validate` calls `ensure_supplier_is_not_blocked` (`payment_entry.py:196`).
- Outstanding-invoice fetch for payment excludes held suppliers by `release_date is null or release_date <= CURRENT_DATE` (`payment_entry.py:2404`).
- Odoo: `action_toggle_block_payment` (`account_move.py:7091-7098`) toggles `payment_state` between blocked and recomputed; blocking a paid/in_payment invoice is refused; register-payment rejects blocked moves (`account_move.py:6741`, `wizard/account_payment_register.py:1051`); `_compute_payment_state` leaves `blocked` untouched (`account_move.py:1281`).

**Threshold-based withholding** (`erpnext/erpnext/accounts/doctype/tax_withholding_entry/tax_withholding_entry.py`) — reusable for variable retention (rate change at a threshold):
- Threshold crossed (`:581-620`): manual override → true; transaction-only mode → `taxable ≥ single_threshold`; `cumulative_threshold == 0` → true; tax-on-excess → true; otherwise sum prior entries for party/tax_id, category, company, date window (`:636-657`): any `Settled` → true ("once deducted, always deducted"); else `remaining = cumulative − Σ under_withheld`, also capped by `single_threshold`, crossed if `taxable ≥ remaining`.
- Entry creation (`:400-433`): not crossed → one Under Withheld entry with zero withholding; tax-on-excess → first a Threshold Exemption slice `min(unused_threshold, taxable)` (`:446-455`, unused = cumulative − exempted so far `:622`); then net prior under/over-withheld entries, apply lower-deduction certificates, then regular entries.
- Amount (`:1069`): `taxable × rate / 100`, optional round to integer.
- Status (`:60-73`): no withholding voucher and no reason → Under Withheld; no taxable voucher → Over Withheld; else Settled.

**Payment request amount guard** (`payment_request.py:198-225`): sum of existing requests + this one must not exceed the reference document amount. Status recompute on payment allocation (`:1219-1243`): `outstanding = outstanding − allocated`; negative → throw; `== grand_total` → Initiated/Requested; `0` → Paid; `>0` → Partially Paid.

**Odoo payment move construction** (`account_payment.py:356-420`): liquidity line = ±amount minus withholding lines; counterpart = −liquidity − write-off − withholding. `_prepare_move_withholding_lines` (`:319`) is an empty hook, so withholding-at-payment is extension-only in base; write-off and withholding lines are mutually exclusive (`:380`).

**Odoo invoice payment_state** (`account_move.py:1271-1362`): from partial reconciles grouped per receivable/payable line: residual zero and all linked payments matched to bank → paid; residual zero but unmatched → in_payment; residual zero with only refunds → reversed; residual nonzero with any reconcile → partial; else not_paid.

## State machines and workflows

**ERPNext Purchase Invoice status** (`purchase_invoice.py:950-986`), evaluated on submitted docs in order: Internal Transfer → Overdue (`is_overdue`) → Partly Paid (`0 < outstanding < total`) → Unpaid (`outstanding > 0` and due ≥ today) → Debit Note Issued → Return → Paid (`outstanding ≤ 0`) → Submitted. docstatus 2 → Cancelled; 0 → Draft. `is_overdue` (`accounts/doctype/sales_invoice/services/status.py:96-116`): without schedule `due_date < today`; with schedule, overdue when `total − outstanding < Σ payment_amount of rows due before today`.

**Payment Entry**: Draft → Submitted → Cancelled, from docstatus (`payment_entry.py:944-952`); `payment_order_status` Initiated → Payment Ordered set by Payment Order submit, reverted on cancel (`payment_order/payment_order.py:38-56`).

**Payment Request**: Draft → (submit) Initiated (Outward) or Requested (Inward) (`payment_request.py:281-284`) → Partially Paid / Paid via Payment Entry allocation (`:1238-1243`) or `set_as_paid` (`:539`); Payment Ordered via Payment Order; Failed (`set_failed` `:684`); Cancelled on discard/cancel (`:129`, `:687`).

**Tax Withholding Entry**: Under Withheld / Over Withheld → Settled when the counterpart voucher is linked; Cancelled with docstatus 2.

**Odoo account.payment** (`account_payment.py:495-518`, `:1202-1247`): draft → (action_post; outbound requires `partner_bank_id.allow_out_payment` when the method requires a bank) paid → reconciled (liquidity residual zero, or all reconciled bills paid on non-cash outstanding account, or `action_validate`); any → rejected (`action_reject`); any → canceled (`action_cancel` deletes draft move / cancels posted); → draft (`action_draft`).

**Odoo account.move payment_state**: not_paid ↔ partial ↔ in_payment → paid; reversed; blocked is a manual toggle that suspends computation.

**Odoo purchase approval** (`odoo/addons/purchase/models/purchase_order.py:108-114`, `:698-722`, `:1333-1341`): draft/sent → `button_confirm` → if `_approval_allowed` then purchase else "to approve"; `_approval_allowed` = company `po_double_validation == one_step`, or two_step and `amount_total < po_double_validation_amount` (converted), or user in purchase manager group. `button_approve` sets purchase + `date_approve`, locks if `po_lock == lock`.

**Approval routing for invoices**: ERPNext ships no hard-coded invoice approval; routing is configured with frappe Workflow on Purchase Invoice (see D24: role per transition, condition expressions such as `doc.grand_total > X`, self-approval flag, docstatus mapping).

## Cross-domain links

- Purchase Invoice / Purchase Order → Supplier (procurement/subcontracts domain), Project (project setup), Cost Center/Account (budget and cost domains).
- Payment Entry → Bank Account, Account, Project; Payment Ledger Entry and GL Entry (accounting/cost control domain).
- Bank Guarantee → Project, Supplier/Customer (bonds; contract/subcontract domain).
- Approval routing and holds depend on D24 (frappe Workflow, Workflow Action, Assignment Rule, Notification).
- Audit trail: frappe Version/Comment (D24.07) on every payment doctype.
- Change orders (D23.10) would reference the contract/change-management domain entities; nothing in sources links them to payments.

## Gaps

- **Contract hierarchy and SOV (D23.01, D23.03, D23.08, D23.10)**: need `contract(id, parent_contract_id, project_id, vendor_id, original_value, retention_policy_id)`, `sov_line(contract_id, code, description, scheduled_value, change_order_id nullable, version)`, `sov_revision`. Pay request lines: `this_period_pct | this_period_amount`, `stored_materials`, `previous_billed`, `completed_to_date = previous + this + stored`, `balance_to_finish = scheduled − completed_to_date`; reject when completed_to_date > scheduled (reuse ERPNext allowance check shape). G702 assembly = Σ approved sub lines + GC lines, retention per line, `current_payment_due = completed_to_date − retention − previous_certificates`.
- **Draws (D23.02)**: `draw(project_id, number, period_end, sub_invoice_due, gc_review_due, owner_due, status)`, with a frappe-style workflow Open → Invoicing → GC Review → Owner/Lender Approval → Funded → Paid → Closed and deadline reminders (D24.04).
- **Retention (D23.04)**: `retention_policy(rate_steps[{until_pct_complete, rate}], include_stored_materials)`; per line `retention_held = rate(pct_complete) × (work_completed [+ stored])`; release requests as their own invoice type. The ERPNext Tax Withholding Entry pattern (taxable voucher vs withholding voucher, Under/Over/Settled status, cumulative threshold query) maps directly to held/released retention.
- **Lien waivers (D23.05)**: `lien_waiver(payment_id|draw_id, contract_id, sub_tier_vendor_id, type {conditional, unconditional} × {progress, final}, state_form_template, amount, through_date, signer, signed_at, status)`; amount defaults from approved payment; payment release guard = ERPNext `on_hold` / Odoo `blocked` primitive driven by "required waivers not received".
- **Compliance (D23.06)**: `compliance_requirement(contract_id, type, required, expires_on, document_id, status)`; nightly expiry sweep (reuse frappe Date Based automation, D24.04) that sets Supplier `on_hold` with `hold_type = Payments` and notifies.
- **E-signature (D23.11)**: no OSS source; needs signer identity, document hash, signed artifact, and the rule "invoice number required before signature".
- **Disbursement (D23.09)**: no ACH/NACHA or joint-check model; Payment Order references give bank account per line but no file export or funds-flow chain owner → GC → subs.
- **Fees (D23.13)**: fee schedule table by contract value bands; no source.
