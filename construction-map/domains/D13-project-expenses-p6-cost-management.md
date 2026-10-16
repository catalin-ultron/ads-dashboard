# D13 Project Expenses and P6 Cost Management

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D13.01 | Expenses (activity non-resource costs, accrual) | MPXJ `ExpenseItem` + P6 `ActivityExpenseType`; LibrePlan `ExpenseSheet`/`ExpenseSheetLine` | partial | Full P6 field set and XER/PMXML mapping; no time-phased accrual spreading in OSS |
| D13.02 | Cost accounts (hierarchy, rollups) | MPXJ `CostAccount`; ERPNext `Cost Center` (nested set) | partial | Hierarchy stored; no per-account cost rollup implemented |
| D13.03 | Project budget, budget change log, spending/benefit plan | P6 schema `ProjectType` budget fields, `ProjectBudgetChangeLogType`, `ProjectSpendingPlanType`; OpenProject `Budget`; ERPNext `Budget` | partial | P6 shape; OpenProject budget = base + labor + material items vs spent; ERPNext revision + period distribution |
| D13.04 | Funding sources | P6 schema `FundingSourceType`, `ProjectFundingType`, `EPSFundingType` | partial | Data model only; allocation logic absent |
| D13.05 | Cost totals per activity | MPXJ `RollupHelper` | full | Labor/nonlabor/material/expense × planned/actual/remaining + at completion, recursive to WBS |
| D13.06 | Summarization service | LibrePlan `SumExpenses` (+ `SumChargedEffort`); P6 `Summary*` fields and spread types | partial | LibrePlan maintains precomputed direct/indirect totals per order element asynchronously; P6 summary tables only as schema |

## Storage model

### Expense item (P6 / MPXJ)

| Field | P6 PMXML (`ActivityExpenseType`) | XER `projcost` column | MPXJ `ExpenseItem` |
|---|---|---|---|
| id | `ObjectId:int` | `cost_item_id` | `m_uniqueID: Integer` |
| activity | `ActivityObjectId`, `WBSObjectId`, `ProjectObjectId` | `task_id`, `proj_id` | `m_task: Task` (required, builder arg) |
| name / description | `ExpenseItem:string(120)`, `ExpenseDescription` | `cost_name`, `cost_descr` | `m_name`, `m_description` |
| cost account | `CostAccountObjectId` | `acct_id` | `m_account: CostAccount` |
| category | `ExpenseCategoryObjectId` | `cost_type_id` | `m_category: ExpenseCategory` |
| vendor / document | `Vendor:string(100)`, `DocumentNumber:string(32)` | `vendor_name`, `po_number` | `m_vendor`, `m_documentNumber` |
| costs | `PlannedCost`, `ActualCost`, `RemainingCost`, `AtCompletionCost` | `target_cost`, `act_cost`, `remain_cost` | `m_plannedCost`, `m_actualCost`, `m_remainingCost`, `m_atCompletionCost` |
| units | `PlannedUnits`, `ActualUnits`, `RemainingUnits`, `AtCompletionUnits`, `PricePerUnit`, `UnitOfMeasure:string(30)` | `target_qty`, `cost_per_qty`, `qty_name` | `m_plannedUnits`, `m_actualUnits`, `m_remainingUnits`, `m_atCompletionUnits`, `m_pricePerUnit`, `m_unitOfMeasure` |
| accrual | `AccrualType` {Start of Activity, End of Activity, Uniform Over Activity} | `cost_load_type` {CL_Start, CL_End, CL_Uniform} | `m_accrueType: AccrueType` {START 1, END 2, PRORATED 3} |
| flags | `AutoComputeActuals`, `OverBudget`, `ExpensePercentComplete` | `auto_compute_act_flag` | `m_autoComputeActuals: boolean` |
| CBS | `CBSId`, `CBSCode` | — | — |

