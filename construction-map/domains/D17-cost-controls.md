# D17 Cost Controls: CBS, Budget, Cost Sheet and Forecast

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D17.01 | Project cost sheet | ERPNext Budget + Project costing; iDempiere C_Project/C_ProjectLine; OpenProject Budget | partial | Fixed columns only (Planned, Committed, Invoiced, Actual, Margin); no configurable column/formula engine |
| D17.02 | Company cost sheet rollup | ERPNext Cost Center tree (nested set); OpenProject `self_and_descendants`; Odoo analytic plans | partial | Tree rollup by lft/rgt or project hierarchy; no program/shell attribute grouping |
| D17.03 | Original budget and distribution | ERPNext Budget + Budget Distribution, Monthly Distribution | partial | Equal split per period or manual %; no bell/S-curve/front/back-loaded profiles |
| D17.04 | Budget transfers and changes | ERPNext `revise_budget` (cancel + copy, `revision_of`) | partial | Revision only; no zero-sum transfer document |
| D17.05 | Cost rules (validation) | ERPNext budget control (Stop/Warn/Ignore per doc type); iDempiere GL_BudgetControl; ERPNext over-billing allowance | partial | Hard-coded rule set (actual+committed ≤ budget, invoice ≤ PO + allowance); no user-defined column-vs-column rules |
| D17.06 | Forecasting (EAC/ETC) | LibrePlan OrderEarnedValueCalculator; ERPNext Budget Variance report | partial | EAC = BAC/CPI only; no manual ETC by CBS by period |
| D17.07 | Work packages (CBS subsets) | OpenProject Budget ↔ WorkPackage (`budget_id`) | partial | Budget is a cost object grouping work packages; no alternate cost sheet views |
| D17.08 | Worksheets | IfcOpenShell cost value formulas (lark grammar) | partial | Formula trees per cost item, not free-form sheets linked to columns |
| D17.09 | Cost snapshots | OpenProject `budget_journals`; ERPNext Budget revisions (amended chain) | partial | Version history of budget header; no full cost-sheet snapshot |
| D17.10 | Generic cost sheets (no CBS) | ERPNext Budget against Cost Center or any Accounting Dimension | partial | Budget against arbitrary dimension; no program shell concept |
| D17.11 | Estimating linkage | IfcOpenShell IfcCostSchedule (ESTIMATE / SCHEDULEOFRATES), quantity takeoff | full | Quantities from model Qto/Pset formulas × rates, nested rollup; conversion to budget is a copy (`copy_cost_schedule`) |
| D17.12 | Actuals from ERP | ERPNext GL Entry by project/cost center; Odoo account.analytic.line; iDempiere Fact (POST_Actual) | full | Actuals are GL/analytic postings with dimension keys |

## Storage model

### ERPNext (Frappe doctypes)
- **Budget** (`erpnext/erpnext/accounts/doctype/budget/budget.json`, submittable, naming `BUDGET-.########`): `budget_against` Select(Cost Center|Project)*, `company` Link*, `cost_center` Link, `project` Link, `account` Link(Account)* (one expense account per budget, non-group, P&L root type), `budget_amount` Currency*, `from_fiscal_year`/`to_fiscal_year` Link(Fiscal Year)*, `budget_start_date`/`budget_end_date` Date (derived), `distribution_frequency` Select(Monthly|Quarterly|Half-Yearly|Yearly)*, `distribute_equally` Check, `budget_distribution` Table(Budget Distribution), `budget_distribution_total` Currency, `revision_of` Data, `amended_from` Link(Budget). Control flags: `applicable_on_material_request`, `applicable_on_purchase_order`, `applicable_on_booking_actual_expenses`, `applicable_on_cumulative_expense` and paired actions `action_if_annual_budget_exceeded[_on_mr|_on_po]`, `action_if_accumulated_monthly_budget_exceeded[_on_mr|_on_po]`, `..._on_cumulative_expense`, each Select(Stop|Warn|Ignore).
- **Budget Distribution** (child, `budget_distribution/budget_distribution.json`): `start_date`*, `end_date`*, `amount`*, `percent`*. 1 Budget : N rows.
- **Monthly Distribution** (`monthly_distribution/monthly_distribution.json`): `distribution_id`*, `fiscal_year`, `percentages` Table(month Data, percentage_allocation Float). Older seasonal profile, still used by reports.
- **Cost Center** (`cost_center/cost_center.json`, tree): `cost_center_name`*, `cost_center_number`, `parent_cost_center`*, `company`*, `is_group`, `lft`/`rgt` Int (nested set), `disabled`. This is the CBS-equivalent tree.
- **Cost Center Allocation** (submittable): `main_cost_center`*, `valid_from`*, `company`*, `allocation_percentages` Table(cost_center, percentage). Splits postings on a main center to children.
- **Accounting Dimension** (`accounting_dimension/accounting_dimension.json`): `document_type` Link(DocType)*, `fieldname`, `disabled`. Adds a dimension column to GL Entry and transaction lines; budgets can be keyed on any dimension (`budget.py:440`).
- **Project** cost fields (`projects/doctype/project/project.json`): `estimated_costing`, `total_costing_amount` (timesheets), `total_purchase_cost` (purchase invoices), `total_consumed_material_cost` (stock entries), `total_sales_amount`, `total_billable_amount`, `total_billed_amount`, `gross_margin`, `per_gross_margin`, `cost_center`.
- **GL Entry** is the actuals ledger: `account`, `posting_date`, `debit`, `credit`, `project`, `cost_center`, dimension columns, `is_cancelled`, `docstatus` (queried in `budget.py:763-810`).

