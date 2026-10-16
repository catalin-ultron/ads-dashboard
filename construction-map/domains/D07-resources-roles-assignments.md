# D07 Resources, Roles and Assignments

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D07.01 | Resource dictionary | MPXJ `Resource` + P6 field maps (`rsrc`, `rsrcrate`); LibrePlan `Resource`/`Worker`/`Machine` | full | MPXJ carries every P6 resource attribute (type, parent, calendar, default/max units effective-dated, 5 prices effective-dated, primary role, UoM, currency, location, shift, auto-compute flag, timesheet manager via PMXML schema) |
| D07.02 | Roles, proficiency, role rates/limits | MPXJ (`Resource.getRole()`, `getRoleAssignments()` → `SkillLevel`), PMXML `RoleRateType`/`RoleLimitType`/`ResourceRoleType`; LibrePlan `Criterion` + `CriterionSatisfaction` | partial | Storage complete in MPXJ; role-to-resource matching (search by role + proficiency + availability) only exists as LibrePlan criterion matching, without proficiency ranking |
| D07.03 | Resource assignments | MPXJ `ResourceAssignment` + XER `taskrsrc` map; LibrePlan `ResourceAllocation` (specific/generic) | full | MPXJ: budget/actual/remaining units and costs, rate source/type, cost account, remaining early/late dates, curve, lag; cost = work × effective-dated rate |
| D07.04 | Resource curves | MPXJ `WorkContour` (21-point), PMXML `ResourceCurveValuesType`; LibrePlan `StretchesFunction`, `SigmoidFunction` | full | MPXJ stores curves but does not spread with them; LibrePlan has working spreading functions (stretches, interpolated, sigmoid) |
| D07.05 | Manual planning (time-phased overrides) | LibrePlan `ManualFunction` + per-day `DayAssignment`; MPXJ raw timephased lists | partial | LibrePlan persists per-day effort; MPXJ round-trips P6 `target_crv`/`remain_crv` strings; no period-bucket editor model |
| D07.06 | Time-phased spreading engine | MPXJ `TimephasedUtility.segmentWork/segmentCost`, `ResourceAssignment.getTimephasedCost`; LibrePlan `AssignmentsAllocator` + `Distributor` | full | MPXJ splits stored timephased work into arbitrary ranges by calendar; LibrePlan generates daily assignments from calendar capacity |
| D07.07 | Resource teams and pools | LibrePlan `GenericResourceAllocation` (criteria-defined pool), TaskJuggler resource groups (`allLeaves`), MPXJ `Resource.getGeneric()` | partial | Pool-as-criteria and group allocation exist; no team entity with capacity |
| D07.08 | Material and equipment resources | MPXJ `ResourceType` WORK/MATERIAL/COST + `UnitOfMeasure`; LibrePlan `Machine` + `MachineWorkersConfigurationUnit`; Odoo `resource.resource.resource_type` | full | MPXJ material units/cost fields (`getPlannedMaterial` etc.); LibrePlan derives worker allocations from machine allocations |
| D07.09 | Auto-compute actuals | MPXJ flag `auto_compute_act_flag` | partial | Flag stored on resource/task; no OSS implements the "actual = budget × %" rule; LibrePlan consolidation is the nearest behaviour (see D10) |
| D07.10 | Price/unit and cost-per-use | MPXJ `CostRateTable` (5 tables × 5 rates, cost-per-use, shift period); OpenProject `HourlyRate`; LibrePlan `HourCost` | full | Effective-dated lookup in three sources; MPXJ adds cost-per-use into the first timephased bucket |

## Storage model

### MPXJ / Primavera P6 (most complete reference model)
Paths relative to `mpxj/src/main/java/org/mpxj/`.

**Resource** (`Resource.java`; XER table `RSRC`, PMXML `ResourceType`). Roles are stored as `Resource` instances with `getRole()==true`; XER `ROLES` rows map into the same class via `getDefaultRoleFieldMap` (`primavera/TableContextReader.java:1238`) with a clash map to keep IDs distinct.

