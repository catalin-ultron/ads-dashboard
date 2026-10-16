# D11 Earned Value and Performance Measurement

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D11.01 | EV fields (PV, EV, AC, BAC, EAC, ETC, VAC, SV, CV, SPI, CPI, TCPI) | LibrePlan `EarnedValueCalculator` + `OrderEarnedValueCalculator`; MPXJ `TaskField` | partial | LibrePlan computes all but TCPI as daily time series, in hours not money; MPXJ stores all incl. TCPI but derives only CV and SV |
| D11.02 | Performance % complete techniques | MPXJ P6 schema `WBSType`/`ProjectType.EarnedValueComputeType` | partial | Enum and parameter fields exist; no OSS computes 0/100, 50/50, custom X/Y or WBS-milestone EV |
| D11.03 | ETC/EAC techniques (PF variants) | MPXJ P6 schema `EarnedValueETCComputeType`, `EarnedValueETCUserValue` | partial | Enum only; LibrePlan hard-codes EAC = BAC / CPI |
| D11.04 | EV rollups (ratios from sums) | LibrePlan `OrderEarnedValueCalculator`, MPXJ `RollupHelper` | partial | LibrePlan sums task series to order, then derives ratios from summed series; MPXJ rolls costs but not EV fields |
| D11.05 | Time-phased S-curves, earned schedule | LibrePlan (SortedMap<LocalDate,BigDecimal> cumulative series); P6 schema `ActivitySpreadType`, `ActivityPeriodActualType` | partial | Daily cumulative BCWS/BCWP/ACWP exist; no earned schedule (ES, SPI(t)) anywhere |
| D11.06 | Baseline selection for EV | P6 schema `ProjectType.UseProjectBaselineForEarnedValue`, `GlobalPreferencesType.EarnedValueCalculation` | partial | Flags only; LibrePlan has no baseline, PV = current plan |
| D11.07 | Labor / nonlabor / material splits | P6 schema `Summary*ByCost` vs `Summary*ByLaborUnits`; MPXJ `RollupHelper.resourceAssignmentCostRollup` | partial | MPXJ splits planned/actual/remaining cost by resource type; EV by units vs cost only as P6 stored fields |
| D11.08 | ANSI-748 support (control accounts, MR, UB, budget logs, VAR) | P6 schema `ProjectBudgetChangeLogType`, `WBSType.UnallocatedBudget/DistributedCurrentBudget` | partial | Budget log and undistributed budget fields; no control account, management reserve or variance-explanation entity |

## Storage model

### LibrePlan (calculation-only; no persisted EV table)
EV values are not stored; every series is recomputed on read from planning and actuals entities.

