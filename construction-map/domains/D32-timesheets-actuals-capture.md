# D32 Timesheets and Actuals Capture

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D32.01 | Timesheet periods | LibrePlan `PersonalTimesheetsPeriodicityEnum` (MONTHLY, TWICE_MONTHLY, WEEKLY); PMXML `TimesheetPeriodType`; ERPNext `Timesheet.start_date/end_date` | full | LibrePlan computes period start/end/previous/next from any date; P6 period rows stored |
| D32.02 | Timesheets (rows, hours per day, overtime, status, approvals) | ERPNext `Timesheet` + `Timesheet Detail`; LibrePlan `WorkReport`/`WorkReportLine`; OpenProject `time_entries`; PMXML `TimesheetType`/`ResourceHourType`/`TimesheetAuditType` | partial | Submit/cancel lifecycle (ERPNext docstatus), overlap checks, period completeness checks (TaskJuggler); P6 two-level approval only as schema fields (`ApprovedHours`, `UnapprovedHours`, `TimesheetApprovingAs`) |
| D32.03 | Overhead (nonproject) activities | PMXML `OverheadCodeType` + `ResourceHourType.OverheadCodeObjectId`; Odoo company internal project (Training, Meeting); OpenProject `TimeEntryActivity`; ERPNext `Activity Type` | partial | Codes and internal-project booking exist; exclusion from project cost is implicit (separate project) |
| D32.04 | Apply actuals | LibrePlan `SumChargedEffortDAO` (direct/indirect rollup), `MoneyCostCalculator`; ERPNext `Task.update_time_and_costing`, `Project.update_costing`; Odoo `project.task.effective_hours/remaining_hours` | partial | Hours and cost roll up to task/project and set actual start/end; nobody posts hours into assignment actual units with remaining recompute |
| D32.05 | Unifier timesheet BP (rate × hours to cost sheet) | ERPNext `Timesheet Detail.update_cost` + `_get_activity_cost`; OpenProject `Entry::Costs`; Odoo `_timesheet_postprocess_values` | full | Rate resolution and cost = hours × rate, stored on the line and summed to project actual cost |

## Storage model

### ERPNext (`erpnext/erpnext/projects/doctype/`)
| Doctype | Fields | Notes |
|---|---|---|
| `Timesheet` (submittable, naming `TS-.YYYY.-`) | `company`, `employee`, `user`, `department`, `start_date`, `end_date`, `status` {Draft, Submitted, Partially Billed, Billed, Payslip, Completed, Cancelled}, `time_logs` (child table, required), `total_hours`, `total_billable_hours`, `total_billed_hours`, `total_costing_amount`, `total_billable_amount`, `total_billed_amount`, `per_billed`, `parent_project`, `customer`, `currency`, `exchange_rate`, `base_*` totals, `sales_invoice`, `amended_from` | `timesheet/timesheet.json` |
| `Timesheet Detail` (child) | `activity_type` → Activity Type, `from_time`, `to_time`, `hours`, `expected_hours`, `completed`, `project`, `task`, `is_billable`, `billing_hours`, `billing_rate`, `billing_amount`, `costing_rate`, `costing_amount`, `base_*`, `sales_invoice`, `description` | `timesheet_detail/timesheet_detail.json` |
| `Activity Type` | `activity_type` (name), `costing_rate`, `billing_rate`, `disabled` | `activity_type/activity_type.json` |
| `Activity Cost` | `activity_type`, `employee` (optional), `department`, `costing_rate`, `billing_rate` | `activity_cost/activity_cost.json` |
| HRMS `Salary Slip Timesheet` | links timesheets to payroll (status Payslip) | `hrms/hrms/payroll/doctype/salary_slip_timesheet/` |

### LibrePlan work reports (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/workreports/entities/WorkReports.hbm.xml`)
| Table | Fields | Citation |
|---|---|---|
| `work_report_type` | `name`, `code`, `date_is_shared_by_lines`, `resource_is_shared_in_lines`, `order_element_is_shared_in_lines`, `hours_management` {NUMBER_OF_HOURS, HOURS_CALCULATED_BY_CLOCK, NUMBER_OF_HOURS_AND_CLOCK}, label type assignments, heading and line field definitions `{fieldName, length, positionNumber}` | `:8-60`; `java/.../workreports/entities/HoursManagementEnum.java:30-33` |
| `work_report` | `code`, `date`, FK type, FK `resource`, FK `order_element` (header-level when shared), labels, description values | `:64-112` |
| `work_report_line` | `code`, `effort` (seconds), `date`, `clock_start`, `clock_finish`, FK work report, FK `resource`, FK `order_element`, FK `type_of_work_hours` (overtime/normal etc.), labels, description values, `finished` (marks the task done from the timesheet) | `:115-170` |
| `sum_charged_effort` | FK `order_element`, `direct_charged_effort`, `indirect_charged_effort`, `first_timesheet_date`, `last_timesheet_date`, `finished_timesheets` | `java/.../orders/entities/SumChargedEffort.java:40-55` |
| `type_of_work_hours` / `hour_cost` / `cost_category` / `resources_cost_category_assignment` | priced hour types, effective-dated | `costcategories/entities/CostCategories.hbm.xml:7-104` |
Predefined report types: PERSONAL_TIMESHEETS, JIRA_TIMESHEETS (`java/.../workreports/entities/PredefinedWorkReportTypes.java:32-33`).