| Field | Type | P6 column | Citation |
|---|---|---|---|
| uniqueID | Integer PK | `rsrc_id` | `primavera/TableContextReader.java:1206` |
| resourceID (short name), name, code (employee code), email, notes, GUID | String | `rsrc_short_name`, `rsrc_name`, `employee_code`, `email_addr`, `rsrc_notes`, `guid` | same map |
| type | enum `ResourceType` {WORK, MATERIAL, COST} | `rsrc_type` | `ResourceType.java:30-32` |
| parentResourceUniqueID | FK self (hierarchy) | `parent_rsrc_id` | map |
| calendarUniqueID | FK calendar (D05) | `clndr_id` | `TableContextReader.java:848-855` |
| defaultUnits | Number (% = qty/hr × 100) | `def_qty_per_hr` (null means 0) | `TableContextReader.java:858-862` |
| availability | `AvailabilityTable` = list of `Availability{range, units}` effective-dated | `rsrcrate.max_qty_per_hr`, `start_date` | `Availability.java:31-77`, `AvailabilityTable.java:43,194` |
| costRateTables[0..4] | `CostRateTable` = list of `CostRateTableEntry{start,end,rates[5],costPerUse,shiftPeriod}` | `rsrcrate.cost_per_qty..cost_per_qty5`, `shift_period_id` | `CostRateTable.java:126 (MAX_TABLES=5)`, `CostRateTableEntry.java:174-180 (MAX_RATES=5)`, `TableContextReader.java:906-943` |
| primaryRoleUniqueID | FK role | `role_id` | map |
| roleAssignments | `Map<Resource role, SkillLevel>`; `SkillLevel` {MASTER, EXPERT, SKILLED, PROFICIENT, INEXPERIENCED} | `RSRCROLE.skill_level` | `Resource.java:1776`, `SkillLevel.java:29-36`, `primavera/TableProjectReader.java:875` |
| unitOfMeasureUniqueID, currencyUniqueID, locationUniqueID, shiftUniqueID | FKs | `unit_id`, `curr_id`, `location_id`, `shift_id` | map |
| calculateCostsFromUnits, autoComputeActuals, active, sequenceNumber | boolean/int | `def_cost_qty_link_flag`, `auto_compute_act_flag`, `active_flag`, `rsrc_seq_num` | map |
| generic, canLevel, overtime rate, cost per use | boolean / Rate / Number | MSP-originated | `Resource.java` getters |
| resource codes | set of `ResourceCodeValue` | `RSRCRCAT` | `TableContextReader.java:833, 878-900` |
| UDF values | via `UserDefinedField` subject `RSRC` | `UDFVALUE` | `TableContextReader.java:865` |

PMXML-only resource fields bound in `primavera/schema/ResourceType.java:329-330`: `TimesheetApprovalManager`, `TimesheetApprovalManagerObjectId`.

**Role rates and limits** (PMXML schema, `primavera/schema/`): `RoleRateType` {RoleObjectId, EffectiveDate, MaxUnitsPerTime, PricePerUnit..PricePerUnit5}; `RoleLimitType` {RoleObjectId, EffectiveDate, MaxUnitsPerTime}; `ResourceRoleType` {ResourceObjectId, RoleObjectId, Proficiency}; `ResourceRateType` {ResourceObjectId, EffectiveDate, MaxUnitsPerTime, PricePerUnit..5, ShiftPeriodObjectId}. Role limits are read into the role's `AvailabilityTable` (`TableContextReader.java:1142-1170`).

**ResourceAssignment** (`ResourceAssignment.java`; XER `TASKRSRC`, map at `primavera/TableProjectReader.java:1069`).