### iDempiere (project cost header/lines)
- **C_Project** (`idempiere/org.adempiere.base/src/org/compiere/model/I_C_Project.java`): `PlannedAmt`, `PlannedQty`, `PlannedMarginAmt`, `CommittedAmt`, `CommittedQty`, `InvoicedAmt`, `InvoicedQty`, `ProjectBalanceAmt`, `IsCommitment`, `IsCommitCeiling`, `ProjInvoiceRule`, `ProjectLineLevel` (Project|Phase|Task), `ProjectCategory`, `C_Currency_ID`, `C_PaymentTerm_ID`, `DateContract`, `DateFinish`, `IsSummary`.
- **C_ProjectPhase** (`I_C_ProjectPhase.java`): `C_Project_ID`, `PlannedAmt`, `CommittedAmt`, `IsCommitCeiling`, `Qty`, `PriceActual`, `StartDate`, `EndDate`, `IsComplete`, `C_Order_ID`, `ProjInvoiceRule`.
- **C_ProjectLine** (`I_C_ProjectLine.java`): `C_Project_ID`, `C_ProjectPhase_ID`, `C_ProjectTask_ID`, `M_Product_ID`/`M_Product_Category_ID`, `PlannedQty`, `PlannedPrice`, `PlannedAmt`, `PlannedMarginAmt`, `CommittedAmt`, `CommittedQty`, `InvoicedAmt`, `InvoicedQty`, `C_OrderPO_ID`, `C_Order_ID`, `C_ProjectIssue_ID`. Project 1:N Phase 1:N Task; lines hang off any level. This is the closest OSS shape to a cost sheet row (Planned / Committed / Invoiced columns).

### OpenProject budgets module
- **budgets** (`openproject/modules/budgets/db/migrate/tables/budgets.rb`): `project_id` bigint*, `author_id`*, `subject`*, `description`*, `fixed_date` date* (rate lookup date), timestamps; `base_amount` decimal(20,2) default 0 (`20250714142919_add_base_amount_to_budget.rb`).
- **labor_budget_items**: `budget_id`*, `hours` float*, `user_id`, `comments`, `amount` decimal(15,4) (override).
- **material_budget_items**: `budget_id`*, `units` float*, `cost_type_id`, `comments`, `amount` decimal(15,4) (override).
- **work_packages.budget_id** (`1004015_aggregated_budget_migrations.rb`): N work packages : 1 budget; validated project-scoped (`budgets/app/models/work_packages/budget_assignment.rb:39-46`).
- **budget_journals**: versioned copy of budget header (acts_as_journalized, `budget.rb:52`).
- **cost_entries** (`costs/db/migrate/tables/cost_entries.rb`): `user_id`, `project_id`, `work_package_id`, `cost_type_id`, `units`, `spent_on`, `overridden_costs`, `costs`, `rate_id`, `tyear/tmonth/tweek`, `blocked`. **rates** (`tables/rates.rb`): STI `type` (HourlyRate, DefaultHourlyRate, CostRate), `valid_from`, `rate` decimal(15,4), `project_id`, `user_id`, `cost_type_id`. **cost_types**: `name`, `unit`, `unit_plural`, `default`, `deleted_at`.

