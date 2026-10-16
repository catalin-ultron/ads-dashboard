# D24 Business Process and Workflow Engine

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D24.01 | BP definitions (metadata record types) | frappe DocType / DocField / Custom Field | partial | Full metadata-defined records with child tables, naming, submittable lifecycle; no staged design→deploy versioning |
| D24.02 | Workflow schemas | frappe Workflow (states, transitions, conditions, docstatus); OpenProject Workflow (role×status matrix) | partial | Role-gated transitions with Python conditions and per-state field updates; no parallel consensus, no sub-workflows, no step durations |
| D24.03 | Non-workflow BPs | frappe docstatus lifecycle; ERPNext computed `status`; OpenProject Status | full | Draft/Submitted/Cancelled plus derived statuses without routing |
| D24.04 | Tasks, due dates, escalation | frappe Workflow Action, ToDo, Assignment Rule, Notification (Days/Minutes Before/After), Automation Flow Wait | partial | Pending-action inbox, assignment with due dates, offset alerts, timed waits; no built-in SLA/auto-advance on timeout |
| D24.05 | Auto-creation and linking | frappe Workflow Transition Tasks, Automation Flow Create Document / Set Field Value, DocField `fetch_from` | full | Create downstream docs and auto-populate fields on transition or event |
| D24.06 | Record numbering | frappe naming series (`tabSeries`), Document Naming Rule | full | Prefix tokens incl. field values and dates; counter keyed by resolved prefix |
| D24.07 | Comments, attachments, markups | frappe Comment, File, Version | partial | Comments/attachments/audit; no markup layers |
| D24.08 | Bulk actions and integration | frappe `bulk_workflow_approval`, Data Import, whitelisted `apply_workflow`/`get_transitions` | full | Up to 500 docs per bulk action; CSV/XLSX import; RPC endpoints |
| D24.09 | Aconex document review workflows | frappe Workflow (modelable) | partial | Sequential steps by role; no parallel reviewer set, no outcome aggregation per revision |
| D24.10 | Formula and validation engine | OpenProject calculated-value custom fields (Dentaku); frappe `safe_eval` conditions | partial | Formula fields with dependency propagation; frappe conditional-mandatory is not enforced server-side |

## Storage model

### frappe Workflow (`frappe/frappe/workflow/doctype/*/*.json`)

- **Workflow** (`workflow/workflow.json`, named by `workflow_name`): `document_type` Link(DocType)*, `is_active`, `priority` Int, `workflow_state_field` Data* (default `workflow_state`), `override_status`, `send_email_alert`, `enable_action_confirmation`, `conditions` Table(Workflow Condition), `states` Table(Workflow Document State), `transitions` Table(Workflow Transition), `workflow_data` JSON (builder layout). N workflows per doctype; selection by priority + conditions.
- **Workflow Condition** (child): `field`*, `condition` Select(= != > < >= <=)*, `value`*. Decides which documents the workflow governs.
- **Workflow Document State** (child): `state` Link(Workflow State)*, `doc_status` Select(0 | 1 | 2), `allow_edit` Link(Role)*, `update_field` + `update_value` + `evaluate_as_expression`, `message`, `next_action_email_template`, `is_optional_state`, `send_email`, `avoid_status_override`.
- **Workflow Transition** (child): `state`*, `action` Link(Workflow Action Master)*, `next_state`*, `allowed` Link(Role)*, `allow_self_approval` (default 1), `condition` Code (Python expression), `send_email_to_creator`, `transition_tasks` Link(Workflow Transition Tasks).
- **Workflow Transition Task** (child of Workflow Transition Tasks): `task` Select*, `enabled`, `link` Dynamic Link(task) (Webhook or Server Script name), `asynchronous`.
- **Workflow Action** (`workflow_action/workflow_action.json`): `status` Select(Open | Completed), `reference_doctype` + `reference_name`, `workflow_state`, `user`, `completed_by`, `completed_by_role`, `permitted_roles` Table MultiSelect(Workflow Action Permitted Role). Index (reference_name, reference_doctype, status) (`workflow_action.py:54-58`). This is the per-document pending-task row.
- On save, Workflow creates a hidden Link custom field `workflow_state_field` → Workflow State on the target doctype if missing (`workflow/workflow.py:74-97`).