| Field | Type | P6 column |
|---|---|---|
| uniqueID, GUID | Integer PK | `taskrsrc_id`, `guid` |
| task, resource, role | FKs (resource null + role set ⇒ role-only "unstaffed" assignment, the role becomes the resource) | `task_id`, `rsrc_id`, `role_id` (`TableProjectReader.java:654-662`) |
| costAccountUniqueID | FK cost account (D17) | `acct_id` |
| plannedWork / remainingWork / actualRegularWork / actualOvertimeWork | Duration | `target_qty`, `remain_qty`, `act_reg_qty`, `act_ot_qty` |
| plannedCost / remainingCost / actualRegularCost / actualOvertimeCost | Number | `target_cost`, `remain_cost`, `act_reg_cost`, `act_ot_cost` |
| units / remainingUnits | % (qty/hr × 100) | `target_qty_per_hr`, `remain_qty_per_hr` (`TableProjectReader.java:703-704`) |
| rateSource | enum `RateSource` {RESOURCE, ROLE, OVERRIDE} | `cost_per_qty_source_type` |
| rateIndex | 0..4 | `rate_type` |
| overrideRate | Rate/hr | `cost_per_qty` |
| plannedStart/Finish, actualStart/Finish, remainingEarly/Late Start/Finish | LocalDateTime | `target_start_date`, `target_end_date`, `act_start_date`, `act_end_date`, `restart_date`, `reend_date`, `rem_late_start_date`, `rem_late_end_date` |
| delay / remainingDelay (lag) | Duration | `target_lag_drtn_hr_cnt`, `relag_drtn_hr_cnt` |
| workContour | FK `WorkContour` | `curv_id` |
| calculateCostsFromUnits | boolean | `cost_qty_link_flag` |
| resourceRequestType | {NONE, REQUEST, DEMAND} | MSP (`ResourceRequestType.java`) |
| raw timephased planned/actual/remaining work | `List<TimephasedWork>` | `target_crv`, `actual_crv`, `remain_crv` (`TableProjectReader.java:710-712`) |
| assignment codes, UDFs | `ResourceAssignmentCodeValue`, UDF subject `TASKRSRC` | `ASGNMNTACAT`, `UDFVALUE` |

Derived on read: `actualWork = act_reg_qty + act_ot_qty`, `work = actual + remaining`, `actualCost = act_reg_cost + act_ot_cost`, `cost = actual + remaining`, then cost rolled up to the parent task (`TableProjectReader.java:681-700`, `primavera/RollupHelper.java`).

**WorkContour** (`WorkContour.java:28-135`): `{uniqueID, name, isDefault, double[21] curveValues}`; `null` curve = manual (contoured); built-ins FLAT, BACK_LOADED, FRONT_LOADED, DOUBLE_PEAK, EARLY_PEAK, LATE_PEAK, BELL, TURTLE. PMXML `ResourceCurveValuesType` has `Value0, Value5 … Value100` (21 points at 5% of duration).

### LibrePlan (allocation engine model)
Mappings under `libreplan/libreplan-business/src/main/resources/org/libreplan/business/`.

| Table | Key fields | Relations | Citation |
|---|---|---|---|
| `resource` | `code` (unique), `resource_type` (NON_LIMITING / LIMITING) | 1–N `criterion_satisfaction`, 1–N `day_assignment`, N–1 `calendar`, 1–N `resources_cost_category_assignment` | `resources/entities/Resources.hbm.xml:6-50` |
| `worker` (joined) | `first_name`, `surname`, `nif`, FK `user` | subclass `virtual_worker` (`observations`) represents a group/capacity >1 | `Resources.hbm.xml:54-66` |
| `machine` (joined) | `name`, `description` | 1–N `machine_workers_configuration_unit` {`name`, `alpha`, M–N required criteria, 1–N `machine_worker_assignment` {start,finish, worker}} | `Resources.hbm.xml:70-80, 222-266` |
| `criterion_type` | `name`, `allow_simultaneous_criterions_per_resource`, `allow_hierarchy`, `resource` (WORKER/MACHINE/ANY), `enabled` | 1–N `criterion` | `Resources.hbm.xml:182-217` |
| `criterion` | `code`, `name`, `active`, FK `id_criterion_type`, FK `parent` (tree), FK `id_cost_category` | 1–N children | `Resources.hbm.xml:106-150` |
| `criterion_satisfaction` | `start_date`, `finish_date`, `is_deleted`, FK criterion, FK resource | effective-dated skill/role membership | `Resources.hbm.xml:155-178` |
| `resource_allocation` | `resources_per_day`, `intended_resources_per_day`, `intended_total_hours`, `intended_total_assignment`, `intended_non_consolidated_effort`, FK `task`, FK `assignment_function` | joined `specific_resource_allocation` (FK resource) or `generic_resource_allocation` (M–N `all_criterions`, `resource_type`) | `planner/entities/ResourceAllocations.hbm.xml:8-77` |
| `specific/generic/derived_day_assignments_container` | FK allocation, FK `scenario`, `intraDayStart/End` (date + effort in first/last day) | 1–N `day_assignment` | `ResourceAllocations.hbm.xml:81-180` |
| `day_assignment` (discriminator `specific_day`/`generic_day`/`derived_day`) | `day`, `duration` (seconds), `consolidated`, FK resource, FK container | the per-day time-phased unit | `ResourceAllocations.hbm.xml:265-304` |
| `assignment_function` | joined `stretches_function` (list `stretches` {`length_percentage`, `amount_work_percentage`}, `type` STRETCHES/INTERPOLATED), `sigmoid_function`, `manual_function` | curve per allocation | `ResourceAllocations.hbm.xml:307-342` |
| `derived_allocation` | FK `resource_allocation_id` (machine), FK configuration unit | worker allocations generated from a machine allocation | `ResourceAllocations.hbm.xml:345-362` |
| `cost_category` / `hour_cost` / `type_of_work_hours` / `resources_cost_category_assignment` | `hour_cost{price_cost, init_date, end_date, FK type, FK category}`; assignment `{init_date, end_date, FK category, FK resource}`; `type_of_work_hours.default_price` | effective-dated rates per resource via category | `costcategories/entities/CostCategories.hbm.xml:7-104` |

