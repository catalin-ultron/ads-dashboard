# D33 Reporting Data Layer and Analytics

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D33.01 | Operational reporting data (ODS) and star schema | OpenProject journals (`validity_period` tstzrange) + historic relation; MPXJ `TimephasedUtility` (spreads); TaskJuggler `TraceReport` (periodic snapshot); Odoo `_auto=False` report models | partial | History-as-of-timestamp, period spreading and snapshot append exist; no warehouse, no nightly ETL, no conformed dimensions |
| D33.02 | Report definitions (backend) | Odoo `ir.actions.report` + `ir.cron`; OpenProject `CostQuery` + `CostReports::ScheduleExportService` + `Exports::Register`; ERPNext Script Reports; TaskJuggler `Report` formats | full | Parameterised report definitions, server-side PDF/XLSX/CSV/HTML, async export jobs, cron scheduling |
| D33.03 | KPI calculations library | LibrePlan `OrderEarnedValueCalculator`; MPXJ `Task` calculated fields; ERPNext project gross margin, budget variance; Odoo purchase/task report measures | partial | CPI, CV, SV, EAC, ETC, critical by float, variance, delay days; no SPI/BEI/CPLI/PPC/RFI-turnaround/submittal-cycle library |
| D33.04 | Data views for reporting | Odoo SQL-view models (`report.project.task.user`, `timesheets.analysis.report`, `purchase.report`, `account.invoice.report`, `project.task.stage.report`, burndown); MPXJ `PrimaveraDatabaseReader` | full | `CREATE VIEW` on init, table-query models, readonly ORM over views, group-by validation |

## Storage model

### History and snapshot storage

| Source | Table / class | Key fields | Notes |
|---|---|---|---|
| OpenProject | `journals` (`openproject/db/migrate/tables/journals.rb:35-60`) | journable_type+journable_id (polymorphic), user_id, version int, notes, data_type+data_id (polymorphic to per-type data table), cause jsonb, validity_period tstzrange, restricted bool, created_at, updated_at | CHECK `NOT isempty(validity_period)`; EXCLUDE `(journable_id =, journable_type =, validity_period &&)` = non-overlapping versions per object; type-2 slowly changing dimension equivalent |
| OpenProject | `work_package_journals`, `project_journals`, `customizable_journals`, `attachable_journals`, ... (`db/migrate/tables/*_journals.rb`) | full attribute snapshot per version | data rows referenced by `journals.data_id` |
| OpenProject | `exports`, `export_settings` tables (`db/migrate/tables/exports.rb`, `export_settings.rb`) | export job storage | presumably backs `CostReports::Export.create!` (inferred; table bodies not read) |
| TaskJuggler | trace CSV `<report>.csv` | header `Date` + one column per (property, attribute, scenario); one row per `now.midnight` | `lib/taskjuggler/reports/TraceReport.rb:79-140` |
| MPXJ | `TimephasedWork` / `TimephasedCost` (start, finish, totalAmount, amountPerHour) per assignment; actual/remaining/planned raw lists | `mpxj/.../ResourceAssignment.java:2471-2533` | source rows for spread facts |
| MPXJ PMXML | `Spread`, `ProjectResourceSpread`, `ProjectRoleSpread` elements under Project | `mpxj/.../primavera/schema/ProjectType.java` | P6 spread export shape (not consumed by reader) |
| Odoo | `project_task.duration_tracking` jsonb (`{"s": current_stage, "d": since, "<stage_id>": minutes}`) | source for burndown and time-in-stage | read in `addons/project/report/project_task_burndown_chart_report.py:83-91` |

### Reporting views / fact-like models (Odoo)

| Model (`_auto = False`) | Grain | Dimensions | Measures | File |
|---|---|---|---|---|
| `report.project.task.user` | task | project, stage, state, milestone, partner, company, parent, priority, dates | nbr, rating_avg, working_days/hours open/close, delay_endings_days, dependent_ids_count, is_closed, has_late_and_unreached_milestone | `addons/project/report/project_report.py:10-160` (CREATE VIEW in `init` :155) |
| `project.task.burndown.chart.report` | task x stage-transition | date, stage, project, milestone, partner, tags, assignees, state | `__count` (+1/-1 per transition), allocated_hours | `project_task_burndown_chart_report.py` |
| `project.task.stage.report` | task x stage | stage | time in stage | `project_time_by_stage_report.py:6-96` |
| `timesheets.analysis.report` | analytic line with project | user, project, task, parent task, employee, manager, company, department, partner, date | amount, unit_amount | `addons/hr_timesheet/report/timesheets_analysis_report.py:44-74` |
| `purchase.report` | PO line grouped by order+product | date_order, state, product, template, category, vendor, country, commercial partner, buyer, company, currency, fiscal position | qty_ordered/received/billed/to_be_billed, price_total, untaxed_total, price_average (avg), delay, delay_pass (avg), nbr_lines, weight, volume | `addons/purchase/report/purchase_report.py:10-110` |
| `account.invoice.report` | invoice line | (not fully read) | (not fully read) | `addons/account/report/account_invoice_report.py:9-93` |