### frappe Automation Flow engine (`frappe/frappe/automation/doctype/*`, `frappe/frappe/automation_engine/*`)

- **Automation Flow** (`automation_flow.json`): `title`*, `document_type`, `enabled`, `disabled_reason`, `trigger_type` Select(Doc Created | Doc Updated | Field Value Changed | Doc Deleted | Doc Submitted | Doc Cancelled | Date Based | Scheduled | Custom Event | Manual)*, `trigger_field`, `from_value`, `to_value`, `custom_event`, `date_field`, `date_offset`, `date_direction` (Before | After), `cron_expression`, `next_run`, `filters` JSON, `condition` Python expression, `relationships` JSON (aliases to related records), `revalidate_on_run`, `actions` Table(Automation Action), `run_as` (Triggering User | Document Owner | Automation User), `automation_user`, `stop_on_error`.
- **Automation Action** (child, step plan): `step_key`, `step_type` (Action | Wait | WaitForEvent | If), `action_type`, `target` alias, `output_alias`, `params` JSON, `step_condition`, `related_condition` JSON, `parent_step` Int (idx of enclosing If), `branch` (If | Else).
- **Automation Trigger Queue**: `automation`*, `ref_doctype`, `ref_name`, `status` (Pending | Scheduled | Running | Done | Failed | Skipped), `triggered_at`, `run_after`, `attempt`, `depth`, `triggered_by`, `event_payload` JSON, `resume_run`, `resume_from_idx`; unique `dedup_key` (`automation_engine/dispatch.py:106-110`).
- **Automation Run**: `automation`, `status` (Running | Waiting | Success | Partially Failed | Failed | Skipped), `reference_doctype/name`, `user`, `depth`, `queue_row`, `started_at`, `ended_at`, `error_summary`, `steps` Table(Automation Run Step: `step_idx`, `step_key`, `action_type`, `status` Success|Failed|Skipped|Waiting, `duration_ms`, `detail`, `message`, `exception`, `traceback`, `condition`, `condition_values`, `output`), `actions_snapshot` JSON, `relationships` JSON, `run_state` JSON (step outputs, records, branches).
- **Automation Event Subscription**: `event_name`*, `correlation_key`*, `status` (Waiting | Matched | Timed Out | Cancelled)*, `expires_at`*, `run`*, `step_key`*, `resume_queue`*, `event_payload`.
- Settings defaults (`automation_engine/settings.py`): max_depth 3, failure_threshold 10, stale_running_minutes 30, max_attempts 3, commit_every 50, queue_retention_days 7, step_output_limit and event_payload_limit 65536.
- Built-in actions (`automation_engine/actions/core.py`): Set Field Value (`:49`), Create Document (`:96`), Increment Field Value (`:136`), Send Notification (`:215`), Assign to User (`:298`), Call Webhook (`:334`), Run Script (`:395`).

### frappe assignment, notification, audit, numbering

