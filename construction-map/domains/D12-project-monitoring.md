# D12 Project Monitoring: Thresholds, Issues, Work Products and Notifications

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D12.01 | Project thresholds | MPXJ P6 schema `ProjectThresholdType`, `ThresholdParameterType`; ERPNext `Budget` Stop/Warn actions | partial | Full P6 data model; no threshold monitor job in OSS. ERPNext budget enforcement is the only working limit-breach evaluator |
| D12.02 | Project issues | MPXJ P6 schema `ProjectIssueType`, `IssueHistoryType`; OpenProject work packages + workflows + notifications | partial | P6 shape exactly; lifecycle/notification engine comes from OpenProject work packages (generic) |
| D12.03 | Work products and documents | MPXJ P6 schema `DocumentType`, `ProjectDocumentType`, `DocumentStatusCodeType`, `DocumentCategoryType`; OpenProject `documents` module | partial | P6 fields captured; no review lifecycle logic or check-in/out in OSS |
| D12.04 | Notifications engine | OpenProject `Notification`, `NotificationSetting`, `Notifications::CreateFromModelService`, `MailService`, `Reminder` | full | Event (journal) → recipients by reason → in-app + immediate mail + digest flags, per-user and per-project settings |
| D12.05 | Status reporting | Odoo `project.update`; ERPNext `Project Update` + collect-progress scheduler; OpenProject `projects.status_code` | full | Odoo: RAG status snapshot with task counts; ERPNext: periodic e-mail collection of narrative replies |
| D12.06 | Change and decision logs | OpenProject work package types + statuses (generic) | partial | No dedicated log entity; typed work packages with workflow serve as configurable logs (inferred) |

## Storage model

### P6 thresholds and issues (`mpxj/src/main/java/org/mpxj/primavera/schema/`)

| Type | Fields | Keys / FKs |
|---|---|---|
| `ThresholdParameterType` | `ObjectId:int`, `Name:string(80)`, `Type` {AV - Accounting Variance (Cost), CV - Cost Variance (Cost), SV - Schedule Variance (Cost), VAC - Variance at Completion (Cost), Cost Percent of Planned (Percent), CPI - Cost Performance Index (Ratio), CVI - Cost Variance Index (Ratio), SPI - Schedule Performance Index (Ratio), SVI - Schedule Variance Index (Ratio), Duration Percent of Planned (Percent), Start Date Variance (In Days), Finish Date Variance (In Days), Total Float (In Days), Free Float (In Days)} | global catalogue (`ThresholdParameterType.java`) |
| `ProjectThresholdType` | `ObjectId`, `ProjectObjectId`, `ThresholdParameterObjectId`, `LowerThreshold:double`, `UpperThreshold:double`, `DetailToMonitor` {Activity, WBS}, `WBSObjectId` (scope), `OBSObjectId` (responsible manager), `IssuePriority` {Top, High, Normal, Low, Lowest}, `Status` {Enabled, Disabled}, `FromDate`/`ToDate:dateTime`, `FromDateExpression`/`ToDateExpression:string(50)` (relative monitoring window), `IsBaseline`, `IsTemplate`, audit fields | N thresholds : 1 project; FK to parameter, WBS, OBS (`ProjectThresholdType.java`) |
| `ProjectIssueType` | `ObjectId`, `Name:string(100)`, `Priority` {Top, High, Normal, Low, Lowest}, `Status` {Open, On Hold, Closed}, `DateIdentified`, `IdentifiedBy:string(255)`, `ResolutionDate`, `OBSObjectId` (responsible manager), `ActivityObjectId`, `WBSObjectId`, `ResourceObjectId`, `ProjectThresholdObjectId`, `ThresholdParameterObjectId`, `LowerThreshold`, `UpperThreshold`, `ActualValue:double` (value that breached), `Notes`, `RawTextNote`, `UDF[]` | 1 issue → 0..1 threshold; optional activity/WBS/resource (`ProjectIssueType.java`) |
| `IssueHistoryType` | `ProjectIssueObjectId`, `ProjectObjectId`, `Notes`, audit fields | N : 1 issue (`IssueHistoryType.java`) |

`ProjectType` embeds `ProjectThreshold[]` (`mpxj/src/main/java/org/mpxj/primavera/schema/ProjectType.java`). MPXJ has no model class or reader for these types (no `getProjectThreshold`/`ProjectIssue` outside `schema/`).

