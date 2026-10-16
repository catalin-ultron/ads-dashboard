# D19 Commitments and Contracts

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D19.01 | Base commitments (subcontracts, POs) | ERPNext Purchase Order; Odoo purchase.order; iDempiere C_Order + C_ProjectLine.CommittedAmt | partial | PO with lines, CBS keys, payment terms, approval, budget check; no retainage %, insurance, bonds, SOV lines on the commitment |
| D19.02 | Commitment summaries | ERPNext PO `per_received`/`per_billed`/`billed_amt`/`advance_paid`; iDempiere project Committed/Invoiced roll-up | partial | Billed and received % per PO; no revised value = base + COs, no retainage held/released |
| D19.03 | POs, amendments, three-way match | ERPNext Purchase Invoice ↔ PO ↔ Purchase Receipt (status updater, `po_required`, `pr_required`); iDempiere M_MatchPO price tolerance; Odoo purchase.bill.line.match; ERPNext `update_child_qty_rate` | full | Qty/amount overflow with allowance and override role; price match tolerance; post-submit line amendment with guards |
| D19.04 | Contract administration | Odoo purchase.requisition (agreement dates); ERPNext Purchase Invoice hold/release date | partial | Start/end dates and validity; no clause library, notice periods, insurance certificates, time-bar notices |
| D19.05 | Owner / prime contracts (revenue side) | ERPNext Project (sales order, billed, gross margin); iDempiere C_Project PlannedMarginAmt, SO commitment | partial | Margin = billed − cost; no prime contract entity with owner COs |
| D19.06 | Contract types and pricing | iDempiere `ProjInvoiceRule` (Committed Amount, Product Qty, T&M, T&M max committed) + `IsCommitCeiling`; Odoo `purchase_method` (ordered vs received qty) | partial | Lump sum vs unit vs T&M with ceiling exist; no cost-plus fee %, GMP savings share |
| D19.07 | Bid / procurement (RFB) | iDempiere C_RfQ / C_RfQResponse ranking + RfQCreatePO; ERPNext RFQ + Supplier Quotation + comparison report; Odoo purchase.requisition (alternatives) | full | Invited vendors, response completeness, line/total ranking, winner → PO; sealed-bid opening absent |

## Storage model

### ERPNext
- **Purchase Order** (`erpnext/erpnext/buying/doctype/purchase_order/purchase_order.json`, submittable, `PUR-ORD-.YYYY.-`): `supplier`*, `company`*, `transaction_date`*, `schedule_date`, `project`, `cost_center`, `currency`*, `conversion_rate`*, `items` Table(Purchase Order Item)*, `taxes` Table, `grand_total`, `base_grand_total`, `rounded_total`, `advance_paid`, `advance_payment_status` (Not Initiated|Initiated|Partially Paid|Fully Paid), `payment_terms_template`, `payment_schedule` Table(Payment Schedule), `per_received`, `per_billed`, `status` (Draft|On Hold|To Pay|To Receive and Bill|To Bill|To Receive|Completed|Cancelled, plus Closed/Delivered from status map), `ref_sq` Link(Supplier Quotation), `amended_from`, `is_subcontracted`, `tc_name`/`terms`.
- **Purchase Order Item** (fields used by logic): `qty`, `stock_qty`, `rate`, `amount`, `received_qty`, `billed_amt`, `expense_account`, `project`, `cost_center`, dimension columns, `material_request`, `closed` (`budget.py:717-743`, `purchase_order/services/status.py:61-75`).
- **Purchase Invoice Item → PO link**: `purchase_order`, `po_detail`, `purchase_receipt`, `pr_detail`, `project`, `base_net_amount` (`erpnext/erpnext/accounts/doctype/purchase_invoice/purchase_invoice.py:226-244,469-494`).
- **Request for Quotation** (`buying/doctype/request_for_quotation/request_for_quotation.json`): `company`*, `transaction_date`*, `schedule_date`, `subject`*, `suppliers` Table(supplier*, contact, email_id, send_email, email_sent, `quote_status` Pending|Received), `items` Table, `status` (Draft|Submitted|Cancelled), `message_for_supplier`, `terms`, `opportunity`.
- **Supplier Quotation** (`supplier_quotation.json`, submittable): `supplier`*, `transaction_date`*, `items` (with `request_for_quotation_item` link), totals, `taxes`, `valid_till`, `status`.
- **Payment Terms Template / Payment Schedule** on PO (see D21): `invoice_portion`, `due_date_based_on`, `credit_days`, `credit_months`, `discount`.

