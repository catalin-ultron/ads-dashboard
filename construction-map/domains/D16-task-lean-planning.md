# D16 Task and Lean Planning (Last Planner)

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D16.01 | Work plan tasks under activities | ERPNext `Task` (parent task tree, dates bounded by parent, progress → project %); Odoo `project.task`; OpenProject work packages | partial | Task entity, statuses, date-bound validation and completion feed exist; no company/trade, crew size, location, committed state |
| D16.02 | Look-ahead planning | OpenProject `Sprint` (dated window) + backlog buckets | partial | Fixed time-boxes with backlog; no rolling N-week window or make-ready flow |
| D16.03 | Constraints register | Odoo task dependencies → `04_waiting_normal`; OpenProject relations `blocks`/`blocked`, `requires`; ERPNext `depends_on` completion guard | partial | "Ready only when blockers closed" exists for task-to-task blockers; no typed constraint entity (RFI, material, permit), need date, or aging |
| D16.04 | Weekly commitments | OpenProject sprint start/finish (lock scope, carry-over) | partial | Sprint start locks a time-box and creates a task board; no per-task committer/commit date |
| D16.05 | Percent Plan Complete | OpenProject `Burndown` (remaining story points per working day from journals) | partial | Journal time-line replay gives as-of-day state needed for PPC; PPC formula itself absent |
| D16.06 | Reasons for non-completion | none | none | Finish service offers carry-over actions but records no reason code |
| D16.07 | Pull planning / phase planning | TaskJuggler ALAP (`forward=false`) backward scheduling; Odoo `project.milestone` + task dependencies; ERPNext template-to-project task conversion | partial | Backward-from-end scheduling, milestones and dependency-preserving task instantiation exist separately; no trade handoff or sticky-note model |
| D16.08 | Takt planning | none | none | No zone, takt time or wagon/train entity in any source (grep "takt" hits only an MPXJ locale file) |
| D16.09 | Task notifications | OpenProject date alerts (`notification_settings.start_date/due_date/overdue`, reasons `date_alert_*`), daily digest; ERPNext daily overdue job | partial | Due-date and overdue alerts with immediate/daily delivery; no proposed-due-date trigger, no weekly frequency |

## Storage model

### ERPNext Task (`erpnext/erpnext/projects/doctype/task/task.json`)
`subject*`, `project` → Project, `issue` → Issue, `type` → Task Type, `is_group`, `parent_task` → Task (nested set `lft`/`rgt`/`old_parent`), `status` {Open, Working, Pending Review, Overdue, Template, Completed, Cancelled}, `priority` {Low, Medium, High, Urgent}, `exp_start_date`, `exp_end_date` (Datetime), `expected_time`, `task_weight`, `progress` (Percent), `is_milestone`, `depends_on` (child table `Task Depends On`: `task`, `subject`, `project`), `depends_on_tasks` (code, ro), `act_start_date`, `act_end_date`, `actual_time`, `total_costing_amount`, `total_billing_amount`, `review_date`, `closing_date`, `completed_on`, `completed_by`, `department`, `company`, template fields `is_template`, `start`, `duration`, `template_task`. Naming `TASK-.YYYY.-.#####`.

### Odoo task (`odoo/addons/project/models/project_task.py`)
`priority` (`:156`), `stage_id` → `project.task.type` (`:163`), `state` {01_in_progress, 02_changes_requested, 03_approved, 1_done, 1_canceled, 04_waiting_normal} computed + stored (`:85-88,169-176`), `is_closed` (`:177`), `date_deadline` (`:184`), `date_end`, `date_assign`, `date_last_stage_update`, `allocated_hours` (`:197`), `user_ids` M2M (`:206`), `parent_id`/`child_ids` (`:249-250`), `milestone_id` (`:261`), `depend_on_ids` / `dependent_ids` M2M via `task_dependencies_rel` (`:280-285`). Stage `project.task.type`: `name`, `sequence`, `fold`, `project_ids`, `rotting_threshold_days` (stale after N days; 0 disables), `auto_validation_state`, `user_id` (`odoo/addons/project/models/project_task_type.py:23-51`). Milestone `project.milestone`: `name`, `project_id`, `deadline`, `is_reached`, `reached_date`, `task_ids` (`odoo/addons/project/models/project_milestone.py:21-35`).

### OpenProject backlogs (`openproject/modules/backlogs/`)

| Table | Columns | Constraints |
|---|---|---|
| `sprints` | `name` (not null), `status` {in_planning, active, completed} default in_planning, `start_date`, `finish_date` (made nullable later), `project_id`, `started_at`, `completed_at`, timestamps | check `finish_date >= start_date`; partial unique index `project_id WHERE status='active'` (added then removed for multi-active setting) (`db/migrate/20260202093215_create_sprints.rb`, `20260313170000_add_uniqueness_for_active_sprints.rb`, `20260824132100_...`) |
| `sprint_goals` | `sprint_id` (cascade), `project_id` (cascade), `text` | unique (sprint_id, project_id) (`20260519144514_create_sprint_goals.rb`) |
| `backlog_buckets` | `name`, `project_id` (cascade) | (`20260415182824_create_backlog_buckets.rb`) |
| `work_packages` additions | `sprint_id`, `backlog_bucket_id`, `position`, `story_points` | check `backlog_bucket_id IS NULL OR sprint_id IS NULL` (`20260416213200_...`) |
| `done_statuses_for_project` | `project_id`, `status_id` | per-project "done" definition (`db/migrate/tables/done_statuses_for_project.rb`) |
| project `settings.sprint_sharing` | {no_sharing, share_all_projects, share_subprojects, receive_shared} | `app/models/projects/sprint_settings.rb:33-38` |

