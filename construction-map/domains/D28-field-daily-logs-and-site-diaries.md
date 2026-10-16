# D28 Field: Daily Logs and Site Diaries

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D28.01 | Daily reports | LibrePlan WorkReport (+ WorkReportType heading/line fields); ERPNext Project Update; OpenProject cost entries (equipment units) | partial | Dated report header + lines per resource/task with configurable extra fields; email-collected daily status per user; no weather fetch, per-company manpower roll-up, deliveries/visitors/delays sections, or approve/lock |
| D28.02 | Field progress quantities | LibrePlan DirectAdvanceAssignment + AdvanceMeasurement + AdvanceType(unit) | full | Installed quantity per task by date with unit and max (budget) quantity; % = value / maxValue; monotonic measurements; feeds planning progress/EV |
| D28.03 | Photos and media | Mayan file_metadata (EXIF via exiftool) + DocumentFileSourceMetadata; OpenProject BCF viewpoint snapshots | partial | EXIF key/values stored per file; snapshots tied to 3D viewpoints; no geotag→drawing pin, no linked-record model beyond attachments |
| D28.04 | Field issues / observations | OpenProject BCF issue (1:1 work package) + viewpoint + status workflow | partial | Issue with 3D location (camera, components, clipping planes), assignee, due date, status workflow, comments; no 2D drawing pin coordinates |
| D28.05 | Forms and checklists engine | LibrePlan QualityForm/TaskQualityForm; ERPNext Quality Inspection Template + Quality Feedback Template | partial | Templates with ordered items, numeric min/max or formula acceptance, ratings; no conditional questions, no auto-issue on failure |
| D28.06 | Offline mobile sync | OpenProject `lock_version` optimistic locking + journals | partial | Record-version conflict detection; no queued upload protocol or field-level merge |
| D28.07 | Timecards / crew time | LibrePlan WorkReportLine; OpenProject time_entries; ERPNext Timesheet Detail | full | Hours by resource × task × date × hour type, clock in/out effort, cost via rates; crews only as resource groups (see D32) |

## Storage model

### LibrePlan work reports (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/workreports/entities/WorkReports.hbm.xml`)

| Entity / table | Key fields | Relations |
|---|---|---|
| WorkReportType `work_report_type` | `name` unique, `code` unique, `date_is_shared_by_lines`, `resource_is_shared_in_lines`, `order_element_is_shared_in_lines`, `hours_management` (NUMBER_OF_HOURS, HOURS_CALCULATED_BY_CLOCK, NUMBER_OF_HOURS_AND_CLOCK; `java/.../workreports/entities/HoursManagementEnum.java:31`) | 1:N `heading_field`/`line_field` (fieldName, length, positionNumber) = configurable diary fields; 1:N WorkReportLabelTypeAssignment (label type, default label, `labels_shared_by_lines`) |
| WorkReport `work_report` | `code` unique, `date`, `last_work_report_line_sequence_code` | N:1 type, resource, orderElement (when shared); M:N labels; set `description_values` (fieldName, value) |
| WorkReportLine `work_report_line` | `code` unique, `effort` (EffortDuration), `date`, `clockStart`, `clockFinish`, `finished` bool | N:1 workReport, resource, orderElement (task), typeOfWorkHours (cost category hour type); M:N labels; `description_values_in_line` |

### LibrePlan progress (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/advance/entities/Advance.hbm.xml`)