Citations: `mpxj/src/main/java/org/mpxj/primavera/schema/ActivityExpenseType.java`, `mpxj/src/main/java/org/mpxj/ExpenseItem.java:285-304`, `mpxj/src/main/java/org/mpxj/AccrueType.java:35-39`, `mpxj/src/main/java/org/mpxj/primavera/AccrueTypeHelper.java:92-102`, `mpxj/src/main/java/org/mpxj/primavera/PrimaveraXERFileWriter.java:1740-1761`. Cardinality: N expense items : 1 activity (`Task.getExpenseItems()`, `mpxj/src/main/java/org/mpxj/Task.java:4351-4363`).

### Cost accounts, categories
- `CostAccount` (MPXJ): `uniqueID`, `id:String`, `name`, `notes`, `sequenceNumber`, `parent: CostAccount` (self-reference tree) (`mpxj/src/main/java/org/mpxj/CostAccount.java:126-131`). P6 `CostAccountType`: `Id:string(40)`, `Name:string(100)`, `Description`, `ParentObjectId`, `SequenceNumber`.
- `ExpenseCategory` / P6 `ExpenseCategoryType`: `Name:string(36)`, `SequenceNumber` (global list).
- ERPNext `Cost Center`: `cost_center_name`, `cost_center_number`, `parent_cost_center` (required), `company`, `is_group`, `lft`, `rgt` (nested set), `disabled` (`erpnext/erpnext/accounts/doctype/cost_center/cost_center.json`).

### P6 budget, change log, spending plan, funding (`mpxj/src/main/java/org/mpxj/primavera/schema/`)

| Type | Fields |
|---|---|
| `ProjectType` budget | `OriginalBudget`, `ProposedBudget`, `CurrentBudget`, `DistributedCurrentBudget`, `UnallocatedBudget`, `TotalFunding`, `TotalSpendingPlan`, `TotalSpendingPlanTally`, `TotalBenefitPlan`, `TotalBenefitPlanTally`, `AnnualDiscountRate` (all double) |
| `WBSType` budget | `OriginalBudget`, `ProposedBudget`, `CurrentBudget`, `DistributedCurrentBudget`, `CurrentVariance`, `UnallocatedBudget`, `IndependentETCTotalCost` (`WBSType.java:507-670`) |
| `ProjectBudgetChangeLogType` | `ObjectId`, `ProjectObjectId`, `WBSObjectId`, `ChangeNumber:string(32)`, `Date`, `Amount:double`, `Reason:string(130)`, `Responsible:string(255)`, `Status` {'' , Pending, Approved, Not Approved} |
| `EPSBudgetChangeLogType` | same at EPS level (`EPSObjectId`) |
| `ProjectSpendingPlanType` | `ProjectObjectId`, `WBSObjectId`, `Date` (month), `SpendingPlan:double`, `BenefitPlan:double` |
| `EPSSpendingPlanType` | `EPSObjectId`, `Date`, `SpendingPlan`, `BenefitPlan` |
| `FundingSourceType` | `Name:string(100)`, `Description`, `ParentObjectId` (tree), `SequenceNumber` |
| `ProjectFundingType` | `ProjectObjectId`, `FundingSourceObjectId`, `Amount:double`, `FundShare:double` (%) |
| `EPSFundingType` | `EPSObjectId`, `FundingSourceObjectId`, `Amount`, `FundShare` |

### OpenProject budgets and actual costs (`openproject/modules/`)

| Table | Columns | Relations |
|---|---|---|
| `budgets` | `project_id`, `author_id`, `subject` (≤255), `description`, `fixed_date date` (rate date), `base_amount decimal(20,2) default 0` | 1 project : N budgets; budget 1 : N work_packages (`budget_id`) |
| `labor_budget_items` | `budget_id`, `hours float`, `user_id`, `comments`, `amount decimal(15,4)` (override) | N : 1 budget |
| `material_budget_items` | `budget_id`, `units float`, `cost_type_id`, `comments`, `amount decimal(15,4)` | N : 1 budget |
| `cost_entries` | `user_id`, `project_id`, `entity` (polymorphic, replaces `work_package_id`), `cost_type_id`, `units float`, `spent_on date`, `tyear/tmonth/tweek`, `costs decimal(15,4)`, `overridden_costs decimal(15,4)`, `rate_id`, `blocked`, `comments`, `logged_by_id` | expense-like actual |
| `cost_types` | `name` (unique), `unit`, `unit_plural`, `default`, `deleted_at` | |
| `rates` (STI `type`: HourlyRate, DefaultHourlyRate, CostRate) | `valid_from date`, `rate decimal(15,4)`, `project_id`, `user_id`, `cost_type_id` | effective-dated |