### OpenProject time entries (`openproject/modules/costs/`)
`time_entries` (`db/migrate/tables/time_entries.rb`): `project_id`, `user_id`, `entity_type/entity_id` (polymorphic: WorkPackage or Meeting; `20250416095154_add_entity_to_time_entry.rb`), `hours` float, `comments`, `activity_id` → `TimeEntryActivity`, `spent_on` date, `tyear`, `tmonth`, `tweek`, `overridden_costs`, `costs`, `rate_id`, `logged_by_id`, `ongoing` (unique per user where true), `start_time` (minutes 0..1439), `time_zone`. Custom fields via `TimeEntryCustomField`; journaled (`app/models/journal/time_entry_journal.rb`). Rates in `rates` (`HourlyRate` per user/project, `DefaultHourlyRate` per user, `valid_from`) (`app/models/rate.rb`, `hourly_rate.rb`).

### Odoo (`odoo/addons/`)
Timesheet line = `account.analytic.line` with `project_id` (`hr_timesheet/models/account_analytic_line.py:59-83`): `task_id`, `parent_task_id`, `project_id`, `employee_id`, `user_id`, `department_id`, `manager_id` (= employee parent), `unit_amount` (hours), `amount` (cost, negative), `date`, `account_id` + per-plan analytic columns, `milestone_id`. Overhead: `res.company.internal_project_id` with default tasks Training and Meeting (`hr_timesheet/models/res_company.py:26, 46-66`).

### P6 timesheet model (PMXML schema bound in MPXJ, `mpxj/src/main/java/org/mpxj/primavera/schema/`)
| Type | Fields |
|---|---|
| `TimesheetPeriodType` | `ObjectId`, `StartDate`, `EndDate` |
| `TimesheetType` | `ResourceObjectId`, `TimesheetPeriodObjectId`, `Status`, `StatusDate`, `IsDaily`, `LastReceivedDate`, `Notes`, `ResourceHour[]` |
| `ResourceHourType` | `ObjectId`, `Date`, `ResourceObjectId`, `ProjectObjectId`, `WBSObjectId`, `ActivityObjectId`, `ResourceAssignmentObjectId`, `OverheadCodeObjectId`, `ApprovedHours`, `ApprovedOvertimeHours`, `UnapprovedHours`, `UnapprovedOvertimeHours`, `ActivityTimesheetLinkFlag`, `Status`, `TimesheetPeriodObjectId`, `TimesheetStatusDate` |
| `TimesheetAuditType` | `ResourceObjectId`, `TimesheetPeriodObjectId/StartDate/EndDate`, `TimesheetStatus`, `TimesheetActivityStatus`, `TimesheetApprovingAs`, `ApproverUserObjectId/Name`, `AuditDate`, `ProjectHours`, `ProjectOvertimeHours`, `OverheadHours`, `OverheadOvertimeHours`, `Pending*Hours` |
| `TimesheetDelegateType` | `ProjectObjectId`, `ApproverUserObjectId`, `DelegateUserObjectId`, `ActiveFlag` |
| `OverheadCodeType` | `ObjectId`, `Name`, `Description`, `SequenceNumber` |
Resource-level approver: `ResourceType.TimesheetApprovalManagerObjectId` (`ResourceType.java:329-330`).

### TaskJuggler time sheets (`taskjuggler/lib/taskjuggler/TimeSheets.rb`)
`TimeSheet{resource, interval, scenarioIdx, records[]}`; `TimeSheetRecord{task, work (slots or %), remaining, expectedEnd, status{headline, summary, details, alertLevel}}` (`:22-60, 244-275`).

## Algorithms and logic

