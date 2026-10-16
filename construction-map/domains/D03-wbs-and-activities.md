# D03 WBS and Activities

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D03.01 | Work Breakdown Structure | MPXJ (P6 `PROJWBS` + PMXML `WBSType`), LibrePlan `OrderElement` tree | full | Hierarchy, code path concatenation with separator, sequence, estimated weight, anticipated dates; date rollup in scheduler |
| D03.02 | WBS milestones | PMXML `WBSMilestoneType` (MPXJ schema) | partial | Entity (name, weight, completed, sequence) and `WBSMilestonePercentComplete` field; no computation code |
| D03.03 | Activity entity | MPXJ `Task` (P6 `TASK` column map) | full | All P6 types, duration types, % complete types, status, OD/RD/actual/at-completion, all date families, expected finish, suspend/resume, primary resource, priority; type rules in scheduler |
| D03.04 | Duration type equation | LibrePlan `CalculatedValue` + allocation; MPXJ `TaskType` enum | partial | P6 four duration types stored; no Units = Duration × Units/Time solver in MPXJ; LibrePlan fixes end date / hours / resources-per-day |
| D03.05 | Percent complete types | MPXJ readers + `PrimaveraScheduler` | full | Duration % and Units % formulas; Physical stored; recalculated on schedule |
| D03.06 | Activity steps | MPXJ `Step` (P6 `TASKPROC`), PMXML step templates | partial | Name, seq, weight, % complete, complete flag; project flag `step_complete_flag`; weighted physical % not computed |
| D03.07 | Notebooks and documents | MPXJ `TASKMEMO`/`MEMOTYPE` notes; PMXML `DocumentType`, `ProjectDocumentType` | partial | Notebook topics read; WP&D entities in schema only |
| D03.08 | Global change | PMXML `GlobalReplaceType` (schema only) | none | No evaluation engine in any source |
| D03.09 | Activity ID auto-numbering | P6 project fields (prefix/suffix/increment) via MPXJ; IfcOpenShell `add_task` identification; LibrePlan sequence codes | partial | Settings stored; generation exists only in IFC (parent.n) and LibrePlan (sequence codes); no renumber |
| D03.10 | Expected finish and suspend/resume | MPXJ `PrimaveraScheduler` | full | Expected finish overrides EF and recomputes RD; suspend/resume gap removed from actual duration |
| D03.11 | Feedback and comments | PMXML `ActivityType` fields (Feedback, IsNewFeedback, ReviewRequired, ReviewStatus, ReviewFinishDate) | partial | Fields only; no approval workflow implementation |

## Storage model

### P6 WBS (XER `PROJWBS`; MPXJ represents each WBS node as a summary `Task`)

| Column | MPXJ field | Notes (`mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java:987-1009`) |
|---|---|---|
| `wbs_id` | UNIQUE_ID | PK |
| `parent_wbs_id` | parent task | hierarchy built after all rows read (TableProjectReader.java:246-259) |
| `proj_id` | — | owning project |
| `wbs_short_name` | WBS | short code; full path optional |
| `wbs_name` | NAME | |
| `seq_num` | SEQUENCE_NUMBER | sibling order |
| `est_wt` | ESTIMATED_WEIGHT | estimation weight |
| `anticip_end_date` | DEADLINE | anticipated finish |
| `orig_cost` | ORIGINAL_BUDGET | |
| `indep_remain_total_cost`, `indep_remain_work_qty` | REMAINING_COST / REMAINING_WORK | WBS-level independent ETC |
| `tmpl_guid`, `guid` | METHODOLOGY_GUID, GUID | |
| `WBSMEMO` (`wbs_memo_id`, `wbs_id`, `memo_type_id`, `wbs_memo`) | notes | `mpxj/src/main/java/org/mpxj/primavera/XerProjectReader.java:138` |

