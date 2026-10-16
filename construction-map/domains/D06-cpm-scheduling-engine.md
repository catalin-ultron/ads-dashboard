# D06 CPM Scheduling Engine

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D06.01 | Forward pass | MPXJ `PrimaveraScheduler` (P6 clone) | full | Per-link, per-progress-state ES rules for FS/SS/FF/SF, lag calendar, data date, primary constraints, external early start, expected finish |
| D06.02 | Backward pass | MPXJ `PrimaveraScheduler` | full | Reverse topological order from must-finish-by or latest EF; primary and secondary late constraints; ALAP re-placement |
| D06.03 | Float calculation | MPXJ `PrimaveraSlackCalculator` | full | Start/finish/total float in working hours on activity calendar; TF type option (min, start, finish); per-link free float |
| D06.04 | Critical path definition | MPXJ `Task.calculateCritical` + `PrimaveraScheduler.calculateLongestPath` | partial | TF ≤ critical-float threshold and longest path via driving links; no multiple float paths |
| D06.05 | Retained logic vs progress override | MPXJ `PrimaveraScheduler` (retained-logic behaviour only) | partial | Option is read (`SchedulingProgressedActivities`) but the scheduler never branches on it; behaviour is retained logic |
| D06.06 | Schedule options | MPXJ `ProjectProperties` from XER `SCHEDOPTIONS` | partial | All P6 options are stored; scheduler uses status date, must-finish-by, expected finish, lag calendar, TF type, critical threshold |
| D06.07 | LOE and WBS Summary computation | MPXJ `PrimaveraScheduler.levelOfEffortPass` / `wbsSummaryPass` | full | LOE span from predecessor/successor links incl. actuals; WBS Summary from unfinished descendant activities |
| D06.08 | Schedule log and validation report | TaskJuggler `TaskScenario.postScheduleCheck`, MPXJ `CpmException` | partial | Error/warning codes per run; no structured P6-style log (open ends, OOS list, statistics) |
| D06.09 | Multi-project scheduling | MPXJ `PrimaveraXERFileReader.setLinkCrossProjectRelations` + external dates | partial | Cross-project links can be materialised on read; scheduler runs per `ProjectFile`; external ES/LF honoured |
| D06.10 | DCMA 14-point checks | none | none | No implementation in any source |
| D06.11 | What-if and scenarios | TaskJuggler scenarios; IfcOpenShell `create_baseline` | partial | Scenario-indexed attribute sets; IFC baseline copy with back-reference; no diff/merge |
| D06.12 | Fragnet and TIA | none (IfcOpenShell `duplicate_task` as copy primitive) | none | No fragnet entity or impacted-vs-unimpacted comparison |

## Storage model

### Source files

