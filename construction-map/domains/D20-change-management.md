# D20 Change Management

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D20.01 | Change events / potential change orders | none (OpenProject work packages + workflows could host it, see D24) | none | No change-event entity with cause, exposure per CBS, schedule impact |
| D20.02 | Change requests / proposals (markups) | ERPNext Purchase Taxes and Charges (`charge_type` chain); Odoo account.tax (`include_base_amount`, group taxes) | partial | Simple vs compound markup arithmetic exists as tax/charge rows; no PCO/COR document |
| D20.03 | Change orders (commitment side) | ERPNext `update_child_qty_rate` on submitted PO; cancel-and-amend (`amended_from`) | partial | Line qty/rate/add/remove after approval with budget re-check; no CO document, no days added, no SOV adjustment |
| D20.04 | Owner change orders (revenue side) | ERPNext same mechanism on Sales Order (`child_item_update.py`) | partial | Sales order line amendment; no PCO bundling |
| D20.05 | Trend management | none | none | |
| D20.06 | Schedule impact linkage | none (IFC IfcCostItem controls IfcTask is the only cost↔task link) | none | No fragnet/TIA |
| D20.07 | Change order log and aging | OpenProject journals / Frappe versioning (not change-specific) | none | Audit trails exist, no aging or cycle time metrics |
| D20.08 | Allowance and contingency drawdown | ERPNext budget revision (`revise_budget`) | none | No contingency line or transfer-on-approval |

## Storage model

### ERPNext post-approval amendment
- **Purchase Order / Sales Order** with child items (see D19). Amendment request payload `trans_items` (JSON list of `docname`, `item_code`, `qty`, `rate`, `uom`, `conversion_factor`, `schedule_date`, `fg_item`, `fg_item_qty`) processed by `ChildItemUpdateService` (`erpnext/erpnext/accounts/services/child_item_update.py:30-142`); entry point `update_child_qty_rate(parent_doctype, trans_items, parent_doctype_name, child_docname)` (`:421-425`).
- **amended_from** Link on PO, Budget, PI, RFQ, SQ: cancel-and-amend chain (new document `NAME-1`, `NAME-2`; Frappe core naming, inferred from field usage).
- **Budget.revision_of** (`erpnext/erpnext/accounts/doctype/budget/budget.json`): link from revised budget to cancelled original (`budget.py:887-898`).

### Markup rows (ERPNext)
- **Purchase Taxes and Charges** (`erpnext/erpnext/accounts/doctype/purchase_taxes_and_charges/purchase_taxes_and_charges.json`): `charge_type` Select(Actual | On Net Total | On Previous Row Amount | On Previous Row Total | On Item Quantity)*, `row_id` (referenced row for previous-row types), `rate`, `tax_amount`, `total`, `add_deduct_tax` (Add|Deduct)*, `category` (Valuation and Total|Valuation|Total)*, `account_head`*, `cost_center`, `project`, `included_in_print_rate`.

### Markup rows (Odoo)
- **account.tax** (`odoo/addons/account/models/account_tax.py`): `amount_type` (group | fixed | percent | division) (`:67-68`), `amount`, `include_base_amount` "Affect Base of Subsequent Taxes" (`:131`), `is_base_affected` (`:133`), `sequence`, children for group taxes.

## Algorithms and logic

### Post-approval line change (ERPNext `child_item_update.py`)
1. Permission per operation (`create`/`write`/`delete`) on child doctype (`:246-256`); workflow transition conditions re-evaluated (`:258-278`).
2. Parent state: PO not Closed, On Hold or Delivered (`:280-290`).
3. Per row: qty > 0 unless zero qty allowed (`:353-360`); new stock qty ≥ already received (PO) / delivered (SO) (`:363-377`); if quoted lines were already ordered, rate cannot change and qty cannot drop below ordered (`:379-394`); UoM cannot change after fulfilment (`:337-351`); blanket order must be open (`:324-335`).
4. Deleted rows must have no receipt, billing, delivery, work order or issued proforma (`:495-578`).
5. Post-update (`:143-213`): recompute taxes and totals; `Authorization Control.validate_approving_authority` on new `base_grand_total` (approval limit by amount); regenerate payment schedule; PO: minimum order qty and `validate_budget` (budget rule re-applied to the changed commitment); update requested/ordered qty and receiving %; save.
This is the OSS path for "CO approval updates commitment value and re-checks budget".

### Markup calculation: simple vs compound (ERPNext `erpnext/erpnext/controllers/taxes_and_totals.py:664-705`)
Per item and charge row in order:
- `Actual`: fixed amount distributed to items by `item.net_amount / doc.net_total`.
- `On Net Total`: `rate% × item.net_amount` (simple markup on base cost).
- `On Previous Row Amount`: `rate% × tax_amount_for_current_item` of row `row_id` (markup on a previous markup, e.g. bond on fee).
- `On Previous Row Total`: `rate% × grand_total_for_current_item` of row `row_id` (compound: markup on running total).
- `On Item Quantity`: `rate × qty`.
- `Deduct` rows negate; running `total = previous_row.total + tax_amount` (`:655-662`).
Construction markup "overhead 10% then profit 5% compound then bond 1% on total" maps to rows [On Net Total 10, On Previous Row Total 5 (row 1), On Previous Row Total 1 (row 2)].

### Odoo compound taxes (`account_tax.py`)
Taxes evaluated by sequence; a tax with `include_base_amount` adds its amount to the base of subsequent taxes flagged `is_base_affected`; `group` taxes expand children; `division` computes price-included percentage (`:1077-1100`).

### Budget revision as contingency adjustment (ERPNext `budget.py:887-898`)
Cancel + copy with `revision_of`; distribution kept when manual (`:255-256`); existing-spend guard skipped for revisions (`:195-196`). No transfer between budget lines.

## State machines and workflows
- ERPNext submitted documents are immutable except through whitelisted after-submit services (`ignore_validate_update_after_submit`, `child_item_update.py:155`) or cancel-and-amend.
- Approval routing for amendments follows Frappe Workflow and Authorization Control by amount (`child_item_update.py:164-166,258-278`; engine in D24).
- No change-event state machine (Open, Pending, Approved, Rejected, Void) in any source.

## Cross-domain links
- Commitment amendments act on D19 Purchase Orders and re-run D17 budget control.
- Owner change orders would feed D21 SOV and billing; schedule impact would reference D03 activities and D06 scheduling.
- Origin links (RFI, field issue) belong to D27/D28; approvals to D24; audit to D02/D36 journals.

## Gaps
- Change event entity: number, title, cause enum (owner request, design error, unforeseen condition, value engineering), scope text, origin link (RFI/issue), estimated cost lines per CBS, schedule impact days, status Open/Pending/Approved/Rejected/Void; posts exposure to cost sheet Pending Changes column (D17).
- PCO/COR document with vendor quote lines and markup profile per contract (rows as above, compound or simple flag, tax base selection).
- Change order BP referencing commitment, line items by CBS/SOV, amount and days; approval posts to commitment revised value, cost sheet, SOV lines, contract dates; rule Revised Budget ≥ Commitments.
- Owner CO bundling many PCOs (N:1), billing through SOV.
- Trend items as forecast adjustments before formal change.
- Schedule impact: link to activities, fragnet insertion and TIA comparison against baseline.
- Log metrics: days in status (from status-change journal), approval cycle time, cumulative change % = Σ approved COs / original contract value.
- Contingency/allowance lines with drawdown transfers on CO approval and remaining contingency.