- **Assignment Rule** (`automation/doctype/assignment_rule/assignment_rule.json`): `document_type`, `priority`, `disabled`, `assign_condition`, `unassign_condition`, `close_condition` (Python), `rule` (Round Robin | Load Balancing | Based on Field | Weighted Distribution), `users` / `weighted_users` (user, weight), `last_user`, `current_index`, `field`, `due_date_based_on`, `assignment_days` (weekday filter).
- **ToDo** (`desk/doctype/todo/todo.json`): `status` (Open | Closed | Cancelled), `priority`, `date` (due), `allocated_to` User, `reference_type/name`, `role`, `assigned_by`, `assignment_rule`.
- **Notification** (`email/doctype/notification/notification.json`): `document_type`, `event` (New | Save | Submit | Cancel | Days After | Days Before | Minutes After | Minutes Before | Value Change | Method), `date_changed`, `days_in_advance`, `datetime_changed`, `minutes_offset`, `value_changed`, `condition` / `condition_type` (Python | Filters), `channel` (Email | Slack | System Notification | SMS), `recipients` Table, `set_property_after_alert` + `property_value`, `attach_print`.
- **Reminder**: `user`*, `reminder_doctype/docname`, `remind_at`*, `description`*, `notified`.
- **Milestone Tracker / Milestone**: tracker (`document_type`, `track_field`); milestone row per change (`reference_type/name`, `track_field`, `from_value`, `value`) (`milestone_tracker.py:32-44`). Provides state-entry timestamps for SLA analytics.
- **Version** (`core/doctype/version/version.json`): `ref_doctype`*, `docname`*, `data` JSON diff (changed, added/removed rows, impersonator) (`version.py:31-76`).
- **Comment**: `comment_type` (Comment | Like | Info | Label | Workflow | Created | Submitted | Cancelled | Updated | Deleted | Assigned | Assignment Completed | Attachment | Attachment Removed | Shared | Unshared | Bot | Relinked | Edit), `reference_doctype/name`, `content`, `comment_email`. Workflow transitions write a `Workflow` comment (`model/workflow.py:266`).
- **DocShare**: per-document grant (`user`, `share_doctype/name`, read/write/share/submit, `everyone`).
- **Series** table `tabSeries(name, current)` (`model/naming.py:428-452`); **Document Naming Rule**: `document_type`, `priority`, `conditions`, `prefix`, `prefix_digits` (`core/doctype/document_naming_rule/document_naming_rule.py:30-70`).
- **DocType / DocField** metadata (`core/doctype/doctype/doctype.json`, `core/doctype/docfield/docfield.json`): DocType `is_submittable`, `istable`, `issingle`, `autoname`, `naming_rule`, `track_changes`, `queue_in_background`, `states`, `permissions`, `fields`; DocField `fieldtype`, `options`, `reqd`, `depends_on`, `mandatory_depends_on`, `read_only_depends_on`, `fetch_from`, `fetch_if_empty`, `allow_on_submit`, `set_only_once`, `permlevel`, `unique`, `non_negative`, `min_value`, `max_value`.
- **Server Script** (`core/doctype/server_script/server_script.json`): `script_type` (DocType Event | Scheduler Event | Permission Query | API | Workflow Task), `doctype_event` (Before/After Insert, Validate, Save, Submit, Cancel, Delete, …), `event_frequency` (All … Cron).

### OpenProject workflow (`openproject/app/models`)

- **Workflow** (`workflow.rb:30-93`): `name` unique per `project_id`; `project_id` nullable (global vs project-owned); has_many `status_transitions`, `type_variants`.
- **Workflows::StatusTransition** (`workflows/status_transition.rb:30-35`): `workflow_id`, `role_id`, `old_status_id`, `new_status_id`, `author` Bool, `assignee` Bool. Rows are the allowed edges of the role×status matrix; `author`/`assignee` flags add edges for the work package author or assignee.
- **TypeVariant** (`type_variant.rb:66`): belongs_to `workflow`; a work-package type variant binds one workflow.
- **Status** (`status.rb`): `is_closed`, `is_default` (single default enforced `:57-62`), `is_readonly`, `default_done_ratio` 0..100.
- **Automation** (`automation.rb:30-61`): `name`, `actions` (serialized list), HABTM condition sets `status_conditions`, `role_conditions`, `type_conditions`, `project_conditions`; has_many `triggers` (`automation_triggers`, STI e.g. Button; at most one Button trigger).
- **CustomField calculated value** (`custom_field/calculated_value.rb`): `formula` JSONB `{formula, referenced_custom_fields[]}`.

## Algorithms and logic

**Workflow resolution** (`frappe/frappe/model/workflow.py:35-72`, `workflow/doctype/workflow/workflow.py:209-220`): active workflows for the doctype sorted by `priority` desc then `modified` desc (cached); the first whose every condition holds governs the doc (`applies_to`: each condition evaluated alone; unset field matches nothing). No match → doc behaves as un-workflowed.