### Odoo
- **purchase.order** (`odoo/addons/purchase/models/purchase_order.py`): `state` (draft RFQ, sent, to approve, purchase, cancel) (`:108-114`), `locked`, `invoice_status` (no|to invoice|invoiced) (`:131`), `receipt_status` (pending|partial|full) (`:189-193`), `date_approve`, `amount_total`, `partner_id`, `currency_id`, `payment_term_id`, `requisition_id` (`purchase_requisition/models/purchase.py:10`), `project_id` (project_purchase).
- **purchase.order.line** (`purchase/models/purchase_order_line.py`): `product_qty`, `qty_received`, `qty_invoiced`, `qty_to_invoice` (`:83`), `price_unit`, `analytic_distribution` (mixin), `invoice_lines`.
- **purchase.requisition** (`purchase_requisition/models/purchase_requisition.py:8-45`): `name` (sequence per type), `requisition_type` (blanket_order|purchase_template), `vendor_id`, `date_start`, `date_end`, `state` (draft|confirmed|done|cancel), `purchase_ids` O2M purchase.order, `line_ids`, `currency_id`. **purchase.requisition.line** (`:163-196`): `product_id`, `product_qty`, `price_unit`, `price_subtotal`, `qty_ordered` (computed), `uom_id`, `analytic_distribution`, `supplier_info_ids`, `display_type` section/subsection/note.
- **purchase.bill.line.match** (`purchase/models/purchase_bill_line_match.py:7-40`): SQL view union of PO lines and bill lines: `pol_id`, `aml_id`, `qty_invoiced`, `qty_to_invoice`, `line_amount_untaxed`, `matching_id`, `purchase_order_id`, `account_move_id`.

### iDempiere
- **C_Project** commitment fields: `IsCommitment`, `IsCommitCeiling`, `CommittedAmt`, `CommittedQty`, `InvoicedAmt`, `ProjInvoiceRule` (`-` None, `C` Committed Amount, `P` Product Quantity, `T` Time & Material, `c` T&M max Committed) (`idempiere/org.adempiere.base/src/org/compiere/model/X_C_Project.java:961-969`), `ProjectCategory` (Asset, General, Service Charge, Work Order) (`:1009-1015`).
- **C_ProjectLine**: `C_OrderPO_ID` (generated PO), `CommittedAmt/Qty`, `InvoicedAmt/Qty`, `PlannedQty/Price/Amt` (`I_C_ProjectLine.java`).
- **M_MatchPO**: `C_OrderLine_ID`, `C_InvoiceLine_ID`, `M_InOutLine_ID`, `Qty`, `PriceMatchDifference`, `IsApproved` (`MMatchPO.java`).
- **C_RfQ** (`X_C_RfQ.java`): `C_RfQ_Topic_ID`, `QuoteType`, `IsQuoteTotalAmt`, `IsQuoteAllQty`, `IsInvitedVendorsOnly`, `IsRfQResponseAccepted`, `DateResponse`, `DateWorkStart`, `DateWorkComplete`, `DeliveryDays`, `Margin`, `C_Currency_ID`, `C_Order_ID`, `Processed`. **C_RfQLine** → **C_RfQLineQty** (`IsRfQQty`, `IsPurchaseQty`, `BestResponseAmt`). **C_RfQResponse** (`X_C_RfQResponse.java`): `C_BPartner_ID`, `DateInvited`, `DateResponse`, `Price`, `IsComplete`, `IsSelectedWinner`, `Ranking`, `C_Order_ID`. **C_RfQResponseLine** (`IsSelectedWinner`) → **C_RfQResponseLineQty** (`Price`, `Discount`, `Ranking`).

## Algorithms and logic

### Commitment approval and budget check
- ERPNext: on PO submit each item runs `validate_expense_against_budget` with doctype "Purchase Order" (`erpnext/erpnext/controllers/buying_controller.py:1295-1312`); amount = open ordered value; actions per budget `action_if_annual_budget_exceeded_on_po` etc. (`erpnext/erpnext/accounts/doctype/budget/budget.py:674-686`).
- Odoo `button_confirm` (`purchase_order.py:708-721`): only from draft/sent; `_confirmation_error_message`; `order_line._validate_analytic_distribution()` (100% on mandatory plans); if `_approval_allowed` → `button_approve` else state `to approve`. `_approval_allowed` (`:1332-1341`): company `po_double_validation == one_step`, or two_step and `amount_total < po_double_validation_amount` converted to PO currency, or user in `purchase.group_purchase_manager`. `button_approve` sets `purchase`, `date_approve`, and locks if `lock_confirmed_po == lock` (`:698-702`).
- iDempiere commitment posting on PO completion (see D18): POST_Commitment DR expense / CR CommitmentOffset (`idempiere/org.idempiere.acct/src/org/idempiere/acct/doc/Doc_Order.java:336-375`).

