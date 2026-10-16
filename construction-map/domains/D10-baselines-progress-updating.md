# D10 Baselines, Progress and Updating

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D10.01 | Baseline storage and variances | MPXJ `BaselineStrategy` + `ProjectFile.setBaseline(baseline, 0..10)` + PMXML `BaselineProjectType`; IfcOpenShell `create_baseline`; OpenProject journals `validity_period` | full | MPXJ: P6 baselines are full project copies keyed by `OriginalProjectObjectId`, mapped by Activity ID into baseline fields; start/finish/duration/cost/work variances computed |
| D10.02 | Update baseline (selective merge) | PMXML `UpdateBaselineOptionType` | partial | Option flags only (add new, delete non-existing, update existing, per data type); no merge code |
| D10.03 | Baseline restore and comparison | OpenProject `Journable::WithHistoricAttributes` + `at_timestamp`; MPXJ `AbstractBaselineStrategy` key matching | partial | OpenProject diffs current vs historic attributes per timestamp and tells whether each item existed/matched filters; no added/deleted/changed report generator |
| D10.04 | Progress update workflow | MPXJ `PrimaveraScheduler` (data date, actuals, remaining duration, suspend/resume); LibrePlan advances + consolidation; OpenProject progress derivation | partial | Rescheduling from data date with actuals exists; "Update Progress" (auto-status as planned) and "Apply Actuals" not implemented |
| D10.05 | Progress spotlight / look-ahead | none | none | Pure query, no implementation |
| D10.06 | Period-based progress history | PMXML `ActivityPeriodActualType`, `ResourceAssignmentPeriodActualType`; OpenProject journals; ERPNext/Odoo `project.update` | partial | Period actual tables bound but unused; status update records exist; no trend analysis |
| D10.07 | Planned / schedule % complete | MPXJ `Task.calculateSchedulePercentComplete`; LibrePlan `TaskElement.getTheoreticalAdvancePercentageUntilDate` | full | Calendar-hours ratio against baseline dates (MPXJ) and allocated-effort ratio (LibrePlan) |
| D10.08 | Check-in/check-out | PMXML `ProjectType.CheckOutStatus/CheckOutDate/CheckOutUserObjectId`; XER `checkout_flag` | partial | Lock fields only; no lock/merge logic |

## Storage model

### P6 baselines and progress (MPXJ)
Paths relative to `mpxj/src/main/java/org/mpxj/`.

