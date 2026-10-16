# D21 Invoicing, Schedule of Values and Spends

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D21.01 | Schedule of Values sheets | iDempiere C_ProjectPhase/C_ProjectLine (planned qty/price/amt per phase); IFC PRICEDBILLOFQUANTITIES cost schedule | partial | Line structure with scheduled value exists; no SOV auto-built from contract + COs, no payment-app vs general-spends types |
| D21.02 | Payment applications (pay apps) | none | none | No G702/G703 period arithmetic (previous, this period, stored materials, % complete, balance to finish) |
| D21.03 | Invoices and general spends | ERPNext Purchase Invoice; Odoo account.move (in_invoice) | full | Vendor, PO ref, lines, tax, totals, ≤ PO rule via over-billing allowance, posting to project cost and analytic actuals |
| D21.04 | Payments | ERPNext Payment Entry + Payment Schedule; Odoo account.payment / payment_state; iDempiere C_InvoicePaySchedule | full | Allocation to invoices and terms, outstanding, overdue, partial/paid states |
| D21.05 | Retainage tracking | none | none | No retention %, held or released amounts in any source |
| D21.06 | Payment-to-ERP | ERPNext / Odoo are the AP ledger themselves | partial | Approved invoice posts GL payable; no outbound integration contract |

## Storage model

### ERPNext invoice and payment
- **Purchase Invoice** (`erpnext/erpnext/accounts/doctype/purchase_invoice/purchase_invoice.json`, submittable): `supplier`*, `bill_no`, `bill_date`, `posting_date`, `due_date`, `project`, `items` (Purchase Invoice Item with `purchase_order`, `po_detail`, `purchase_receipt`, `pr_detail`, `project`, `cost_center`, `expense_account`, `base_net_amount`), `taxes`, `grand_total`, `base_grand_total`, `total_advance`, `write_off_amount`, `outstanding_amount`, `paid_amount`, `payment_schedule` Table(Payment Schedule), `on_hold`, `release_date`, `hold_comment`, `is_return`, `return_against`, `update_billed_amount_in_purchase_order`, `update_stock`, `apply_tds`, `tax_withholding_entries`, `status` (Draft|Return|Debit Note Issued|Submitted|Paid|Partly Paid|Unpaid|Overdue|Cancelled|Internal Transfer).
- **Payment Schedule** (child, `accounts/doctype/payment_schedule/payment_schedule.json`): `payment_term`, `due_date`*, `invoice_portion` %, `payment_amount`*, `base_payment_amount`, `paid_amount`, `base_paid_amount`, `outstanding`, `base_outstanding`, `discounted_amount`, `discount_type`, `discount`, `discount_date`, `mode_of_payment`, `due_date_based_on`, `credit_days`, `credit_months`.
- **Payment Term** (`payment_term/payment_term.json`): `invoice_portion`, `due_date_based_on` (Day(s) after invoice date | Day(s) after the end of the invoice month | Month(s) after the end of the invoice month), `credit_days`, `credit_months`, `discount_type`, `discount`, `discount_validity_based_on`, `discount_validity`. **Payment Terms Template** with detail rows of the same shape plus `allocate_payment_based_on_payment_terms`.
- **Payment Entry** (`payment_entry/payment_entry.json`): `payment_type` (Receive|Pay|Internal Transfer)*, `posting_date`*, `party_type`, `party`, `paid_amount`*, `received_amount`*, `references` Table(Payment Entry Reference), `deductions` Table, `unallocated_amount`, `reference_no` (cheque/UTR), `reference_date`, `mode_of_payment`, `project`, `cost_center`, `status` (Draft|Submitted|Cancelled).
- **Payment Entry Reference** (`payment_entry_reference/payment_entry_reference.json`): `reference_doctype`*, `reference_name`* (Dynamic Link), `due_date`, `bill_no`, `total_amount`, `outstanding_amount`, `allocated_amount`, `exchange_rate`, `payment_term`, `payment_term_outstanding`, `payment_request`, `exchange_gain_loss`, `account`.