### Report definition storage

| Source | Table / model | Key fields |
|---|---|---|
| Odoo | `ir.actions.report` | report_type {qweb-html, qweb-pdf, qweb-text}, paperformat_id, save_as_attachment, attachment_use, attachment (filename expression) (`odoo/odoo/addons/base/models/ir_actions_report.py:49-68`) |
| Odoo | `ir.cron` + `ir_cron_trigger` | interval_number, interval_type, nextcall, lastcall, priority, failure_count, first_failure_date, active (`ir_cron.py:114-123`) |
| Odoo | `ir.exports` / `ir.exports.line` | saved export field lists per model (`ir_exports.py`) |
| OpenProject | `CostQuery` (filters, group_bys, operators) | `modules/reporting/app/models/cost_query/*.rb`; filters in `cost_query/filter/*.rb`, group-bys in `cost_query/group_by/*.rb` (user, project, work package, activity, cost type, budget, version, status, priority, category, type, assigned_to, author, logged_by, spent_on, tweek, tmonth, tyear, custom fields) |
| OpenProject | `Exports::Register` | per model: list exporters, single exporters, formatters keyed by format (`app/models/exports/register.rb`) |
| ERPNext | Report JSON (`report_type: Script Report`, ref_doctype, prepared_report flag) + `execute(filters)` | e.g. `erpnext/erpnext/projects/report/project_summary/project_summary.json`, `.py` |
| TaskJuggler | Report property (formats list, columns, scenarios, start/end, hide/rollup expressions) | `taskjuggler/lib/taskjuggler/reports/Report.rb:48-150` |

## Algorithms and logic

**As-of-timestamp query (OpenProject)**
- `Journal.at_timestamp(ts)`: `WHERE validity_period @> timestamp with time zone :ts` (`app/models/journal/timestamps.rb`).
- `Journable::HistoricActiveRecordRelation` (`app/models/journable/historic_active_record_relation.rb`): rewrites a normal relation into a CTE that joins `journals` -> `<type>_journals` on `data_id`, selects historic attribute values instead of live columns, substitutes join tables (incl. custom values) in WHERE predicates, and adds the validity-period condition; with several timestamps emits `CASE WHEN validity_period @> ts THEN ...` (:156-175). Query validates allowed timestamps (`app/models/query.rb:152-156`). API exposure: `lib/api/v3/work_packages/work_package_at_timestamp_representer.rb`, `timestamped_representer.rb`.
- Rebuild use: activity/WBS dimensions as SCD-2 by keeping one row per version with a non-overlapping period; fact queries join on `period @> as_of`.

**Unified cost/time fact (OpenProject reporting)** (`modules/reporting/app/models/cost_query/sql_statement.rb`)
- `for_entries` = `unified_entry(TimeEntry) UNION unified_entry(CostEntry) AS entries`.
- Common columns: user_id, project_id, entity_type, entity_id, rate_id, comments, spent_on, created_at, updated_at, tyear, tmonth, tweek, costs, overridden_costs, type; plus count=1, real_costs = `CASE WHEN overridden_costs IS NULL THEN costs ELSE overridden_costs END`, week = ISO year-week of spent_on, entity_gid.
- Time entries: units = hours, cost_type_id = -1, cost_type = "Labor" label; cost entries: units, cost_type_id, cost_type = cost_types.name.
- Aggregation: every SQL group-by sums units, real_costs, display_costs (`group_by/sql_aggregation.rb`); `WrappedResult.display_costs` = 1 if any child may show costs, real_costs summed only then (`cost_query/result.rb`) — cost visibility is permission-driven per row.