### Task notification settings (OpenProject)
`notification_settings` integer columns `start_date` (default 1), `due_date` (default 1), `overdue` (default nil) = days before start/due or overdue repeat interval, per user globally or per project (`openproject/db/migrate/tables/notification_settings.rb`); allowed values start/due ∈ {nil, 0, 1, 3, 7}, overdue ∈ {nil, 1, 3, 7} (`openproject/app/contracts/user_preferences/params_contract.rb:32-33,56-67`). Generated notifications use reasons `date_alert_start_date` (10) and `date_alert_due_date` (11) (`openproject/app/models/notification.rb:31-48,66`). Digest timing from `user_preferences.settings.daily_reminders` {enabled, times} (default enabled at 08:00 UTC), `workdays`, `pause_reminders`, `time_zone` (`openproject/app/models/user_preference.rb:172-234`).

### Pull-planning primitives
- TaskJuggler task scenario attribute `forward` (ASAP when true, ALAP when false); ALAP tasks need an end or successor and are placed backward from it (`taskjuggler/lib/taskjuggler/TaskScenario.rb:346-347,374-399`).
- ERPNext `Project Template` → `Project Template Task` rows referencing template `Task`s with `start` (day offset), `duration`, `depends_on`, `parent_task` (`erpnext/erpnext/projects/doctype/project_template*`, `task.json`).
- Odoo `project.milestone` (`deadline`, `is_reached`, `task_ids`) as pull targets (`odoo/addons/project/models/project_milestone.py:21-35`).

OpenProject relations: `relates`, `precedes`/`follows`, `blocks`/`blocked`, `duplicates`/`duplicated`, `includes`/`partof`, `requires`/`required`, `parent`/`child` (`openproject/app/models/relation.rb:34-49`).

## Algorithms and logic

### Task bounds and completion (ERPNext `task.py`)
- Child `exp_end_date` must be ≤ parent task `exp_end_date` (`erpnext/erpnext/projects/doctype/task/task.py:115-130`); task dates checked against project dates (`:132-166`).
- Completing requires every `depends_on` task to be Completed or Cancelled, sets `completed_on = today` if empty, closes all assignments (`:183-203`). Progress forced to 100 on Completed; 0..100 validated (`:205-210`). Reopen from Completed clears `completed_on`/`completed_by` and resets progress to 0 unless progress was edited (`:212-219`).
- `is_overdue` = `exp_end_date < today` (`:482-484`); daily `set_tasks_as_overdue` sets Overdue for non-closed tasks, skipping Pending Review whose `review_date` is in the future (`:486-489,532-543`). Leaving Overdue when not overdue reverts to Working if `actual_time` else Open (`:189-190`).
- `reschedule_dependent_tasks`: when a task's end moves, each dependent task in the same project (excluding its parent) that is Open/Working/Overdue and starts before the new end is shifted to start end + 1 day keeping its day duration (`:392-422`).
- Task completion feeds project %: Task Completion = (Completed + Cancelled)/total × 100; Task Progress = mean progress with closed tasks = 100; Task Weight = weighted mean by `task_weight`; status auto-set Completed at 100 else Open unless Cancelled/On hold; manual Completed refused below 100% (`erpnext/erpnext/projects/doctype/project/project.py:286-350`).

### Readiness from blockers (Odoo)
`_compute_state` (depends on `stage_id`, `depend_on_ids.state`): if dependencies are enabled and any blocking task is not in {1_done, 1_canceled}, a non-closed task becomes `04_waiting_normal`; when all blockers close, a waiting task returns to `01_in_progress` (`odoo/addons/project/models/project_task.py:398-413`). `is_blocked_by_dependences()` = any blocker open (`:454-455`). Stage change resets non-waiting open state to in progress (`:440-443`). Stale tasks: rotting domain excludes closed tasks (`:429-433`) with per-stage `rotting_threshold_days`.

### Sprint lifecycle (OpenProject)
- Validation: name/project required; dates required when active; finish ≥ start; only one active sprint per project unless `allow_multiple_active_sprints?` (`openproject/modules/backlogs/app/models/sprint.rb:64-79,123-127`). `duration` = count of working days in range (`:85-89`).
- Start: for each project receiving the sprint (sharing modes), create a sprint task board named "<project>: <sprint>" if missing, then `status=active`, `started_at=now` (`openproject/modules/backlogs/app/services/backlogs/sprints/start_service.rb:46-74`).
- Finish: open work packages (status not considered closed) are moved per `unfinished_action`: `move_to_sprint` (to target sprint at position 1, iterating position desc), `move_to_top_of_backlog` (sprint nil, position 1), `move_to_bottom_of_backlog` (sprint nil, position nil); then `status=completed`, `completed_at=now` (`finish_service.rb:38-87`).