### Odoo analytic accounting
- **account.analytic.plan** (`odoo/addons/analytic/models/analytic_plan.py:12-90`): `_parent_store` tree (`parent_id`, `parent_path`, `root_id`), `default_applicability`, `applicability_ids`. Each root plan materialises as a column on analytic lines: `account_id` for the project plan, `x_plan<id>_id` for others (`analytic_plan.py:113-119`).
- **account.analytic.account** (`analytic_account.py:12-95`): `name`, `code`, `plan_id`, `root_plan_id`, `company_id`, `partner_id`, computed `balance/debit/credit`.
- **account.analytic.line** (`analytic_line.py:164-235`): `date`, `amount` Monetary, `unit_amount`, `product_uom_id`, `partner_id`, `general_account_id`, `move_line_id`, `category` (invoice|vendor_bill|other), one column per root plan. This is the actuals fact table by CBS-equivalent.
- **analytic.mixin.analytic_distribution** (`analytic_mixin.py:17`): JSON `{"<acct_id>[,<acct_id>...]": percent}` stored on PO lines, move lines, requisition lines, expenses; GIN index over keys (`analytic_mixin.py:33-41`).
- **project.project.account_id** (`project/models/project_project.py:114`): project ↔ analytic account.

### IfcOpenShell (IFC4 cost model)
- **IfcCostSchedule**: `Name`, `PredefinedType` (BUDGET, COSTPLAN, ESTIMATE, TENDER, PRICEDBILLOFQUANTITIES, UNPRICEDBILLOFQUANTITIES, SCHEDULEOFRATES, from schema enum via `util/cost.py:303-319`), `Status`, `SubmittedOn`, `UpdateDate` (set on create, `api/cost/add_cost_schedule.py:26`).
- **IfcCostItem**: `PredefinedType`, `CostValues` (list IfcCostValue), `CostQuantities` (list IfcPhysicalQuantity). Root items attached to schedule by IfcRelAssignsToControl; children by IfcRelNests (`api/cost/add_cost_item.py:27`). Items control products/resources/tasks via IfcRelAssignsToControl.
- **IfcCostValue** (IfcAppliedValue): `Name`, `AppliedValue` (number or IfcMeasureWithUnit), `UnitBasis` (IfcMeasureWithUnit), `Category` (`*` = sum of children, or a named category), `ArithmeticOperator` (ADD|SUBTRACT|MULTIPLY|DIVIDE), `Components` (nested values), `ApplicableDate`, `FixedUntilDate`.

### LibrePlan
- **OrderLine.budget** BigDecimal scale 2, non-negative (`libreplan/libreplan-business/src/main/java/org/libreplan/business/orders/entities/OrderLine.java:54,389-391`); **OrderLineGroup.getBudget** = Σ children (`OrderLineGroup.java:1130-1135`); **Order.budgetMargin** % applied in `OrderElement.calculateBudgetWithMargin` (`OrderElement.java:1708-1719`).
- **cost_category**, **hour_cost** (`price_cost`, `init_date`, `end_date`, `type_of_work_hours_id`, `cost_category_id`), **type_of_work_hours** (`default_price`), **resources_cost_category_assignment** (`init_date`, `end_date`, `resource_id`, `cost_category_id`) (`resources/org/libreplan/business/costcategories/entities/CostCategories.hbm.xml`).

## Algorithms and logic

### Budget validation on save (ERPNext `budget.py`)
1. Dimension mandatory (`:71`); `budget_amount > 0` (`:82-84`); fiscal years belong to company (`:86-97`); start/end dates copied from fiscal years, start ≤ end (`:99-110`).
2. Duplicate check: no other non-cancelled budget for same company + dimension value + account with overlapping fiscal range (`:112-149`).
3. Account: leaf, same company, `report_type == "Profit and Loss"` (`:151-168`).
4. Applicability chain: MR implies PO and Actual; PO implies Actual; none set → Actual on (`:176-192`).
5. New budget (non-revision) cannot be below actual already spent in range: `get_actual_expense` > `budget_amount` throws (`:194-233`).