**Period spreading (MPXJ)** (`mpxj/src/main/java/org/mpxj/TimephasedUtility.java:48-175`)
1. Inputs: assignment calendar, ordered timephased work blocks (start, finish, amountPerHour), target timescale ranges, target units.
2. Special case: a single block with start == finish and non-zero work puts all work in the last range.
3. Two-pointer sweep over ranges and blocks; for each intersection, hours = `calendar.getWork(max(starts), min(finishes))`, or elapsed minutes/60 if the block lies in non-working time; value += hours x amountPerHour, converted to target units; ranges with no work stay null.
4. `segmentCost` (:174) and `segmentMaterial` (:279) apply the same sweep to cost and material quantities; `addTimephasedDurations/Numbers` (:400-413) sum series.
- Rebuild use: activity spread and resource-assignment spread fact rows at day/week/month/financial-period grain.

**Periodic snapshot (TaskJuggler TraceReport)** (`lib/taskjuggler/reports/TraceReport.rb:36-150`)
1. Build query context (load unit, number/currency formats, time format fixed `%Y-%m-%d`, account/resource/task lists with hide/rollup filters).
2. Header = `Date` + generated columns for accounts, resources, tasks.
3. Load existing CSV; if header changed, reorder via `TableColumnSorter`, moving discontinued columns to the end.
4. Row key = `project.now.midnight`: overwrite that row if present (keeping discontinued-column values) else append; sort rows by date with header first.
- Equivalent to an EV/KPI history fact with one row per data date.

**Burndown from stage tracking (Odoo)** (`project_task_burndown_chart_report.py:61-130`)
1. Split the incoming domain into task-level and report-level parts (`_determine_domains`, :150-180); task part is pushed into a CTE `task_ids`.
2. Expand `duration_tracking` with `jsonb_each`, adding elapsed minutes for the current stage; per task, `date = now() - SUM(duration) OVER (PARTITION BY task ORDER BY stage.sequence DESC)` gives entry time into each stage.
3. Emit +1 row (enter stage) and -1 row with `LAG(stage_id)` (leave previous stage) and signed allocated hours; `__count` aggregated with SUM.
4. `_read_group` requires both a date group-by and `stage_id` (UserError otherwise).

**SQL-view model mechanics (Odoo)**
- `init()` drops and recreates the view: `CREATE or REPLACE VIEW <table> AS (<_table_sql>)` (`timesheets_analysis_report.py:72-74`, `project_report.py:155-158`).
- Alternative: `_table_sql` property returns a subquery used directly as the FROM table (`odoo/orm/models.py:531`, `odoo/orm/query.py:64,107`); `purchase.report` builds it from an ORM `_search` on `purchase.order.line` so record rules and company filters apply, then `GROUP BY` from `_groupby_list` (`purchase_report.py:54-110`). Registry skips table creation for such models (`odoo/orm/registry.py:1053`).
- Currency normalisation in view: `SUM(price_total / COALESCE(currency_rate,1)) * consolidation_rate`; UoM normalisation ratio `COALESCE(line_uom.factor,1)/NULLIF(COALESCE(product_uom.factor,1),0)` (`purchase_report.py:60-90`).

**KPI formulas found in code**
- CPI (LibrePlan, percent) = round(BCWP / ACWP, 4, HALF_UP) x 100, 0 if ACWP = 0 (`libreplan/.../planner/entities/OrderEarnedValueCalculator.java:167-175`).
- CV = BCWP - ACWP (:178; MPXJ `Task.calculateCV`, `Task.java:6787`).
- SV = BCWP - BCWS, null if either missing (MPXJ `Task.java:6792-6801`).
- EAC = BAC / CPI x 100 (CPI as percent), 0 if CPI = 0 (`OrderEarnedValueCalculator.java:183-190`); ETC = EAC - ACWP (:193). BAC = last value of cumulative budgeted-cost map (:103-106); BCWP/ACWP at date = value of cumulative map at the latest key <= date (`getValueAt`, :130-147).
- Critical (MPXJ) = not finished AND total slack (converted to the critical-slack-limit units) <= limit (`Task.java:6813-6830`, `CALCULATED_FIELD_MAP` :7265-7269).
- Budget variance (ERPNext) = budget - actual per period column and total (`erpnext/erpnext/accounts/report/budget_variance_report/budget_variance_report.py:240-253`).
- Project gross margin (ERPNext) = total_billed_amount - expenses; per_gross_margin = margin / billed x 100, 0 if no billing (`erpnext/erpnext/projects/doctype/project/project.py:382-393`).
- Task counts per project (total, completed, overdue) by grouped count (`projects/report/project_summary/project_summary.py`).
- Purchase delay (days) = epoch(age(date_approve, date_order))/86400; delay_pass = epoch(age(date_planned, date_order))/86400 (`purchase_report.py`).
- Task delay_endings_days = (date_deadline - now())/86400 (`project_report.py`).

