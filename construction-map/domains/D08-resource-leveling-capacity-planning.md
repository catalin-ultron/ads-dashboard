# D08 Resource Leveling and Capacity Planning

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D08.01 | Resource leveling (serial heuristic) | TaskJuggler `Project.scheduleScenario` + `TaskScenario.scheduleSlot/bookResources` + `ResourceScenario` scoreboard; LibrePlan limiting resource queue | partial | TaskJuggler is a priority-ordered serial slot-booking scheduler (leveling is inherent, not a post-pass); no "level within float" or leveling delay field computation; LibrePlan does first-fit gap insertion per limiting resource |
| D08.02 | Leveling options | MPXJ `ProjectProperties` from XER `schedoptions` / PMXML `ScheduleOptionsType` | partial | All P6 options stored (level all, within float, preserve dates, float threshold, over-allocation %, other projects priority, priority list); no OSS consumes them |
| D08.03 | Remaining early/late dates | MPXJ `PrimaveraScheduler.setRemainingEarlyDates/LateDates`, assignment `updateDates` | partial | Remaining dates computed from CPM + data date; leveled dates never written (no leveler) |
| D08.04 | Resource and role capacity analysis | LibrePlan `OrderResourceLoadCalculator`, `Capacity`, `AvailabilityCalculator`; TaskJuggler `ResourceScenario.getEffectiveFreeWork/getAllocatedTime`; MPXJ `Resource.calculateOverallocated` | full | Daily load vs capacity lines, order vs all-projects load and overload; criterion (role) aggregate availability |
| D08.05 | Portfolio resource planning scenarios | LibrePlan `Scenario` / `OrderVersion` | partial | Scenarios version whole orders' allocations; no activity-free demand plan |
| D08.06 | Resource allocation requests | none (MSP `ResourceRequestType` flag only) | none | No request/booking workflow in any source |
| D08.07 | Leveling logs | TaskJuggler `@competitors`, `@contendedResources`, `unscheduled_tasks` warnings | partial | Per-task contention tracking and failure warnings; no persisted log |

## Storage model

### Leveling options (P6 via MPXJ)
`mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java:822-875` maps XER `schedoptions` columns into `ProjectProperties`:

| P6 column | MPXJ property | Type |
|---|---|---|
| `level_all_rsrc_flag` | `levelAllResources` | boolean |
| `level_within_float_flag` | `levelResourcesOnlyWithinActivityTotalFloat` | boolean |
| `level_float_thrs_cnt` | `preserveMinimumFloatWhenLeveling` | Duration (hours) |
| `level_over_alloc_pct` | `maxPercentToOverallocateResources` | Double |
| `level_keep_sched_date_flag` | `preserveScheduledEarlyAndLateDates` | boolean |
| `level_outer_assign_flag` / `level_outer_assign_priority` | `considerAssignmentsInOtherProjects` / `...WithPriorityEqualHigherThan` | boolean / Integer |
| `levelprioritylist` | `levelingPriorities` | String (encoded list) |

Leveling outputs stored by P6 and read by MPXJ: task `LEVELING_DELAY` (`Task.java:804,1830`), assignment `levelingDelay`, `restart_date`/`reend_date` (remaining early), `rem_late_start_date`/`rem_late_end_date` (`TableProjectReader.java:1069-1105`), project `LastLevelDate` (PMXML `BaselineProjectType`/`ProjectType`). Resource capacity: `AvailabilityTable` (max units effective-dated), role limits `RoleLimitType{EffectiveDate, MaxUnitsPerTime}` (`primavera/schema/RoleLimitType.java`).

### TaskJuggler scheduler state (in memory)
Paths relative to `taskjuggler/lib/taskjuggler/`.

| Structure | Contents | Citation |
|---|---|---|
| `ResourceScenario @scoreboard` | array indexed by time slot (granularity `scheduleGranularity`): `nil` = free working slot; `Task` = booked; Integer bit field: bit1 = non-working, bits 2-5 = leave type index, bit 8 = shift leave replacement | `ResourceScenario.rb:830-905` |
| `@effort`, `@efficiency`, `@criticalness`, `@limits`, `@duties`, `@firstBookedSlot(s)`, `@lastBookedSlot(s)` | per-resource booking totals and limits | `ResourceScenario.rb:187-219` |
| `TaskScenario` attrs `priority` (default 500), `pathcriticalness`, `effort`, `doneEffort`, `length/doneLength`, `duration/doneDuration`, `@allocate`, `@mandatories`, `@competitors`, `@contendedResources`, `@allLimits`, `@currentSlotIdx`, `forward` | per-task scheduling state | `TaskScenario.rb:825-980, 1753-1960`; `Project.rb:92` |
| `Allocation` | candidates list, `selectionMode` (0 order, 1 min alloc probability, 2 min loaded, 3 max loaded, 4 random), `persistent`, `mandatory`, `atomic`, `lockedResource`, `shifts` | `Allocation.rb:75-125` |
| `Limits::Limit` | `dailymax/min`, `weeklymax/min`, `monthlymax/min`, `maximum/minimum`, optional interval and resource; counters per period | `Limits.rb:27-140, 181-240` |