| Input entity | Role in EV | Key fields | Citation |
|---|---|---|---|
| `DayAssignment` (per task, `FilterType.WITHOUT_DERIVED`) | BCWS source | `day: LocalDate`, `duration: EffortDuration` | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/HoursCostCalculator.java:124` |
| `DirectAdvanceAssignment` (report-global advance of the `OrderElement`) → `AdvanceMeasurement` | BCWP source | `date: LocalDate`, `value: BigDecimal` (percent for the percentage type) | `.../HoursCostCalculator.java:69-79` |
| `Task.getHoursSpecifiedAtOrder()` | BAC per task in hours | `Integer` | `.../HoursCostCalculator.java:77` |
| `WorkReportLine` (order element and children) | ACWP source | `date`, `effort: EffortDuration` | `.../HoursCostCalculator.java:207-232` |
| `Task.isSubcontracted()` | switches BCWS and ACWP to the advance series | boolean | `.../HoursCostCalculator.java:118-120, 208-210` |

Interfaces: `IEarnedValueCalculator` (generic series math), `IOrderEarnedValueCalculator` (per order), `ICompanyEarnedValueCalculator` (all orders in an `AvailabilityTimeLine.Interval`) in `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/`.

### MPXJ (stored EV fields; file-format model)

| Entity | Field | Type | Citation |
|---|---|---|---|
| `Task` | `BCWP`, `BCWS`, `SV`, `CV`, `ACWP`, `VAC`, `EAC` | CURRENCY | `mpxj/src/main/java/org/mpxj/TaskField.java:62-64,135,165,289,640` |
| `Task` | `CPI`, `SPI`, `TCPI` | NUMERIC | `mpxj/src/main/java/org/mpxj/TaskField.java:632,653,660` |
| `Task` | `EARNED_VALUE_METHOD` (enum `PERCENT_COMPLETE`=0, `PHYSICAL_PERCENT_COMPLETE`=1; out-of-range defaults to physical) | enum | `mpxj/src/main/java/org/mpxj/EarnedValueMethod.java:32-60`, `TaskField.java:641` |
| `Task` | `PHYSICAL_PERCENT_COMPLETE`, `PERCENT_COMPLETE_TYPE` | PERCENTAGE / enum | `mpxj/src/main/java/org/mpxj/TaskField.java:646,1015` |
| `ProjectProperties` | `DEFAULT_TASK_EARNED_VALUE_METHOD`, `EARNED_VALUE_METHOD`, `STATUS_DATE` | enum / LocalDateTime | `mpxj/src/main/java/org/mpxj/ProjectProperties.java:1343,1503,1903` |
| `ResourceAssignment`, `Resource` | MSP EV fields (BCWS/BCWP/ACWP per assignment) | CURRENCY | `mpxj/src/main/java/org/mpxj/ResourceAssignment.java` (grep hit) |

### P6 data model (PMXML schema bound in MPXJ)

| P6 type | EV-related fields | Citation |
|---|---|---|
| `ProjectType`, `WBSType` | `EarnedValueComputeType` {Activity Percent Complete, 0 / 100, 50 / 50, Custom Percent Complete, WBS Milestones Percent Complete, Activity Percent Complete Using Resource Curves}; `EarnedValueUserPercent: double` (custom X% at start); `EarnedValueETCComputeType` {ETC = Remaining Cost for Activity, PF = 1, PF = Custom Value, PF = 1 / CPI, PF = 1 / (CPI * SPI)}; `EarnedValueETCUserValue: double ≥ 0`; `IndependentETCLaborUnits`, `IndependentETCTotalCost` | `mpxj/src/main/java/org/mpxj/primavera/schema/WBSType.java:52-103,510-520`, `ProjectType.java:209-241` |
| `ProjectType` | `UseProjectBaselineForEarnedValue: boolean`, `PrimaryBaselineObjectId`, `SecondaryBaselineObjectId`, `TertiaryBaselineObjectId`, `CurrentBaselineProjectObjectId` | `mpxj/src/main/java/org/mpxj/primavera/schema/ProjectType.java:794` |
| `GlobalPreferencesType` | `EarnedValueCalculation` {At Completion Values with Current Dates, Planned Values with Planned Dates, Planned Values with Current Dates} | `mpxj/src/main/java/org/mpxj/primavera/schema/GlobalPreferencesType.java:118-123` |
| `WBSType` / `ProjectType` summary | `SummaryPlannedValueByCost|ByLaborUnits`, `SummaryEarnedValueByCost|ByLaborUnits`, `SummaryActualValueByCost|ByLaborUnits`, `SummaryBudgetAtCompletionByCost|ByLaborUnits`, `SummaryEstimateAtCompletionByCost|ByLaborUnits`, `SummaryEstimateAtCompletionHigh/LowPercentByLaborUnits`, `SummaryEstimateToCompleteByCost|ByLaborUnits`, `SummaryCostVarianceByCost|ByLaborUnits`, `SummaryScheduleVarianceByCost|ByLaborUnits`, `SummaryCostPerformanceIndexByCost|ByLaborUnits`, `SummarySchedulePerformanceIndexByCost|ByLaborUnits`, `SummaryCostVarianceIndex*`, `SummaryScheduleVarianceIndex*`, `SummaryToCompletePerformanceIndexByCost`, `SummaryVarianceAtCompletionByLaborUnits`, `SummaryAccountingVariance*`, `SummaryPerformancePercentCompleteByCost|ByLaborUnits`, `SummarySchedulePercentComplete*` | `mpxj/src/main/java/org/mpxj/primavera/schema/WBSType.java:178-290` |
| `ActivitySpreadType` (per period) | `StartDate`, `EndDate`, `Period`, `PeriodType`; per-period and `Cumulative*` variants of `PlannedValueCost/LaborUnits`, `EarnedValueCost/LaborUnits`, `ActualCost`, `EstimateAtCompletionCost/LaborUnits`, `EstimateToCompleteCost/LaborUnits`, `BaselinePlanned*`, `BaselineActual*`, `RemainingLate*` | `mpxj/src/main/java/org/mpxj/primavera/schema/ActivitySpreadType.java` |
| `ActivityPeriodActualType` (stored past-period performance) | `ActivityObjectId`, `FinancialPeriodObjectId`, `PlannedValueCost`, `PlannedValueLaborUnits`, `EarnedValueCost`, `EarnedValueLaborUnits`, `ActualLabor/NonLabor/Material/ExpenseCost`, `ActualLabor/NonLaborUnits`, `WBSObjectId` | `mpxj/src/main/java/org/mpxj/primavera/schema/ActivityPeriodActualType.java` |
| `FinancialPeriodType` | `Name(60)`, `StartDate`, `EndDate`, `FinancialPeriodTemplateId` | `mpxj/src/main/java/org/mpxj/primavera/schema/FinancialPeriodType.java` |

XER column names for WBS EV settings appear only in the XER writer, as constants: `ev_compute_type="EC_Cmp_pct"`, `ev_etc_compute_type="EE_PF_cpi"`, `ev_user_pct=6`, `ev_etc_user_value=0.88` (`mpxj/src/main/java/org/mpxj/primavera/PrimaveraXERFileWriter.java:1553-1563`). No MPXJ reader maps these WBS EV settings into the model (grep of `XerProjectReader`, `TableProjectReader`, `XmlProjectReader` for `EarnedValue`/`ev_` returns nothing).

## Algorithms and logic

### LibrePlan series algebra (`EarnedValueCalculator`)
All operands are `SortedMap<LocalDate, BigDecimal>`; binary ops iterate the first map's keys and look up the same key in the second (`forValuesAtSameKey`, `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/EarnedValueCalculator.java:117-124`). Null operand: subtraction skips the key (`:126-140`), multiplication writes 0 (`:195-210`), division writes the default (0) also when divisor is zero (`:222-250`). Division uses `RoundingMode.HALF_UP` at the dividend's scale (`:230`).

| Metric | Formula | Citation |
|---|---|---|
| CV(t) | BCWP(t) − ACWP(t) | `EarnedValueCalculator.java:47-51` |
| SV(t) | BCWP(t) − BCWS(t) | `:54-58` |
| BAC(t) | max(BCWS values), constant across all days of BCWS | `:61-69` |
| EAC(t) | (ACWP(t) / BCWP(t)) × BAC(t) (= BAC / CPI) | `:72-78` |
| VAC(t) | BAC(t) − EAC(t) | `:81-85` |
| ETC(t) | EAC(t) − ACWP(t) | `:88-92` |
| CPI(t) | BCWP(t) / ACWP(t), 0 if ACWP = 0 | `:95-99` |
| SPI(t) | BCWP(t) / BCWS(t), 0 if BCWS = 0 | `:102-106` |

### LibrePlan per-order point values (`OrderEarnedValueCalculator`)
- Scalar CPI is a percentage: `BCWP.setScale(4) / ACWP` (HALF_UP) × 100, scale 2; returns 0 when ACWP = 0 (`libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java:167-175`).
- Scalar EAC = `BAC.setScale(2) / CPI% × 100`; 0 when CPI = 0 (`:183-190`). ETC = EAC − ACWP (`:193-195`). CV = BCWP − ACWP (`:178-180`).
- BAC = last value of the cumulative BCWS series, else 0 (`:103-106`).
- `getValueAt(series, date)`: exact key; otherwise value of the first key after `date`; if `date` is after the last key, last value; else 0 (`:131-148`). Lookup takes the next later point, not the previous one.

### LibrePlan series construction (`HoursCostCalculator`, units = hours)
1. Task set = all children task elements of the order plus the order's own task element; only `Task` leaves contribute (`OrderEarnedValueCalculator.java:91-95,110-118`).
2. BCWS per task: for each non-derived `DayAssignment`, parse `duration` as "hh:mm" and add whole hours to that day; minutes are summed across all assignments and added once on the last assignment (+1 h if 30..60 min, +min/60 h if >60) (`HoursCostCalculator.java:114-183`). Subcontracted tasks use the advance series instead (`:118-120`).
3. BCWP per task: for each `AdvanceMeasurement` of the report-global advance assignment, `value × hoursSpecifiedAtOrder / 100` with `MathContext(2, HALF_UP)` (two significant digits) (`:82-102`).
4. ACWP per task: Σ `WorkReportLine.effort` in hours (scale 2) per date, across the order element and its children (`:207-232`).
5. Order series = per-day sum across tasks (`addCost`, `OrderEarnedValueCalculator.java:80-89`), then running cumulative (`accumulateResult`, `:65-78`).
- Edge cases read in code: advance measurement values are already cumulative progress, and step 5 accumulates them again, so BCWP is a sum of cumulative values (inferred overstatement); `MathContext(2)` rounds 1 234 h to 1 200 h; ACWP is hours, not cost, so CPI compares hours.

### LibrePlan company-wide (`CompanyEarnedValueCalculator`)
Uses precomputed snapshots (`PredefinedDatabaseSnapshots.snapshotEstimatedCostPerTask`, `snapshotAdvanceCostPerTask`, `snapshotWorkReportLines`). Task filter: start or end inside the interval (`libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/CompanyEarnedValueCalculator.java:67-75`). BCWS and ACWP are accumulated (`:53-65,117-139`); BCWP is returned without `accumulateResult` (`:142-154`), so the company curve mixes cumulative and per-day series.

### MPXJ derived fields
CV = BCWP − ACWP with null treated as 0 (`mpxj/src/main/java/org/mpxj/Task.java:6787-6790`); SV = BCWP − BCWS, null if either missing (`:6792-6800`); dependency graph `CV ← {BCWP, ACWP}`, `SV ← {BCWP, BCWS}` (`:7305-7306`). CPI, SPI, TCPI, EAC, VAC are read/written verbatim (MSP/PWA mapping `mpxj/src/main/java/org/mpxj/pwa/PwaReader.java:1032,1110`).

### Cost rollups usable for EV denominators (MPXJ)
`RollupHelper.resourceAssignmentCostRollup` adds assignment planned/actual/remaining/at-completion cost to the task and to the WORK→labor, MATERIAL→material, COST→nonlabor bucket (null type = WORK) (`mpxj/src/main/java/org/mpxj/primavera/RollupHelper.java:70-115`). `rollupCosts` recursively sums children into WBS summary tasks for planned, actual, remaining (each split labor/nonlabor/material/expense), cost, fixed cost (`:241-316`). Ratios are not rolled.

## State machines and workflows
No EV-specific state machine in any source. P6 `ProjectBudgetChangeLogType.Status` {'' , Pending, Approved, Not Approved} is the only baseline-change control state (`mpxj/src/main/java/org/mpxj/primavera/schema/ProjectBudgetChangeLogType.java`); transitions are not implemented in OSS (see D13).

## Cross-domain links
- PV source = time-phased resource assignments and day assignments (D07 assignments, D06 CPM dates, D05 calendars).
- EV source = progress/advance measurements, percent-complete type and physical % (D10 progress).
- AC source = work reports/timesheets (D32) and expenses (D13).
- Baselines (D10) supply BCWS when `UseProjectBaselineForEarnedValue`.
- WBS-level EV settings live on the WBS node (D03).
- Thresholds on CPI/SPI/CV/SV/VAC (D12.01) consume these metrics.
- Financial periods and period actuals shared with D13.06 summarization and D33 reporting; budgets with D17.

## Gaps
- Performance % techniques: compute EV per activity as BAC × f(technique): 0/100 (0 until actual finish), 50/50 (50% at actual start, 100% at finish), custom X/Y (`EarnedValueUserPercent` at start), WBS milestones (Σ weight of completed milestones / Σ weights), activity % using resource curves (spread curve value at performance %). Needs a WBS-level setting with inheritance from project default.
- ETC/PF techniques: ETC = (BAC − EV) × PF with PF ∈ {1, user, 1/CPI, 1/(CPI·SPI)} or ETC = remaining cost; EAC = AC + ETC; TCPI = (BAC − EV)/(BAC − AC) and EAC-based variant. LibrePlan only has PF = 1/CPI on BAC.
- Money-based EV: LibrePlan is hours-based; a rebuild needs cost-rate application on day assignments (D07 cost categories) and on actuals.
- Rollups at activity/WBS/project/EPS with ratios recomputed from sums; store `Summary*` snapshots per WBS (see D13.06).
- Earned schedule: ES = t where cumulative PV(t) = EV(now) by linear interpolation between periods; SPI(t) = ES / AT; none in OSS.
- Baseline selection and "earned value calculation" global option (at-completion vs planned values, planned vs current dates).
- ANSI-748: control account entity (WBS × OBS), work/planning package flag, management reserve, undistributed budget, variance analysis records with thresholds and narrative explanations.
- Fix-ups if reusing LibrePlan logic: do not re-accumulate cumulative advance values; use full precision; carry previous (not next) value in point lookups.