PMXML `WBSType` (`mpxj/src/main/java/org/mpxj/primavera/schema/WBSType.java`) adds AnticipatedStartDate/FinishDate, Code, EarnedValueComputeType, EarnedValueETCComputeType, EarnedValueETCUserValue, EarnedValueUserPercent, EstimatedWeight, IntegratedType, IsWorkPackage, OBSObjectId (responsible OBS), ParentObjectId, SequenceNumber, Status, StatusReviewerObjectId, WBSCategoryObjectId, WBSMilestonePercentComplete and ~150 Summary* rollup fields (SummaryActualStartDate, SummaryPlannedValueByCost, SummaryTotalFloat, …).

PMXML `WBSMilestoneType`: ObjectId, WBSObjectId, ProjectObjectId, Name, Weight, IsCompleted, SequenceNumber (`schema/WBSMilestoneType.java`).

Project-level WBS setting: `PROJECT.name_sep_char` → `wbsCodeSeparator` (TableProjectReader.java:119).

### P6 activity (XER `TASK`, map at TableProjectReader.java:1011-1062 plus explicit reads 290-330)

| Column | MPXJ field / type | Values |
|---|---|---|
| `task_id` | UNIQUE_ID (int PK) | |
| `wbs_id` | parent WBS task | FK → PROJWBS |
| `task_code` | ACTIVITY_ID | user-visible id |
| `task_name` | NAME | |
| `task_type` | `ActivityType` | `TT_Task` TASK_DEPENDENT, `TT_Rsrc` RESOURCE_DEPENDENT, `TT_LOE` LEVEL_OF_EFFORT, `TT_Mile` START_MILESTONE, `TT_FinMile` FINISH_MILESTONE, `TT_WBS` WBS_SUMMARY (`ActivityTypeHelper.java:125-141`); MPXJ enum also HAMMOCK, START_FLAG (`mpxj/src/main/java/org/mpxj/ActivityType.java`) |
| `duration_type` | TYPE (`TaskType`) | `DT_FixedRate` FIXED_UNITS (Fixed Units/Time), `DT_FixedDrtn` FIXED_DURATION (Fixed Duration and Units/Time), `DT_FixedQty` FIXED_WORK (Fixed Units), `DT_FixedDUR2` FIXED_DURATION_AND_UNITS (`TaskTypeHelper.java`) |
| `complete_pct_type` | PERCENT_COMPLETE_TYPE | `CP_Phys`, `CP_Drtn`, `CP_Units` (MPXJ also SCOPE) (`PercentCompleteTypeHelper.java`) |
| `status_code` | ACTIVITY_STATUS | `TK_NotStart`, `TK_Active`, `TK_Complete` (`ActivityStatusHelper.java`) |
| `clndr_id` | calendar FK | |
| `target_drtn_hr_cnt` | PLANNED_DURATION (hours) | original duration |
| `remain_drtn_hr_cnt` | REMAINING_DURATION (hours) | |
| `act_work_qty`, `act_equip_qty`, `remain_work_qty`, `remain_equip_qty`, `target_work_qty`, `target_equip_qty` | ACTUAL/REMAINING/PLANNED_WORK_LABOR/NONLABOR | summed into ACTUAL/REMAINING/PLANNED_WORK; WORK = actual + remaining (TableProjectReader.java:292-295) |
| `phys_complete_pct` | PHYSICAL_PERCENT_COMPLETE | user-entered |
| `target_start_date`, `target_end_date` | PLANNED_START/FINISH | |
| `early_start_date`, `early_end_date`, `late_start_date`, `late_end_date` | EARLY_*/LATE_* | |
| `restart_date`, `reend_date`, `rem_late_start_date`, `rem_late_end_date` | REMAINING_EARLY_*/REMAINING_LATE_* | |
| `act_start_date`, `act_end_date` | ACTUAL_START/FINISH | |
| `expect_end_date` | EXPECTED_FINISH | |
| `suspend_date`, `resume_date` | SUSPEND_DATE, RESUME | |
| `cstr_type`, `cstr_date`, `cstr_type2`, `cstr_date2` | constraints | see D04 |
| `priority_type` | PRIORITY | |
| `rsrc_id` | PRIMARY_RESOURCE_UNIQUE_ID | primary resource FK |
| `total_float_hr_cnt`, `free_float_hr_cnt` | TOTAL_SLACK, FREE_SLACK | |
| `driving_path_flag`, `float_path`, `float_path_order` | LONGEST_PATH, FLOAT_PATH, FLOAT_PATH_ORDER | |
| `external_early_start_date`, `external_late_end_date` | EXTERNAL_* | |
| `est_wt` | ESTIMATED_WEIGHT | |
| `location_id`, `tmpl_guid`, `create_date`, `guid`, `auto_compute_act_flag` | misc | |

