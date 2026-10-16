# D04 Relationships and Constraints

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D04.01 | Activity relationships | MPXJ (P6 `TASKPRED` model + `PrimaveraScheduler` link rules) | full | FS/SS/FF/SF, lag in hours, lag-calendar option, driving flag computed, per-link free float computed; critical flag per link not stored |
| D04.02 | External (inter-project) relationships | MPXJ `ExternalRelation` + EXTERNAL_EARLY_START / EXTERNAL_LATE_FINISH | partial | External links captured on read, optional cross-project linking; external dates always applied as constraints (option not consulted) |
| D04.03 | Primary and secondary constraints | MPXJ `PrimaveraScheduler` | full | All nine P6 types in forward/backward pass; secondary limited to SNLT/FNLT in backward pass (as implemented) |
| D04.04 | Project must-finish-by | MPXJ `PrimaveraScheduler` | full | Late finish of open ends = must-finish-by, else latest EF |
| D04.05 | Logic validation | MPXJ `DepthFirstGraphSort`, TaskJuggler `checkDependency`/`checkForLoops`, LibrePlan `doesNotProvokeLoop`, ERPNext `check_recursion` | partial | Loop detection and dangling/self/parent links; no open-end, OOS or constraint-conflict report |

## Storage model

### P6 relationship (XER `TASKPRED`, read at `mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java:594-645`)

| Column | Type | Notes |
|---|---|---|
| `task_pred_id` | int PK | generated if null (TPR:598-602) |
| `task_id` | int FK → TASK | successor |
| `pred_task_id` | int FK → TASK | predecessor; may belong to another project |
| `pred_type` | enum | `PR_FS`, `PR_FF`, `PR_SS`, `PR_SF` (`mpxj/src/main/java/org/mpxj/primavera/RelationTypeHelper.java`) |
| `lag_hr_cnt` | decimal hours | negative = lead |
| `comments` | text | → relation notes |

PMXML `RelationshipType` (`mpxj/src/main/java/org/mpxj/primavera/schema/RelationshipType.java`) adds read-only computed fields: `Driving`, `PredFreeFloat`, `PredTotalFloat`, `PredActIsLongestPath`, predecessor/successor project ids, activity ids/names/types, dates and WBS paths, `Aref`/`Arls`.

MPXJ in-memory `Relation` (`mpxj/src/main/java/org/mpxj/Relation.java:164-170`): `uniqueID`, `predecessorTask`, `successorTask`, `type` (`RelationType` FINISH_START/START_START/FINISH_FINISH/START_FINISH), `lag` (`Duration` with units), `notes`, mutable `driving` (output of scheduling). Multiple links between the same pair are allowed (free-float merge rule handles duplicates).

MPXJ `ExternalRelation` (`mpxj/src/main/java/org/mpxj/primavera/ExternalRelation.java:48-180`): `uniqueID`, `externalTaskUniqueID`, `targetTask` (the in-project end), `type`, `lag`, `predecessor` flag (true = the external task is the predecessor), `notes`. Created when one end of a `TASKPRED` row is missing from the project being read (TPR:625-641).

Activity external surrogate dates (`TASK.external_early_start_date`, `TASK.external_late_end_date` → EXTERNAL_EARLY_START, EXTERNAL_LATE_FINISH, TPR:1050-1051).

### P6 constraints (on `TASK`)

| Column | Values (XER code → MPXJ `ConstraintType`) |
|---|---|
| `cstr_type`, `cstr_date` | `CS_MSO` START_ON, `CS_MSOB` START_NO_LATER_THAN (Start On or Before), `CS_MSOA` START_NO_EARLIER_THAN (Start On or After), `CS_MEO` FINISH_ON, `CS_MEOB` FINISH_NO_LATER_THAN, `CS_MEOA` FINISH_NO_EARLIER_THAN, `CS_ALAP` AS_LATE_AS_POSSIBLE, `CS_MANDSTART` MUST_START_ON (Mandatory Start), `CS_MANDFIN` MUST_FINISH_ON (Mandatory Finish) (`mpxj/src/main/java/org/mpxj/primavera/ConstraintTypeHelper.java:112-135`) |
| `cstr_type2`, `cstr_date2` | secondary constraint, same codes (TPR:1036-1037) |

Null constraint type is treated as AS_SOON_AS_POSSIBLE (`PrimaveraScheduler.java:4280`).

Project: `PROJECT.plan_end_date` → `mustFinishBy` (TPR:116); `PROJECT.scd_end_date` → scheduledFinish (output).

### Relationship lag calendar option