### Budget time distribution (ERPNext `budget.py:235-375`)
- `before_save` → `allocate_budget`. Skip if revision and not `distribute_equally` (`:255`). If only `budget_amount` changed and rows exist and manual: `row.amount = percent/100 × budget_amount` (`:258-279`). Else regenerate when new, no rows, or any of fiscal years / amount / frequency changed, or `distribute_equally` (`:281-298`).
- `get_budget_periods`: from first-of-month of start, step 1/3/6/12 months, period end = last day of start+0/2/5/11 months, clipped to budget end (`:315-351`).
- Equal split: `row_percent = 100 / n`, `amount = budget_amount × row_percent / 100` rounded to 3 dp (`:300-355`).
- `on_update` → totals must match: |Σamount − budget_amount| ≤ 0.10 and |Σpercent − 100| ≤ 0.10 (`:357-374`).

### Budget control check (cost rule engine) (ERPNext `budget.py:377-585`)
Inputs: transaction line (doctype, company, posting date, account, item_code, project, cost_center, dimensions), optional `expense_amount`.
1. Called from buying controller on submit of Material Request / Purchase Order per item (`erpnext/erpnext/controllers/buying_controller.py:1295-1312`) and from GL posting (`erpnext/erpnext/accounts/general_ledger.py:180,394`).
2. Exit if no submitted budget overlaps the posting fiscal year (`budget.py:388-410`).
3. If no account/cost center, derive from Item Default → Item Group → Company defaults (`:832-873`).
4. For each dimension in [project, cost_center] + accounting dimensions with a value and an Expense-root account: select submitted budgets for company/account whose date range contains posting date; tree dimensions match any ancestor (`lft <= node.lft AND rgt >= node.rgt`) (`:438-497`).
5. Per budget: choose action pair (annual, accumulated monthly) by doctype (`get_actions`, `:674-686`). Annual compares against `budget_amount`; monthly compares against Σ distribution rows with `start_date <= posting_date` (`get_accumulated_monthly_budget`, `:813-829`).
6. `compare_expense_with_budget` (`:540-584`): actual = Σ(debit − credit) of GL in budget range (and ≤ month end for monthly), tree-aware (`:763-810`); requested = Σ(stock_qty − ordered_qty) × rate of open purchase MRs (`:689-714`); ordered = Σ(amount − billed_amt) × conversion_rate of open PO items (`:717-743`). For MR: amount = requested + ordered; for PO: amount = ordered; for GL: amount = posted line. `total = actual + amount`; if `total > budget` → message with "already exceeded" vs "will be exceeded".
7. Role override: user holding company `exception_budget_approver_role` downgrades Stop → Warn (`budget.py:412-415,576-579`). Stop throws `BudgetError`, Warn shows message.
This is the OSS equivalent of rules like "Revised Budget ≥ Actual + Open Commitments".

### Budget revision (ERPNext `budget.py:887-898`)
`revise_budget`: cancel submitted budget (docstatus 2), deep-copy to new draft with `revision_of = old.name`. On a revision, existing-spend check is skipped (`:195-196`) and distribution is preserved unless equal split (`:255-256`).

### Cost center allocation on posting (ERPNext `general_ledger.py:170-223`)
Before splitting a GL line on a main cost center, budget is checked on the main center; then the line is cloned per child with `percentage`. Allocation record chosen = latest `valid_from <= posting_date`. Percentages must total 100 (`cost_center_allocation.py:62-66`).

### Project cost roll-up (ERPNext `project.py`)
- `update_costing` (`:352-380`): timesheet detail sums (costing, billing, hours, min from_time, max to_time) → actual dates and `total_costing_amount`; then purchase, sales, billed, margin.
- `total_purchase_cost` = Σ Purchase Invoice Item `base_net_amount` where project = P, docstatus 1 (`:954-964`); incrementally updated with row lock on PI submit/cancel (`purchase_invoice.py:867-884`).
- `total_consumed_material_cost` = Σ Stock Entry Detail amount with no target warehouse + landed cost on Manufacture entries (`project.py:184-216`).
- `gross_margin = total_billed_amount − (costing + purchase + consumed material)`; `per_gross_margin = gross_margin / billed × 100` (`:382-393`).