### ERPNext timesheet validation and costing
`Timesheet.validate` order (`timesheet/timesheet.py:69-79`): set status → set user → validate dates → calculate hours → validate time logs → reject cancelled tasks → update cost → totals → % billed → set dates.
- Overlap (`:225-305`): per `user` and per `employee` (each skippable via Projects Settings), a row overlaps another non-cancelled timesheet's row if `from` falls strictly inside, `to` falls strictly inside, or the new row encloses it; internal overlap between rows of the same sheet checked the same way; raises `OverlapError`.
- Mandatory (`:175-185`): from/to time, activity type, hours > 0.
- Rate resolution `_get_activity_cost(employee, activity_type)` (`:560-597`): Activity Cost for (employee, type) → Activity Cost for (no employee, type) → Activity Type default; convert by exchange rate when currency differs from base.
- Line costing `TimesheetDetail.update_cost` (`timesheet_detail/timesheet_detail.py:74-99`): fill missing rates from activity cost; `billing_amount = billing_rate × billing_hours`, `costing_amount = costing_rate × hours`; base amounts × exchange rate. Non-billable lines force billing rate 0 (`timesheet.py:309-311`).
- Totals and billing % (`:107-136`): sums over lines; `per_billed = billed_amount / billable_amount × 100` (or by hours).
- Status (`:141-151`): docstatus 0/1/2 → Draft/Submitted/Cancelled, then Billed (≥100%), Partially Billed (0..100), Completed (has sales invoice). HRMS override adds Payslip when a salary slip is linked and Completed when both invoice and salary slip exist (`hrms/hrms/overrides/employee_timesheet.py:8-17`).

### Actuals rollup (ERPNext)
- On submit/cancel `update_task_and_project` (`timesheet.py:186-203`): for each task, `Task.update_time_and_costing` sums submitted lines: `actual_time = Σhours`, `total_costing_amount = Σbase_costing_amount`, `total_billing_amount`, `act_start_date = min(from_time)`, `act_end_date = max(to_time)` (`task/task.py:332-351`); task status from lines: Open if none, Completed if any line has `completed`, else Working; Completed/Cancelled tasks never reopen (`timesheet.py:324-337`).
- `Project.update_costing` (`project/project.py:352-393`): same aggregation per project, plus purchase cost, sales and billed amounts; `gross_margin = billed − (costing + purchase + consumed material)`.

### LibrePlan charged effort and cost
- Incremental rollup on save of a work report line (`orders/daos/SumChargedEffortDAO.java:88-175`): load previous effort and order element in a separate transaction; same element → add or subtract the delta; element changed → subtract previous effort from the old element, add new effort to the new one. Direct effort goes to the line's element; the same delta is added as indirect effort to every ancestor recursively. Deletes subtract (`:180-230`).
- Full recalculation (`:253-345`): reset, recompute direct effort, `first/last_timesheet_date` = min/max line dates over the subtree, `finished_timesheets` = any line on the element has `finished = true` (`WorkReportLineDAO.java:194-200`).
- Clock-based effort: when the type's `hours_management` is HOURS_CALCULATED_BY_CLOCK, `effort = clockFinish − clockStart` (`java/.../workreports/entities/WorkReportLine.java:371-384`); constraints require clocks in clock modes, start ≤ finish, and header-shared fields (date, resource, order element) to equal the header (`:259-282, 391-414`).
- Labor cost: Σ over lines of `effort_hours × price`, price from the resource's active cost category hour cost for the line's hour type at the line date, fallback type default price (`planner/entities/MoneyCostCalculator.java:134-158`, `costcategories/daos/HourCostDAO.java:64-78`).
- Personal timesheet per period: the sheet for (resource, date) is the PERSONAL_TIMESHEETS report whose first line date lies in `[periodicity.getStart(date), getEnd(date)]` (`workreports/daos/WorkReportDAO.java:144-163`); periods: MONTHLY = calendar month; TWICE_MONTHLY = days 1–15 and 16–end; WEEKLY (`common/entities/PersonalTimesheetsPeriodicityEnum.java:35-130`).
- Progress from timesheets: work reports attached to a task move it to IN_PROGRESS (`planner/entities/Task.java:1210-1222`); predefined advance type TIMESHEETS exists (`advance/bootstrap/PredefinedAdvancedTypes.java:35`).