Activity codes (`TASKACTV`), UDFs (`UDFVALUE` with `TASK` subject) and notes are attached during read (TableProjectReader.java:316-324). `Task.milestone` is derived from `task_type` (TableProjectReader.java:299). Resource Dependent is the only type that honours resource calendars (`setIgnoreResourceCalendar(!"TT_Rsrc")`, 303-304).

PMXML `ActivityType` (`schema/ActivityType.java`) mirrors these and adds: AtCompletionDuration, ActualDuration, DurationPercentComplete, PerformancePercentComplete, SchedulePercentComplete, Feedback, IsNewFeedback, ReviewRequired, ReviewStatus, ReviewFinishDate, NotesToResources, LevelingPriority, Min/Max/MostLikelyDuration, IsStarred, OwnerIDArray, ActivityOwnerUserId, FinancialPeriodTmplId, CBSObjectId.

### Steps (XER `TASKPROC`, read at TableProjectReader.java:794-815)

`proc_id` (PK), `task_id` (FK), `proc_name`, `seq_num`, `proc_wt` (weight), `complete_pct`, `proc_descr` → MPXJ `Step` (task, uniqueID, name, percentComplete, sequenceNumber, weight, description) with `getComplete() ⇔ percentComplete == 100` (`mpxj/src/main/java/org/mpxj/Step.java:54-137`). Project flag `PROJECT.step_complete_flag` → `activityPercentCompleteBasedOnActivitySteps` (TableProjectReader.java:111). PMXML `ActivityStepType` adds IsCompleted, WeightPercent, step UDFs; templates: `ActivityStepTemplateType` (Name, SequenceNumber, StepCount) and `ActivityStepTemplateItemType` (template FK, Name, Description, SequenceNumber, Weight, UDF).

### Notebooks and documents

- `MEMOTYPE` (`memo_type_id`, topic name) and `TASKMEMO` (`task_memo_id`, `task_id`, `memo_type_id`, `task_memo` HTML) → structured notes per topic (`mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java:510-530`). PMXML `ActivityNoteType`: ActivityObjectId, NotebookTopicObjectId, Note, RawTextNote.
- PMXML `DocumentType` (WP&D): ObjectId, Title, ReferenceNumber, Version, Author, Description, Deliverable, DocumentCategoryObjectId, DocumentStatusCodeObjectId, DocumentType, PrivateLocation, PublicLocation, ResourceObjectId, RevisionDate, ParentObjectId, SequenceNumber, GUID, UDF. `ProjectDocumentType` (assignment): DocumentObjectId, ActivityObjectId or WBSObjectId, IsWorkProduct (work product vs reference), ProjectObjectId.

### Global change

PMXML `GlobalReplaceType`: GreplaceObjectId, GlobalReplaceName, SubjectAreaType, SearchCriteria, ReplaceFieldNameOne, GlobalReplaceData, AllProjects, ProjectIds, UserObjectId (`schema/GlobalReplaceType.java`).

### Activity ID numbering settings

`PROJECT.task_code_prefix` → activityIdPrefix, `task_code_base` → activityIdSuffix (starting number), `task_code_step` → activityIdIncrement, `task_code_prefix_flag` → increment based on selected activity (TableProjectReader.java:121-124).