**Workflow save-time validation** (`workflow/workflow.py:60-334`):
- All active workflows of a doctype must share `workflow_state_field` (`:232-252`).
- Activating an unconditional workflow deactivates other unconditional ones (`:298-316`).
- Same-priority peers must be provably disjoint (`:254-296`): for each field both constrain, a pinned value (`=`, or `>=`/`<=` equal) must violate the other's conditions, or a lower/upper bound pair must leave an empty range; strict bounds on Int/Check/Date are converted to inclusive by ±1 step (`:359-382`).
- docstatus edge rules (`:167-207`): non-submittable doctype → all states docstatus 0; no transition out of docstatus 2; no 1 → 0; no 0 → 2.
- On update, existing documents with unset (or peer-only) state are bulk-seeded with the first state per docstatus, restricted to this workflow's conditions and excluding docs claimed by higher-priority workflows (`:99-136`).

**Available transitions** (`model/workflow.py:75-112`): doc must be saved and readable; current state from state field; return transitions where `transition.state == current` and `transition.allowed ∈ user roles` and `condition` evaluates true via `frappe.safe_eval` with restricted globals (`frappe.db.get_value/get_list`, session, date utils) and `doc` as dict (`:115-135`).

**Apply action** (`model/workflow.py:153-268`):
1. Reload doc; resolve workflow; find transition with matching `action` among available ones.
2. Self-approval guard: allowed if Administrator, or `allow_self_approval`, or user ≠ doc owner (`:364-365`).
3. Set state field to `next_state`; if the next state has `update_field`, set it to `update_value` (optionally evaluated as an expression).
4. Transition tasks: enabled rows ordered by idx; Webhook → `execute_for_doc`, Server Script → `execute_workflow_task`, else app hook `workflow_methods`; synchronous tasks run in the same transaction, asynchronous ones are enqueued after commit (`:190-241`).
5. docstatus mapping: 0→0 save; 0→1 submit (queued if `queue_in_background`); 1→1 save; 1→2 cancel (queued likewise); anything else throws.
6. Add a `Workflow` comment with the new state.

**Direct-edit guard** (`model/workflow.py:303-356`, called from `Document.validate_workflow` `model/document.py:1189-1197`): if the state field changed on save, the new state must be reachable by a transition available to the user from the pre-save state; a new document may only start at the first state. On submit/cancel without an explicit transition, `set_workflow_state_on_action` moves to the first state with matching docstatus (`:509-523`).

**Pending actions and notification** (`workflow/doctype/workflow_action/workflow_action.py:94-130`, hooked on every doc `on_update`, `on_cancel`, `on_trash`, `on_update_after_submit` in `frappe/frappe/hooks.py:203-230`):
1. Mark the Open Workflow Action whose permitted roles intersect the user roles that could have caused the move as Completed with `completed_by`, `completed_by_role` (`:258-316`).
2. Compute next transitions from the new state, skipping optional next states and failed conditions (`:319-337`); insert one Open Workflow Action with permitted roles = the union of `allowed` roles (`:376-392`).
3. If enabled for the workflow and the state, email each user holding a role who passes the self-approval and read-permission checks (owner excluded unless `send_email_to_creator`); each email carries signed action links (`:340-374`, `:395-413`).
- Email link handler (`:132-167`) verifies the signature, shows a confirmation, and shows "link expired" if the doc is no longer in `current_state`; confirm calls `apply_workflow`.
- List permission (`:61-83`): users see only Open actions whose permitted roles include one of their roles.

**Bulk approval** (`model/workflow.py:380-454`): fewer than 20 docs inline, 20 to 500 enqueued on the short queue, more than 500 refused; each doc in its own commit/rollback; results classified per doc as successful/failed. `get_common_transition_actions` (`:479-500`) intersects the actions available across the selected docs.

**Assignment rules** (`automation/doctype/assignment_rule/assignment_rule.py`):
- `apply` on each save (`:274-372`): rules by priority desc; skip rules not active on today's weekday; first try unassign (`unassign_condition`), then assign only if no current assignment (`assign_condition`), then close ToDos when `close_condition` holds, else reopen closed ones.
- User selection (`:117-202`): Round Robin = next after `last_user` (read FOR UPDATE), wrapping; Load Balancing = user with fewest Open ToDos for the doctype; Based on Field = doc field value if it is a User; Weighted = `slot = current_index mod Σweights`, pick user whose cumulative weight exceeds slot, increment `current_index`.
- Due date sync (`:374-425`): when the `due_date_based_on` field changes, update open ToDo `date`.