| Entity / field | Contents | Citation |
|---|---|---|
| `BaselineProjectType` (PMXML) | full project payload plus `OriginalProjectObjectId`, `BaselineTypeName`, `BaselineTypeObjectId`, `LastBaselineUpdateDate`, `LastUpdateBaselineOptions`, `LastLevelDate`, `LastScheduleDate`, `SummarizedDataDate`, ~150 `Summary*` rollup fields (baseline/actual/remaining/at-completion costs, units, dates, SPI/CPI, % complete) | `primavera/schema/BaselineProjectType.java` |
| `BaselineTypeType` | `{ObjectId, Name, SequenceNumber}` | `primavera/schema/BaselineTypeType.java` |
| project properties | `baselineProjectUniqueID` (current baseline, PMXML `CurrentBaselineProjectObjectId`), `baselineTypeName`, `baselineTypeUniqueID`, `lastBaselineUpdateDate`, `projectIsBaseline`, `statusDate` (data date), `baselineDate[0..10]` | `primavera/XmlProjectReader.java:203, 242-264`; `ProjectProperties.java:1503, 2677, 3328, 3368` |
| `ProjectFile.m_baselines` | `Map<Integer index, ProjectFile>`; indexes 0..10 populate task baseline fields | `ProjectFile.java:781-800` |
| task baseline fields | index 0: `BASELINE_COST/DURATION/FINISH/FIXED_COST_ACCRUAL/FIXED_COST/START/WORK`; index n: `BASELINEn_*` from `TaskFieldLists` | `AbstractBaselineStrategy.java:89-150`, `common/TaskFieldLists.java:388` |
| task progress fields | `actualStart`, `actualFinish`, `remainingDuration`, `actualDuration`, `percentageComplete` (duration), `physicalPercentComplete`, `percentageWorkComplete` (units), `percentCompleteType` {DURATION, PHYSICAL, UNITS, SCOPE}, `suspendDate`, `resume`, `expectedFinish`, `remainingEarly/Late Start/Finish` | `PercentCompleteType.java:26-31`; `primavera/TableProjectReader.java` field list (`complete_pct_type`, `phys_complete_pct`, `suspend_date`, `resume_date`, `expect_end_date`, `restart_date`, `reend_date`) |
| progress scheduling options | `schedulingProgressedActivities` {RETAINED_LOGIC, PROGRESS_OVERRIDE, ACTUAL_DATES} from `sched_retained_logic`/`sched_progress_override`; `useExpectedFinishDates`; `dataDateAndPlannedStartSetToProjectForecastStart` | `primavera/TableProjectReader.java:845-857` |
| `UpdateBaselineOptionType` (PMXML) | booleans/filters: `AddNewActivitiesData`, `DeleteNonExistingActivities`, `UpdateExistingActivities`, `AllActivities`/`FilteredActivities` + `ActivitiesFilter*`, per-data flags `ActivityInformation`, `DatesDurationDatadates`, `BudgetUnitsCost`, `Relationships`, `Constraints`, `Expenses`, `Steps`, `ActivityCodeAssignments`, `ActivityUdfs`, `WbsAssignments`, `ProjectDetails`, `AddNewRsrcRole`, `UpdateExistRsrcRoleAssignment`, `IgnoreLastUpdateDate`, … | `primavera/schema/UpdateBaselineOptionType.java` |
| `ActivityPeriodActualType` | `{ActivityObjectId, FinancialPeriodObjectId, ActualLaborUnits/Cost, ActualNonLaborUnits/Cost, ActualMaterialCost, ActualExpenseCost, EarnedValueCost, EarnedValueLaborUnits, PlannedValueCost, PlannedValueLaborUnits, ProjectObjectId, WBSObjectId, IsBaseline}` | `primavera/schema/ActivityPeriodActualType.java` |
| `ResourceAssignmentPeriodActualType` | `{ResourceAssignmentObjectId, FinancialPeriodObjectId, ActualUnits, ActualCost, ResourceType}` | `primavera/schema/ResourceAssignmentPeriodActualType.java` |
| `FinancialPeriodType` | period definitions for the above | `primavera/schema/FinancialPeriodType.java` |
| check-out | `ProjectType.CheckOutStatus`, `CheckOutDate`, `CheckOutUserObjectId`; XER writer emits `checkout_flag = false` | `primavera/schema/ProjectType.java:1262-1264`, `primavera/PrimaveraXERFileWriter.java:1452` |

### LibrePlan progress (advances) and consolidation
Mappings under `libreplan/libreplan-business/src/main/resources/org/libreplan/business/`.

| Table | Fields | Citation |
|---|---|---|
| `advance_type` | `unit_name` (unique), `default_max_value`, `updatable`, `unit_precision`, `active`, `percentage`, `quality_form`, `read_only`; predefined CHILDREN, PERCENTAGE, UNITS, SUBCONTRACTOR, TIMESHEETS | `advance/entities/Advance.hbm.xml:7-33`; `java/.../advance/bootstrap/PredefinedAdvancedTypes.java:31-35` |
| `advance_assignment` | `report_global_advance` (exactly one per order element drives progress), FK `advance_type` | `Advance.hbm.xml:36-48` |
| `direct_advance_assignment` | FK order element, `max_value`, 1–N `advance_measurement`, 1–N `non_calculated_consolidation` | `Advance.hbm.xml:50-70` |
| `indirect_advance_assignment` | FK order element (computed from children), 1–N `calculated_consolidation` | `Advance.hbm.xml:73-86` |
| `advance_measurement` | `date`, `value`, `communication_date`, FK assignment | `Advance.hbm.xml:91-114` |
| `consolidation` (discriminator non_calculated / calculated) | FK direct or indirect advance assignment; 1–N `consolidated_value` {`date`, `value`, `task_end_date` + effort, FK advance measurement} | `planner/entities/AdvanceConsolidations.hbm.xml:7-84` |
| `day_assignment.consolidated` | boolean marking days frozen by consolidation | `planner/entities/ResourceAllocations.hbm.xml:279` |
| `task_element.advance_percentage` | cached BigDecimal 0..1 | `java/.../planner/entities/TaskElement.java:97` |
| `ProgressType` (configuration) | SPREAD_PROGRESS, ALL_NUMHOURS, CRITICAL_PATH_NUMHOURS, CRITICAL_PATH_DURATION | `java/.../common/entities/ProgressType.java:34-39` |

