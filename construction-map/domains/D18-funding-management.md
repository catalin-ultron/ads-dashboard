# D18 Funding Management

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D18.01 | Fund codes and fund sheet | ERPNext Accounting Dimension + Budget; Odoo analytic plan as "Fund" root plan | partial | A fund can be modelled as a dimension with a budget ceiling; no fund type, restrictions, appropriated/allocated/consumed columns |
| D18.02 | Project funding allocation | Odoo analytic distribution models; ERPNext Budget against (dimension, project) | partial | Rule-based default distribution exists; no funding BP with approval |
| D18.03 | Fund consumption (waterfall / ratio) | Odoo analytic distribution (ratio split per posting) | partial | Ratio consumption is native; priority waterfall and unfunded tracking absent |
| D18.04 | Funding commitments (encumbrance) | iDempiere commitment/reservation accounting (Doc_Order, Doc_Requisition, Doc_MatchInv) + GL_BudgetControl | full | Requisition reserves, PO commits and reverses reservation, invoice match releases commitment |

## Storage model

### iDempiere encumbrance accounting
- **C_AcctSchema.CommitmentType** (`idempiere/org.adempiere.base/src/org/compiere/model/X_C_AcctSchema.java:364-392`): `A` PO/SO Commitment & Reservation, `B` PO Commitment & Reservation, `C` PO Commitment only, `O` PO/SO Commitment, `S` SO Commitment only, `N` None. Read through `MAcctSchema.isCreatePOCommitment()` / `isCreateReservation()`.
- **GL_BudgetControl** (`idempiere/org.idempiere.acct/src/org/idempiere/acct/base/model/X_GL_BudgetControl.java`): `C_AcctSchema_ID`, `GL_Budget_ID`, `CommitmentType` (same list, `:194-204`), `BudgetControlScope` (`P` Period only, `T` Total, `Y` Year to date, `:140-144`), `IsBeforeApproval`, `Name`, `Description`.
- **Fact postings** carry a posting type: `Fact.POST_Actual`, `Fact.POST_Commitment`, `Fact.POST_Reservation` (`idempiere/org.idempiere.acct/src/org/idempiere/acct/doc/Fact.java:78-84`). Encumbrance lines live in the same Fact_Acct table, separated by PostingType; offset account `CommitmentOffset_Acct` (purchase) / `CommitmentOffsetSales_Acct` (sales).
- **C_Project.IsCommitment, IsCommitCeiling, CommittedAmt** (`I_C_Project.java`) and **C_ProjectPhase.IsCommitCeiling, CommittedAmt** (`I_C_ProjectPhase.java`): commitment ceiling flags at project/phase level.

### Odoo analytic plans as funding sources (inferred mapping)
- **account.analytic.plan** root plan (`odoo/addons/analytic/models/analytic_plan.py:12-90`) with accounts per fund; each root plan adds a column `x_plan<id>_id` on analytic lines (`:113-119`) so every cost line carries a fund key alongside the project key.
- **analytic_distribution** JSON on cost documents (`analytic/models/analytic_mixin.py:17`) holds `{"<project_acct>,<fund_acct>": pct}`; percentages per root plan must sum 100 when the plan is mandatory (`:182-196`).
- **account.analytic.distribution.model** (`analytic/models/analytic_distribution_model.py:10-40`): `analytic_distribution` JSON*, `partner_id`, `partner_category_id`, `company_id`, `sequence` (plus `account_prefix`, `product_id`, `product_categ_id` criteria added by the `account` module, `odoo/addons/account/models/account_analytic_distribution_model.py:9-25`). Acts as an allocation rule table.

### ERPNext dimension budgets (inferred mapping)
- **Accounting Dimension** (`erpnext/erpnext/accounts/doctype/accounting_dimension/accounting_dimension.json`): `document_type` Link(DocType)*, `fieldname`. A "Fund" doctype registered here gets a column on GL Entry and on all transaction lines.
- **Budget** can be keyed on that dimension (`erpnext/erpnext/accounts/doctype/budget/budget.py:438-497` iterates `[project, cost_center] + get_accounting_dimensions()`), giving a fund ceiling per account and fiscal range.