### LibrePlan WBS and tasks

- Order/WBS tree: `OrderElement` (abstract; `OrderLineGroup` = node, `OrderLine` = leaf with `HoursGroup`s), fields `code` (unique per order, info component), name, `initDate`, `deadline`, labels, criterion requirements, `SchedulingState` (`libreplan/libreplan-business/src/main/java/org/libreplan/business/orders/entities/OrderElement.java:83-191`); `Order.lastOrderElementSequenceCode` drives generated codes (`Order.java:441-451`).
- Planning tree (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/planner/entities/Tasks.hbm.xml`): `task_element` (id, name, notes, start_date + start_day_duration, end_date + end_day_duration as `IntraDayDate`, deadline, advance_percentage, sum_of_assigned_effort, parent FK → task_group, base_calendar_id, updated_from_timesheets) with joined subclasses `task` (calculated_value, constraint_type/constraint_date, workable_days, allocation_direction, priority, resource allocations, subcontracted data, consolidation), `task_group` (ordered children `position_in_parent`, `planning_data` with progress_all_by_num_hours, progress_by_duration, progress_by_num_hours), `task_milestone` (start constraint). `TaskSource` links an `OrderElement` scheduling point to its `TaskElement`.

### IFC

`IfcTask` (Name, Description, Identification, PredefinedType, IsMilestone, Status, WorkMethod, Priority, TaskTime) nested under parent tasks via `IfcRelNests`, controlled by `IfcWorkSchedule` via `IfcRelAssignsToControl` (`ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/add_task.py`). `IfcTaskTime` (DurationType, ScheduleDuration/Start/Finish, Early*/Late*, FreeFloat, TotalFloat, IsCritical, StatusTime, ActualDuration/Start/Finish, RemainingTime, Completion); `IfcTaskTimeRecurring` variant (`api/sequence/add_task_time.py`).

### Other

- ERPNext `Task`: `is_group`, `parent_task` (nested set), `exp_start_date`, `exp_end_date`, `act_start_date`, `act_end_date`, `progress`, `task_weight`, `status` (Open/Working/Pending Review/Overdue/Template/Completed/Cancelled), `depends_on` (`erpnext/erpnext/projects/doctype/task/task.py`).
- TaskJuggler `Task` tree (container vs leaf), `milestone`, `effort`/`length`/`duration`, `complete`, `priority`, `responsible`, `note` (`taskjuggler/lib/taskjuggler/TaskScenario.rb`).

## Algorithms and logic

### WBS code path and hierarchy

- MPXJ builds the tree from `parent_wbs_id`, then, when `wbsIsFullPath`, sets each node's WBS = parent WBS + `name_sep_char` + own short name recursively; activity id of a WBS node = its WBS (TableProjectReader.java:246-265, 424-432). Activities get the parent's WBS path when `matchPrimaveraWBS` is on (TableProjectReader.java:309-312).
- IFC: `add_task(parent_task=…)` sets `Identification = parent.Identification + "." + n` where n = number of nested siblings after insertion (add_task.py, IFC4+ only).
- LibrePlan `SchedulingState.Type` per OrderElement: SCHEDULED (scheduling point), SCHEDULED_SUBELEMENT (below a scheduling point), PARTIALY_SCHEDULED_SUPERELEMENT, COMPLETELY_SCHEDULED_SUPERELEMENT, NO_SCHEDULED; detaching a SCHEDULED_SUBELEMENT makes it NO_SCHEDULED (`orders/entities/SchedulingState.java:19-115`). Synchronisation creates/removes `TaskSource`s and planning tasks accordingly (`OrderElement.java:293-490`).

### WBS rollup (MPXJ P6 scheduler, `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java:3398-3571`)

Recursive over WBS children: start/planned start/actual start = min; finish/planned finish = max; early/late/remaining dates exclude finished LOE children; actual finish set only when every child has one; planned duration = work(planned start, planned finish) on WBS calendar; actual duration = work(actual start, remaining early start); remaining duration = work(remaining early start, remaining early finish); duration % = (planned − remaining)/planned × 100 clamped to [0,100], percent-complete type set to Duration; critical = any child critical. TaskJuggler containers: start = min child start, end = max child end (`TaskScenario.rb:1126-1171`); completion = average of children (`TaskScenario.rb:2439-2449`). IfcOpenShell `derive_date` returns the earliest/latest of nested tasks' dates (`util/sequence.py:41-75`).

### Type-specific scheduling rules (PrimaveraScheduler.java)

- `isActivity` excludes WBS nodes, LOE and WBS Summary from the main network (3125-3128).
- Start milestone: EF = ES; finish milestone: ES aligned to a work-finish boundary, EF = ES on Finish On (459-475, 441-448). Milestones skip next-work-start adjustment of LS (937-944).
- Resource Dependent: dates from each time-based assignment on the resource calendar with work × 100 / units; latest finish wins (3000, 3027-3117, 4193-4208).
- LOE: separate pass spanning predecessor and successor link dates (3592-3939). WBS Summary: dates from the parent WBS and its unfinished descendant activities (4022-4047).
- Validation: activity type required; durations required except for Resource Dependent with assignments (262-296).

### Percent complete

- Duration % (MPXJ XER read, TableProjectReader.java:956-976; scheduler, PrimaveraScheduler.java:688-712): PD = 0 ⇒ 100 if RD = 0 and status complete (reader) / 100 if RD = 0 (scheduler), else 0; otherwise (PD − RD)/PD × 100 when RD < PD, else 0.
- Units % (TableProjectReader.java:929-948): (act_work + act_equip) / (act_work + act_equip + remain_work + remain_equip) × 100; 0 if no actuals.
- Physical %: `phys_complete_pct` as entered (TableProjectReader.java:919-922); the scheduler leaves Physical activities' durations and % untouched (PrimaveraScheduler.java:595-598).
- Scheduler recomputes actual, remaining and at-completion durations for in-progress non-Physical activities (PrimaveraScheduler.java:593-680).
- TaskJuggler `calcTaskCompletion` (TaskScenario.rb:2439-2475): leaf ended before `now` = 100, not started = 0, effort tasks = effective work done / effort, others = elapsed fraction (now − start)/(end − start).
- LibrePlan: `advancePercentage` (scale 4) on task_element, fed by the advance (progress) subsystem (D10).

### Duration type equation

- MPXJ stores P6 `duration_type` only; the P6 scheduler does not re-solve units/duration/rate (it schedules from durations or assignment work).
- LibrePlan (`planner/entities/Task.java:154, 334-345, 440-452, 590-640`): `CalculatedValue` ∈ {END_DATE, NUMBER_OF_HOURS, RESOURCES_PER_DAY} chooses which variable the allocation recomputes; END_DATE clears `workableDays`, otherwise `workableDays` is fixed and resizing the task updates it and re-runs allocation (`resizeTo` → `updateWorkableDays` → `doReassignment`). `calculateEndGivenWorkableDays(days)` / `calculateStartGivenWorkableDays` place a fixed number of workable days on the task calendar.
- IfcOpenShell (`api/sequence/calculate_task_duration.py`): duration days = ceil(work seconds / seconds per workday / ScheduleUsage) over assigned IfcConstructionResource, max across resources; `edit_task_time` recalculates resource usage when `Usage.ScheduleWork` is locked (Units held, rate recomputed) (`api/sequence/edit_task_time.py`).
- MPXJ `MicrosoftScheduler` treats FIXED_DURATION or no assignments as duration-driven, else work-driven (`mpxj/src/main/java/org/mpxj/cpm/MicrosoftScheduler.java:1264-1267`).

### Expected finish and suspend/resume (PrimaveraScheduler.java:559-571, 610-649)

Expected finish replaces EF and remaining early finish, and RD = work(remaining early start, EF), when option `sched_use_expect_end_flag` is on, the activity is not complete, not ALAP, expected finish ≥ ES and ≥ data date, no FF/SF predecessor, and working time exists between computed EF and expected finish. Free float is 0 for activities with an expected finish (`PrimaveraSlackCalculator.java:87`). Suspend/resume: actual duration ends at the suspend date while suspended; once resumed before the data date, work(suspend, resume) is subtracted from work(actual start, data date).

### IFC task time editing (`api/sequence/edit_task_time.py`)

Duration wins over finish when both are given; starts snapped to the next working day at 09:00, finishes at 17:00; ScheduleStart + ScheduleDuration ⇒ finish; start + finish ⇒ duration counted in working days (+1 inclusive); any date/duration change triggers `cascade_schedule` (D06).

### Identification and codes

- IFC hierarchical identification (above).
- LibrePlan: `Order.incrementLastOrderElementSequenceCode()` (Order.java:441-446) and `BaseCalendar.generateCalendarExceptionCodes` show the per-parent sequence pattern; codes unique per entity type.
- P6 prefix/suffix/increment are stored but no generator exists in MPXJ.

## State machines and workflows

- P6 activity status: Not Started (`TK_NotStart`, no actual start) → In Progress (`TK_Active`, actual start) → Completed (`TK_Complete`, actual finish). The scheduler branches on actual start/finish, not on the status code.
- LibrePlan task status (`planner/entities/Task.java:1172-1265`): FINISHED (advance = 1) → else IN_PROGRESS (0 < advance < 1 or work reports attached) → else READY_TO_START (all END_START origins finished and START_START origins started, including parents' dependencies) → else BLOCKED. Cached in `currentStatus` once FINISHED/IN_PROGRESS.
- TaskJuggler status (`TaskScenario.rb:2477-2498`): complete 0 → "not started" (milestone "not reached"), ≥ 100 → "done", else "in progress", unknown if completion not computable; gauge: on schedule / ahead / behind vs computed completion (2500-2532).
- ERPNext task status (`erpnext/erpnext/projects/doctype/task/task.py:183-203`): template tasks forced to Template; Overdue without overdue condition reverts to Working (if actual time) or Open; transition to Completed refused while any `depends_on` task is not Completed/Cancelled, then sets `completed_on` and closes assignments.
- P6 feedback/review: fields ReviewRequired, ReviewStatus, ReviewFinishDate, IsNewFeedback exist; transitions not implemented.

## Cross-domain links

- D04: relationships and constraints attach to activities; WBS-level links fanned out in LibrePlan.
- D05: activity and WBS calendars (`clndr_id`, `base_calendar_id`).
- D06: activity type and progress fields select CPM rules; scheduler writes dates, floats, durations, duration %.
- D07: primary resource, assignments, Resource Dependent type.
- D09: activity codes, UDFs, WBS categories.
- D10: actuals, remaining duration, expected finish, suspend/resume, baselines.
- D11: WBS EV technique, WBS milestones, estimated weight, Performance % Complete.
- D12/D25: WP&D documents and notebook topics.
- D17: WBS original budget, independent ETC; LibrePlan hours groups.

## Gaps

- WBS milestone % complete (Σ weight completed / Σ weight) not computed anywhere; needs the WBS milestone table plus rollup into WBS EV.
- Duration-type solver: for each of the four P6 types, recompute the free variable of Units = Duration × Units/Time when one changes (per assignment), and propagate to activity duration.
- Weighted step % (Σ weight × step % / Σ weight) when `step_complete_flag` is on; step templates applied to activities.
- Global change engine: condition evaluation per row, expression assignment, preview and commit/rollback.
- Activity ID generator and bulk renumber from prefix/suffix/increment.
- Feedback/status-update approval workflow (pending updates reviewed by PM before applying to actuals).
- WBS status (whatif/planned/active/inactive) and responsible OBS are schema fields only in the sources read.