### Commitment summary metrics
- ERPNext `update_receiving_percentage`: `per_received = Σ min(received_qty, qty) / Σ qty × 100` over non-closed items (all items if all closed) (`purchase_order/services/status.py:61-69`). Billing %: `get_percent_billed_by_qty` uses invoiced qty against billable qty (`:71-75`); status updater keeps `billed_amt` per PO item from PI items (`purchase_invoice.py:226-244`).
- Remaining to bill (inferred from fields): `amount − billed_amt` per line, the same term used as open commitment in budget control (`budget.py:717-743`).
- iDempiere project header: Σ CommittedAmt / InvoicedAmt from project lines, also to phase and task (`MProjectLine.java:280-328`). `ProjectGenPO` creates PO lines from project lines (`qty = PlannedQty`) and writes `C_OrderPO_ID` back (`idempiere/org.adempiere.base.process/src/org/compiere/process/ProjectGenPO.java:175-206`).
- Odoo `qty_to_invoice` = `product_qty − qty_invoiced` when product `purchase_method == purchase` (bill on ordered), else `qty_received − qty_invoiced` (`purchase_order_line.py:211-223`); `invoice_status` derived (`purchase_order.py:49-71`).

### Three-way match
- ERPNext link integrity (`purchase_invoice.py:469-504`): PI header must equal PO/PR on supplier, company, currency; PI item must equal PO item / PR item on project, item_code, uom; optional same-rate enforcement (`Buying Settings.maintain_same_rate`).
- Mandatory upstream docs: `po_required` (Buying Settings = Yes, not internal, supplier not exempt) blocks PI items without `purchase_order` (`:531-550`); `pr_required` blocks stock/asset items without `purchase_receipt` unless `update_stock` or supplier exempt (`:552-572`).
- Overflow (`erpnext/erpnext/controllers/status_updater.py:492-540`): `overflow % = (target_field − target_ref_field)/target_ref_field × 100` (e.g. PO item `billed_amt` vs `amount`); allowed = item `over_billing_allowance` or Accounts Settings global (`:852-918`); if overflow − allowance > 0.01 → error with `max_allowed = ref × (100+allowance)/100`, unless user has `role_allowed_to_over_bill` (warn only). Rule "Invoice ≤ Approved PO" is this check with allowance 0.
- iDempiere price match (`MMatchPO.java:1069-1101`): `difference = (PO PriceActual − Invoice PriceActual) × Qty`; tolerance = PO amount × BP Group `PriceMatchTolerance` / 100; `IsApproved = |difference| ≤ tolerance`; zero difference auto-approved. Match updates `QtyDelivered`/`QtyInvoiced` on the order line (`:1191-1213`).
- Odoo `purchase.bill.line.match` exposes unmatched PO lines and bill lines; `action_match_lines` links bill lines to PO lines, `action_add_to_po` appends bill lines to a PO (`purchase_bill_line_match.py:186-255`).

### PO amendment after submit (ERPNext `erpnext/erpnext/accounts/services/child_item_update.py`)
- Guards: permission per action (`:246-256`), workflow condition (`:258-278`), parent not Closed/On Hold/Delivered (`:280-290`), qty > 0 unless allowed, new stock qty ≥ received qty (`:353-394`), cannot delete received/billed/ordered rows (`:495-532`), blanket order still open (`:324-335`).
- Post-update (`:143-213`): recompute taxes/totals, approving authority on new grand total, regenerate payment schedule, re-run `validate_budget`, update requested/ordered qty and receiving %, save. Cancel-and-amend (`amended_from`) is the alternative full revision path.

### Blanket orders (Odoo `purchase_requisition.py`)
- `action_confirm` (`:129-139`): blanket lines need price > 0 and qty > 0; creates `product.supplierinfo` per line so PO prices default from the agreement.
- PO from agreement (`purchase_requisition/models/purchase.py:13-73`): copies partner, payment terms, fiscal position, currency, `date_order = max(now, date_start)`; lines get agreement price; qty = agreement qty for purchase_template, 0 for blanket_order (call-off). Line price recompute prefers same-UoM requisition line (`:106-130`).
- `qty_ordered` = Σ confirmed PO line qty (UoM converted) per product (`purchase_requisition.py:232-250`); drawdown remaining = `product_qty − qty_ordered` (inferred).
- Warning when vendor already has an open confirmed blanket order (`:47-62`); dates validated `date_end ≥ date_start` (`:77-83`); adding lines to a confirmed blanket order requires price > 0 (`:268-285`).