- **AdvanceType** `advance_type` (`:7`): `unitName` unique (`:17`), `defaultMaxValue` (`:19`), `unitPrecision` (`:23`), `percentage` bool (`:27`), `active`, `updatable`, `qualityForm` flag (inferred from QualityForm.advanceType link).
- **DirectAdvanceAssignment** (`:48-60`): N:1 orderElement, N:1 advanceType, `reportGlobalAdvance` bool (which assignment drives the task's global %), `maxValue` scale 2 (budget quantity); sorted set of measurements.
- **AdvanceMeasurement** `advance_measurement` (`:91`): `date`, `value` scale 2, `communicationDate`; consolidated values link to planning tasks.
- **IndirectAdvanceAssignment** (`:127`): aggregated on parents.

### ERPNext daily status collection

- **Project** fields `collect_progress`, `frequency` (Hourly | Twice Daily | Daily | Weekly), `from_time`, `to_time`, `first_email`, `second_email`, `daily_time_to_send`, `day_to_send`, `weekly_time_to_send`, `subject`, `message`, `holiday_list`, `users` Table(Project User) (`erpnext/erpnext/projects/doctype/project/project.json`).
- **Project Update** (`erpnext/erpnext/projects/doctype/project_update/project_update.json`): `project`, `date`, `time`, `sent`, `users` Table(Project User: `user`, `full_name`, `project_status` HTML of the reply). Naming `UPDATE-.project.-.YY.MM.DD.-.####` (`project.py:767`).

### OpenProject time and unit costs (`openproject/modules/costs/db/migrate/tables/`)

- `time_entries` (`time_entries.rb:35`): `project_id`, `user_id`, `work_package_id`, `hours`, `comments`, `activity_id`, `spent_on`, `tyear/tmonth/tweek`, `costs`, `overridden_costs`, `rate_id`, `logged_by_id`, `ongoing` (running timer), `start_time` (minutes), `time_zone`.
- `cost_types` (`cost_types.rb:35`): `name`, `unit`, `unit_plural`, `default`, `deleted_at` — e.g. "Excavator hour".
- `cost_entries` (`cost_entries.rb:35`): `user_id`, `project_id`, `work_package_id`, `cost_type_id`, `units`, `spent_on`, `comments`, `blocked`, `costs`, `overridden_costs`, `rate_id` — equipment/material quantities per day.

### Field issues and photos

- BCF tables (`openproject/modules/bim/db/migrate/tables/bcf_issues.rb`, `bcf_viewpoints.rb`, `bcf_comments.rb`): issue 1:1 work_package; viewpoint `json_viewpoint` jsonb + snapshot attachment; comments with optional viewpoint and `reply_to`.
- Mayan `FileMetadataEntry` (`mayan-edms/mayan/apps/file_metadata/models.py:87`: `internal_name`, `key`, `value`, unique (driver entry, internal_name)) under `DocumentFileDriverEntry` (driver × document file, `:22`); driver enable per document type `DocumentTypeDriverConfiguration` (`:44`). EXIF driver `mayan-edms/mayan/apps/file_metadata_exif/drivers.py:15` (exiftool path, timeout).

### Checklists

- LibrePlan `quality_form` (`name` unique, `description`, `quality_form_type` BY_PERCENTAGE | BY_ITEMS, list `quality_form_items` (name, percentage, position), `report_advance`, `advance_type_id`) and `task_quality_form` (orderElement, qualityForm, list items with `passed`, `date`) (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/qualityforms/entities/QualityForms.hbm.xml`).
- ERPNext Quality Inspection Template / Item Quality Inspection Parameter (`specification`, `numeric`, `min_value`, `max_value`, `value`, `formula_based_criteria`, `acceptance_formula`, `parameter_group`) — see D29.
- ERPNext Quality Feedback Template (`parameters` list) → Quality Feedback rows `parameter`, `rating` 1–5, `feedback` (`erpnext/erpnext/quality_management/doctype/quality_feedback/quality_feedback.json`).

## Algorithms and logic

**Work report effort** `libreplan/libreplan-business/src/main/java/org/libreplan/business/workreports/entities/WorkReportLine.java`
- When type's hours management is clock-based, setting `clockStart`/`clockFinish` recomputes `effort = secondsBetween(start, finish)` (`updateEffort` `:371`, `getDiferenceBetweenTimeStartAndFinish` `:381`).
- Constraints: clock start/finish required when clock-based (`:259,268`), start ≤ finish (`:277`); line fields must equal header fields when the type shares date/resource/task (`:391`).
- Header constraints (`WorkReport.java`): shared date/resource/task required (`:227,234,243`); only label types defined by the type (`:252`); all description fields present and unique (`:273,295`); line codes unique (`:414`); personal timesheets: one line per day per task (`:455`), all lines in one period (`:477`), resource bound to a user (`:506`).

**Progress % from quantities** `libreplan/libreplan-business/src/main/java/org/libreplan/business/advance/entities/DirectAdvanceAssignment.java:131`
- `percentage(date) = value(last measurement on or before date) / maxValue` (4 decimals, round down); maxValue 0 → 0.
- Invariants: measurements non-decreasing in date order (`isValidAdvanceMeasurementsConstraint` `:193`); percentage-type max must be 100 (`:224`); max > 0 (`:235`).
- `finished` on WorkReportLine marks the task as finished by field report (`WorkReports.hbm.xml` `finished` property).

**Unit cost of field entries** `openproject/modules/costs/app/models/entry/costs.rb:44`: on save, `rate = cost_type.rate_at(spent_on)` (`cost_entry.rb:109`); `costs = calculated_costs(rate)` (units × rate), `overridden_costs` takes precedence; no rate → costs 0.

**Daily status by email** `erpnext/erpnext/projects/doctype/project/project.py`
1. Scheduler picks Open projects with `collect_progress` and matching frequency (`get_projects_for_collect_progress` `:746`); hourly only inside from/to window, window may cross midnight (`is_now_between` `:640`).
2. Holiday → skip; else insert Project Update and send email with reply-to default incoming account (`send_project_update_email_to_users` `:756`).
3. `collect_project_status` (`:787`): received Communications referencing the update → sender mapped to User → reply parsed (EmailReplyParser, Markdown → sanitized HTML) → rows appended, duplicates suppressed with a Counter of (user, text).
4. Next day `send_project_status_email_to_users` (`:844`) mails a "Daily Project Summary" of all replies and sets `sent = 1`.

**EXIF extraction** (Mayan): on file upload, enabled drivers for the document type run (exiftool), each tag stored as a FileMetadataEntry row (key/value); queryable via search; geotag interpretation not implemented (inferred from driver scope).

**Checklist sequencing** `libreplan/libreplan-business/src/main/java/org/libreplan/business/qualityforms/entities/TaskQualityForm.java:98-158`: for BY_PERCENTAGE forms, an item may be passed only if the previous item (position − 1) is passed, and its date must be ≥ previous item's date; unpassed items must have no date. QualityForm BY_ITEMS auto-distributes 100% equally, remainder to last item (`QualityForm.java:361`).

**Conflict detection** OpenProject `lock_version` on work_packages, meetings, agenda items (`openproject/db/migrate/tables/work_packages.rb:46`; Rails optimistic locking raises StaleObjectError on mismatched version — inferred standard Rails behaviour); journals (`validity_period` non-overlapping) give full history for merge.

## State machines and workflows

- **BCF / field issue**: statuses from the work-package type workflow (e.g. Open → Ready for Inspection → Closed), transitions limited by role and author/assignee flags (`openproject/app/models/workflows/status_transition.rb:53`); blocked issues cannot close (`openproject/app/contracts/work_packages/base_contract.rb:736`).
- **Project Update**: created (`sent=0`) → replies collected → summary sent (`sent=1`).
- **WorkReport**: no status; personal timesheet type constrains period (see D32 for approval).
- **Time entry**: `ongoing` true (timer running) → false (stopped).

## Cross-domain links

- Scheduling/progress domain: AdvanceMeasurement drives task progress and consolidated values used in EV.
- D32 Timesheets: WorkReport/TimeEntry are the actuals source; TypeOfWorkHours → cost category rates.
- Cost domain: cost_entries/time_entries `costs` roll into project actual cost.
- D29: checklists (QualityForm, Quality Inspection) and failed items → punch/NCR; BCF issues double as punch items.
- D25: photos are documents; EXIF metadata via D25 file metadata pipeline.
- D27: field issue `relates` to RFI work package.

## Gaps

- **Daily log aggregate**: `daily_log(project, date, company, author, status draft/submitted/approved/locked)` unique per (project, date, company); child sections `weather(temp_hi, temp_lo, precip, wind, source=auto)`, `manpower(company, trade, headcount, hours)`, `equipment(type, hours_used, hours_idle)`, `delivery`, `visitor`, `delay(cause, duration)`, `work_performed(activity, location, qty)`, `note`, `photo`. Lock after approval; manpower trend = Σ headcount by trade/day.
- **Weather auto-fetch**: geocoded project location → daily weather API snapshot stored on the log.
- **Drawing pins**: `pin(document_version_page_id, x_pct, y_pct, record_type, record_id)`; Mayan page model + percent-based coordinates (as in `redaction_percent`) fit.
- **Forms engine**: conditional logic (show_if on prior answer), scoring, signature fields, and rule "failed answer ⇒ create issue/punch item".
- **Offline sync**: client-side queue, idempotency keys, per-field last-write-wins or 3-way merge using journal snapshots.