### Burndown from journals (OpenProject `Burndown`)
1. Day series = working days from sprint start to finish (`openproject/modules/backlogs/app/models/burndown.rb:54-60`).
2. Ticks = working days from start to min(today, finish) at 23:59:59 in the user's time zone (`:79-89`).
3. Remaining points per tick = Σ `story_points` of work-package journals valid at the tick with `sprint_id` = sprint, project = project, status open (`is_closed=false` and not in project done statuses), via `WorkPackages::JournalTimeline` grouping by tick (`:62-77,91-95`).
4. Ideal line: max = first value; δ = max/(days − 1); ideal[i] = max − δ·i (`:97-107`).
The journal time-line gives the as-of-date state of each item, the primitive needed for PPC (inferred).

### Backward planning and conversion (D16.07)
- TaskJuggler validation for direction: a task with a start, an end and dependencies in its scheduling direction is over-specified (error); ALAP tasks with bookings are rejected (`alap_booking`); tasks with on-start dependencies must be ASAP (`onstart_wrong_direction`) (`taskjuggler/lib/taskjuggler/TaskScenario.rb:374-399`). Loop detection follows the scheduling direction: moving forward it traverses ASAP tasks start→end but not ALAP ones (`:625-728`; ALAP reverse traversal inferred).
- ERPNext `copy_from_template`: only when the project has a template and no tasks; project start defaults to today; for each template task create an Open task with `exp_start_date = project start + start` days and `exp_end_date = start + duration` days, each pushed forward past holidays of the project (or company) holiday list; then re-map `depends_on` and `parent_task` from template ids to the new task ids (`erpnext/erpnext/projects/doctype/project/project.py:114-237`). This is the closest "convert planned cards into activities" routine (inferred analogue).

### Task date alerts (D16.09)
Alert rule = per user (project override else global, via `applicable(project)`; D12) N days before start/due date, and every N days while overdue; delivery in-app plus the daily digest of unread, unmailed notifications (`openproject/app/models/notifications/scopes/unsent_reminders_before.rb`). The alert job is in `app/workers` (not cloned). ERPNext complements with the daily `set_tasks_as_overdue` status flip (`erpnext/erpnext/projects/doctype/task/task.py:532-543`), which emits no message itself.

## State machines and workflows
- ERPNext task: Open → Working → Pending Review → Completed; Overdue set by daily job and cleared on validation; Cancelled; Template fixed for template tasks (`task.py:183-190`). Completion guarded by dependencies.
- Odoo task: 01_in_progress ↔ 02_changes_requested ↔ 03_approved → 1_done | 1_canceled; 04_waiting_normal entered/exited automatically from blocker states.
- OpenProject sprint: in_planning → active (start service, board creation) → completed (finish service, carry-over). Work package belongs to a sprint xor a backlog bucket (DB check).

## Cross-domain links
- Tasks hang under schedule activities/WBS (D03) and use dependency semantics (D04); completion can feed activity progress (D10).
- Working-day logic for sprints/burndown uses calendars (D05).
- Constraints of type RFI/submittal (D27), material/PO (D19), permit/design documents (D25), labor/equipment (D07).
- Assignments and time actuals (D32); notifications on assignment/due dates (D12.04).
- Field execution logs (D28) and quality checklists (D29) for task checklists.

## Gaps
- Task fields for LPS: company/trade, crew size, location, proposed due date, task type, checklist items; constraint that task dates lie within the parent activity's dates (ERPNext checks only parent-task end and project dates).
- Look-ahead: rolling window (N weeks from data date) query over activities and tasks; make-ready status per task.
- Constraint register: typed constraint (RFI, submittal, material, labor, equipment, permit, predecessor, design), owner, need date, status open/closed, link to task and to source record; readiness = all constraints closed (generalize Odoo waiting-state rule to constraint rows); aging = today − created, reminders before need date.
- Commitments: (task, week, committer, committed date, locked flag) captured at the weekly meeting; immutable after lock.
- PPC per week = completed commitments / total commitments, sliced by company and project, with trend series (as-of-week evaluation using journals).
- Variance reasons: reason-code list, mandatory reason on missed commitment at week close, Pareto (count by reason, sorted, cumulative %).
- Pull planning: board session per milestone/phase with cards (trade, duration, handoff deliverable) and card-to-card dependencies; backward pass from the milestone date (ALAP latest finish = successor latest start − lag) to get the latest dates; conversion of cards into schedule activities and relationships (D03/D04), keeping a card → activity link.
- Takt: zone hierarchy (location breakdown), takt time (period length), trains of trades (wagons) with ordered work packages; sequencing places wagon k in zone z in takt slot z + k − 1 (offset by buffers); output = zone × time matrix and generated tasks; none in OSS.
- Task notifications: trigger on proposed due date change (request/accept), due-soon and overdue, with per-user frequency immediate/daily/weekly (OpenProject lacks weekly and proposed-date events).