| Short name | Path (relative to `oss/`) |
|---|---|
| PS | `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java` |
| PDC | `mpxj/src/main/java/org/mpxj/cpm/PrimaveraDateCalculator.java` |
| PSC | `mpxj/src/main/java/org/mpxj/cpm/PrimaveraSlackCalculator.java` |
| DFS | `mpxj/src/main/java/org/mpxj/cpm/DepthFirstGraphSort.java` |
| DR | `mpxj/src/main/java/org/mpxj/cpm/DrivingRelation.java` |
| MS | `mpxj/src/main/java/org/mpxj/cpm/MicrosoftScheduler.java` (MS Project-style CPM, same structure) |
| TPR | `mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java` |
| XFR | `mpxj/src/main/java/org/mpxj/primavera/PrimaveraXERFileReader.java` |
| RS | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/recalculate_schedule.py` |
| CS | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/cascade_schedule.py` |
| US | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/util/sequence.py` |
| TJS | `taskjuggler/lib/taskjuggler/TaskScenario.rb` |
| TJP | `taskjuggler/lib/taskjuggler/Project.rb` |
| CPC | `libreplan/ganttzk/src/main/java/org/zkoss/ganttz/data/criticalpath/CriticalPathCalculator.java` (cloned for this domain) |
| GDG | `libreplan/ganttzk/src/main/java/org/zkoss/ganttz/data/GanttDiagramGraph.java` (cloned for this domain) |

### Engine inputs and outputs (P6 model, via MPXJ)

Activity scheduling fields read/written by PS (P6 `TASK` column → MPXJ field, map in TPR:1011-1062):

| P6 column | MPXJ field | Role in engine |
|---|---|---|
| `target_drtn_hr_cnt` | PLANNED_DURATION | denominator of duration % (PS:688) |
| `remain_drtn_hr_cnt` | REMAINING_DURATION | EF = ES + RD for started work |
| (derived act+remain) | DURATION (at completion) | used for unstarted ES/EF (`getDateFromStartAndDuration`, PS:3010) |
| `act_start_date`, `act_end_date` | ACTUAL_START/FINISH | progress state selector in every link rule |
| `early_start_date`, `early_end_date` | EARLY_START/FINISH | output |
| `late_start_date`, `late_end_date` | LATE_START/FINISH | output |
| `restart_date`, `reend_date` | REMAINING_EARLY_START/FINISH | output (PS:3302) |
| `rem_late_start_date`, `rem_late_end_date` | REMAINING_LATE_START/FINISH | output (PS:3350) |
| `target_start_date`, `target_end_date` | PLANNED_START/FINISH | overwritten for unstarted activities (PS:144) |
| `cstr_type`/`cstr_date`, `cstr_type2`/`cstr_date2` | CONSTRAINT_*, SECONDARY_CONSTRAINT_* | constraint rules |
| `expect_end_date` | EXPECTED_FINISH | expected-finish override |
| `suspend_date`, `resume_date` | SUSPEND_DATE, RESUME | actual-duration gap |
| `external_early_start_date`, `external_late_end_date` | EXTERNAL_EARLY_START/LATE_FINISH | external-link surrogate constraints |
| `total_float_hr_cnt`, `free_float_hr_cnt` | TOTAL_SLACK, FREE_SLACK | output (computed lazily by PSC) |
| `driving_path_flag` | LONGEST_PATH | output (PS:4056) |
| `float_path`, `float_path_order` | FLOAT_PATH, FLOAT_PATH_ORDER | stored only; never computed |
| `TASKPRED.pred_type`, `lag_hr_cnt` | Relation type, lag | link rules; `Relation.driving` is output |

Project-level inputs (TPR:102-127, 822-873; XER `PROJECT` / `SCHEDOPTIONS`):

| P6 column | MPXJ property | Used by engine |
|---|---|---|
| `last_recalc_date` | statusDate (data date) | yes (PS:64) |
| `plan_start_date` | plannedStart / scheduler `startDate` arg | yes (PS:68) |
| `plan_end_date` | mustFinishBy | yes (PS:94) |
| `scd_end_date` | scheduledFinish | output (PS:130); used by free float of open ends (PSC) |
| `critical_drtn_hr_cnt` | criticalSlackLimit | yes (Task critical) |
| `critical_path_type` (CT_TotFloat / CT_DrivPath) | criticalActivityType | stored; scheduler always computes both TF and longest path |
| `sched_float_type` (FT_Min / FT_SS / FT_FF) | totalSlackCalculationType | yes (PSC) |
| `sched_calendar_on_relationship_lag` (rcal_Predecessor / rcal_Successor / rcal_ProjDefault / rcal_24Hour) | relationshipLagCalendar | yes (PDC) |
| `sched_use_expect_end_flag` | useExpectedFinishDates | yes (PS:66) |
| `sched_retained_logic`, `sched_progress_override` | schedulingProgressedActivities (RETAINED_LOGIC / PROGRESS_OVERRIDE / ACTUAL_DATES) | not read by PS |
| `sched_outer_depend_type` (`SD_None` = ignore) | ignoreRelationshipsToAndFromOtherProjects | not read by PS |
| `sched_open_critical_flag` | makeOpenEndedActivitiesCritical | not read by PS |
| `sched_lag_early_start_flag` | computeStartToStartLagFromEarlyStart | not read by PS |
| `sched_use_project_end_date_for_float` | calculateFloatBasedOnFinishDateOfEachProject | not read |
| `enable_multiple_longest_path_calc`, `use_total_float_multiple_longest_paths`, `key_activity_for_multiple_longest_paths`, `limit_multiple_longest_path_calc`, `max_multiple_longest_path` | multiple-float-path properties | not read |
| `level_*` | leveling options | not read (see D08) |

PMXML `ScheduleOptionsType` element list (schema `mpxj/src/main/java/org/mpxj/primavera/schema/ScheduleOptionsType.java`): CalculateFloatBasedOnFinishDate, ComputeTotalFloatType, CriticalActivityFloatThreshold, CriticalActivityPathType, ExternalProjectPriorityLimit, IgnoreOtherProjectRelationships, IncludeExternalResAss, LevelAllResources, LevelWithinFloat, MakeOpenEndedActivitiesCritical, MaximumMultipleFloatPaths, MinFloatToPreserve, MultipleFloatPathsEnabled, MultipleFloatPathsEndingActivityObjectId, MultipleFloatPathsUseTotalFloat, OutOfSequenceScheduleType, OverAllocationPercentage, PreserveScheduledEarlyAndLateDates, PriorityList, RelationshipLagCalendar, StartToStartLagCalculationType, UseExpectedFinishDates.

Transient engine state (PS:4323-4329): `m_dataDate`, `m_projectStartDate`, `m_forwardPassFinishDate`, `m_backwardPassFinishDate`, `m_useExpectedFinish`, `m_dateCalculator`. `DrivingRelation` (DR) = (relation, startDate, finishDate) where either date may be null; it carries the candidate date a link imposes plus an "applied" counterpart date.

### IFC (IfcOpenShell)

`IfcTaskTime` attributes written by RS:180-200: EarlyStart, EarlyFinish, LateStart, LateFinish (IfcDateTime), FreeFloat, TotalFloat (IfcDuration), IsCritical (bool). Inputs: ScheduleStart, ScheduleDuration, DurationType (WORKTIME / ELAPSEDTIME). Links: `IfcRelSequence` (RelatingProcess = predecessor, RelatedProcess = successor, SequenceType, TimeLag → `IfcLagTime`). Network is built in memory as a `networkx.DiGraph` with dummy `start` and `finish` nodes (RS:104-178).

### LibrePlan critical path

In-memory only: `Node` (task, previousTasks, nextTasks, earliestStart/Finish, latestStart/Finish as integer day offsets from `initDate`, duration = days between start and end) (`libreplan/ganttzk/.../criticalpath/Node.java`). `InitialNode` / `LastNode` are dummy begin/end nodes.

### TaskJuggler

Per scenario per task (TJS:75-160): `@start`, `@end`, `@forward` (ASAP = true, ALAP = false), `@durationType` (`:effortTask`, `:lengthTask`, `:durationTask`, `:startEndTask`), `@doneEffort/@doneLength/@doneDuration`, `@currentSlotIdx`, `@startpreds/@startsuccs/@endpreds/@endsuccs` (pairs [task, onEnd]), `@criticalness`, `@pathcriticalness`, `@isRunAway`, `@scheduled`.

## Algorithms and logic

### A1. MPXJ P6 scheduler: top-level sequence (PS:61-131)

1. `m_dataDate = statusDate`; `m_projectStartDate = startDate`. Topologically sort activities with DFS (only `isActivity`: not WBS summary node, not LOE, not WBS Summary type; PS:3125).
2. Validate (PS:262): every activity needs an activity type; Resource Dependent activities with assignments need assignment work and remaining work; others need duration and remaining duration. Throws `CpmException`.
3. Clear all early/late/remaining dates, longest-path flag, CRITICAL/FREE_SLACK/TOTAL_SLACK, all `Relation.driving` flags, project start/finish (PS:3364).
4. If no data date, data date = start date; else if start date < data date, project start = data date (PS:80-90).
5. Forward pass in topological order.
6. `earlyFinish = max(EF)` over activities. `forwardPassFinish = max(earlyFinish, mustFinishBy)`; `backwardPassFinish = mustFinishBy ?? earlyFinish` (PS:94-113). The backward-pass anchor can be earlier than the forward finish, which yields negative float.
7. Backward pass in reverse topological order.
8. Set Start/Finish (actual if present else early) and, for unstarted activities, overwrite Planned Start/Finish with Start/Finish (PS:138-151). Resource-assignment remaining dates recomputed (PS:158-244).
9. LOE pass, WBS rollup, WBS Summary pass, longest path.
10. Project start = earliest start, project finish = forwardPassFinish, scheduled finish = earlyFinish (PS:128-130).

### A2. Topological sort and loop detection (DFS:46-125)

Depth-first visit over successor links from every included task with temporary/permanent marks; on revisit of a temporarily-marked task throws `CycleException` (no cycle path reported, no auto-break; TODO at DFS:96). Finished nodes are pushed on a deque so the deque order is a valid topological order (predecessors first).

### A3. Lag and date arithmetic (PDC)

- Lag calendar by project option (PDC:83-110): PREDECESSOR → predecessor effective calendar; SUCCESSOR → successor effective calendar; PROJECT_DEFAULT → project default calendar; TWENTY_FOUR_HOUR (default branch) → synthetic calendar with all 7 days working 00:00-24:00 (PDC:142-152). MPXJ default when absent: PREDECESSOR (`ProjectProperties.java:3972`).
- `addLag(rel, date, lag)` = `calendar.getDate(date, lag)` on lag calendar; if lag < 0 and result < data date, clamp to data date (PDC:57-70). Negative lag cannot pull work before the data date.
- `removeLag(rel, date, lag)` = `getDate(date, -lag)` with no clamp (PDC:72-81).
- `getDate` rounds to the nearest minute: seconds ≥ 30 round up for positive durations, > 30 for negative (PDC:112-128).
- Lag in hours = `lag.convertUnits(HOURS, projectProperties)` (project hours-per-day/week/month), used whenever lag is compared to actual durations.
- Activity duration arithmetic (PS:3010-3117): for Task Dependent or Resource Dependent with no time-based resources, use activity effective calendar with Duration (at completion) or Remaining Duration. For Resource Dependent with labor/nonlabor assignments (units > 0), each assignment is placed on its resource calendar with `work × 100 / units` (PS:4193-4208; units < 0.001 treated as 0, PS:4210); forward date = max over assignments, backward date = min.
- `getNextWorkStart(task, d)`: if complete return d, else calendar next work start (PS:4228). `getEquivalentNextWorkStart` moves forward only if zero working minutes lie in between (PS:4159); `getEquivalentPreviousWorkFinish` moves back to the previous work finish only if zero working hours lie in between (PS:4131). `isWorkingTime` treats range start/end as inclusive (PS:4293).

### A4. Forward pass per activity (PS:316-574)

Predecessors considered = links whose predecessor `isActivity` (LOE and WBS Summary predecessors are ignored).

**Unstarted (no actual start):**
- No predecessors: SNET → ES = max(constraint date, data date); FNET → EF = constraint date (shifted to equivalent next work start if not working time), ES = EF − Duration; otherwise ES = project start (PS:325-357).
- With predecessors: compute a `DrivingRelation` per link (A5). ES = max over links of `nextWorkStart(successor, candidate)`; every link that ties the maximum is kept as driving (PS:721-727). If ES < project start then ES = project start, else EF = the driving link's applied early finish (only FF/SF links supply one).
- Primary constraint (PS:372-457):
  - Start On or After: if ES < constraint, or on the same calendar day, ES = constraint date; when the constraint has time 00:00 and ES has a time, the ES time is grafted onto the constraint date if that stays on the same day as the next work start. Driving links cleared.
  - Finish On or After: earliest start = constraint − Duration; if ES < that, ES = that, EF recomputed, driving cleared.
  - Mandatory Start: ES = constraint date unconditionally (logic overridden; driving flags kept).
  - Start On: if ES < constraint, ES = next work start of constraint, driving cleared (forward pass only pushes later).
  - Mandatory Finish: EF = constraint, ES = EF − Duration, driving cleared.
  - Finish On: start-on = constraint − Duration; if later than ES, ES = start-on, EF = start-on (finish milestone) or equivalent previous work finish of constraint.
  - Start On or Before, Finish On or Before, ALAP: no forward effect. Secondary constraints are not applied in the forward pass.
- Alignment: finish milestones move to next work start only if not already at a work-finish boundary; all others ES = next work start; start milestone EF = ES (PS:459-475).

**In progress (actual start, no actual finish):**
- No predecessors: no actual duration → ES = next work start of data date, EF = ES + Duration; actual duration and remaining > 0 → EF = AS + Duration, ES = EF − RD; actual > 0 and remaining 0 → ES = EF = next work start of data date (PS:481-503).
- With predecessors: ES = next work start of the driving link date (floored at project start), EF = ES + RD (PS:506-513). Remaining work therefore waits for incomplete predecessors (retained-logic behaviour).

**Complete:** no predecessors → ES = EF = data date; with predecessors → ES from driving link (floored), EF = ES + RD (PS:517-532).

**Post-steps for all states:**
- External early start overrides if later (EF recomputed) (PS:535-539).
- EF default = actual finish or ES + Duration (PS:541-544).
- Remaining early dates (PS:3302-3343): unstarted → RES/REF = ES/EF; started with actual duration → RES = ES; else RES = ES or next work start of data date; REF = RES + RD. Complete activities keep nulls.
- Driving flags set on all tied driving links unless the activity is ALAP and not complete (PS:551-554).
- Expected finish (PS:559-571) applies when the option is on, expected finish is set, activity not complete, not ALAP, expected finish ≥ ES and ≥ data date, no FF/SF predecessor, and working time exists between EF and expected finish: EF = REF = expected finish and RD = work(RES, EF).
- Durations and duration % (PS:593-657) for non-Physical in-progress activities: actual duration = work(AS, end) where end = data date, or suspend date when suspended at data date and not yet resumed; when resumed before data date the suspend→resume work is subtracted. RD = work(RES, EF); at-completion = RD if actual = 0, actual if RD = 0, else work(AS, EF); duration % = (PD − RD)/PD × 100 (100 if PD = RD = 0; 0 if RD ≥ PD).

### A5. Forward link rules (candidate successor ES), all four types

Notation: P = predecessor, S = successor, L = lag, `+L` = addLag on lag calendar, `-Dur(S)` / `-RD(S)` = subtract S duration/remaining on S calendar, `remLag` = L − work_lagCal(P.AF or P.AS, data date) (0 consumed if the actual is after the data date) or L − P.actualDuration (hours).

FS (PS:1005-1232):

| P state | S state | L = 0 | L > 0 | L < 0 |
|---|---|---|---|---|
| not started | not started | P.EF | P.EF + L | P.EF + L (clamped ≥ data date) |
| not started | started / finished | P.EF + L | P.EF + L | P.EF + L |
| in progress | any | P.EF + L | P.EF + L | P.EF + L |
| finished | not started or in progress | P.EF | remLag > 0 ? P.EF + remLag : P.EF (remLag measured from P.AF to data date) | P.EF |
| finished | finished | P.EF | P.EF | P.EF |

SS (PS:1240-1477):

| P state | S state | Rule |
|---|---|---|
| not started | not started | L = 0: lagCalendar.nextWorkStart(P.ES); else P.ES + L |
| not started | started/finished | P.ES + L |
| finished | not started | P.AS + L; if result < data date (≤ for negative L) use P.ES |
| finished | in progress | L > 0: P.AS + L, falls back to P.ES if < data date; L ≤ 0: P.ES |
| finished | finished | P.ES |
| in progress | not started or in progress | L ≤ 0 or P.actualDuration = 0 (not-started S only): P.ES; P.actualDuration ≥ L: P.ES; else P.ES + (L − P.actualDuration) |
| in progress | finished | P.ES |

FF (PS:1485-1708) returns ES = target − RD(S) and, in some cases, an applied EF:

| P state | S state | Target finish |
|---|---|---|
| not started | not started | L = 0: P.EF (applied EF = P.EF moved to S next work start if non-working); L > 0: P.EF + L; L < 0: P.EF + L (also applied EF) |
| not started | started/finished | P.EF + L |
| finished | not started | L = 0: P.AF; L > 0: L > P.actualDuration ? P.AF + L : (P.EF + L) + L (double lag, as implemented); L < 0: (P.EF + L) + L |
| finished | in progress | P.AF + L |
| finished | finished | ES = P.EF directly |
| in progress | any | P.EF + L |

SF (PS:1716-1890):

| P state | S state | Rule |
|---|---|---|
| not started | not started | ES = (P.ES − Dur(S)) + L; with L ≠ 0 and ES > data date, applied EF = P.ES + L |
| not started | in progress | L ≤ 0: EF = S.AS + Dur(S), ES = EF − RD(S); L > 0: EF = P.ES + L, ES = EF − RD(S) |
| not started | finished | L = 0: P.ES; else P.ES + L |
| finished | not started | (P.ES − Dur(S)) + L |
| finished or in progress | in progress | remLag (from P.AS to data date) > 0: EF = P.ES + remLag, ES = EF − RD(S); else P.ES |
| finished | finished | L = 0: P.ES; else min(P.ES + L, data date) |
| in progress | not started | min((P.ES − Dur(S)) + L, data date) |
| in progress | finished | L = 0: P.ES; else equivalent next work start of data date |

### A6. Backward pass per activity (PS:762-954)

Successors considered = links whose successor `isActivity`.

**Not complete:**
- No successors: LF = external late finish if set; else must-finish-by (moved to previous work finish if non-working) or backward-pass finish (= latest EF) (PS:770-791).
- With successors: driving = link with minimum candidate LF (A7); LS = its applied late start (may be null), LF = its LF; if LF > backward-pass finish then LS = null and LF = previous work finish of backward-pass finish (PS:794-804).
- Primary constraint (PS:806-870): Start On (unstarted) → latest finish = constraint + Duration, LF = min (to previous work finish), LS = constraint when an applied LS exists; Mandatory Start (unstarted) → LF = constraint + Duration; Mandatory Finish → LF = constraint; Start On or Before → LF = min(LF, constraint + Duration); Finish On / Finish On or Before → if LF > constraint, LF = constraint and LS = null.
- Secondary constraint (PS:872-904): only Start On or Before and Finish On or Before, same arithmetic.
- Non start-milestones: LF = equivalent previous work finish (PS:907-910).

**Complete:** LF = must-finish-by / backward-pass finish (no successors) or driving link LF capped at the backward-pass finish (PS:912-930).

**Post-steps:** external late finish caps LF; LS = LF − RD (next work start for non-milestones with remaining duration) unless supplied; remaining late = late; ALAP adjustment (A8).

### A7. Backward link rules (candidate predecessor LF)

`-L` = removeLag (no data-date clamp).

- FS (PS:2722-2996): default LF(P) = S.LS − L. Unstarted P and S with L = 0: result moved to previous work finish if non-working. S finished: S.LS. P finished: L > 0 → remLag (from P.AF to data date) > 0 ? S.LS − remLag : S.LS; L ≤ 0 → S.LS. P finished, S in progress: L > 0 → S.actualDuration = 0 ? S.LS − L : S.LS. P in progress, S in progress: lag removed when S has no actual duration, otherwise S.LS (L > 0 removes the lag in both sub-cases).
- SS (PS:1953-2230): LS(P) = S.LS − L moved to P next work start, LF(P) = LS + RD(P). Unstarted P and S with L = 0: LS(P) = S.LS if working time on P calendar, else nearest of previous work finish / next work start (PS:4314). P finished: remLag (from P.AS to data date) when L > 0 for unstarted or finished S. P in progress: remLag = L − P.actualDuration when L > 0.
- FF (PS:2255-2490): LF(P) = S.LF − L; P finished → S.LF, with remLag (from P.AF) when L > 0 and S is not started or finished.
- SF (PS:2492-2720): LF(P) = (S.LF + Dur(P)) − L in most cases (start of P constrained by finish of S; S.LF used as P late start, then P duration added); P in progress & S not started: LF = S.LF + RD(P) (lag ignored); P in progress & S finished: remLag variant; P finished & S finished: S.LF.

All candidate LFs are filtered through `adjustLateFinish` (cap at backward-pass finish) in the completed-activity branch (PS:1936).

### A8. As Late As Possible (PS:3158-3295)

After an ALAP activity's late dates are set, ES/EF are recomputed from successors' early dates: no successors → EF = previous work finish of forward-pass finish, ES = EF − RD. Otherwise per successor link: SS → equivalent next work start of (S.ES − L); FS → (S.ES − RD(P)) − L (P finished: next work start of data date or data date); FF → (S.EF − L) − RD(P); SF → equivalent next work start of (S.EF − L). ES = minimum; EF = ES + RD; driving set on that link unless the successor is itself an open-ended ALAP. ALAP thus consumes free float but not total float.

### A9. Float (PSC)

- Start float = working-hours variance(ES, LS) on activity effective calendar; finish float = variance(EF, LF) (PSC:59-83).
- Total float (PSC:115-193): complete → 0. Option START_SLACK → start float; FINISH_SLACK → finish float; SMALLEST_SLACK (MPXJ default, `ProjectProperties.java:3971`) → finish float for in-progress activities, otherwise min(start, finish). Negative values are kept.
- Free float (PSC:85-113): 0 for activities with expected finish, complete, LOE, WBS nodes, Mandatory Finish. Per successor (LOE successors excluded) the link free float on the predecessor calendar (PSC:211-295), using P remaining early dates when P has started:
  - FS: variance(P.EF + L, S.ES); SS: variance(P.ES + L', S.ES) where L' = max(0, L − P.actualDuration); FF: variance(P.EF + L, S.EF); SF: variance(P.ES + L, S.EF).
  - Duplicate links to the same successor merge: both ≥ 0 → min, else max (PSC:195-209).
  - FF = min over successors; with no successors: Mandatory Start/Finish → 0, else variance(EF, project scheduled finish). Negative → 0. Rounded to whole minutes.
- Critical (`mpxj/src/main/java/org/mpxj/Task.java:6814-6831`): false if actual finish or TF null; TF converted to the threshold's units; critical when TF ≤ `criticalSlackLimit` and % complete ≠ 100 and auto-scheduled.
- Longest path (PS:4056-4087): activities whose EF = max EF seed a recursive walk over predecessors through `driving` links; WBS Summary activities with EF = max EF also flagged. P6 `driving_path_flag` is the stored result.

### A10. Level of Effort pass (PS:3573-3939)

LOE activities are topologically sorted among themselves and scheduled after the main passes. Complete LOE keep actual dates. Otherwise:
- Early start candidates (minimum wins; ties all driving): predecessor SS → P.ES + L (or P.AS + L, next-work-start adjusted while P open); predecessor FS → P.EF + L (or P.AF + L); successor SS → S.ES − L (or S.AS − L); successor SF → S.EF − L (or S.AF − L).
- Early finish = later of the predecessor-derived finish (SF: P.ES + L; FF: P.EF + L or actuals) and successor-derived finish (FS: S.ES − L; FF: S.EF − L), each snapped back to a work finish when no work lies between (`adjustFinish`, PS:3982).
- Late start = earliest of the corresponding late-date candidates; late finish = later of successor/predecessor late candidates; with no finish candidates LF = forward-pass finish.
- No links: ES = next work start of data date, EF = ES.
- ES before data date: actual-derived ES becomes data date; otherwise ES = next work start of data date and the original start becomes the actual start. EF < data date → data date; EF < ES → ES; LS > LF → LF.
- Actuals are inferred when start/finish ≤ data date and derived from actuals. Duration = work(Start, Finish); unstarted LOE planned dates = dates; remaining dates and duration % recomputed; links contributing ES/EF marked driving.

### A11. WBS rollup and WBS Summary (PS:3398-3571, 4022-4047)

WBS node: Start/Planned/Actual start = min of children; finishes = max; early/late/remaining dates exclude completed LOE children; actual finish only when all children finished; planned duration = work(planned start, planned finish); actual/remaining duration from remaining early dates; duration % = (PD − RD)/PD clamped to [0,100] and percent-complete type forced to Duration; critical = OR of children. WBS Summary activity: Start/Finish/actuals copied from parent WBS; early/late/remaining dates = min/max over all unfinished non-summary descendant activities.

### A12. Resource assignment dates (PS:158-244)

Complete activity → assignment remaining dates null. Complete assignment → zero-length at activity remaining dates. Otherwise start = activity RES (plus assignment remaining lag `relag_drtn_hr_cnt` when both lag values ≠ 0), finish = start + remaining work at remaining units on the governing calendar (resource calendar for Resource Dependent, else assignment effective calendar); zero at-completion work with planned work falls back to planned duration; LOE assignments take activity dates.

### A13. IfcOpenShell CPM (RS)

1. Graph (RS:104-178): one node per leaf IfcTask controlled by the work schedule (summary tasks are expanded to their nested children); node duration = whole days of ScheduleDuration; calendar = assigned IfcWorkCalendar or nearest ancestor's (`derive_calendar`, US:78). Edges from IfcRelSequence with lag in whole days (`TimeLag.LagValue`) and type FS/SS/FF/SF (null, USERDEFINED, NOTDEFINED → FS). Tasks with no predecessor get `start → task` FS and, if they have ScheduleStart, a fixed early start ("we assume this task is constrained"). Tasks with no successor get `task → finish` FF.
2. Forward pass (RS:207-328) is iterative relaxation: nodes whose predecessors are all resolved get dates; repeated until none pending. Loop detection: if attempts exceed (pending nodes)² the graph is declared cyclic and `RecursionError` raised (RS:69-92).
   - FS: start = offset(P.EF, (P.duration > 0 ? 1 : 0) + lag) at 09:00, computed once on S calendar and once on P calendar (both kept, max wins).
   - SS: P.ES + lag (both calendars). FF: P.EF + lag. SF: offset(P.ES, lag − 1) at 17:00.
   - Both start and finish candidates: ES = max(starts), EF = max(finishes); if ES + duration > EF then EF = ES + duration, else ES = EF − duration.
3. Backward pass (RS:330-496): `finish.LF = finish.EF`. FS: LF = offset(S.LS, −(1 + lag)) at 17:00; SS: LS = S.LS − lag; FF: LF = S.LF − lag; SF: LS = offset(S.LF, −((S.duration = 0 ? 0 : −1) + lag)) at 09:00; reconcile with duration as in the forward pass using min.
4. Float: WORKTIME → TF = `count_working_days(EF, LF)` (inclusive day count, 0 when equal; US:96-108); ELAPSEDTIME → LF − EF, with an "8 hours ⇒ +1 day" correction. Free float per successor link (FS: from day after P.EF to S.ES; SS: P.ES→S.ES; FF: P.EF→S.EF; SF: P.ES→S.EF) less lag on either calendar (min), FF = min. IsCritical = TF.days == 0.
5. Date helpers (US:111-153): `offset_date` steps day by day decrementing only on working days (WORKTIME) or every day (ELAPSEDTIME or no applicable calendar), then snaps to the soonest/most recent working day; `get_start_or_finish_date` subtracts 1 from duration because the start day counts, and stamps 09:00 starts / 17:00 finishes. Months = 30 days, years = 360 days.
6. Cascade (CS:113-324) is a forward-only push used on edit: DFS from one task through `IsPredecessorTo` and nested tasks with the same link formulas; ratio lags (`IfcRatioMeasure`) become predecessor duration × ratio; stops recursing when a task's date is unchanged; cycles raise `RecursionError` with the printed path.

### A14. LibrePlan critical path (CPC)

1. `initDate` = min task start (day-rounded); dummy begin node has the initial tasks (no visible incoming links), dummy end node has the latest tasks; containers are replaced by their leaf children and container links are fanned out to all children with the link type (default END_START) (CPC:65-215).
2. Forward (CPC:244-290) recursive from begin node, visiting a successor only after all its predecessors have visited it: START_START → ES ≥ P.ES; END_END → ES ≥ P.EF − duration(S); END_START (and START_END, which falls through to default) → ES ≥ P.EF. `Node.setEarliestStart` keeps the max and sets EF = ES + duration.
3. Optional task constraints (when `dependenciesConstraintsHavePriority` is false): candidate date converted to a GanttDate and passed through the coalesced start/end constraints of the task (CPC:292-327).
4. Backward (CPC:329-385) symmetric: START_START → LF(P) ≤ S.LS + duration(P); END_END → LF(P) ≤ S.LF; END_START → LF(P) ≤ S.LS; `setLatestFinish` keeps the min.
5. Critical = nodes where LS == ES (CPC:401-409). No lag, no float values, integer days only.

### A15. LibrePlan live dependency enforcement (GDG)

Graph-wide incremental rescheduling on each move: tasks are vertices, dependencies edges; topological sort of TaskPoints (task × START/END) (GDG:428-540). Forward scheduling: START is the dominating point; new start = coalesce(dependency constraints `≥ source date` from `ConstraintCalculator`, task position constraints, global constraints) and END follows from END_END/START_END dependency constraints (GDG:1527-1817). Backward scheduling (project scheduled from deadline) inverts: END dominates, constraints are `≤` and dependency types inverted (`DependencyType.inverse`) (GDG:1818-1855). `dependenciesConstraintsHavePriority` controls whether dependency constraints are applied after (override) or before task constraints (GDG:1696-1710). Loops are refused when a dependency is added: `doesNotProvokeLoop` checks reachability from the destination TaskPoint (GDG:2197-2207); END_END into a container and START_START out of a container are forbidden (GDG:1999-2015).

### A16. TaskJuggler heuristic scheduler (TJP:1170-1265, TJS:911-1283)

Not a CPM pass: a list scheduler with resource booking.
1. Prepare (TJP:1065-1140): build start/end pred/succ lists (`Xref`, TJS:166-180), propagate fixed dates (TJS:188-207), loop checks in both directions, criticalness = effort × mean resource criticalness (milestones: priority/500) (TJS:825-850), path criticalness = max over successor paths + own criticalness (TJS:859-909).
2. Leaf tasks sorted by (priority desc, pathcriticalness desc, seqno asc). Loop: pick the first task that is `readyForScheduling?` (ASAP: start and (duration spec or end); ALAP: end and (duration spec or start)), schedule it fully, restart from the top. No ready task → `deadlock` warning.
3. `schedule` walks time slots from start (ASAP) or end−1 (ALAP), booking resources per slot (`scheduleSlot`, TJS:1753-1822); effort tasks finish when booked effort ≥ effort, length tasks count only global working slots, duration tasks count every slot; leaving the project window marks the task runaway.
4. On completion `propagateDate` sets the end (or start) and pushes it to dependents; a dependent end/start is set only once all its dependencies are known: `earliestStart` = max(dep date + gapLength working slots, dep date + gapDuration calendar seconds) and parent explicit start; `latestEnd` symmetric with min (TJS:1173-1282). Containers take min start / max end of children (TJS:1126-1171).
5. Projection mode: with bookings and `now` inside the task, scheduling resumes at `now` (TJS:945-951).

### A17. Other engines

- OpenProject (`openproject/app/services/work_packages/set_schedule_service.rb`): only FS "follows" with lag in working days; successor start = soonest working day of max(predecessor due date + lag) (`schedule_dependency/dependency.rb`, `relation.rb:178`); due date from duration in working days; parents span children; work packages with no predecessors/children switch to manual scheduling. Order by dependency-closure insertion sort (`schedule_dependency/dependency_graph.rb`).
- ERPNext (`erpnext/erpnext/projects/doctype/task/task.py:392-422`): on task save, each open dependent task whose expected start < this task's end is moved to end + 1 day keeping its calendar-day duration. No backward pass or float.
- MPXJ `MicrosoftScheduler` (MS): same forward/backward architecture with MS Project semantics (leveling delay, summary task relationships), not P6.

## State machines and workflows

- P6 activity progress state per link rule is a 3×3 matrix of (not started / in progress / finished) for predecessor × successor, selected by actual start/finish (PS:1011-1229 etc.). `isComplete` additionally treats non-milestones with RD = 0 as complete in SS backward rules (PS:2238).
- Driving flag lifecycle: cleared at run start (PS:3386), set in forward pass on tied driving links (PS:553), set by ALAP and LOE passes; consumed by longest path.
- IFC run: build → forward relaxation loop → (cyclic → RecursionError) → backward relaxation loop → write task times.
- TaskJuggler task: unscheduled → (ready) → scheduling slots → scheduled | runaway; container scheduled when all children scheduled (TJS:1126).
- LibrePlan project scheduling mode: FORWARD or BACKWARD (`GanttDiagramGraph.create(scheduleBackwards, ...)`, GDG:264); moving a task converts its constraint to START_NOT_EARLIER_THAN (forward) or FINISH_NOT_LATER_THAN (backward) (`libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/PositionConstraintType.java`).

## Cross-domain links

- D03: activity type, duration, % complete type, WBS hierarchy drive engine branches and rollup.
- D04: relationships (type, lag), constraints, must-finish-by, external dates are the engine's logic inputs; cycle detection lives in the engine sort.
- D05: every date addition goes through `ProjectCalendar.getDate/getNextWorkStart/getPreviousWorkFinish/getWork`; lag calendar option selects among D05 calendars.
- D07: resource assignments, units, resource calendars for Resource Dependent activities; assignment remaining dates.
- D08: leveling options stored in the same SCHEDOPTIONS row; TaskJuggler couples scheduling and booking.
- D10: data date, actual dates, remaining duration, expected finish, suspend/resume, baselines (scenarios).
- D11: duration % complete feeds EV.

## Gaps

- Progress override and Actual Dates modes (D06.05): option stored but no branch; a rebuild needs, for in-progress successors, ES = data date ignoring incomplete predecessors (progress override) and, for Actual Dates, schedule remaining work from actual dates of predecessors.
- Ignore external relationships / make open-ended critical / SS lag from early vs actual start options (D06.06) not honoured.
- Multiple float paths (D06.04): no implementation; needs iterative driving-path extraction from an end activity ranked by TF or relationship free float, writing `float_path`/`float_path_order`.
- Schedule log (D06.08): needs a structured report (open ends, constraints applied, OOS activities, loops with paths, counts).
- Multi-project network (D06.09): merge multiple `ProjectFile`s into one graph before scheduling; MPXJ only links the relations on read.
- DCMA 14-point (D06.10): all metrics (logic, leads, lags, FS%, hard constraints, high float > 44 d, negative float, high duration > 44 d, invalid dates, resources, missed tasks, CP test, CPLI = (CP length + TF)/CP length, BEI) must be built from scratch on top of engine output.
- Scenarios (D06.11) diff/merge and fragnet/TIA (D06.12): need project copy-on-write, impacted schedule run, finish-date delta comparison.
- Circular-logic handling: all sources abort; none breaks the loop or reports the full cycle except IfcOpenShell cascade (path printed) and TaskJuggler (path listed as info).