**Automation Flow engine** (`frappe/frappe/automation_engine/`)
- Dispatch (`dispatch.py:22-103`): document hooks map to trigger types; Doc Updated suppressed during insert; match = Field Value Changed (old ≠ new, optional from/to equality as strings) + filter tree (and/or nested, `conditions.py:28-49`) + Python condition; recursion depth > max_depth is refused and logged; queue rows inserted or merged.
- Dedup (`dispatch.py:106-175`): one waiting row per (automation, doctype, name) without `resume_run`; repeat triggers refresh `triggered_at`, `triggered_by`, `run_after`, payload, and keep the max depth. A drain job is enqueued after commit with a fixed deduplicated job id.
- Drainer (`drainer.py:106-337`): claim up to 500 due rows `FOR UPDATE SKIP LOCKED` (falls back to `FOR UPDATE` on MariaDB < 10.6), mark Running, commit; execute in commit groups of 50 with a savepoint per row; if the group commit fails, rerun rows serially; rows whose run already produced external effects (Redis mark) are failed, not retried; escaped errors retry up to `max_attempts`; Running rows older than 30 min are requeued; Failed/Skipped rows and settled subscriptions are purged after 7 days.
- Runner (`runner.py:44-360`): load target (missing → Skipped); `revalidate_on_run` rechecks the rule; switch identity per `run_as`; require read permission on the trigger doc; walk the actions snapshot: steps in a non-taken If arm are skipped; If records the chosen arm in run state; per-step `step_condition` false → Skipped; Wait inserts a resume queue row at `now + value × unit` with `resume_from_idx = pos + 1` and returns Waiting; WaitForEvent inserts a subscription plus a resume row due at timeout; any Failed step → Partially Failed, or Failed and stop if `stop_on_error`.
- Finalize (`runner.py:507-626`): Success / Partially Failed / Waiting delete the queue row; Failed/Skipped keep it; consecutive failures counted in Redis; at `failure_threshold` the flow is disabled with a reason, its backlog is marked Skipped, and the owner gets a Notification Log.
- Events (`events.py:17-75`): `emit(event, doc, payload, correlation_key)` queues Custom Event flows and claims Waiting subscriptions with that correlation key; when the resume row runs, an unclaimed subscription becomes Timed Out, so steps after the wait can branch on match vs timeout.
- Date Based (`scheduler.py:179-240`): hourly; `target = today + offset` (Before) or `today − offset` (After); docs with `date_field` on target, after filters and condition, are queued once per day. Scheduled flows use croniter `next_run` (`scheduler.py:18-65`, `automation_flow.py:220-234`).

**Notifications with offsets** (`email/doctype/notification/notification.py:32`, `:267-340`, `:400-430`): Days Before/After matches docs whose `date_changed` equals today ± `days_in_advance` (daily job); Minutes Before/After evaluated every 5 minutes (`hooks.py:255-262`); Value Change on a chosen field; after sending, `set_property_after_alert` can write a field (only if `allow_on_submit` when submitted), which gives a basic escalation-flag primitive.

**Record numbering** (`model/naming.py`):
- `set_new_name` (`:144-201`): amended → suffix; autoincrement → DB sequence; UUID → uuid7; then Document Naming Rule; then controller `autoname`; then meta `autoname` (field:, naming_series:, format:, prompt, hash); fallback hash.
- `parse_naming_series` (`:346-407`): split on `.`; `#…` → zero-padded counter (only the first hash group); YY, YYYY, MM, DD, JJJ, WW (ISO week kept consecutive at year edges `:415-426`), timestamp; `{field}` or bare fieldname → document value; hook-registered custom tokens; literal otherwise.
- `getseries` (`:428-452`): `SELECT current … FOR UPDATE` on `tabSeries` keyed by the **resolved prefix**, increment or insert 1 (SQLite: UPSERT RETURNING). Because the key includes resolved field values and dates, `{project}-RFI-.YYYY.-.####` gives one counter per project per year. `revert_series_if_last` (`:455-507`) decrements on deletion of the last number.
- Document Naming Rule (`document_naming_rule.py:56-70`): first rule by priority whose conditions all hold sets `name = prefix + getseries(prefix, prefix_digits)`.