### Contract pricing rules (iDempiere)
`ProjInvoiceRule` per project/phase selects billing basis: committed amount (lump sum), product quantity (unit price), time & material, or T&M capped at committed (`X_C_Project.java:961-969`); `IsCommitCeiling` marks committed amount as ceiling (`I_C_Project.java`, `I_C_ProjectPhase.java`). Billing generation code for these rules is outside the cloned files.

### Bid evaluation and award
- iDempiere response completeness `MRfQResponse.checkComplete` (`MRfQResponse.java:309-360`): total amount required if `IsQuoteTotalAmt`; every line needs a positive net amount if quote-all-lines; total-only RfQ allows one qty per line (`MRfQ.java:283-302`).
- Net amount = `Price × (100 − Discount)/100` (`MRfQResponseLineQty.java:153-165`); invalid or ≤ 0 → ranking 999.
- `RfQResponseRank.rankLines` (`idempiere/org.adempiere.base.process/src/org/compiere/process/RfQResponseRank.java:112-245`): per RfQ line qty, sort responses by net amount, dense ranking (ties share rank), best amount stored on `BestResponseAmt`; per response `Ranking = Σ line ranks`; line winner = rank 1 on purchase qty; overall winner = lowest positive total rank (unless selected-lines quoting). `rankResponses` (`:253-278`): total-only → order by price, rank 1 winner, missing price 999. Single response wins automatically (`:90-95`).
- `RfQCreatePO` creates a PO for the overall winner, or per line winners, pricing from winning response qty with `IsPurchaseQty` (`RfQCreatePO.java:91-137`).
- ERPNext: `update_rfq_supplier_status` sets supplier `quote_status = Received` only when submitted SQ items exist for every RFQ item (`request_for_quotation.py:394-421`); comparison report computes price per stock unit and flags the minimum per item (`buying/report/supplier_quotation_comparison/supplier_quotation_comparison.py:101-185`).

## State machines and workflows
- **ERPNext Purchase Order** (`erpnext/erpnext/controllers/status_updater.py:85-108`): Draft (docstatus 0) → on submit status by rule: To Receive and Bill (rec<100, bill<100), To Bill (rec≥100, bill<100), To Receive (rec<100, bill=100), Completed (rec≥100, bill=100), To Pay (advance initiated); manual On Hold / Closed (`purchase_order.py:617-668`, allowed targets Draft|Submitted|On Hold|Closed); Cancelled (docstatus 2). Reopen from Closed validated (`purchase_order/services/status.py:27-29`); concurrent modification check (`:51-59`).
- **Odoo purchase.order**: draft → sent (`button_*` send, `:696`) → to approve → purchase; draft/sent → purchase directly when approval allowed; any → cancel only if unlocked and no non-draft bills (`:723-731`); `button_draft` back to draft; lock/unlock flag.
- **Odoo purchase.requisition**: draft → confirmed (`action_confirm`) → done (`action_done`, blocked while related RFQs are draft/sent/to approve, `:145-155`); any → cancel (cancels draft POs, `:118-127`); confirmed → draft; delete only draft/cancel (`:157-160`); type/company change only in draft (`:97-111`).
- **ERPNext RFQ**: Draft → Submitted → Cancelled; supplier rows Pending → Received.
- **iDempiere RfQ response**: invited → responded → complete (checkComplete) → ranked → winner → PO created.

## Cross-domain links
- PO lines carry CBS keys (project, cost center, analytic distribution) from D17; budget control and encumbrance in D17/D18.
- Change orders on commitments (D20) are realised as PO amendments (`update_child_qty_rate`) or cancel-and-amend.
- Invoices, payments, retention and SOV (D21) consume `billed_amt`, payment schedule; cash flow of commitments (D22.07) from payment schedule.
- Approval routing via D24 (Frappe workflow, Odoo double validation); vendor master and portal users from D02/D01.
- Document attachments (contracts, certificates) in D25.

## Gaps
- Commitment header attributes: type (subcontract/PO/service), retainage %, insurance and bond records with expiry, key dates, SOV lines per commitment.
- Commitment summary with Revised = Base + Approved COs, Pending COs, Invoiced, Paid, Retainage held/released, Remaining, % billed.
- Contract clause library, notice periods, time-bar calculators (NEC early warning / compensation event deadlines) with reminders.
- Prime contract entity with owner change orders and margin = revenue commitments − cost commitments.
- Cost-plus (cost + fee %, GMP cap, savings share split) billing calculations.
- Sealed bids: responses encrypted or hidden until closing time, then opened; bid leveling sheet with normalisation adjustments and qualification notes; award → commitment with SOV from bid items.