### Odoo
- **account.move** (`odoo/addons/account/models/account_move.py`): `move_type` (in_invoice, in_refund, ...), `state` draft|posted|cancel (`:139-150`), `payment_state` (not_paid, in_payment, paid, partial, reversed, blocked, invoicing_legacy) (`:619-624`), `status_in_payment` (`:625-635`), `amount_residual` (`:578`), `invoice_date_due`, `invoice_payment_term_id`, `matched_payment_ids`.
- **account.move.line**: `balance`, `amount_residual`, `analytic_distribution`, `purchase_line_id` (`purchase/models/purchase_order_line.py:787-791`), `account_id`; payable lines reconcile through **account.partial.reconcile** / **account.full.reconcile**.
- **account.payment.term** (`account/models/account_payment_term.py:10-45`): `line_ids`, `early_discount`, `discount_percentage`, `discount_days`, `early_pay_discount_computation`. **account.payment.term.line** (`:275-301`): `value` percent|fixed, `value_amount`, `delay_type` (days_after | days_after_end_of_month | days_after_end_of_next_month | days_end_of_month_on_the), `nb_days`, `days_next_month`.

### iDempiere
- **C_ProjectPhase / C_ProjectLine** as value breakdown: phase `PlannedAmt`, `Qty`, `PriceActual`, `IsComplete`, `C_Order_ID`, `ProjInvoiceRule`; line `PlannedQty`, `PlannedPrice`, `PlannedAmt`, `InvoicedAmt`, `InvoicedQty` (`idempiere/org.adempiere.base/src/org/compiere/model/I_C_ProjectPhase.java`, `I_C_ProjectLine.java`).
- **C_PaySchedule / C_InvoicePaySchedule** (`MPaySchedule.java`, `MInvoicePaySchedule.java`): per-invoice instalments with due date and amount.

### IFC
- **IfcCostSchedule** PredefinedType `PRICEDBILLOFQUANTITIES` / `UNPRICEDBILLOFQUANTITIES` with nested IfcCostItem lines (quantity × rate) (`ifcopenshell/src/ifcopenshell-python/ifcopenshell/util/cost.py:303-319`), usable as an SOV-shaped tree.

## Algorithms and logic

### Invoice validation against commitment
- Header/line consistency with PO and receipt, mandatory PO/receipt, same rate (`purchase_invoice.py:469-572`; detail in D19).
- Over-billing: PI item `amount` accumulates into PO item `billed_amt`; overflow vs PO `amount` beyond allowance blocks unless role `role_allowed_to_over_bill` (`purchase_invoice.py:226-244`, `erpnext/erpnext/controllers/status_updater.py:492-540`). Returns update billed amount only when `update_billed_amount_in_purchase_order` (`purchase_invoice.py:239-241`).
- Budget check at GL posting with the posted expense amount (`erpnext/erpnext/accounts/general_ledger.py:180-183,394`).
- Odoo: analytic distribution must be 100% on mandatory plans at posting (`account/models/account_move_line.py:3534-3565`).

### Posting to Spends / actuals
- ERPNext project: on PI submit/cancel, `total_purchase_cost += / −= Σ item base_net_amount` per project with row lock, then gross margin recomputed (`purchase_invoice.py:867-884`).
- Odoo: `_create_analytic_lines` on post creates analytic lines per distribution key with `category = 'vendor_bill'` (`account_move_line.py:3567-3631`).
- iDempiere: Doc_Invoice POST_Actual facts DR expense per line, CR vendor liability (`idempiere/org.idempiere.acct/src/org/idempiere/acct/doc/Doc_Invoice.java:428-860`); commitment released on invoice match (D18).

### Payment schedule generation (ERPNext `erpnext/erpnext/accounts/services/payment_schedule.py`)
1. Skip for POS sales and opening entries (`:20-22`). Base date = `bill_date` or `posting_date` or `transaction_date` (`:30`).
2. Amount basis = rounded total or grand total, minus write-off (invoices), minus `total_advance` (in company or party currency) (`:33-56`).
3. If no rows: fetch from linked order when "automatically fetch payment terms" and order has terms; else expand template (`_get_payment_terms`); else one row 100% due at `due_date` (`:58-84`).
4. Per row with `invoice_portion`: `payment_amount = grand_total × portion/100`, outstanding = payment_amount (`:96-107`).
5. Term due date (`:425-434`): days after invoice date → `date + credit_days`; days after end of invoice month → `last_day(date) + credit_days`; months after end of invoice month → `last_day(date + credit_months)`. Early discount date computed the same way (`:437-446`); due date never before posting date (`:419-420`).
6. Validation: Σ payment_amount equals grand total within 0.1 in both currencies (`:247-296`).