### LibrePlan limiting resource queue
`libreplan/libreplan-business/src/main/resources/org/libreplan/business/planner/entities/ResourceAllocations.hbm.xml`:

| Table | Fields | Citation |
|---|---|---|
| `limiting_resource_queue` | FK `resource_id` unique (one queue per resource with `resource_type = LIMITING_RESOURCE`) | `resources/entities/Resources.hbm.xml:85-101` |
| `limiting_resource_queue_element` | FK `resource_allocation_id`, FK `limiting_resource_queue_id`, `earlier_start_date_because_of_gantt`, `earliest_end_date_because_of_gantt`, `creation_timestamp`, `start_date`/`start_hour`, `end_date`/`end_hour` | `ResourceAllocations.hbm.xml:184-230` |
| `limiting_resource_queue_dependency` | `type`, FK `origin_queue_element_id`, FK `destiny_queue_element_id` | `ResourceAllocations.hbm.xml:233-260` |
| `day_assignment` | per resource/day load used for all load/capacity calculations | `ResourceAllocations.hbm.xml:265-304` |

### LibrePlan scenarios (planning versions)
`scenario` {name, description, FK predecessor, map `Order → OrderVersion`}; each allocation container (`specific/generic_day_assignments_container`) carries FK `scenario`, so a scenario holds its own day-assignment set (`scenarios/entities/Scenario.java:53-67`, `ResourceAllocations.hbm.xml:97-99, 136-138`).

## Algorithms and logic

### TaskJuggler serial priority scheduler (leveling by construction)
`Project.scheduleScenario` (`Project.rb:1170-1260`):
1. Work list = leaf, non-milestone, unscheduled tasks.
2. Sort by `priority` desc, then `pathcriticalness` desc, then `seqno` asc (`Project.rb:1185-1188`).
3. Loop: scan list in order, pick first task with `readyForScheduling?` (forward: start known and (duration spec or end); backward: mirror) (`TaskScenario.rb:911-925`); call `task.schedule`; remove it; restart scan from the top (scheduling may make higher-priority tasks ready).
4. No ready task and no failures → `deadlock` warning; failures → `unscheduled_tasks` warning listing up to 10.

`TaskScenario.schedule` (`TaskScenario.rb:931-975`): start slot = start (or `now` in projection mode for tasks with allocations); call `scheduleSlot` slot by slot (+1 forward / −1 backward); exceeding the project interval → `markAsRunaway`.

`scheduleSlot` (`TaskScenario.rb:1753-1822`): by duration type: effort tasks book until `doneEffort >= effort` then propagate end; length tasks count only on-shift slots; duration tasks count every slot; start-end tasks book until the other end.

`bookResources` (`TaskScenario.rb:1824-1913`), per slot:
1. Skip if no resource available at all, or projection mode and slot before `now`.
2. Task-level limits (`limitsOk?`) and task shifts must allow the slot.
3. Mandatory allocations: at least one candidate whose every leaf resource is available and within limits; otherwise book nothing this slot.
4. For each allocation: if persistent and a locked resource exists, try it; atomic allocation with locked resource booked elsewhere → `rollbackBookings`; persistence broken past the locked resource's last slot → warn and unlock.
5. Iterate `allocation.candidates(scenario)` in selection-mode order and book the first that succeeds.

`bookResource` (`TaskScenario.rb:1915-1960`): for each leaf resource: stop if effort reached; `r.book(slot, task)` succeeds only if scoreboard slot is `nil` and resource limits OK (`ResourceScenario.rb:162-219`); on first booking of an effort task, propagate start date to the slot; `doneEffort += efficiency`. On failure, record the competing task in `@competitors` and count `@contendedResources[competitor][r]` (contention log).

Priority heuristic (`TaskScenario.rb:825-905`, `ResourceScenario.rb:77-89`): resource criticalness = `allocatedEffort / freeSlots` (1.0 if none free); task criticalness = `effort × mean(candidate resource criticalness)` (milestones `priority/500`); path criticalness = max over successor paths of summed criticalness, computed recursively with memoization. Candidate ordering mode 1 sorts by resource criticalness (persistent: booked effort first).

Limits (`Limits.rb:181-278`): `setLimit` creates per-day/week/month/total counters with upper or lower bound; `ok?(slot, upper, resource)` checks the counter for the period containing the slot; `inc` on each booking.