**Audit diff** (`core/doctype/version/version.py:31-120`): on update store `get_diff(old, new)` (changed fields, row additions/removals/changes in child tables), plus impersonator/audit user; on insert only when an updater reference (e.g. data import) exists.

**Mandatory validation** (`model/base_document.py:1004-1048`, `model/document.py:1499-1520`): server enforces `reqd` only (Text Editor/HTML treated as empty when no text/img; Check never missing). `mandatory_depends_on` is referenced only in DocType/DocField metadata validation in the Python sources read, so conditional-mandatory is client-evaluated (inferred).

**OpenProject status transitions** (`openproject/app/contracts/work_packages/base_contract.rb:186-200`, `:724-762`): allowed statuses = current status ∪ `new_status_id` of StatusTransition rows for the type variant's workflow where `old_status_id = current`, `role_id ∈ user roles in project`, and (author/assignee flags match: plain rows always; author rows if user is author; assignee rows if user was or is assignee) (`workflows/status_transition.rb:53-66`). The base status is the persisted value, so a status cannot be skipped without an intermediate save. A closed status with a closed target version only allows itself; a blocked work package excludes closed statuses. Matrix copy (`status_transition.rb:73-115`) replaces all rows for (workflow, role) with a source's rows in one SQL insert-select.

**OpenProject automations apply** (`openproject/app/services/automations/update_work_package_service.rb:44-90`): apply actions sorted by priority, validate with `WorkPackages::UpdateContract`; on errors drop the actions whose attribute failed, restore attributes and retry, then save via `WorkPackages::UpdateService`.

**OpenProject calculated values** (`custom_field/calculated_value.rb:30-140`, `acts_as_customizable/calculated_value.rb:41-104`): allowed tokens = `{{cf_N}}` references, numbers, operators `+ - * / % ^ < > <= >= <> != = == AND && OR ||`, functions IF/AND/OR/XOR/NOT/SWITCH/MIN/MAX/SUM/AVG/ROUND/ROUNDDOWN/ROUNDUP/ABS, CASE/WHEN/THEN/ELSE/END. Referenced fields are restricted to int/float/bool/calculated/weighted list fields that may be referenced (cycle guard `can_be_referenced_by?` `:177`). Evaluation: store given values, `Dentaku.solve(to_compute)` resolves dependencies; non-numeric results become nil with a persisted CalculatedValueError. Affected fields after a change are found by fixpoint over `referenced_custom_fields` (`:79-96`).

## State machines and workflows

**frappe docstatus** (`model/document.py:1418-1466`): 0 Draft → 0 (save) | 1 (submit, requires `is_submittable` and submit permission); 1 → 1 (update after submit, only `allow_on_submit` fields) | 2 (cancel, cancel permission); 0 → 2 and 1 → 0 are refused. Workflow states map onto these via `doc_status`; amend after cancel creates a new name with suffix (`naming.py:578`).

**frappe Workflow**: states and transitions are configuration (see Storage model). Guards: role, Python condition, self-approval, docstatus edge rules. Side effects: state field set, optional field update, transition tasks (webhook/server script/app method, sync or async), submit/cancel, Workflow comment, Workflow Action completion/creation, emails. Optional states are excluded from pending-action generation.

**Workflow Action**: Open → Completed (by the next transition from a user whose role is in `permitted_roles`); deleted when the document is trashed.

**Automation Trigger Queue**: Pending/Scheduled → Running (claim) → deleted on Success/Partially Failed/Waiting, or Failed/Skipped (kept for purge); escaped error → Pending (retry) until `max_attempts` → Failed; stale Running → Pending; breaker trip → all waiting rows Skipped.

**Automation Run**: Running → Waiting (Wait/WaitForEvent; resumed by the resume row on the same run) → Success | Partially Failed | Failed | Skipped.