`SCHEDOPTIONS.sched_calendar_on_relationship_lag` → `RelationshipLagCalendar` {`rcal_Predecessor`, `rcal_Successor`, `rcal_ProjDefault`, `rcal_24Hour`} (`mpxj/src/main/java/org/mpxj/primavera/RelationshipLagCalendarHelper.java`; TPR:863). MPXJ default PREDECESSOR (`mpxj/src/main/java/org/mpxj/ProjectProperties.java:3972`). Other link options stored but unused by the scheduler: `sched_outer_depend_type` (`SD_None` → ignore other-project relationships, TPR:850), `sched_lag_early_start_flag` (SS lag from early start, TPR:858).

### IFC (IfcOpenShell)

`IfcRelSequence` (`ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/assign_sequence.py`): GlobalId, OwnerHistory, RelatingProcess (predecessor), RelatedProcess (successor), SequenceType {START_START, START_FINISH, FINISH_START, FINISH_FINISH, USERDEFINED, NOTDEFINED}, TimeLag → `IfcLagTime` (`api/sequence/assign_lag_time.py`): LagValue (IfcDuration or IfcRatioMeasure), DurationType (WORKTIME / ELAPSEDTIME). Uniqueness: one relation per (predecessor, successor, sequence type); a second type between the same pair is allowed ("ladder" SS + FF) (assign_sequence.py). No constraint entity; a predecessor-less task with ScheduleStart is treated as fixed.

### LibrePlan