## Algorithms and logic

### Reservation and commitment lifecycle (iDempiere)
1. **Requisition (reservation)**: `Doc_Requisition.createFacts` posts `Fact.POST_Reservation` DR expense / CR offset for requisition lines (`org.idempiere.acct/src/org/idempiere/acct/doc/Doc_Requisition.java:124`).
2. **Purchase order (commitment)** (`Doc_Order.java:336-410`): if `isCreatePOCommitment`, Fact POST_Commitment: per line DR product expense account `line.getAmtSource()`, CR `CommitmentOffset` total; missing offset account aborts posting. If `isCreateReservation`, a second Fact POST_Reservation reverses the linked requisition lines (CR expense, DR offset).
3. **Invoice match (release)**: `Doc_MatchInv` calls `Doc_Order.getCommitmentRelease(as, doc, qty, C_InvoiceLine_ID, multiplier)` when accrual accounting and PO commitment are on (`Doc_MatchInv.java:426-430,1028-1032,1348-1352`).
4. `getCommitments` (`Doc_Order.java:493-577`) finds order lines linked to the invoice line directly or via M_MatchPO; qty per line `QtyOrdered.max(maxQty)` (observed: `max`, likely intended `min`); amount = qty × PriceCost if set, else full LineNetAmt when qty equals remaining, else qty × PriceActual; tax-included prices are net-of-tax corrected.
5. `getCommitmentRelease` (`Doc_Order.java:589-630`) posts POST_Commitment CR expense / DR offset for the matched amount × multiplier; rejects mixed currencies across order lines.
Result: per (account, dimension) the encumbrance balance = reservations open + commitments not yet invoiced; budget control compares budget against actual + encumbrance according to `BudgetControlScope`.

### Commitment-aware budget check (ERPNext, usable as fund ceiling)
`compare_expense_with_budget` (`erpnext/erpnext/accounts/doctype/budget/budget.py:540-584`) sums actual GL + open requested (MR) + open ordered (PO unbilled `amount − billed_amt`) and blocks or warns when over the budget ceiling. When the budget dimension is a fund, this yields "available fund = ceiling − actual − encumbered" without separate encumbrance postings (encumbrance is computed live from open documents, `:689-743`).

### Ratio fund consumption (Odoo)
`_prepare_analytic_lines` (`odoo/addons/account/models/account_move_line.py:3580-3631`) splits each posted move line into one analytic line per distribution key: `amount = −balance × pct/100`; the account completing 100% for a root plan receives `−balance × (100 − already)/100` so per-plan totals equal the line balance. With a fund root plan, a 60/40 split consumes two funds pro rata per spend.
Default selection of the split: distribution models filtered by matching criteria (`analytic_distribution_model.py:87-99`) and merged in sequence, one model per root plan (`:61-77`).

## State machines and workflows
- iDempiere documents post facts on completion and reverse on void/reversal (standard DocAction, not cloned); posting types are independent ledgers in Fact_Acct.
- ERPNext Budget: Draft → Submitted → Cancelled, revision chain via `revision_of` (`budget.py:887-898`).
- No funding BP state machine in any source.

## Cross-domain links
- Encumbrance is driven by D19 commitments (PO, requisition) and released by D21 invoices/matches.
- Fund keys sit on the same lines as CBS keys (D17) via Accounting Dimension / analytic plan columns.
- Company fund sheet relates to D15 capital planning (appropriations).

## Gaps
- Fund master: source (grant, bond, equity, loan), restrictions (eligible CBS, date window, max %), appropriated amount; company fund sheet with appropriated / allocated / committed / consumed / available columns.
- Funding BP (fund code, CBS, amount) with approval moving money from company to project fund sheet; zero-sum validation against appropriation.
- Waterfall consumption: on spend approval, iterate eligible funds by priority, consume `min(remaining_fund, remaining_spend)` until spend is covered; residual posts to Unfunded. Ratio mode is available in Odoo; priority mode needs a consumption ledger (spend_line_id, fund_id, amount) and re-run on spend reversal.
- Encumbrance release at payment (cash basis) is supported in iDempiere via the `multiplier` path only for allocation; no explicit fund-level encumbrance report.