**Server-side report generation and scheduling**
- Odoo: `_render(report_ref, res_ids, data)` dispatches on report_type to `_render_qweb_pdf` / `_render_qweb_html` / `_render_qweb_text` (`ir_actions_report.py:677-860`); with `attachment_use` a previously stored attachment is returned instead of re-rendering (:459-473); PDF engines via `base_report_wkhtmltox` / `base_report_paper_muncher` overrides (exist in repo, not read). Scheduled runs through `ir.cron` (`SKIP LOCKED` acquisition, interval rescheduling in user TZ, deactivation after 5 failures over 7 days; `ir_cron.py:300-690`).
- OpenProject: `CostReports::ScheduleExportService.call(format:, report_name:, report_params:, project:, cost_types:)` creates an export record and enqueues `CostReports::PDF::ExportTimesheetJob` (pdf) or `CostReports::XLS::ExportJob`; returns job id for polling (`modules/reporting/app/services/cost_reports/schedule_export_service.rb`). Generic exports: exporter classes registered per model and format; `formatter_for(model, attribute, format)` picks the first formatter whose `apply?` matches, else Default (`app/models/exports/register.rb`, `exporter.rb`).
- ERPNext Script Report contract: `execute(filters) -> (columns, data, message, chart, report_summary)`; columns carry fieldname, label, fieldtype, options, width (`project_summary.py`). Prepared reports (background-computed) flagged by `prepared_report` (frappe core, not cloned).
- TaskJuggler: one report definition, multiple output formats `iCal, html, csv, ctags, niku, tjp, mspxml` generated from an intermediate format per report type (accountreport, export, iCal, niku, resourcereport, tagfile, textreport, taskreport, tracereport, statusSheet, timeSheet) (`reports/Report.rb:71-150`).
- Odoo `/web/export` CSV/XLSX with group tree and per-field aggregators (sum/avg) for grouped exports (`addons/web/controllers/export.py:58-170`).

## State machines and workflows

- OpenProject export job: created (`CostReports::Export.create!`) -> job queued -> file attached / failed (job classes not read; inferred from service).
- Odoo cron: ready (nextcall <= now or trigger) -> acquired (row lock) -> done (failure_count reset, nextcall advanced) | failed (failure_count+1) -> deactivated at threshold.
- Journal version lifecycle: new version closes previous `validity_period` upper bound and opens a new one (inferred from exclusion constraint; journal creation service not read).

## Cross-domain links

- Facts: activity spread (D03/D06), assignment spread (D07/D08), EV history (D11), cost/time entries (D32, D13), budgets (D17), purchase lines (D19), invoices (D21), tasks/stages (D16).
- Dimensions: project/EPS (D01/D15), WBS (D03), resource/role (D07), calendar/period (D05, financial periods D17), codes/UDFs (D09).
- Row-level visibility uses D02 (OpenProject permission-gated cost display, Odoo record rules via ORM `_search` in table queries).
- Scheduling/cron shared with D36; exports reuse D35 formats.

## Gaps

- No warehouse/ODS: no fact/dimension schema, no nightly ETL, no surrogate keys. Rebuild: dims (project, WBS, activity, resource, role, cost account, code values, calendar date, financial period) as SCD-2 using OpenProject-style `validity_period` + exclusion constraint; facts `activity_spread(date_key, activity_key, planned/actual/remaining units+cost)`, `assignment_spread(...)` via MPXJ-style segmentation, `ev_history(period_key, wbs_key, bcws, bcwp, acwp, bac, eac)` appended per data date like TraceReport.
- KPIs missing: SPI (BCWP/BCWS), BEI (completed / planned-to-complete by date), CPLI ((CP length + float)/CP length), float erosion (total float delta between snapshots), PPC (Last Planner promises kept / made), change % of contract, RFI turnaround, submittal cycle time. All computable from D10 snapshots, D16 weekly plans, D20 change orders, D27 RFI/submittal state timestamps (journals give transition times).
- No published, permission-filtered views for external BI (D33.04 is ORM-internal in Odoo); rebuild needs database views or a read replica schema with row security mirroring D02.
- No BI Publisher-style data-model/template separation with parameter prompts beyond Odoo QWeb and ERPNext filters.