Citations: `openproject/modules/budgets/db/migrate/tables/budgets.rb`, `labor_budget_items.rb`, `material_budget_items.rb`, `openproject/modules/budgets/db/migrate/20250714142919_add_base_amount_to_budget.rb`, `openproject/modules/costs/db/migrate/tables/cost_entries.rb`, `cost_types.rb`, `rates.rb`, `openproject/modules/costs/db/migrate/20250416112143_add_entity_to_cost_entry.rb`, `20260911112833_remove_work_package_id_from_entries.rb`.

### LibrePlan expense sheets and precomputed sums
- `expense_sheet`: `code` (unique), `code_autogenerated`, `first_expense`, `last_expense`, `total`, `description`, `personal`, `last_expense_sheet_line_sequence_code`; 1 : N `expense_sheet_line` (`code` unique, `value`, `concept`, `date`, `order_element_id`, `resource_id`, `expense_sheet_id`) (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/expensesheets/entities/ExpenseSheets.hbm.xml`).
- `sum_expenses`: `order_element_id` (unique 1:1), `total_direct_expenses`, `total_indirect_expenses` (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/orders/entities/Orders.hbm.xml:300-310`).
- `order_table`: `work_budget`, `materials_budget`, `budget_margin`, `hours_margin`; `order_line`/`OrderElement.budget` scale 2 (`Orders.hbm.xml:112-137,192`).

## Algorithms and logic

### Expense import and activity totals (MPXJ)
- XER/DB read: at-completion cost = actual + remaining; if price per unit ≠ 0, actual units = actual cost / price, remaining units = remaining cost / price, at-completion units = sum (`mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java:741-786`).
- `expenseItemCostRollup`: task planned cost += planned; planned expense cost += planned; actual and actual expense += actual; remaining and remaining expense += remaining; cost and fixed cost += at completion (`mpxj/src/main/java/org/mpxj/primavera/RollupHelper.java:123-134`).
- `resourceAssignmentCostRollup`: task planned/actual/remaining/cost += assignment values, then into labor (WORK, default when type null), material (MATERIAL) or nonlabor (COST) buckets (`RollupHelper.java:70-115`).
- `rollupCosts`: post-order recursion; WBS summary = Σ children for 15 split fields + cost + fixed cost (`RollupHelper.java:241-316`). Activity total cost = labor + nonlabor + material + expense follows from these sums.
- No accrual spreading: `AccrueType` is carried but never used to time-phase.

### OpenProject budget arithmetic
- `Budget#budget = base_amount + material_budget + labor_budget` (`openproject/modules/budgets/app/models/budget.rb:106-108`).
- Item cost = `amount` override if present, else calculated: labor = `HourlyRate.at_date_for_user_in_project(fixed_date, user, project).rate × hours`, 0 if no rate (`openproject/modules/budgets/app/models/labor_budget_item.rb:60-80`); material analogous with cost type rate.
- Spent = Σ `COALESCE(overridden_costs, costs)` over visible cost entries and time entries of the budget's work packages (`budget.rb:149-175`); `available = budget − spent`; `budget_ratio = round(spent / budget × 100)`, 0 if budget 0 (`:119-123,177-179`).
- Entry cost: `costs = units × rate` with rate = latest `CostRate` with `valid_from <= spent_on` for the cost type (`openproject/modules/costs/app/models/entry/costs.rb:37-54`, `openproject/modules/costs/app/models/cost_type.rb:81-85`); missing rate → costs 0, rate nil.
- Project rollup over `project.self_and_descendants`: base, material (also grouped by cost type), labor, total, spent ratio = spent / budgeted (`openproject/modules/budgets/app/models/budgets/aggregated_budgets.rb:39-65`, `aggregated_budgets_with_spend.rb:48-54`, `project_aggregation.rb:39-41`).