### OpenProject time entry costing and restrictions
- `before_save :update_costs` (`app/models/time_entry.rb:109`): `rate = user.rate_at(spent_on, project)` = newest `HourlyRate` with `valid_from ≤ spent_on` in the project hierarchy, else `DefaultHourlyRate` (`hourly_rate.rb:96-100`); `costs = hours × rate.rate`; effective cost = `overridden_costs` if present else `costs` (`app/models/entry/costs.rb:32-54`, `time_entry.rb:117-119`).
- Rate edits re-cost affected entries in the rate's validity window (`app/models/rate.rb:94-130`).
- Validation (`time_entry.rb:50-82`): user, project, spent_on, entity required; hours required unless ongoing; comments ≤ 1000; start_time 0..1439 and required when enforced; entity type ∈ {WorkPackage, Meeting}. Enterprise restrictions exposed as class methods: `max_hours_per_entry`, `max_hours_per_day`, `prohibit_logging_on_non_working_days?`, `limit_to_user_working_hours?`, `prohibit_logging_for_past_months?` + `past_month_grace_days` (`:200-243`). Timer: `ongoing_hours = (now − created_at)/3600` (`:137-141`); one ongoing entry per user (unique partial index).
- Permissions: edit own entries via `edit_own_time_entries` on the work package, others via `edit_time_entries` on the project; cost visibility via `view_hourly_rates` / `view_own_hourly_rate` (`:152-169`).

### Odoo timesheet amount and task actuals
- On create/write with `unit_amount`, `employee_id` or `account_id`: require active analytic account in the project plan, single company across project/task/accounts, then `amount = −unit_amount × employee.hourly_cost` converted to the account currency at the line date (`hr_timesheet/models/account_analytic_line.py:453-482, 506-508`); archived employees rejected on write (`:366-392`).
- Task: `effective_hours = Σ unit_amount`; `remaining_hours = allocated − effective − subtask_effective`; `progress = (effective + subtask)/allocated`, `overtime = max(total − allocated, 0)` (`hr_timesheet/models/project_task.py:96-160`).

### TaskJuggler time sheet completeness checks
`TimeSheet.check` (`TimeSheets.rb:277-312`): Σ record work must equal the resource's net working slots in the period ±1 slot (`ts_work_too_low` / `ts_work_too_high`); resources with efficiency 0 must report 0; duplicate task records rejected (`:259-266`). `TimeSheetRecord.check` (`:63-130`): a status is mandatory when ≥ 1 day was worked; headline required; elevated alert levels require summary/details.

## State machines and workflows
- ERPNext timesheet: Draft (docstatus 0) → Submitted (1, actuals posted to task/project) → Partially Billed → Billed → Completed (invoice linked); HRMS: Submitted → Payslip (salary slip) → Completed (invoice + slip); any → Cancelled (2, rollups recomputed on cancel); discard of a draft sets Cancelled (`timesheet.py:92-96, 141-171`). Amendment via `amended_from`.
- ERPNext task status from time logs: Open → Working (submitted hours) → Completed (`completed` line), never reopened (`timesheet.py:324-337`).
- P6 timesheet (schema only): resource hour lines carry `Status`; `TimesheetAuditType` records each transition with `TimesheetApprovingAs` (resource manager vs project manager), pending vs approved hours split; delegates via `TimesheetDelegateType`.
- OpenProject time entry: ongoing (timer running, hours null) → stopped (hours set); every change journaled.
- LibrePlan line `finished` flag marks the order element's work as finished from the timesheet side (`sum_charged_effort.finished_timesheets`).

## Cross-domain links
- Lines reference D03 activities/tasks (ERPNext `task`, LibrePlan `order_element`, OpenProject `entity`), D07 resources/employees and rates, D05 calendars (working-slot completeness, non-working-day prohibition).
- Actual hours/costs feed D10 progress (task status, actual dates), D11 ACWP, D17 cost sheet actuals; Odoo lines are analytic entries in D17/D13 CBS plans.
- Billing links to D21 invoicing (ERPNext `sales_invoice`); payroll link to HR (HRMS salary slip).
- Approval routing maps onto D24 workflow engine; permissions onto D02; audit onto journals (D36).
- Time entry custom fields → D09.

## Gaps
- Two-stage approval (resource manager then project manager) with partial approval of hours: schema only (P6). Rebuild: status per (timesheet, project) {Active, Submitted, RM-Approved, PM-Approved, Rejected}, audit row per transition, approved vs pending hour columns per line.
- Apply actuals to assignments (D32.04): no source posts hours to assignment actual units. Rebuild: for each approved resource-hour line linked to an assignment, `actualUnits += hours` (regular/overtime split), `remainingUnits = max(atCompletion − actual, 0)` or per auto-compute rule, `actualCost = Σ hours × effective rate`; set activity actual start on first hours and status In Progress; then reschedule (D10).
- Overhead activities excluded from project cost: rebuild as lines with `overheadCode` and no project, reported separately and charged to an overhead cost account.
- Auto-generated timesheet periods per resource calendar: LibrePlan computes periods but does not persist them; rebuild as period rows generated ahead (weekly/biweekly) with lock/close dates.
- Unifier shell-level timesheet BP posting into a cost sheet column: rebuild as BP line items (project/shell, cost code, hours, rate) whose approval posts `hours × rate` into the D17 actuals column.
