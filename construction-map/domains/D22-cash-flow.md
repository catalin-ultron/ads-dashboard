# D22 Cash Flow

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D22.01 | Cash flow curves (baseline, actuals, forecast, commitments, payments) | ERPNext Budget Distribution + Budget Variance report; OpenProject `Costs::AggregatedCosts` by month; ERPNext Payment Schedule / AP ageing | partial | Budget and actual per period exist; payments-due by date exist; no unified curve store with baseline/revised/forecast types |
| D22.02 | Distribution profiles | MPXJ WorkContour (P6 resource curves, 21 points at 5% intervals); ERPNext Monthly Distribution; ERPNext equal split | partial | Curve shapes (flat, front, back, bell, peaks, turtle, custom) defined as data; spreading of a lump amount by curve not implemented |
| D22.03 | Schedule-driven cash flow | MPXJ `TimephasedUtility.segmentCost`; LibrePlan `HoursCostCalculator.getEstimatedCost` (BCWS by day) | partial | Calendar-aware timephased cost into period buckets; no CBS-mapped push into a cash flow sheet |
| D22.04 | Forecast curve and auto-forecast | LibrePlan EAC/ETC | partial | EAC/ETC totals only; no spread of ETC over remaining periods |
| D22.05 | Cash flow rollups | OpenProject `self_and_descendants` aggregation; ERPNext tree-aware cost center queries | partial | Hierarchy sums; no attribute filters |
| D22.06 | Snapshots and variance | ERPNext Budget Variance report (budget − actual per period) | partial | Live variance only; no stored snapshot |
| D22.07 | Commitment-level cash flow | ERPNext PO Payment Schedule (term-based instalments) | partial | Commitment payments by due date; retention release absent |

## Storage model

### ERPNext period data
- **Budget Distribution** (`erpnext/erpnext/accounts/doctype/budget_distribution/budget_distribution.json`): `start_date`, `end_date`, `amount`, `percent` per Budget (`distribution_frequency` Monthly | Quarterly | Half-Yearly | Yearly on `budget.json`). Baseline-curve analogue.
- **Monthly Distribution** (`monthly_distribution/monthly_distribution.json`): `distribution_id`, `fiscal_year`, `percentages` (month name, `percentage_allocation`) — a 12-bucket custom profile.
- **Payment Schedule** on PO / PI / SO / SI (`payment_schedule/payment_schedule.json`): `due_date`, `payment_amount`, `paid_amount`, `outstanding`, `invoice_portion`, `discount_date` — payment-date cash curve per commitment or invoice.
- **GL Entry** / **Payment Ledger Entry** (actuals and payments by posting date, queried by `budget_variance_report.py:121-170` and `accounts_receivable.py` PLE query).

### OpenProject
- **cost_entries.spent_on**, **time_entries.spent_on** with `tyear/tmonth/tweek` (`openproject/modules/costs/db/migrate/tables/cost_entries.rb`); aggregation groups by `date_trunc('month', spent_on)` (`modules/costs/app/models/costs/aggregated_costs.rb:93-115`).

### MPXJ (P6 / MS Project)
- **WorkContour** (`mpxj/src/main/java/org/mpxj/WorkContour.java:31-136`): `uniqueID`, `name`, `isDefault`, `curveValues` double[21] = % of total per 5% of duration (index 0 = 0%), Σ = 100. Predefined: FLAT (5.0 each), BACK_LOADED (3.5×10, 6.5×10), FRONT_LOADED (6.5×10, 3.5×10), DOUBLE_PEAK, EARLY_PEAK, LATE_PEAK, BELL (0.5,0.5,1.5,1.5,4,4,7.5,7.5,11.5×4,7.5,7.5,4,4,1.5,1.5,0.5,0.5), TURTLE, CONTOURED (manual, null curve) (`:127-135`). Written to XER `rsrccurvdata.pct_usage_0..20` (`primavera/PrimaveraXERFileWriter.java:1771+`).
- **AccrueType** START | END | PRORATED (`AccrueType.java:35-39`): when a fixed cost is recognised.
- **TimephasedCost** (`TimephasedCost.java`): `start`, `finish`, `amountPerHour`, `totalAmount` per contiguous block; **CostRateTable/Entry** (time-dependent rates).

### LibrePlan
- Day-level assignment hours per task (`DayAssignment`) → `SortedMap<LocalDate, BigDecimal>` BCWS (`libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/HoursCostCalculator.java:103-181`); cumulated by `OrderEarnedValueCalculator.accumulateResult` (`OrderEarnedValueCalculator.java:65`).

## Algorithms and logic

### Period construction and equal spread (ERPNext `budget.py:300-355`)
Periods start at first day of the budget start month, step 1/3/6/12 months, end at last day of the period (clipped to budget end). Each period gets `100/n %` of `budget_amount` (3 dp). Manual rows keep percent and rescale amount when only the total changes (`:277-279`). Totals validated ±0.10 (`:357-374`).

### Custom monthly profile (ERPNext `monthly_distribution.py:30-84`)
Default 100/12 per month; percentages must total 100 (`:53-57`). For a report period starting at `from_date` with length 1/3/6/12 months, period % = Σ percentages of the month names in that window (`get_percentage`, `:73-84`). Applies month-of-year seasonality, not duration-relative curves.