### LibrePlan limiting resource queue insertion (first-fit gap)
`LimitingResourceAllocator.getFirstValidGap(queue, element)` (`planner/limiting/entities/LimitingResourceAllocator.java:107-280`):
1. `startTime` = element's earliest start because of Gantt dependencies (date, hour 0).
2. For position 0..n over the queue's elements ordered by start: gap = `[startTime, first.start)` before the first element; `[max(prev.end, startTime), next.start)` between elements; `[max(startTime, last.end), ∞)` after the last.
3. Specific allocation: accept the gap if `gap.canFit(element)` (enough working effort in the gap). Generic allocation: split the gap into sub-gaps where the queue resource satisfies the element's criteria, accept first sub-gap that fits.
4. Day assignments are then generated from the gap start (or backwards from the end) on the resource calendar (`:293-400`).
Queue elements carry dependencies (`limiting_resource_queue_dependency`) so moving one element re-evaluates dependents (inferred from mapping).

### Capacity, load and overload (LibrePlan)
- `Capacity{standardEffort, allowedExtraEffort}`; `allowedExtraEffort == null` = overassignable without limit (`calendars/entities/Capacity.java:111-160`); `hasSpareSpaceForMoreAllocations(assigned)`, `limitDuration`, `minus`, `multiplyBy(units)` (`:206-262`).
- `OrderResourceLoadCalculator` (`planner/entities/OrderResourceLoadCalculator.java:48-170`) builds `ContiguousDaysLine` series: `maxCapacityOnResources` (availability of resources used by the order), `orderLoad` (order day assignments), `allLoad` (all projects' day assignments on those resources), `orderOverload`, `allOverload` (load above capacity).
- Role (criterion) capacity: `AvailabilityCalculator.buildSumOfAvailabilitiesFor(criteria, resources)` unions resource availability intervals where each resource satisfies the criteria (`planner/entities/AvailabilityCalculator.java`, used at `GenericResourceAllocation.java:216-218`).
- TaskJuggler reporting: `getAllocatedTime`, `getEffectiveWork`, `getEffectiveFreeTime`, `getEffectiveFreeWork` over slot ranges (`ResourceScenario.rb:546-600`).
- MPXJ: `overAllocated = peakUnits > maxUnits` (`Resource.java:3317-3322`).

### Remaining early/late dates (MPXJ P6 scheduler)
`PrimaveraScheduler.setRemainingEarlyDates` (`mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java:3302-3343`): skip completed; not started → remaining early = CPM early dates; started → remaining early start = early start if actual duration > 0 or actual start after data date, else next work start after data date; remaining early finish = start + remaining duration. Remaining late = CPM late dates (`:3350-3361`). Assignment remaining dates follow the activity, cleared when complete (`:158-250`).

## State machines and workflows
- TaskJuggler task scheduling state: `not ready` → `ready` (`readyForScheduling?`) → `scheduling` (slot loop) → `scheduled` (`markAsScheduled`) or `runaway` (`markAsRunaway`, out of project interval) (`TaskScenario.rb:57, 911-975, 2252`). Container tasks are scheduled when all children are (`scheduleContainer`, `:1126`).
- Resource slot state (scoreboard): `off-duty/leave` (integer flags) → `free` (`nil`) → `booked` (Task); `bookBooking` for pre-recorded bookings can force onto off-duty slots only when `overtime` ≥ 1 (non-working) or ≥ 2 (leave), else error (`ResourceScenario.rb:221-261`).
- LibrePlan queue element: unassigned (no queue) → assigned to queue with start/end `QueuePosition` → moved/rescheduled when Gantt constraints change (`earlier_start_date_because_of_gantt`) (inferred from mapping fields).

## Cross-domain links
- Uses D05 calendars and shifts (scoreboard initialization, `Capacity` from calendars).
- Uses D06 CPM early/late dates and D04 relationships for readiness and the earliest-start of queue elements.
- Consumes D07 resources, roles (criteria), assignments and day assignments; writes assignment and activity remaining dates.
- D15 portfolio scenarios (resource plans) map to LibrePlan scenarios.
- Leveling priorities can reference D09 codes/UDFs (P6 `levelprioritylist`).

## Gaps
- P6-style post-CPM serial leveler: not in any source. Rebuild: after CPM, iterate time periods; candidate activities sorted by `levelingPriorities` (priority, early start, total float, code/UDF); for each, test resource demand (time-phased units) against `maxUnits × (1 + overAllocPct)` over its window on the resource calendar; delay to the next feasible window, bounded by total float minus `preserveMinimumFloat` if `levelWithinFloat`; treat other-project assignments with priority ≥ threshold as fixed load; write leveling delay and remaining early dates; log unresolved conflicts.
- Resource requests/booking workflow (D08.06): rebuild as request entity (role, skill, period, units, status Draft → Submitted → Approved/Booked | Rejected) linked to an assignment or demand line.
- Portfolio resource plans not tied to activities (D08.05): rebuild as (project, role/resource, period, units, scenario) demand table compared against capacity.
- Persisted leveling log (D08.07): TaskJuggler's in-memory competitor maps show what to persist (task, resource, contending task, slots lost).