### iDempiere project header roll-up (`MProjectLine.java:206-328`)
- `PlannedAmt = PlannedQty × PlannedPrice`; `PlannedMarginAmt = (PlannedPrice − LimitPrice) × PlannedQty` or category planned margin × qty (`:212-228`).
- After save/delete, SQL `UPDATE C_Project SET (PlannedAmt, PlannedQty, PlannedMarginAmt, CommittedAmt, CommittedQty, InvoicedAmt, InvoicedQty) = (SELECT SUM(...) FROM C_ProjectLine ...)`, then same for phase and task (`:280-328`).
- Project issue (material/time consumption) adds cost to `ProjectBalanceAmt` (`MProjectIssue.java:560-579`).

### OpenProject budget arithmetic (`modules/budgets/app/models/budget.rb`)
- `budget = base_amount + material_budget + labor_budget` (`:106-108`).
- Labor item cost = `amount` override or `HourlyRate.at_date_for_user_in_project(fixed_date, user, project).rate × hours` (`labor_budget_item.rb:60-79`); material item = `amount` or `cost_type.rate_at(fixed_date).rate × units` (`material_budget_item.rb:53-67`).
- `spent = Σ COALESCE(overridden_costs, costs)` over cost_entries + time_entries of budget's work packages (`budget.rb:149-175`); `available = budget − spent` (`:177`); `budget_ratio = round(spent/budget × 100)` (`:119-123`).
- Project/company rollup: `Budgets::AggregatedBudgets` sums over `project.self_and_descendants` (`budgets/aggregated_budgets.rb:63-65`, `project_aggregation.rb:39-41`); `remaining = budgeted_total − spent_total`, `spent_ratio = spent/budgeted` (`aggregated_budgets_with_spend.rb:48-54`).
- Rate resolution: project rate in project hierarchy ordered by `projects.lft DESC, valid_from DESC`, fallback to user default rate (`costs/app/models/hourly_rate.rb:36-44,96-100`); cost type rate = latest `valid_from <= date` (`cost_type.rb:81-84`).
- Rate change propagation: creating a rate re-prices entries between its `valid_from` and the next rate; moving a rate across another rate re-prices both ranges; deleting re-prices entries bound to it (`costs/app/models/rate.rb:94-147`).

### Odoo analytic distribution (CBS split of every cost line)
- Defaults: `account.analytic.distribution.model._get_distribution` finds models matching partner/category/company/product/account (`in [value, False]`), merges them in sequence skipping root plans already applied (`analytic_distribution_model.py:61-99`).
- Validation: for every mandatory root plan (by applicability scoring, `analytic_plan.py:212-266`), Σ percentages of accounts under that root must equal 100 (`analytic_mixin.py:182-196`); enforced on PO confirm and move posting (`account_move_line.py:3534-3565`).
- Merge when only some plans change (`analytic_mixin.py:207-275`): keeps non-changing plan weights, rescales changing ones, cross-multiplies keys.
- Posting: `_prepare_analytic_distribution_line` creates one analytic line per key with `amount = −balance × pct/100`; the last account reaching 100% on a plan takes the remainder to avoid rounding drift (`account_move_line.py:3580-3631`).

### IFC cost item value and rollup (`ifcopenshell/util/cost.py`)
- `calculate_applied_value(root, value)` (`:63-100`): if `ArithmeticOperator` and `Components` → recurse and fold ADD/SUBTRACT/MULTIPLY/DIVIDE (divide by zero ignored); `Category is None` → primitive value; `Category == "*"` → if item has nested children, `sum_child_root_elements` else own value; named category → sum children filtered by that category.
- `sum_child_root_elements` (`:103-128`): for each nested child (substituting a linked rate item if assigned), for each cost value: `qty = Σ CostQuantities[].value` (1 if none); if `UnitBasis` then `qty / UnitBasis.value × applied` else `qty × applied`.
- `get_total_quantity` distinguishes no quantities (None) from zero (`:49-60`).
- Formula language (`:358-443`): `operand (op operand)*`, operand = number | `Category(formula)`, `SUM(...)` → `*`; parsed with lark into nested IfcCostValue components (`api/cost/edit_cost_value_formula.py:26-80`).