### P6 work products and documents

| Type | Fields |
|---|---|
| `DocumentType` | `ObjectId`, `ProjectObjectId`, `ParentObjectId` (folder tree), `Title:string(120)`, `Version:string(20)`, `Author`, `ReferenceNumber:string(32)`, `Deliverable:boolean`, `DocumentCategoryObjectId`, `DocumentStatusCodeObjectId`, `DocumentStatusName` {'' , Not Started, Under Review, In Progress, Completed, On Hold}, `DocumentType` {Non-Collaboration Document, Collaboration Document, Repository Document}, `PrivateLocation:string(4000)`, `PublicLocation:string(4000)`, `ContentRepositoryDocumentInternalId:string(4000)`, `RevisionDate`, `ResourceObjectId`, `ActivityObjectId`, `SequenceNumber`, `GUID`, `UDF[]` |
| `ProjectDocumentType` (assignment) | `DocumentObjectId`, `ActivityObjectId`, `WBSObjectId`, `IsWorkProduct:boolean`, `ProjectObjectId` |
| `DocumentStatusCodeType` | `Name:string(36)`, `SequenceNumber` |
| `DocumentCategoryType` | `Name:string(100)`, `SequenceNumber` |

### OpenProject documents (`openproject/modules/documents/`)
`documents`: `project_id` (not null), `category_id` (FK document_types), `title string(60)`, `description text`, `kind string`, `content_binary text`, timestamps; `document_types`: `name`, `position`, `is_default`, `active`, `documents_count`; journaled via `document_journals` (`openproject/modules/documents/db/migrate/`, `app/models/document.rb`, `app/models/journal/document_journal.rb`).

### OpenProject notifications (`openproject/db/migrate/tables/`)

| Table | Columns | Constraints |
|---|---|---|
| `notifications` | `subject text`, `read_ian bool` (in-app read), `reason smallint`, `recipient_id` → users, `actor_id` → users, `resource_type/resource_id` (polymorphic), `journal_id` → journals (on delete cascade), `mail_reminder_sent bool default false` (digest), `mail_alert_sent bool default nil` (immediate), timestamps | indexes on `read_ian`, `mail_reminder_sent`, `mail_alert_sent` (`notifications.rb`) |
| `notification_settings` | `user_id` (not null), `project_id` (null = global); booleans `watched`, `mentioned`, `assignee`, `responsible`, `shared` (default true); `work_package_commented|created|processed|prioritized|scheduled`, `news_added|commented`, `document_added`, `forum_messages`, `wiki_page_added|updated`, `membership_added|updated` (default false); integers `start_date` (default 1), `due_date` (default 1), `overdue` (default nil) for date alerts | unique `user_id` where project null; unique `(user_id, project_id)` where not null (`notification_settings.rb`) |
| `reminders` | `remindable` (polymorphic), `creator_id`, `remind_at datetime not null`, `completed_at`, `job_id`, `note` | (`reminders.rb`) |
| `reminder_notifications` | `reminder_id`, `notification_id` (unique) | (`reminder_notifications.rb`) |

`Notification::REASONS` = mentioned 0, assigned 1, watched 2, subscribed 3, commented 4, created 5, processed 6, prioritized 7, scheduled 8, responsible 9, date_alert_start_date 10, date_alert_due_date 11, shared 12, reminder 13 (`openproject/app/models/notification.rb:31-48`). User preferences hold `daily_reminders` (enabled + times), `immediate_reminders` (`mentioned`, `personal_reminder`), `workdays`, `pause_reminders`, `time_zone` in a JSON `settings` column (`openproject/app/models/user_preference.rb:172-267`).