### Other sources
- OpenProject rates (`openproject/modules/costs/app/models/`): `rates` STI table with `HourlyRate` (per user per project) and `DefaultHourlyRate` (per user), columns `rate`, `valid_from`, `project_id`, `user_id` (`rate.rb:30-45`). Cost types (`cost_type.rb:81 rate_at`) for material-like unit costs.
- Odoo `resource.resource` (`odoo/addons/resource/models/resource_resource.py:34-62`): `name`, `resource_type` {user, material}, `user_id`, `time_efficiency` (default 100), `calendar_id`, `tz`.
- Odoo `project.role` (`odoo/addons/project/models/project_role.py:7-22`): `name`, M–N `user_ids`; `project.task.role_ids` M–N (`project/models/project_task.py:200`).
- IfcOpenShell: `IfcConstructionResource` with `Usage: IfcResourceTime {ScheduleWork, ScheduleUsage}`, `EPset_Productivity {BaseQuantityConsumed, BaseQuantityProducedName, BaseQuantityProducedValue}` (`ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/resource/calculate_resource_work.py:24-60`).
- ERPNext `Activity Type` {costing_rate, billing_rate} and `Activity Cost` {employee, activity_type, costing_rate, billing_rate} (`erpnext/erpnext/projects/doctype/activity_cost/activity_cost.json`).

## Algorithms and logic

### Effective rate resolution (MPXJ)
`ResourceAssignment.getEffectiveRate(date)` (`ResourceAssignment.java:2314-2340`):
1. `rateSource == OVERRIDE` → return `overrideRate`.
2. Otherwise pick `role` if `rateSource == ROLE` else `resource`; table = `resource.getCostRateTable(costRateTableIndex)` (`:1991-2003`).
3. `entry = table.getEntryByDate(date)`: first entry with `date < entry.endDate` (`CostRateTable.java:32-45`); return `entry.getRate(rateIndex)`.
Edge: missing resource/role or entry → null rate.

### Time-phased cost (MPXJ)
`getTimephasedCost(ranges, rateIndex, workSupplier)` (`ResourceAssignment.java:3205-3300`):
1. Get hours per range from the work supplier (planned, actual, or remaining timephased work).
2. Fetch rate entries overlapping the whole span; refuse (all null) if entries have more than one distinct shift period.
3. For each range: advance to the rate entry whose end is after range start; if range fits inside one entry, `cost = hours × ratePerHour`; otherwise split the range at each rate boundary, re-query work for each sub-range and sum `work × rate`.
4. Accrual dispatch (`:2800-2850`): `ResourceType.COST` uses cost-resource path; accrue START/END puts the whole cost in first/last bucket; PRORATED uses step 3 and then `addTimephasedRemainingCostPerUse` (`:3709-3745`): if not started, add `costPerUse` (scaled by units/100 for time-based resources) to the bucket whose range starts at assignment start.