### OpenProject temporal history (baseline comparison)
`journals` (`openproject/db/migrate/tables/journals.rb`): `journable_type/id`, `version`, `user_id`, `notes`, `data_type/data_id` (pointer to a per-type snapshot row, e.g. `work_package_journals`), `cause` jsonb, `validity_period tstzrange` with CHECK non-empty and GiST EXCLUDE `(journable_id =, journable_type =, validity_period &&)` (no overlapping versions). Work package progress columns: `estimated_hours` (work), `remaining_hours`, `done_ratio`, `derived_estimated_hours`, `derived_remaining_hours`, `derived_done_ratio` (`openproject/app/services/work_packages/update_ancestors_service.rb:112-236`).

### IFC baselines
`IfcWorkSchedule(PredefinedType = BASELINE)` created from a `PLANNED` schedule; each baseline task is a duplicate of the planned task linked by `IfcRelDefinesByObject(RelatingObject = planned, RelatedObjects += baseline copies)` (`ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/create_baseline.py:67-110`).

### Status update records
- ERPNext `Project Update` {project, sent, date, time, users (Project User table)} (`erpnext/erpnext/projects/doctype/project_update/project_update.json`).
- Odoo `project.update` {name, status ∈ on_track/at_risk/off_track/on_hold/done, progress (int), user_id, description, date, project_id, task_count, closed_task_count} (`odoo/addons/project/models/project_update.py:44-63`).

## Algorithms and logic

### Baseline population and variance (MPXJ)
- PMXML read: baselines grouped by `OriginalProjectObjectId`; the project's current baseline (`baselineProjectUniqueID`) is attached at index 0, others at 1, 2, … (`primavera/PrimaveraPMFileReader.java:170, 231-256`). Without a stored baseline, baseline fields are populated from the project's own planned fields (`primavera/BaselineHelper.java:32-39`, call at `XmlProjectReader.java:436, 700`).
- `AbstractBaselineStrategy.populateBaseline(project, baseline, index)` (`AbstractBaselineStrategy.java:38-70`): build map key→baseline task (duplicate keys dropped), map each current task to its baseline task, cache the map for `Task.getBaselineTask()`, then copy source fields into the index's baseline fields; tasks with no match get nulls.
- Key: default GUID; P6 strategy uses canonical Activity ID, WBS entries use `activityID + " " + outlineLevel` (`primavera/PrimaveraBaselineStrategy.java:42-50`).
- Source fields: P6 `PLANNED_ATTRIBUTES` (planned cost/duration/start/finish/work) by default, or `CURRENT_ATTRIBUTES` (`PrimaveraBaselineStrategy.java:54-75`, default at `PrimaveraPMFileReader.java:376`).
- Variances (`Task.java:6729-6800`): start/finish variance = calendar working duration between baseline and current dates on the effective calendar (`LocalDateTimeHelper.getVariance`); duration variance = duration − baseline duration (unit-converted); work variance likewise; cost variance = cost − baseline cost; null if either side is null.