### Status reporting
- Odoo `project.update` (`odoo/addons/project/models/project_update.py:22-63`): `name` (required), `status` {on_track, at_risk, off_track, on_hold, done} (required), `progress:int`, `user_id` (author), `description:html`, `date`, `project_id` (required, non-template), `task_count`, `closed_task_count` (snapshot ints). `project.project.last_update_id` and stored computed `last_update_status` (default `to_define`) (`odoo/addons/project/models/project_project.py:192-200,350-358`).
- ERPNext `Project Update` (submittable; `erpnext/erpnext/projects/doctype/project_update/project_update.json`): `project`, `sent`, `date`, `time`, child table `users` (Project User: `user`, `full_name`, `image`, `project_status` text). Project fields driving collection: `collect_progress`, `frequency` {Hourly, Twice Daily, Daily, Weekly}, `from_time`, `to_time`, `first_email`, `second_email`, `daily_time_to_send`, `day_to_send`, `weekly_time_to_send`, `message`, `subject`, `holiday_list` (`erpnext/erpnext/projects/doctype/project/project.json`).
- OpenProject `projects.status_code` enum {on_track 0, at_risk 1, off_track 2, not_started 3, finished 4, discontinued 5} + `status_explanation text`, journaled (`openproject/app/models/project.rb:154,221-228`, `openproject/db/migrate/tables/projects.rb:45-46`).

## Algorithms and logic

### Notification fan-out (OpenProject `Notifications::CreateFromModelService`)
Input: a `Journal` (or a model) and `send_notifications` flag (`openproject/app/services/notifications/create_from_model_service.rb:81-95`).
1. Abort if model missing/deleted or no `<ResourceClass>Strategy` (`:314-318,356-364`).
2. For each reason in `strategy.reasons` (work packages: mentioned, assigned, responsible, watched, commented, created, processed, prioritized, scheduled, shared; `create_from_model_service/work_package_strategy.rb`), select `NotificationSetting` rows where the reason column is true, for users allowed the strategy permission (`view_work_packages`, or `view_internal_comments` for internal journals) in the project, restricted by `applicable(project)` (`:158-250`).
   - commented only if `journal.notes?`; created only if `journal.initial?`; processed if `status_id` changed; prioritized if `priority_id` changed; scheduled if `start_date` or `due_date` changed (`:199-239`).
   - assigned/responsible resolve a Group to its members (`:320-322`).
   - mentioned parses `<mention data-type="user" data-id>`, `user#id`, `user:"login"`, group tags and `group#id` from notes plus diff additions of `description`/`subject`, ignoring quoted `> ` lines (`:31-58,256-312`).
3. Receivers map user → [reasons]; first reason wins (`transform_values(&:first)`) (`:86`). Actor is removed unless directly mentioned (`:334-348`).
4. Upsert per (resource, journal, recipient): new rows get `read_ian=false` if strategy supports in-app, `mail_reminder_sent=false` if digest supported, `mail_alert_sent=false` only if immediate mail supported (work packages: only `mentioned`) (`:103-135`).
5. Delete notifications on the same journal for recipients no longer targeted (`:137-142`).
- `applicable(project)`: for each user pick the project-specific setting row if present, else the global row (outer-join coalesce) (`openproject/app/models/notification_settings/scopes/applicable.rb`).
- Immediate mail: `MailService` skips if already read in-app, marks `mail_alert_sent`; work-package strategy sends only for reason mentioned and only if `pref.immediate_reminders[:mentioned]` (`openproject/app/services/notifications/mail_service.rb`, `mail_service/work_package_strategy.rb`).
- Digest selection: `created_at <= time`, recipient, `read_ian in (false,nil)`, `mail_reminder_sent=false`, `mail_alert_sent in (false,nil)` (`openproject/app/models/notifications/scopes/unsent_reminders_before.rb`). Digest scheduling job is in `app/workers` (not cloned).

### Threshold enforcement (ERPNext Budget; closest working analogue)
`validate_budget_records` → for each budget with amount: yearly action and accumulated-monthly action ∈ {Stop, Warn, Ignore} per document type (MR, PO, actual expense, cumulative) (`erpnext/erpnext/accounts/doctype/budget/budget.py:500-538`). `compare_expense_with_budget`: total = actual expense + (requested + ordered for MR, ordered for PO, or the given amount); if total > budget → message "already exceeded"/"will be exceeded" with breakdown; users in `exception_approver_role` downgrade Stop to Warn; Stop throws `BudgetError`, Warn shows message (`:540-585`). Accumulated monthly budget = Σ distribution rows with `start_date <= posting_date` (`:813-830`).