Table `dependency` (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/planner/entities/Tasks.hbm.xml`): `id`, `origin` FK → task_element (indexed), `destination` FK → task_element, `type` enum {END_START, START_START, END_END, START_END} (`libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/Dependency.java`), `queue_dependency` FK (limiting-resource queue). No lag column. `TaskElement` has sets `dependenciesWithThisOrigin` / `dependenciesWithThisDestination`.

Constraint (component on `task`): `constraint_type` {AS_SOON_AS_POSSIBLE, START_NOT_EARLIER_THAN, START_IN_FIXED_DATE, AS_LATE_AS_POSSIBLE, FINISH_NOT_LATER_THAN}, `constraint_date` (date) + `constraint_date_effort_duration` (intra-day offset) (`planner/entities/PositionConstraintType.java`, `TaskPositionConstraint.java`). `task_milestone` has its own `startConstraint` component. `task_element.deadline` (date) is informational.

### TaskJuggler

`TaskDependency` (`taskjuggler/lib/taskjuggler/TaskDependency.rb:20-46`): `taskId`, resolved `task`, `onEnd` (true = refer to the other task's end), `gapDuration` (seconds of calendar time), `gapLength` (number of working slots). Task attributes `depends` (constrains this task's start) and `precedes` (constrains this task's end), plus `minstart`, `maxstart`, `minend`, `maxend`, fixed `start`/`end`, scheduling direction (`asap` / `alap`; `depends` sets ASAP, `precedes` sets ALAP, last wins — `taskjuggler/lib/taskjuggler/TjpSyntaxRules.rb:6353-6358`).

### OpenProject

`relations` (`openproject/app/models/relation.rb`): `from_id` (successor for follows), `to_id` (predecessor), `relation_type` {relates, precedes, follows, blocks, blocked, duplicates, duplicated, includes, partof, requires, required} (canonicalised via `reverse_if_needed`), `lag` integer working days in [−2000, 2000], unique (to, from). Only `follows`/`precedes` affect scheduling (FS only).

### ERPNext

`Task Depends On` child table (`erpnext/erpnext/projects/doctype/task/task.py:35-47`): parent task, `task` (predecessor); denormalised `depends_on_tasks` comma list (task.py:306-311). FS only, no lag.

## Algorithms and logic

### Link semantics in the P6 engine

All four link types with lag, per-progress-state rules, lag calendar selection and negative-lag clamping to the data date are implemented in `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java` (forward FS 1005, SS 1240, FF 1485, SF 1716; backward SS 1953, FF 2255, SF 2492, FS 2722) and `PrimaveraDateCalculator.java:57-110`. The full rule tables are in D06 (A5, A7). Key relationship-level behaviours:
- Lag is added on the lag calendar (`getLagCalendar`, PrimaveraDateCalculator.java:83): predecessor, successor, project default or a synthetic 24-hour calendar.
- Negative lag result before the data date is clamped to the data date (PrimaveraDateCalculator.java:65-68).
- For progressed predecessors positive lag is partially consumed: remaining lag = lag − working time (lag calendar) from predecessor actual start (SS/SF) or actual finish (FS/FF) to the data date, or lag − predecessor actual duration for in-progress SS (PrimaveraScheduler.java:1093-1103, 1402-1423, 1797-1809).
- Driving flag: in the forward pass every predecessor link whose candidate ES (after next-work-start on the successor calendar) equals the maximum is marked driving; a constraint that overrides logic clears the set (PrimaveraScheduler.java:721-727, 392, 551-554).
- Link free float: FS variance(P.EF+L, S.ES); SS variance(P.ES+L′, S.ES); FF variance(P.EF+L, S.EF); SF variance(P.ES+L, S.EF), on the predecessor calendar in hours (`PrimaveraSlackCalculator.java:174-231`). It is computed per link but only the minimum is stored on the activity.
- FF and SF predecessors disable the expected-finish override (PrimaveraScheduler.java:582-585).

### Constraint semantics in the P6 engine

Forward pass (PrimaveraScheduler.java:325-457):

| Constraint | Effect on ES/EF | Overrides logic? |
|---|---|---|
| Start On or After (SNET) | ES = max(ES, date) (same-day counts as earlier) | no (raises only) |
| Finish On or After (FNET) | ES = max(ES, date − duration) | no |
| Start On | ES = max(ES, next work start of date) | no |
| Finish On | ES = max(ES, date − duration), EF = date (prev work finish) | no |
| Mandatory Start | ES = date | yes (can be earlier than predecessors) |
| Mandatory Finish | EF = date, ES = EF − duration | yes |
| SNLT, FNLT, ALAP | none | — |

With no predecessors, SNET also floors at the data date and FNET seeds EF.

Backward pass (PrimaveraScheduler.java:806-904):

| Constraint | Effect on LF/LS |
|---|---|
| Start On (unstarted) | LF = min(LF, date + duration), LS = date |
| Mandatory Start (unstarted) | LF = date + duration (overrides successors) |
| Mandatory Finish | LF = date (overrides successors) |
| Start On or Before | LF = min(LF, date + duration) |
| Finish On / Finish On or Before | LF = min(LF, date) |
| secondary SNLT / FNLT | same as primary |

Mandatory constraints therefore produce negative float when logic disagrees. ALAP: after late dates, ES/EF are re-placed as late as successors' early dates allow (PrimaveraScheduler.java:3158-3295), consuming free float; ALAP-driven links get the driving flag only if the successor is not an open-ended ALAP.

Free float is forced to 0 for Mandatory Finish, and for open-ended Mandatory Start/Finish (`PrimaveraSlackCalculator.java:66-70, 249-257`).

### Must-finish-by (PrimaveraScheduler.java:94-113, 770-786)

`backwardPassFinish = mustFinishBy ?? max(EF)`; activities without successors get LF = external late finish, else must-finish-by moved to the previous work finish when it falls in non-working time, else latest EF. Successor-derived LF later than the backward-pass finish is pulled back to it. `forwardPassFinish = max(maxEF, mustFinishBy)` is the reported project finish and the ALAP anchor.

### External relationships

- Reading: a `TASKPRED` row whose predecessor or successor is not in the project becomes an `ExternalRelation` (TableProjectReader.java:625-641).
- Optional linking: with `setLinkCrossProjectRelations(true)` the XER reader reads all projects and, for each external relation, finds the other task in any loaded project and adds a real `Relation` to the successor project (`mpxj/src/main/java/org/mpxj/primavera/PrimaveraXERFileReader.java:163-190`).
- Scheduling: `external_early_start_date` raises ES if later (PrimaveraScheduler.java:535-539) and `external_late_end_date` caps LF (PrimaveraScheduler.java:932-935) and seeds LF for open ends (772-790). The "ignore relationships to/from other projects" option is not consulted, so the surrogate dates are always active when present.

### IFC link and lag handling

`ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/cascade_schedule.py:148-251` and `recalculate_schedule.py:227-283`: lag in whole days from IfcDuration, or ratio × predecessor duration days (cascade only); DurationType WORKTIME uses the task calendar, ELAPSEDTIME counts calendar days; each lagged date is computed on both the successor's and predecessor's calendar and the later wins (a fixed policy instead of P6's option). FS adds a 1-day offset when the predecessor has non-zero duration because finishes are 17:00 and starts 09:00 of whole days.

### LibrePlan dependency enforcement

`libreplan/ganttzk/src/main/java/org/zkoss/ganttz/data/ConstraintCalculator.java:27-85`: a dependency yields a constraint on the destination point (START for END_START/START_START, END for END_END/START_END) of `≥ source date` (start or end of source per type); backward scheduling uses the inverse type and `≤`. No lag. Task position constraints are converted to start/end constraints (START_NOT_EARLIER_THAN, START_IN_FIXED_DATE on the start; FINISH_NOT_LATER_THAN on the end) and combined with dependency constraints in priority order set by `dependenciesConstraintsHavePriority` (`GanttDiagramGraph.java:1696-1710`). `TaskPositionConstraint.isValid` requires a date exactly when the type needs one (TaskPositionConstraint.java). After a manual move, the constraint type becomes START_NOT_EARLIER_THAN (forward mode) or FINISH_NOT_LATER_THAN (backward), except START_IN_FIXED_DATE which stays (PositionConstraintType.java).

### TaskJuggler gaps and limits

`earliestStart` (`taskjuggler/lib/taskjuggler/TaskScenario.rb:1173-1228`): for each `depends` entry, candidate = other task's start/end per `onEnd`; walk `gapLength` working slots on the project scoreboard; candidate = max(after-length, date + gapDuration); result = max over dependencies and any parent explicit start. `latestEnd` (1230-1282) mirrors with `precedes`, min, parent explicit end. `minstart/maxstart/minend/maxend` are checked after scheduling and produce warnings, not hard constraints (TaskScenario.rb `postScheduleCheck`, ~470-500).

### Logic validation

| Check | Source | Behaviour |
|---|---|---|
| Cycle | `mpxj/src/main/java/org/mpxj/cpm/DepthFirstGraphSort.java:89-117` | DFS temp/permanent marks; throws `CycleException`, no path |
| Cycle | `ifcopenshell/.../api/sequence/recalculate_schedule.py:69-92` | relaxation attempts > n² ⇒ `RecursionError` |
| Cycle with path | `ifcopenshell/.../api/sequence/cascade_schedule.py:126-134` | prints each task on the recursive path, raises |
| Cycle at both ends | `taskjuggler/lib/taskjuggler/TaskScenario.rb:628-794` | walks start/end points in and out of containers, forward then backward (`Project.rb:1103-1111`); `loop_detected` warning, each loop member listed, `loop_end` error |
| Cycle on insert | `libreplan/ganttzk/.../GanttDiagramGraph.java:1995-2016, 2197-2207` | `canAddDependency` = not forbidden and destination point cannot reach the source |
| Cycle on save | `erpnext/erpnext/projects/doctype/task/task.py:362-390` | recursive CTE in both directions; `CircularReferenceError` |
| Unknown / self / child / parent / duplicate link | `taskjuggler/lib/taskjuggler/TaskScenario.rb:2318-2364` | link removed + error `task_depend_unknown`, `task_depend_self`, `task_depend_child`, `task_depend_parent`, `task_depend_multi` |
| Dangling link | `mpxj/.../TableProjectReader.java:614-641` | link with missing end becomes external, not an error |
| Start/end dependency conflict | `TaskScenario.rb:1219-1224, 1273-1279` | `impossible_start_dep` / `impossible_end_dep` |
| Predecessor/successor violated after scheduling | `TaskScenario.rb` postScheduleCheck | `task_pred_before`, `task_succ_after` |
| Open ends | IfcOpenShell adds dummy start/finish edges (recalculate_schedule.py:170-178); LibrePlan begin/end nodes | silently tied, never reported |

## State machines and workflows

- P6 link evaluation state = (predecessor progress) × (successor progress) × sign(lag), see D06 A5/A7.
- LibrePlan constraint type transitions on explicit move: any → START_NOT_EARLIER_THAN (forward) / FINISH_NOT_LATER_THAN (backward); START_IN_FIXED_DATE is absorbing (`PositionConstraintType.newTypeAfterMoved`). `Task.convertOnStartInFixedDate` pins a task to its current start.
- LibrePlan task readiness driven by links (`planner/entities/Task.java:1172-1265`): BLOCKED if any END_START origin unfinished or START_START origin neither finished nor in progress (including parents' dependencies); READY_TO_START otherwise when no progress.
- OpenProject relation creation: `before_validation :reverse_if_needed` swaps from/to for reverse types so stored types are canonical (`relation.rb`).

## Cross-domain links

- D03: relationships connect activities; LibrePlan links can target task groups (fanned out to children in critical-path calc).
- D05: lag calendar choice uses activity calendars, project default calendar or a 24-hour calendar.
- D06: all link and constraint evaluation happens in the CPM passes; driving flags feed longest path.
- D10: actual dates and data date change link evaluation (remaining lag, out-of-sequence).
- D35: XER `TASKPRED`, PMXML `Relationship`, IFC `IfcRelSequence` import/export.

## Gaps

- Relationship-level stored outputs (link critical flag, link free float per relationship) are not persisted; rebuild needs a relationship result table.
- "Ignore relationships to/from other projects" semantics must be added: when off, use live external links; when on, apply stored external ES/LF.
- Out-of-sequence detection (successor started before predecessor finished on FS, etc.) is not reported anywhere.
- Constraint-conflict and open-end reporting (no predecessor / no successor lists) must be built.
- Secondary constraints in the forward pass (e.g., secondary SNET/FNET) are not applied by MPXJ.
- LibrePlan and ERPNext have no lag; OpenProject has FS only; IfcOpenShell has no date constraints beyond fixed starts.