### Progressed-activity scheduling (MPXJ P6 scheduler, data date)
`cpm/PrimaveraScheduler.java`:
- `updateDurationsAndPercentComplete` (`:593-660`), for started, unfinished, non-physical tasks: actual duration = working hours from actual start to data date, or to suspend date if suspended before the data date, subtracting suspended span when resumed before the data date; remaining duration = working hours from remaining early start to early finish; at-completion = actual + remaining span (`:665-686`); duration % = `(planned − remaining) / planned × 100`, 100 if both zero (`:688-711`).
- Successor early start when predecessor finished and lag > 0: lag already elapsed = working hours from predecessor actual finish to data date (0 if finish after data date); remaining lag = lag − elapsed, applied from predecessor early finish (`:1076-1135`). This is the retained-logic treatment of progressed predecessors.
- Remaining early dates from the data date: see D08 (`:3302-3361`).
- Assignment dates follow the activity; completed assignments take actual dates (`:158-250`).
- Activity status = NOT_STARTED if no actual start, IN_PROGRESS if actual start without finish, COMPLETED otherwise (`primavera/ActivityStatusHelper.java:44-62`).
- Activity % shown per `percentCompleteType`: UNITS → work %, PHYSICAL → physical %, else duration % (`Task.java:6889-6914`).
- Complete-through date = actual start + duration × % on the calendar (`Task.java:6835-6872`).

### Schedule (planned) % complete
- MPXJ (`Task.java:6916-6950`): null for WBS summaries or missing data date/baseline dates; 0 before baseline start; 100 after baseline finish; else `workingHours(baselineStart, dataDate) / workingHours(baselineStart, baselineFinish) × 100` on the effective calendar.
- LibrePlan (`planner/entities/TaskElement.java:742-755`): `theoreticalCompletedTime(date) / totalAllocatedTime` from day assignments (planned effort to date / total planned effort).

### LibrePlan progress computation
- Direct assignment % at date = latest measurement on or before date ÷ `max_value`, scale 4, round down; 0 if max is 0 or no measurement (`java/.../advance/entities/DirectAdvanceAssignment.java:131-143`).
- Parent (CHILDREN type) % = Σ(child % × child work hours) ÷ parent work hours (`java/.../orders/entities/OrderLineGroup.java:479-500`); a fake direct assignment with daily measurements is synthesized for charting (`:502-545`).
- Root task-group % by `ProgressType`: ALL_NUMHOURS → `getProgressAllByNumHours`, CRITICAL_PATH_DURATION → `getCriticalPathProgressByDuration`, CRITICAL_PATH_NUMHOURS → `getCriticalPathProgressByNumHours`; non-root groups and SPREAD_PROGRESS return the cached spread value copied from the order element (`planner/entities/TaskGroup.java:316-327`, `TaskElement.java:690-694, 765-766`).
- Consolidation: `Task.getFirstDayNotConsolidated()` = consolidated-until + 1 (`planner/entities/Task.java:1058-1067`); every allocation marks day assignments before that day `consolidated = true` (`ResourceAllocation.java:1134-1139`); reallocation keeps consolidated days and redistributes only the remaining effort after them (`ResourceAllocation.java:1126-1131, 1165-1172`). Consolidated values store the task end date at consolidation time.
- Task status (`planner/entities/Task.java:1196-1272`): FINISHED if progress = 1; IN_PROGRESS if 0 < progress < 1 or any work report hours attached; READY_TO_START if no progress/hours and all END_START predecessors finished and all START_START predecessors started or finished; BLOCKED otherwise; PENDING remaining (`TaskStatusEnum.java`).

### OpenProject progress derivation and rollup
- Status-based mode: on user status change, `% complete = status.default_done_ratio`; remaining work = work × (1 − %/100), rounded 2, clamped to [0, work] (`app/services/work_packages/set_attributes_service/derive_progress_values_status_based.rb:34-80`, `progress_values_calculations.rb:40-44`).
- Work-based mode: two of {work, remaining, %} given → derive the third: `work = remaining / (1 − %/100)`; `% = (work − remaining) / work × 100` on 2-decimal-rounded values (`progress_values_calculations.rb:34-60`); derivation fires only for the value the user did not supply; when `complete_on_status_closed` is set and the status changes to a closed one, % is forced to 100 (`derive_progress_values_work_based.rb:61-90`).
- Ancestor rollup (`update_ancestors_service.rb:130-236`): derived totals = sum over self + descendants included in totals; derived % = work-weighted `(Σwork − Σremaining)/Σwork × 100` rounded, or simple average of children's derived/own % (excluding statuses flagged `excluded_from_totals`).