### Time-phased work segmentation (MPXJ)
`TimephasedUtility.segmentWork(calendar, work, ranges, units)` (`TimephasedUtility.java:48-160`): walk ranges and timephased blocks in parallel; for each overlap `[max(starts), min(finishes)]` compute calendar working hours (or elapsed hours if the block lies on non-working time), add `amountPerHour × hours`; split the range when the block ends inside it. MS Project special case: a single zero-length block with non-zero work is placed in the last range (`:58-68`). P6 curve strings `"work:period;..."` are parsed into contiguous blocks starting at the next work start (`primavera/TimephasedHelper.java:51-95`).

### Allocation spreading (LibrePlan)
- Resources-per-day allocation: for each `PartialDay` in `[start, end)`, `effortForDay = allocationCalendar.asDurationOn(day, resourcesPerDay)` then `distributeForDay` (`planner/entities/ResourceAllocation.java:724-735, 1213-1215`).
- Effort-on-interval allocation: build `Capacity` for each day from `taskCalendar.availability AND resourcesAvailability`, then `Distributor.among(capacities).distribute(effort)` (`ResourceAllocation.java:900-957`); days not valid in the availability timeline are skipped.
- Effort-driven end date: `UntilFillingHoursAllocator.untilAllocating` loops day by day assigning `min(remaining, day capacity)` until effort reaches zero; end = last day adjusted by the largest last assignment (`planner/entities/allocationalgorithms/UntilFillingHoursAllocator.java:125-153, 279-290`).
- Reset: non-consolidated day assignments are removed and replaced; consolidated ones are kept (`ResourceAllocation.java:1011-1020, 1165-1172`).

### Generic (pool) allocation across resources (LibrePlan)
`EffortDistributor.distributeForDay(day, total)` (`planner/entities/EffortDistributor.java:312-512`):
1. Candidate set = resources passing `isSelectable(resource, day)`; for generic allocations the selector is the AND of all required criteria evaluated at that date (`GenericResourceAllocation.java:184-191`).
2. Pass 1 (no overtime): compute each candidate's available capacity that day minus effort already assigned; sort descending by availability with resources already picked in this allocation ranked first (`:265-280, 370-382`); greedily assign `min(remaining, available)`.
3. Pass 2 (overtime), recursive: water-fill the remainder across candidates using `ShareDivision.plus` (bucket filling to equalize per-unit load; `ShareDivision.java:116-171`), shares computed per capacity unit from already-assigned seconds minus one-unit capacity (`EffortDistributor.java:482-511`); clip each resource to `standardEffort + allowedExtraEffort` unless overassignable without limit (`:414-448`); recurse with resources still having spare capacity.

### Curves (LibrePlan)
- Sigmoid: cumulative hours at day point `x` = `totalHours / (1 + e^(−x))`, points spaced with constant `12/days` (`planner/entities/SigmoidFunction.java:252-265`); per-day = differences, rounded with remainder redistribution, zero days avoided (`:131-210`).
- Stretches: list of (lengthPercentage, amountWorkPercentage) must sum to 100% (`StretchesFunction.java:420-428`); STRETCHES distributes hours per interval proportionally, INTERPOLATED fits a `SplineInterpolator` over cumulative (day, hours) points and takes daily differences, redistributing the integer remainder (`StretchesFunctionTypeEnum.java:39-190`).

### Machine → worker derived allocation (LibrePlan)
`DerivedAllocationGenerator.generate` creates one `derived_allocation` per `MachineWorkersConfigurationUnit`; each machine day assignment's seconds are multiplied by the unit's `alpha` and distributed to the workers assigned to that unit (`planner/entities/DerivedAllocationGenerator.java:55-115`).

### Criterion satisfaction validity (LibrePlan)
`Resource.canAddSatisfaction` (`resources/entities/Resource.java:595-621`): reject if the criterion type cannot relate to this resource class; reject if an earlier/later satisfaction of the same criterion overlaps the interval; if `allowSimultaneousCriterionsPerResource` is false, also reject overlap with any satisfaction of the same type. `Criterion.isSatisfiedBy(resource, start, end)` = satisfaction enforced over the whole interval (`Criterion.java:284-292`).