### Status collection (ERPNext)
- Scheduler entry points `hourly_reminder` (within `from_time..to_time`, window may cross midnight), `daily_reminder`, `twice_daily_reminder`, `weekly_reminder` (only on `day_to_send`) over projects with `collect_progress=1`, matching `frequency`, `status=Open` (`erpnext/erpnext/projects/doctype/project/project.py:631-682,746-753`).
- Due count = number of send times already passed today − Project Updates already created today, floored at 0 (`:684-689`).
- Send: skip on holiday or no users; insert `Project Update` (series `UPDATE-.project.-.YY.MM.DD.-.####`), e-mail users with reply-to = default incoming account (`:756-784`).
- `collect_project_status`: for today's unsent updates, read received `Communication` replies, strip quoted text (`EmailReplyParser`), convert markdown → sanitized HTML, de-duplicate by multiset of (user, status) already collected, append rows (`:787-841`).
- `send_project_status_email_to_users`: yesterday's unsent updates → summary mail template `daily_project_summary`, set `sent=1` (`:844-864`).

### Status snapshot (Odoo)
Writing `last_update_status` on a project (≠ to_define) creates a `project.update` named "Status Update - <date>" with that status and pops the field (`odoo/addons/project/models/project_project.py:725-733`). On create, the update becomes the project's `last_update_id` and snapshots `task_count` and `closed_task_count = task_count − open_task_count` (`odoo/addons/project/models/project_update.py:88-97`); unlink re-points to the latest remaining update by date (`:99-104`). `closed_task_percentage = round(closed × 100 / count)` (`:80-82`). Default description renders milestones with deadline < today + 1 year or no deadline (`:126-137`).

## State machines and workflows

- P6 issue: Open ↔ On Hold → Closed (enum only; `ProjectIssueType.Status`). Resolution date set at close (inferred). Threshold `Status` Enabled/Disabled.
- P6 document status: Not Started → In Progress → Under Review → Completed, On Hold (enum only; `DocumentType.DocumentStatusName`); user-defined `DocumentStatusCodeType` list in parallel.
- OpenProject work package status transitions (for issues/logs): `workflows` rows (`type_id`, `old_status_id`, `new_status_id`, `role_id`, `author bool`, `assignee bool`) (`openproject/db/migrate/tables/workflows.rb`); `Workflows::StatusTransition.from_status(old, role_ids, author:, assignee:)` returns general transitions plus author-only / assignee-only ones when the user is author/assignee (`openproject/app/models/workflows/status_transition.rb`). Statuses carry `is_closed`, `is_default`, `is_readonly`, `default_done_ratio` (`openproject/db/migrate/tables/statuses.rb`). Side effect: each change writes a journal → notification fan-out above.
- Notification: unread (`read_ian=false`) → read; mail flags false → true when sent; `nil` = channel not applicable.
- ERPNext Project Update: created (sent=0) → replies collected → summary mailed (sent=1); submittable document (docstatus 0/1/2).
- Odoo project last-update status: to_define → {on_track, at_risk, off_track, on_hold, done} by creating updates.

## Cross-domain links
- Threshold parameters consume EV metrics (D11) and float/dates (D06), duration % (D10).
- Issues reference activity/WBS (D03), resource (D07), OBS responsible manager (D01/D02).
- Work products link to activities/WBS (D03) and the document repository (D25).
- Notifications are driven by journals/audit (D36) and permissions (D02); workflow engine (D24).
- Status updates snapshot task counts and milestones (D03, D16); reporting layer (D33).
- Budget-breach evaluation reads purchase orders/material requests (D19) and GL actuals (D17).

## Gaps
- Threshold monitor job: for each enabled `ProjectThreshold`, evaluate the parameter per activity or WBS within `DetailToMonitor` and `WBSObjectId`, over the window resolved from From/To date or expressions; if value < lower or > upper, create a `ProjectIssue` with `ThresholdParameterObjectId`, limits, `ActualValue`, `IssuePriority`, responsible OBS; de-duplicate open issues per (threshold, object). No OSS implementation.
- Issue history notes appended on each change, e-mail to responsible manager on create/transition.
- WP&D review lifecycle and check-in/check-out against a content repository (D25).
- Change/decision log entity (log type, entries, owner, status) as in Primavera Cloud; model as typed items with workflow.
- Channel/frequency per rule (push, weekly digest) beyond OpenProject's in-app + immediate mail + daily digest.