### OpenProject baseline comparison (temporal)
- `Journal.at_timestamp(t)`: `validity_period @> t` (`app/models/journal/timestamps.rb:66-78`).
- `Journable#at_timestamp(t)`: instantiate a read-only record from the journal's data row + id/timestamps; `rollback!` writes historic attributes back onto the live record (`app/models/journable/timestamps.rb:61-120`).
- `WithHistoricAttributes`: for each requested timestamp, historic attributes or only changed attributes vs current; `exists_at_timestamps`, `matches_query_filters_at_timestamps` (whether the item was in the query result then) (`app/models/journable/with_historic_attributes.rb:145-200`). This gives added (not existing at baseline), removed (not existing now / not matching now) and changed fields.

### Odoo / ERPNext progress rollups
- Odoo task progress = (effective + subtask effective hours) / allocated hours, overtime = excess (`odoo/addons/hr_timesheet/models/project_task.py:110-118`).
- ERPNext project % by method: Manual; Task Completion = completed-or-cancelled / total × 100; Task Progress / Task Weight = weighted average of task `progress` (completed/cancelled count as 100) (`erpnext/erpnext/projects/doctype/project/project.py:286-350`); project status Completed iff 100% and manual Completed refused below 100% (`:322-335`).

### IFC baseline
`create_baseline`: only PLANNED schedules; create BASELINE schedule; duplicate each root task subtree; assign duplicates to the baseline schedule; link each original→copy with `IfcRelDefinesByObject` (reusing the original's existing `Declares` relationship) (`api/sequence/create_baseline.py:67-110`).

## State machines and workflows
- Activity progress state (P6/MPXJ): NOT_STARTED → IN_PROGRESS (actual start set) → COMPLETED (actual finish set); suspend/resume dates subtract the suspended span from actual duration (`ActivityStatusHelper.java:44-62`, `PrimaveraScheduler.java:617-645`).
- LibrePlan task status: PENDING/BLOCKED/READY_TO_START → IN_PROGRESS → FINISHED, driven by progress value, attached work reports and predecessor states (`planner/entities/Task.java:1196-1272`).
- LibrePlan consolidation: measurement recorded → consolidated (days frozen, task end recalculated on remaining effort) → unconsolidated by removing the consolidated value (inferred from `consolidation` / `consolidated_value` mapping).
- OpenProject journal version: each save closes the previous `validity_period` and opens a new one (enforced non-overlap constraint, `journals.rb`).
- ERPNext project: Open ↔ Completed by % complete; Cancelled / On hold are manual and suppress automatic status (`project.py:317-322`).

## Cross-domain links
- Baselines copy D03 activities/WBS, D04 relationships, D07 assignments and costs; baseline values are the PV source for D11.
- Progress update re-runs D06 CPM (data date, retained logic / progress override) and D08 remaining dates.
- Actuals arrive from D32 timesheets (LibrePlan TIMESHEETS advance type, ERPNext/Odoo hours rollups).
- Period actuals (`ActivityPeriodActualType`) feed D11 period EV and D33 trend reporting; status updates link to D12 monitoring.
- Journals are the D36 audit trail; check-out locks belong to D02/D35 (XML import/export).

## Gaps
- Update Baseline merge (D10.02): rebuild by matching current↔baseline activities on Activity ID, then per `UpdateBaselineOptionType` flag add new, delete missing, and overwrite selected field groups; stamp `LastBaselineUpdateDate`.
- Claim-Digger style comparison report (D10.03): rebuild a field-by-field diff per entity type over matched keys (MPXJ key strategy) with added/deleted/changed sets; OpenProject's per-timestamp diff is the model.
- "Update Progress" (D10.04): for activities whose planned dates fall before the new data date, set actual start/finish = planned, remaining duration = planned remaining after data date, % from elapsed share; "Apply Actuals": post approved timesheet hours to assignment actual units (see D32), then reschedule.
- Progress spotlight (D10.05): query activities with planned/early start or finish in (old data date, new data date].
- Period history and trends (D10.06): persist `ActivityPeriodActual` per financial period at each period close and a schedule snapshot (finish dates, total float) per update; trend = series over snapshots.
- Check-out/check-in (D10.08): exclusive lock row (project, user, date), reject writes from others, import with merge on check-in.