### ERPNext budget distribution and revision
- `get_budget_periods`: from `budget_start_date` to `budget_end_date`, periods start at first day of month, end at last day after 0/2/5/11 months for Monthly/Quarterly/Half-Yearly/Yearly, clipped at end date (`erpnext/erpnext/accounts/doctype/budget/budget.py:315-351`).
- Equal distribution: percent = 100 / n, amount = budget × percent / 100 (3 decimals) (`:300-313,353-355`). Manual distribution: if only amount changed, rescale rows by stored percent (`:258-279`). Regenerate when fiscal years, amount or frequency change or `distribute_equally` (`:281-298`).
- Totals check: |Σ amount − budget| ≤ 0.10 and |Σ percent − 100| ≤ 0.10 (`:357-375`).
- `revise_budget`: cancel submitted budget, copy as draft with `revision_of` = old name (`:887-897`); revisions with manual distribution skip reallocation (`:255-256`).
- Project costing: `total_costing_amount` = Σ submitted timesheet detail base costing; purchase cost from purchase invoices; gross margin = billed − (costing + purchase + consumed material); % margin = margin / billed × 100 (`erpnext/erpnext/projects/doctype/project/project.py:352-397`).

### LibrePlan summarization (`SumExpensesDAO`, `SumExpensesRecalculator`)
- Incremental: on line save, add `value` to the order element's `totalDirectExpenses` and to every ancestor's `totalIndirectExpenses`; on edit compute delta from previous value fetched in another transaction; if the line moved to another element, reinitialize the old element (`libreplan/libreplan-business/src/main/java/org/libreplan/business/orders/daos/SumExpensesDAO.java:69-184`).
- Full recompute: reset every `SumExpenses` in the order tree, then post-order Σ line values per element as direct and propagate as indirect (`SumExpensesDAO.java:250-283`).
- Runs on a single-thread executor; on `OptimisticLockingFailureException` sleeps 1 s and retries up to 100 times (`libreplan/libreplan-business/src/main/java/org/libreplan/business/orders/entities/SumExpensesRecalculator.java`).
- Budget with margin = budget × (1 + budgetMargin/100); resources budget = Σ hours × cost-category hour price per criterion (`libreplan/libreplan-business/src/main/java/org/libreplan/business/orders/entities/OrderElement.java:1619-1720`).

## State machines and workflows
- P6 budget change: Pending → Approved | Not Approved (enum; `ProjectBudgetChangeLogType.Status`). Current budget = original + Σ approved (feature definition; not in OSS code).
- ERPNext Budget: submittable Draft (0) → Submitted (1) → Cancelled (2); revision creates new Draft with `revision_of` (`budget.json`, `budget.py:887-897`).
- OpenProject cost entry `blocked` flag prevents editing (inferred from column).

## Cross-domain links
- Expense items attach to activities and WBS (D03), cost accounts and CBS (D17), vendors/POs (D19), funding sources (D18).
- Expense and resource costs feed EV actuals and BAC (D11) and cash flow (D22).
- Rates and cost categories from resources (D07); actual hours from timesheets (D32).
- Spending/benefit plans and funding shared with portfolio capital planning (D15).
- Summary tables serve reporting (D33).

## Gaps
- Accrual spreading: start → all cost on activity start period; end → finish period; uniform → prorated by working time per period of the activity calendar (D05). Needed for time-phased expense PV and cash flow.
- Auto-compute actuals: actual = planned × activity % complete (or units % complete) when the flag is set.
- Cost account rollups across assignments and expenses; default project cost account.
- Current budget = original + approved changes; distributed vs undistributed variance (CurrentBudget − Σ child WBS budgets); spending plan tally vs cost-loaded schedule.
- Funding allocation validation (Σ fund share = 100%, Σ amounts vs current budget).
- Summarization job writing per EPS/project/WBS/resource/role/period aggregates with `LastSummarizedDate`, `SummarizeToWBSLevel`, `EnableSummarization` (fields only in P6 `ProjectType`).