### Estimate quantity takeoff (`api/cost/assign_cost_item_quantity.py:122-255`)
- Assign products to cost item (skip spatial elements except spaces). With `prop_name`: pull matching IfcPhysicalSimpleQuantity from product IfcElementQuantity. With `formula`: Python AST restricted to + − × ÷ ** unary-minus, names resolved from first Qto set or `Pset.Prop`, result stored on a quantity with `Formula` attribute. With neither: maintain an IfcQuantityCount = number of non-resource controlled objects.
- Resource-based pricing: `calculate_cost_item_resource_value` replaces cost values with one per controlled IfcConstructionResource (directly or via controlled IfcTask): formula `cost × quantity`, quantity /8 when unit contains "day" (`api/cost/calculate_cost_item_resource_value.py:23-60`).
- Schedule of rates: `assign_cost_value` makes the cost item share the rate item's `CostValues` list by reference (`api/cost/assign_cost_value.py:71`); `get_cost_rate` infers the link back by inverse lookup of the first cost value (`util/cost.py:342-355`).
- Observed defect: `copy_cost_item_values` removes destination values against `source` as parent (`api/cost/copy_cost_item_values.py:54`).

### Labor budget from cost categories (LibrePlan `OrderElement.java:1632-1665`)
When automatic budget is enabled: for each hours group, for each criterion requirement whose criterion has a cost category, `price = HourCost(category, default type).priceCost`, `budget += price × hours`; divided by number of criteria when > 1 (averaging). Hour price for actuals: `HourCostDAO.getPriceCostFromResourceDateAndType` joins resource→category assignment valid on date and hour cost valid on date for the type of work hours; fallback `TypeOfWorkHours.defaultPrice` (`costcategories/daos/HourCostDAO.java:64-81`, `planner/entities/MoneyCostCalculator.java:134-166`). Hour cost validity periods must not overlap (`CostCategory.java:98-120`).

### Forecast metrics (LibrePlan `OrderEarnedValueCalculator.java:103-195`)
BAC = last cumulative BCWS; CPI = BCWP/ACWP × 100; CV = BCWP − ACWP; EAC = BAC / CPI × 100; ETC = EAC − ACWP. Zero guards return 0.

### Budget vs actual by month (ERPNext `budget_variance_report.py:72-118`)
Each distribution row's amount is spread equally over months inside the row; actual per month = Σ(debit − credit) of GL for that account/dimension; variance = budget − actual per period and in total (`:240-253`).

## State machines and workflows
- **ERPNext Budget**: docstatus Draft(0) → Submitted(1) → Cancelled(2); only submitted budgets control spending (`budget.py:401,475`). Revision = cancel + new draft linked by `revision_of` (`:887-898`).
- **ERPNext Cost Center Allocation**: Draft → Submitted; effective by `valid_from`; backdating guarded against existing GL (`cost_center_allocation.py:68-117`).
- **OpenProject Budget**: no status; every change journaled (`budget.rb:52`); permission `edit_budgets` for item changes (`:114-116,238-240`).
- **IFC cost schedule**: `Status` free text; `PredefinedType` drives semantics (SCHEDULEOFRATES excluded from rate inference, `util/cost.py:347-348`).

## Cross-domain links
- Cost Center / analytic account / C_ProjectPhase rows are the CBS keys referenced by D19 (PO lines), D21 (invoice lines), D22 (distribution), D18 (funding by CBS).
- Budget control reads open Material Requests and Purchase Orders (D19) and GL actuals posted by invoices/payments (D21).
- OpenProject budgets aggregate time entries (D32) and cost entries (D13); labor rates from D07 resources.
- LibrePlan/IFC tie budgets to tasks (D03) and resources (D07); EAC metrics shared with D11.
- Budget approval workflows rely on D24 (Frappe docstatus / workflow, not cloned).

## Gaps
- Configurable cost sheet: column definitions with data source = (BP type, status set, amount field), formula columns, manual columns, recompute on BP status transition. Needs a column registry, event-driven posting ledger keyed (project, CBS, column), and a dependency-ordered formula evaluator.
- Budget transfer BP: from/to CBS lines with Σ = 0 validation; approval posts to Revised Budget.
- Generic user-defined cost rules (column A op column B, scope, trigger statuses, hard/soft) evaluated on status change, web-service and auto-creation paths.
- Forecast sheet: ETC by CBS by period, periodic snapshot freeze, variance = Revised Budget − EAC.
- Distribution curves beyond equal split (see D22 gaps).
- Program/company rollup by shell attributes (only tree rollups exist).
- Worksheets with formulas feeding cost sheet columns; full cost-sheet snapshots with period comparison.