### Parametric resource work (IfcOpenShell)
`get_resource_required_work` (`ifcopenshell/src/ifcopenshell-python/ifcopenshell/util/resource.py:115-136`): `required = totalQuantityOfAssignedProducts × (BaseQuantityConsumed / BaseQuantityProducedValue)`; products reached through `IfcRelAssignsToProcess` → task → `IfcRelAssignsToProduct`; quantity "Count" counts products. `calculate_resource_usage`: `ScheduleUsage = ScheduleWork / (taskDuration × 8h or 24h)` (`api/resource/calculate_resource_usage.py:26-48`).

### Rate lookups for labor cost (other sources)
- LibrePlan: price = `HourCost.priceCost` where resource's cost-category assignment and the hour cost are both active at the date and type matches; fallback `TypeOfWorkHours.defaultPrice` (`costcategories/daos/HourCostDAO.java:64-78`, `planner/entities/MoneyCostCalculator.java:134-158`).
- OpenProject: project-hierarchy `HourlyRate` with greatest `valid_from <= date`, else `DefaultHourlyRate` (`modules/costs/app/models/hourly_rate.rb:96-100`).
- Odoo: `employee.hourly_cost` flat (`hr_timesheet/models/account_analytic_line.py:506-508`).

## State machines and workflows
- Assignment staffing: role-only assignment (rsrc null, role set) versus staffed (rsrc set, role optional) is a state implied by the null pattern in P6 (`primavera/TableProjectReader.java:658-662`); MSP's `ResourceRequestType` {NONE, REQUEST, DEMAND} marks requested resources.
- Odoo role-based staffing on template copy: when a project is created from a template, each task's `role_ids` are resolved to users from a supplied role→users mapping, or one random active member of each role's `user_ids` is linked; `role_ids` then cleared on the copy (`odoo/addons/project/models/project_task.py:918-938`).
- LibrePlan criterion satisfaction lifecycle: active interval `[start_date, finish_date)`, soft-deleted via `is_deleted` (`Resources.hbm.xml:167-171`).
- OpenProject rate change propagation: `after_create` re-costs entries between `valid_from` and the next rate; `after_update` re-costs if value or validity moved; `after_destroy` recosts entries that pointed to it (`modules/costs/app/models/rate.rb:94-130`).

## Cross-domain links
- Resource.calendar → D05 calendars; assignment effective calendar drives dates for resource-dependent activities (D06).
- Assignment.task → D03 activities; assignment remaining early/late dates written by D06/D08.
- Assignment.costAccount → D17 CBS/cost accounts; assignment costs roll up to activity/WBS for D11 earned value.
- Resource.currency → D01; resource ↔ user/employee link → D02 identity (LibrePlan `worker.user`, OpenProject rates keyed by user, P6 timesheet approval manager).
- Resource/role/assignment codes and UDFs → D09.
- Timesheet actuals feed assignment actual units/costs → D32; progress → D10.
- Limiting resources and criteria capacity → D08.

## Gaps
- Role staffing search (role + proficiency + availability ranking, P6 "Assign by Role"): only storage exists (`SkillLevel`, `RSRCROLE`). Rebuild: query resources having the role, filter by `Availability` minus booked demand over the assignment window, order by proficiency then free capacity.
- Curve-driven spreading using the 21-point P6 curve: MPXJ stores curves, LibrePlan uses its own functions. Rebuild: interpolate cumulative % at each bucket boundary over assignment working time and take differences.
- Auto-compute actuals rule: no implementation. Rebuild: on progress update, `actualUnits = budgetUnits × activity % complete` (or planned-to-date), `remaining = atCompletion − actual`, recompute costs from rates.
- Manual future-period planning buckets (P6 "Manual Planning"): rebuild as per-period override rows keyed (assignment, period) that replace curve spread for future periods.
- Teams/pools with capacity (Primavera Cloud): rebuild as team entity with member resources and aggregated `AvailabilityTable`; LibrePlan `virtual_worker` is the nearest capacity model.