**Automation Event Subscription**: Waiting → Matched (emit with correlation key) | Timed Out (resume row ran first) | Cancelled.

**ToDo**: Open → Closed (close condition or completion) → Open (reopen when close condition no longer holds) ; Cancelled on unassign.

**Odoo approval flows** (no generic engine in the cloned addons; flows are coded per model):
- purchase.order (`odoo/addons/purchase/models/purchase_order.py:108-114`, `:698-722`, `:1333-1341`): draft → sent → (confirm) to approve | purchase; amount threshold and manager group decide; approve → purchase (+ lock).
- hr.expense (`odoo/addons/hr_expense/models/hr_expense.py:126-146`, `:526-562`, `:1395-1426`, `:1644-1672`, `:1856-1873`): `approval_state` submitted/approved/refused; computed `state` draft → submitted → approved → posted → in_payment → paid, refused last. Submit sets `manager_id` from employee expense manager, else department manager in approver group, else team leader; auto-validate when no approver or approver is the employee; approve requires team-approver (subordinates via `child_of`), approver or admin group; duplicates trigger a confirmation wizard.
- account.move `review_state` todo → reviewed → supervised | anomaly, with group-based access check (`odoo/addons/account/models/account_move.py:60-65`, `:3912-3930`).

**OpenProject**: role×status matrix per workflow (above); Status flags `is_closed`, `is_readonly` (readonly status cannot be default `status.rb:109`).

## Cross-domain links

- Every D23 payment doctype (Purchase Invoice, Payment Entry, Payment Request) is governed by frappe Workflow/Assignment Rule/Notification; holds and approvals in D23.05–D23.07 are expressed through D24.
- D24.09 document review → D25 Document Management (document revision is the workflow subject) and D26 transmittals (auto-transmit on completion would be a transition task or Automation Flow Create Document).
- D27 RFIs/Submittals: ball-in-court and due-date tracking map onto Workflow Action + ToDo `date` + Date Based automations.
- Access control and roles (permissions domain): transitions are gated by Role; Workflow Action visibility uses roles; DocShare gives per-document access.
- Change management (change events → change orders) relies on D24.05 auto-creation.
- OpenProject Workflow binds to work package TypeVariant (scheduling/work-package domain); calculated values live on ProjectCustomField (project attributes domain).

## Gaps

- **Parallel review with consensus (D24.02, D24.09)**: frappe allows one transition per action/role and no reviewer set. A rebuild needs `step_instance(workflow_instance_id, step_id, mode {all, any, majority}, due_at)`, `step_assignment(step_instance_id, user_id, outcome, decided_at)`, an aggregation rule producing the step outcome (Approved, Reviewed with comments, Rejected), and final outcome = function of step outcomes.
- **Sub-workflows**: no OSS support; model as a child workflow instance linked to a parent step, parent waits on child completion (the frappe WaitForEvent/correlation pattern fits).
- **Step durations, SLA, escalation, auto-advance (D24.04)**: no `due_in` on frappe states. Add `due_duration` per step and set `due_at` on entry; reuse the frappe engine pattern (resume row at `due_at`, subscription timeout) to escalate or apply a default transition.
- **Versioned design→deploy (D24.01)**: frappe applies DocType/Workflow changes in place (only `migration_hash` and cache clearing). Needs `bp_definition_version` with immutable published versions, and instances pinned to the version they started on (frappe Automation Run already snapshots its actions in `actions_snapshot`, which is the pattern to copy).
- **Markups (D24.07)**: no markup layers; needs `markup(document_version_id, reviewer_id, layer_json, created_at, superseded_by)`.
- **Server-side conditional validation (D24.10)**: implement `mandatory_depends_on` / `read_only_depends_on` evaluation on the server with the same restricted evaluator used for transition conditions; date arithmetic functions exist only in the workflow safe globals (`add_to_date`, `now_datetime`).
- **Per-shell scoping (D24.02, D24.06)**: frappe workflows are per doctype, not per project/shell; scope via a Workflow Condition on a `project` field (supported) or a project_id on the workflow like OpenProject's project-owned workflows (`workflow.rb:33-47`).