### Odoo instalments (`account_payment_term.py:155-255`)
- Terms must have percent lines summing to 100; early discount only with single 100% line (`:155-167`).
- `_compute_terms`: per line, fixed → `value_amount` (converted at document rate), percent → `total × pct/100`; the last line always takes the residual; due date by `delay_type` (`:303-320`); early discount balance either on total or on untaxed part (excluded/mixed) (`:197-206`).

### Payment allocation and outstanding (ERPNext `payment_entry.py`)
- `allocate_amount_to_references` (`:1660-1760`): for Pay to Supplier: positive outstanding total vs paid amount (after deductions); allocated positive = paid + offsetting negatives (debit notes); then greedily fill each reference `allocated = min(remaining, outstanding)` in row order; negative outstandings consume from the negative pool.
- `validate_allocated_amount` (`:374-395`): allocated ≤ outstanding per row (and sign-aware for negatives); for Customer/Supplier rechecked against latest outstanding (`:432`).
- `update_payment_schedule` (`:826-943`): per (payment_term, invoice) accumulate allocated amount; discounted amount = total × discount% or fixed; `paid_amount += allocated − discount`, `outstanding −= allocated`, mirrored on cancel; unknown term on invoice throws (`:861-863`).

### Invoice status (ERPNext `purchase_invoice.py:950-987`, `erpnext/erpnext/accounts/doctype/sales_invoice/services/status.py:96-117`)
- Overdue = outstanding > 0 and paid so far < Σ schedule amounts with due_date < today (or due_date < today if no schedule).
- Else Partly Paid if 0 < outstanding < total; Unpaid if outstanding > 0 and due date ≥ today; Debit Note Issued if a submitted return exists; Return if is_return; Paid if outstanding ≤ 0.
- Hold: `block_invoice` sets `on_hold`, `release_date`, `hold_comment`; only invoices with outstanding > 0 can be held; `unblock_invoice` clears (`:918-948`).

### Odoo payment state (`account_move.py:1271-1365`)
- residual zero and reconciled with payments/statement lines: `paid` if all payments matched to bank, else `in_payment`; residual zero without payment: `paid` or `reversed` when the only counterparts are refunds.
- residual non-zero with reconciliations → `partial`; registered but not yet journalled payments → `in_payment`.

### Value breakdown roll-up (iDempiere)
Line `PlannedAmt = PlannedQty × PlannedPrice`; phase and project totals recomputed by SQL sums after each line save (`MProjectLine.java:206-328`). Invoiced amounts per line feed the same roll-up, giving scheduled value vs invoiced per phase (inferred SOV analogue).

## State machines and workflows
- **ERPNext Purchase Invoice**: Draft → (submit) Unpaid / Overdue / Partly Paid / Paid / Return / Debit Note Issued (computed) → Cancelled; orthogonal hold flag with release date (`purchase_invoice.py:918-987`).
- **ERPNext Payment Entry**: Draft → Submitted → Cancelled (`payment_entry.py:944-951`).
- **Odoo account.move**: draft → posted (`action_post` `:6826`, `_post` `:6139`) → cancel; `button_draft` back to draft (`:6925`); payment_state computed independently.
- **ERPNext PO billing status** moves To Bill → Completed as `per_billed` reaches 100 (`status_updater.py:85-108`).

## Cross-domain links
- Invoices reference D19 commitments (PO, receipt) and post actuals to D17 cost sheet and Odoo/ERPNext CBS keys.
- Payments and schedules drive D22 Payments and Forecast curves; D18 fund consumption on spend approval.
- Pay applications and retainage overlap with D23 payment management (lien waivers, compliance).
- Approval workflows in D24; supplier portal identities D02.

## Gaps
- SOV sheet per commitment/prime contract: lines (description, CBS, scheduled value) auto-built from contract lines and approved CO lines; types Payment Application SOV vs General Spends SOV.
- Pay application document per period with per-line: previous completed, this period, materials presently stored, total completed and stored = prev + this + stored, % = total/scheduled, balance to finish = scheduled − total, retainage on work and on stored materials; G702 summary: original sum, net COs, contract sum to date, total completed, retainage, total earned less retainage, less previous certificates, current payment due, balance to finish including retainage. Rule: Σ billed ≤ contract + approved COs.
- Retainage: % per commitment or per line (with step-down at % complete), held = Σ completed × %, release BP (partial/full) creating a payable.
- Outbound AP integration: approved invoice → external AP voucher, payment status inbound sync, idempotency keys.