### Budget vs actual time series (ERPNext `budget_variance_report.py:72-118,192-257`)
Each distribution row spread evenly over its months; actual per month = Σ(debit − credit) GL for (dimension, account) grouped by fiscal year and month name; per-period variance = budget − actual; totals at the end. Provides baseline and actual curves at monthly grain.

### Actual spend curve (OpenProject `aggregated_costs.rb`)
Labor: Σ `COALESCE(overridden_costs, costs)` of time entries grouped by month; material: same over cost entries grouped by month and cost type; scope = budgeted work packages in project and descendants, optional date range (`:56-129`). `data_months` = union of months with data (`:117-121`).

### Schedule-driven cost into buckets (MPXJ `TimephasedUtility.segmentCost`, `TimephasedUtility.java:174-266`)
Inputs: calendar, ordered TimephasedCost blocks (start, finish, amountPerHour), target ranges (periods). Two-pointer sweep: skip ranges before the block; advance blocks ending before the range; for the overlap compute working hours via `calendar.getWork(start, finish, HOURS)` (or elapsed hours if the block is on non-working time), add `amountPerHour × hours` to the range; split the range at block end and continue. Ranges without cost return null (not 0). `addTimephasedNumbers` sums series element-wise (`:413+`), used for combining assignments.
Curve application (inferred from data model): a contour distributes assignment work across 20 equal duration slices with weights `curveValues[1..20]`; spreading a lump amount by profile = amount × weight_i/100 into slice i, then slice → calendar periods by overlap.

### Schedule-driven BCWS (LibrePlan `HoursCostCalculator.java:103-181`)
For non-subcontracted tasks, iterate non-derived day assignments within an optional filter window; accumulate hours per day; minute remainders rolled into the last day (+1 h if 30–60 min, +min/60 h if > 60). Subcontracted tasks use advance-based cost. Order-level BCWS = Σ task series, accumulated (`OrderEarnedValueCalculator.java:110-118`); BAC = last cumulative value (`:103-106`).

### Forecast totals (LibrePlan `OrderEarnedValueCalculator.java:167-195`)
CPI = BCWP/ACWP × 100; EAC = BAC/CPI × 100; ETC = EAC − ACWP.

### Commitment / invoice payment curve (ERPNext `payment_schedule.py:18-120,377-434`)
Instalment amount = total × `invoice_portion`/100 (or fixed), due date per term rule (days after invoice, days after end of month, months after end of month). Paid/outstanding per instalment maintained by payment entries (`payment_entry.py:826-943`). Grouping instalments by due-date period gives the committed-payments curve; paid rows by payment posting date give the payments curve (inferred).

### Payables ageing (ERPNext `accounts_receivable.py:818-853`, reused by `accounts_payable.py:5-13`)
Entry date = due date, supplier invoice date or posting date per filter; `age = age_as_on − entry_date`; outstanding placed in first bucket with `age ≤ range_i` (default 30/60/90/120/above); future-dated rows go to `range0`. With `based_on_payment_terms`, outstanding is allocated per schedule row (`:379-382,529`).

### Hierarchy rollups
OpenProject: all aggregations over `project.self_and_descendants` (`modules/budgets/app/models/budgets/project_aggregation.rb:39-41`). ERPNext: tree dimensions summed with nested-set `lft/rgt` containment (`erpnext/erpnext/accounts/doctype/budget/budget.py:782-801`).

## State machines and workflows
- No cash-flow entity lifecycle in any source. Budget distributions inherit Budget docstatus (Draft → Submitted → Cancelled, `budget.py:887-898`); payment schedule rows change only through invoice/payment submission and cancellation.

## Cross-domain links
- Baseline amounts from D17 budgets; schedule-driven spreads from D03/D06 activities and D07 assignments (MPXJ/LibrePlan); EAC from D11.
- Commitment curves from D19 POs; invoice and payment curves from D21; fund draw curves would come from D18.
- Period calendars and fiscal years from D05 / D01; rollup hierarchy from D01 (EPS/company) and D15 portfolios.

## Gaps
- Cash flow detail store: (project, CBS or summary, curve type {Baseline, Revised baseline, Actuals, Forecast, Commitments, Payments}, period, amount), period structure from fiscal calendar (month/quarter/year), period and cumulative views.
- Profile spreader: given amount, start, finish, profile (linear, bell, front, back, S-curve, custom %), compute per-period amounts: map period overlap to normalised duration fraction, integrate the piecewise-constant 20-slice curve (MPXJ-style) or a parametric S-curve over that fraction, rescale to the exact total, mixed profiles per CBS line.
- Schedule integration: map P6 activity CBS codes to cost sheet CBS, import timephased costs (MPXJ `segmentCost`) as Baseline/Forecast curves.
- Auto-forecast: Forecast(period) = actuals for closed periods + (EAC − actuals to date) spread by profile from data date to forecast finish; reforecast stored as snapshot.
- Snapshots: freeze curves with timestamp/label; variance per period between baseline, forecast and actual.
- Commitment cash flow with retention: spread committed value by profile or SOV, hold retention % each period, release retained total at completion period.
- Rollups to program/company with CBS and shell-attribute filters.
