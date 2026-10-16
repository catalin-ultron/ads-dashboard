# Primavera-Class Construction Operations Platform: Backend Feature Inventory

## D01 Enterprise Structure and Tenancy

- **D01.01 Enterprise Project Structure (EPS)**: a single hierarchical tree of nodes that holds every project. *Data:* EPS node (id, parent_id, name, seq, OBS responsible manager), project→EPS link. *Logic:* data from projects rolls up into EPS nodes (dates, costs, units, EV); moving a node re-parents its subtree; access is inherited down the tree.
- **D01.02 Organizational Breakdown Structure (OBS)**: one organization-wide hierarchy of responsible managers that drives security. *Data:* OBS node (id, parent, name, description), user↔OBS assignments with a project security profile. *Logic:* rights over EPS/WBS/project are granted through the OBS element assigned as responsible manager.
- **D01.03 Project entity**: the scheduling and cost container. *Data:* project id/code, name, status (planned/active/inactive/what-if), planned start, must-finish-by, data date, scheduled finish, default calendar, default activity type, duration type, % complete type, currency, priority, risk level, location, budget fields, project codes and UDFs, check-out state, last-scheduled timestamp. *Logic:* derived fields recalculate on schedule and summarize.
- **D01.04 Programs / shells hierarchy (Unifier)**: configurable containers (company → program → project/shell, plus any custom shell type) that carry business processes, managers and cost sheets. *Data:* shell type, shell instance, parent shell, shell attributes, shell status (Active, On-Hold, View-Only, Inactive), enabled managers. *Logic:* data rolls up through the shell hierarchy; shells are auto-created from a template or from a business process.
- **D01.05 Project and shell templates**: create new projects or shells from a template. *Data:* template project (WBS, activities, codes, BP setups, cost sheet structure, roles, groups). *Logic:* deep copy with id remapping; template changes can be pushed to existing shells (template update/propagation).
- **D01.06 Workspaces and portfolios (Primavera Cloud)**: a hierarchy of workspaces with inherited configuration, plus portfolios that group projects across workspaces. *Data:* workspace (parent, owned codes/UDFs/calendars/currencies), portfolio (static list or filter-based membership). *Logic:* configuration is inherited and can be overridden per child workspace; a dynamic portfolio membership is re-evaluated by its filter.
- **D01.07 Multi-company and partner organizations**: model owner, GC, subcontractors, designers and other organizations on shared projects. *Data:* company/organization, company type, users per organization, project participation (Aconex org-on-project). *Logic:* records are owned by an organization; visibility is controlled across organizations (Aconex: documents are private to an organization until transmitted).
- **D01.08 Locations and geographic data**: physical locations attached to projects, activities, resources and assets. *Data:* location (name, address, lat/long, hierarchy). *Logic:* filtering by location and geo rollups.
- **D01.09 Currencies and exchange rates**: multi-currency storage with a single base currency. *Data:* currency (code, symbol, decimal places), exchange rate to base, effective dates; project and user display currency. *Logic:* values are stored in base currency and converted at the effective rate; Unifier also supports project currency with a rate lock.
- **D01.10 Admin preferences and categories**: global settings and lookup lists. *Data:* hours per time period (day/week/month/year), earned-value defaults, expense categories, document categories, notebook topics, risk types, unit-of-measure list, WBS category, overtime factor, timesheet settings. *Logic:* units↔duration conversions use the configured hours per period.

## D02 Security, Identity and Permissions

- **D02.01 Users and authentication**: user accounts with SSO. *Data:* user (login, name, email, status, language, time zone, global profile, license types), auth mode (native, LDAP, SAML/OIDC through Oracle Identity Cloud/IDCS). *Logic:* password policy, account lockout, session timeout.
- **D02.02 Global security profiles (P6)**: enterprise-wide privileges. *Data:* profile → set of global privileges (edit EPS, admin preferences, edit global codes/UDFs/calendars, resources, roles, cost accounts, import/export, security). *Logic:* a privilege is checked at every global-object mutation; Admin Superuser bypasses checks.
- **D02.03 Project security profiles (P6)**: per-OBS project privileges. *Data:* profile → project privileges (edit WBS, add/delete activities, schedule, level, store baselines, view costs, approve timesheets as PM, edit expenses, edit EPS financials); assignment of user + OBS + profile. *Logic:* effective privilege on a project = union of the profiles of the user's OBS elements that are responsible for the project's EPS/WBS nodes; the Project Superuser profile grants everything.
- **D02.04 Resource security**: limits which resources a user can see or assign. *Data:* user → resource node access (all, none, or a subtree). *Logic:* resource hierarchy filtering applies to assignments, leveling and timesheets.
- **D02.05 Cost-field security**: hide monetary fields. *Data:* privilege flags (view project costs/financials). *Logic:* cost columns are masked in API, report and export output.
- **D02.06 Module access and license types**: entitlement by application module. *Data:* user ↔ module access (P6 Pro, EPPM web, Team Member, Timesheets, Integration API, Visualizer). *Logic:* login and API calls are gated by licensed module and named or concurrent licenses.
- **D02.07 Unifier permissions model**: permissions at company, shell and module level, granted to groups and users. *Data:* group, group membership, permission template, per-module permission (create, view, edit, admin), per-business-process permissions (create, view all, edit, view workflow), user mode/company mode. *Logic:* additive union; permission templates are applied in bulk to shells; access through the shell hierarchy is inherited.
- **D02.08 Workflow-role-based record access**: who can act on a business process record. *Data:* workflow step assignees (users/groups/dynamic), record creator, CC list. *Logic:* record-level access is granted while a user is an assignee, the creator or an "editor"; ownership is dynamic (for example the assignee resolved from a shell attribute or a cost code owner).
- **D02.09 Aconex organization-scoped security**: confidentiality based on organization and role. *Data:* organization, user role (per project), document security (private, shared with roles/users), mail confidentiality flag. *Logic:* documents are visible only to the owning organization until a transmittal or share; mail is visible only to its participants.
- **D02.10 Primavera Cloud permission sets**: configurable permission sets per object type. *Data:* permission set (workspace, project, portfolio, idea, program, resource, cost sheet, risk, field), user/team → object assignment. *Logic:* effective rights are resolved at object level and inherited from the workspace.
- **D02.11 Record-level and field-level access**: fine-grained protection. *Data:* field-level read-only/hidden rules per workflow step (Unifier form step editability), confidential flags. *Logic:* enforced server-side per workflow step.
- **D02.12 Delegation / proxy**: a user delegates tasks while absent. *Data:* proxy (delegator, delegate, start/end, scope). *Logic:* tasks are routed to the delegate, and actions are recorded "on behalf of".
- **D02.13 Audit trail**: immutable change log. *Data:* audit record (table, record id, field, old value, new value, user, timestamp, source program/API), login audit. *Logic:* DB-level triggers (P6 auditing levels 0 to 3) or application events; retention policy and purge.
- **D02.14 Electronic signatures**: signed approvals and documents. *Data:* signature record (user, document hash, timestamp, signer role, certificate/DocuSign envelope id). *Logic:* signature authority checks (Textura signer role), tamper-evident hash, DocuSign/Adobe Sign integration in Unifier.

## D03 WBS and Activities

- **D03.01 Work Breakdown Structure**: a per-project hierarchical deliverable breakdown. *Data:* WBS node (id, parent, code, name, seq, status, responsible OBS, anticipated start/finish, EV technique, WBS category, estimation weight). *Logic:* code path concatenation (Project.WBS.Child); dates, units, costs and EV roll up from activities.
- **D03.02 WBS milestones**: weighted milestones on a WBS node. *Data:* WBS milestone (name, weight, completed flag). *Logic:* WBS % complete = sum of weights of completed milestones / sum of all weights (one of the EV techniques).
- **D03.03 Activity entity**: the unit of work. *Data:* activity id, name, WBS, type (Task Dependent, Resource Dependent, Level of Effort, Start Milestone, Finish Milestone, WBS Summary), duration type (Fixed Duration & Units, Fixed Duration & Units/Time, Fixed Units, Fixed Units/Time), % complete type (Physical, Duration, Units), calendar, status (Not Started, In Progress, Completed), original/remaining/at-completion/actual duration, planned/early/late/actual/remaining start-finish dates, expected finish, suspend/resume dates, primary resource, priority, codes, UDFs, notebook. *Logic:* type-specific scheduling rules (LOE spans its predecessors and successors, WBS Summary spans its WBS children, milestones have zero duration).
- **D03.04 Duration type equation**: keeps Units = Duration × Units/Time consistent. *Logic:* when one variable changes, the duration type determines which of the other two is held fixed and which is recalculated.
- **D03.05 Percent complete types**: three ways to report progress. *Logic:* Duration % = (OD − RD)/OD; Units % = actual units/(actual + remaining units); Physical % = user-entered. The chosen type drives Activity % Complete, and Performance % Complete is used for EV.
- **D03.06 Activity steps**: a checklist of weighted sub-steps inside an activity. *Data:* step (name, seq, weight, % complete, completed flag, step UDFs), activity step templates. *Logic:* when "physical % complete based on steps" is enabled, activity physical % = Σ(weight × step %)/Σweight.
- **D03.07 Activity notebooks and documents**: attach text and references to activities. *Data:* notebook entry (topic, rich text), work product/document links (WP&D, deliverable/reference flag, file or URL).
- **D03.08 Global change**: rule-based bulk updates. *Data:* saved global change spec (if-conditions, then-assignments with expressions). *Logic:* evaluates conditions per row and applies arithmetic or string expressions to fields across activities, assignments, expenses or WBS; offers a preview with commit or rollback.
- **D03.09 Activity ID auto-numbering and renumbering**: *Data:* prefix, suffix, increment. *Logic:* generates sequential ids and bulk-renumbers.
- **D03.10 Expected finish and suspend/resume**: *Logic:* expected finish overrides remaining duration when the schedule option is on; suspend/resume inserts a nonwork gap in an in-progress activity.
- **D03.11 Feedback and activity comments**: team-member status updates. *Data:* feedback text, status-update record pending approval. *Logic:* PM approval workflow for progress updates submitted by team members (P6 Team Member/Progress Reporter).

## D04 Relationships and Constraints

- **D04.01 Activity relationships**: logic links. *Data:* relationship (predecessor, successor, type FS/SS/FF/SF, lag, lag calendar, driving flag, critical flag, free float of link, external flag). *Logic:* forward and backward pass constraints; lag measured on the predecessor, successor, 24-hour or project-default calendar (schedule option).
- **D04.02 External (inter-project) relationships**: links across projects. *Data:* relationship whose ends sit in different projects; when a project opens alone, external early start/late finish dates are stored. *Logic:* stored external dates act as constraints if the "ignore relationships to/from other projects" option is set.
- **D04.03 Primary and secondary constraints**: date constraints. *Data:* constraint type (Start On, Start On or Before, Start On or After, Finish On, Finish On or Before, Finish On or After, Mandatory Start, Mandatory Finish, As Late As Possible), constraint date. *Logic:* soft constraints adjust early or late dates within logic; mandatory constraints override logic and can produce negative float; ALAP uses free float to delay.
- **D04.04 Project must-finish-by**: *Logic:* sets the late finish of open-ended activities for the backward pass; if absent, the latest early finish is used.
- **D04.05 Logic validation**: integrity checks. *Logic:* loop (circular) detection by graph cycle detection during scheduling; open-end detection (no predecessor or no successor); dangling relationships; out-of-sequence progress detection; constraint conflicts.

## D05 Calendars and Time

- **D05.01 Calendar types**: global, project and resource calendars. *Data:* calendar (id, name, type, project owner, base calendar for inheritance, hours per day/week/month/year, default flag). *Logic:* project and resource calendars can inherit holidays and exceptions from a global base.
- **D05.02 Work week and shifts**: standard work week with intervals. *Data:* per weekday a list of work intervals (start/end, 30-minute or finer granularity). *Logic:* work time per day is computed from the intervals.
- **D05.03 Exceptions and holidays**: date-specific overrides. *Data:* exception date (working or nonworking, custom intervals). *Logic:* a date-addition function walks working intervals to convert durations into dates.
- **D05.04 Resource shifts and availability**: resource-specific capacity. *Data:* shift (periods with start hour, limit), resource max units/time effective-dated, calendar. *Logic:* resource availability per period = calendar working hours × max units/time.
- **D05.05 Time units and conversions**: *Logic:* hour, day, week, month conversion uses admin "hours per time period" or the calendar-specific values (user-selectable option); duration is stored in hours.
- **D05.06 Financial periods**: user-defined accounting periods. *Data:* financial period (name, start, end), stored period performance (actual units/costs per period per activity/assignment, past-period actuals). *Logic:* "Store Period Performance" snapshots to-date actuals into the current period; period values can be edited afterward.
- **D05.07 Time zones**: *Data:* user and project time zone (Primavera Cloud), UTC timestamps. *Logic:* date-only versus datetime normalization.

## D06 CPM Scheduling Engine

- **D06.01 Forward pass**: compute early dates. *Logic:* topological traversal from the data date; ES = max(predecessor-driven dates by link type ± lag on the lag calendar, constraint, data date for unstarted work); EF = ES + remaining duration on the activity calendar; in-progress activities start remaining work at the data date.
- **D06.02 Backward pass**: compute late dates. *Logic:* reverse traversal from the project must-finish-by (or latest EF); LF = min(successor-driven), LS = LF − remaining duration.
- **D06.03 Float calculation**: total and free float. *Logic:* Total Float = LF − EF (option: LS − ES, or the smaller of the two); Free Float = min(successor ES) − EF adjusted for link type and lag; float is computed in working time on the activity calendar; negative float is permitted.
- **D06.04 Critical path definition**: *Logic:* critical when total float ≤ a threshold (configurable), or "longest path" (a driving chain traced back from the last activity); a multiple float paths analysis ranks successive paths by total float or free float to an end activity.
- **D06.05 Retained logic versus progress override**: out-of-sequence handling. *Logic:* retained logic schedules the remaining duration after the predecessor finishes; progress override ignores logic for started activities; actual dates also available as an option.
- **D06.06 Schedule options**: engine configuration. *Data:* options per project (ignore external links, make open-ended activities critical, use expected finish, schedule automatically, level when scheduling, calculate start-to-start lag from actual or early start, total-float definition, relationship lag calendar, compute multiple float paths, LOE handling, start-to-start).
- **D06.07 Level of Effort and WBS Summary computation**: *Logic:* LOE dates = span of predecessor start to successor finish, with duration derived; WBS Summary = span of children; neither drives logic.
- **D06.08 Schedule log and validation report**: *Data:* log entries (open ends, constraints, out-of-sequence, loops, statistics). *Logic:* generated per run.
- **D06.09 Multi-project scheduling**: *Logic:* schedules a set of projects together, resolving external links in one network.
- **D06.10 Schedule quality checks (DCMA 14-point style)**: *Logic:* missing logic, leads (negative lag), lags, relationship-type mix, hard constraints, high float (>44 d), negative float, high duration, invalid dates, resources, missed tasks, critical path test, CPLI = (CP length + TF)/CP length, BEI = completed/planned-to-complete.
- **D06.11 What-if and scenarios**: *Data:* what-if project copy or Primavera Cloud scenario (project copy with a diff). *Logic:* copy-on-write, comparison and merge back (Primavera Cloud "Scenarios"; P6 "Update Baseline" and "Restore Baseline").
- **D06.12 Fragnet and TIA support**: insert fragments for delay analysis. *Data:* fragnet (set of activities and relationships), baseline versus impacted snapshots. *Logic:* insert, reschedule, compare finish (time impact analysis).

## D07 Resources, Roles and Assignments

- **D07.01 Resource dictionary**: an enterprise resource hierarchy. *Data:* resource (id, name, parent, type Labor/Nonlabor/Material, unit of measure for material, calendar, default units/time, max units/time effective-dated, price/unit 1..5 effective-dated, overtime allowed + factor, primary role, employee/user link, timesheet approval manager, codes, UDFs, location, currency, auto-compute actuals flag).
- **D07.02 Roles**: skill/job definitions. *Data:* role (id, name, parent, rates 1..5, role limits effective-dated), resource↔role with proficiency 1..5. *Logic:* staffing by role, then fill with a matching resource (search by role + proficiency + availability).
- **D07.03 Resource assignments**: link resources/roles to activities. *Data:* assignment (activity, resource, role, cost account, budgeted/actual/remaining/at-completion units and costs, units/time, rate source (resource, role, override), rate type 1..5, planned/actual/remaining start and finish, lag, remaining duration, curve, drive-activity-dates flag, overtime units, staffed/unstaffed). *Logic:* cost = units × price/unit (effective-dated, time-phased); for resource-dependent activities, assignment dates are driven by the resource calendar.
- **D07.04 Resource curves**: non-linear distribution of units. *Data:* curve (21-point distribution 0..100%). *Logic:* time-phased spreading of units and costs over the assignment duration.
- **D07.05 Manual planning (time-phased future periods)**: *Data:* planned/remaining units per period override (future bucket planning). *Logic:* overrides the curve-based spread.
- **D07.06 Time-phased spreading engine**: *Logic:* spreads units and costs over calendar working time by day/week/month/financial period; serves resource usage profiles, spreadsheets and EV curves; computes histograms of planned/remaining/actual per period.
- **D07.07 Resource teams and pools (Primavera Cloud)**: *Data:* resource team, generic resources, capacity. *Logic:* aggregated demand versus capacity.
- **D07.08 Material and equipment resources**: *Data:* nonlabor/material resource, unit of measure, quantity. *Logic:* cost = quantity × price; reported as consumed quantities.
- **D07.09 Auto-compute actuals**: *Logic:* when progress is entered, actual units/costs = budget × % complete (or planned-to-date), and remaining = at-completion − actual.
- **D07.10 Price/unit and cost-per-use**: *Logic:* effective-dated rate tables; cost-per-use fees (MSP import compatibility).

## D08 Resource Leveling and Capacity Planning

- **D08.01 Resource leveling (serial heuristic)**: resolve over-allocation by delaying activities. *Logic:* serial schedule generation: iterate time periods, for candidate activities sorted by leveling priorities (activity priority, early start, total float, user field, etc.) and check resource availability (max units/time, optionally a threshold %) over the activity window; delay activities to the next feasible slot within float or beyond (configurable "level within float" and "preserve scheduled early and late dates"); honor relationships and calendars; record leveling delay.
- **D08.02 Leveling options**: *Data:* resources to level (all or selected), consider assignments in other projects with priority ≥ N, max float to preserve, over-allocation % allowance, level all or selected, use of role limits. *Logic:* treats cross-project demand as fixed load.
- **D08.03 Remaining early/late dates**: *Logic:* leveling writes remaining early start/finish separately from CPM early dates; leveled dates become the new remaining early dates.
- **D08.04 Resource and role capacity analysis**: *Logic:* demand (sum of time-phased assignment units) versus capacity (max units/time × calendar hours) by period; over/under allocation by resource, role and code; aggregated across projects.
- **D08.05 Resource planning portfolio scenarios**: long-range demand at the portfolio level. *Data:* resource plan (role or resource demand by period per project, not tied to activities), scenario. *Logic:* compare demand to capacity across scenarios; commit a plan to the project.
- **D08.06 Resource allocation requests**: *Data:* resource request (role, skill, period, units), status. *Logic:* request → resource manager review → booked or rejected (Unifier Resource Booking BP; P6 staffing).
- **D08.07 Resource leveling logs**: *Data:* log of delayed activities, unresolved conflicts.

## D09 Codes, User-Defined Fields and Classification

- **D09.01 Project codes**: hierarchical classification of projects. *Data:* code type (global/EPS), code value (value, description, parent, color/weight), project↔value. *Logic:* grouping, filtering and portfolio rollups.
- **D09.02 Activity codes**: global, EPS-level or project-level code types. *Data:* code type scope, values hierarchy, activity↔value (one value per type per activity). *Logic:* grouping/summarization and global change.
- **D09.03 Resource, role and assignment codes**: *Data:* code types and values, assignments.
- **D09.04 User-defined fields (UDFs)**: custom fields by subject area. *Data:* UDF definition (subject area: activity, WBS, project, resource, assignment, expense, step, risk, issue, etc.; data type text, start/finish date, cost, integer, number, indicator, code); UDF values. *Logic:* formula UDFs (calculated from other fields), indicator thresholds (traffic light by value range), summary aggregation (sum, min, max, average) to WBS and project.
- **D09.05 Unifier data elements and data definitions**: metadata-driven fields. *Data:* data definition (type, size, picklist, data set), data element (label, DD), form design per BP, upper (header) and detail (line item) forms. *Logic:* formula fields, auto-populate across BPs (reference and query-based), dynamic data sets (dependent picklists).
- **D09.06 Cost codes / CBS**: *Data:* CBS code hierarchy (segments, delimiter), CBS attributes (cost type, owner, item description). *Logic:* rollups by segment and rollup of sheet columns.
- **D09.07 Industry classification standards**: *Data:* CSI MasterFormat, UniFormat II, OmniClass code libraries, used for cost codes, specs and asset classes. *Logic:* mapping tables between standards.

## D10 Baselines, Progress and Updating

- **D10.01 Baseline storage**: snapshot copies of the project. *Data:* baseline project (full copy: activities, assignments, relationships, costs), baseline type, date stored; up to N baselines per project; assigned primary/secondary/tertiary project baseline plus user baselines. *Logic:* copy-on-save; variance fields compare current against the baseline (start variance, finish variance, duration variance, cost variance).
- **D10.02 Update baseline**: refresh a baseline with selected changes. *Logic:* merge from current project, with options per data type (add new activities, delete, update fields).
- **D10.03 Baseline restore and comparison**: *Logic:* activity-by-activity diff (added, deleted, changed fields; Claim Digger-style comparison report).
- **D10.04 Progress update workflow**: periodic status. *Data:* data date, actual start/finish, remaining duration, % complete, actual units/costs, expected finish. *Logic:* move data date → apply actuals → reschedule; "Apply Actuals" uses timesheet hours; "Update Progress" auto-statuses activities as if they went exactly as planned through the new data date.
- **D10.05 Progress spotlight and look-ahead**: *Logic:* selects activities that should have started or finished between the old and new data date.
- **D10.06 Period-based progress history**: *Data:* period performance records, schedule snapshots per update period (Primavera Cloud "Schedule history"). *Logic:* trend analysis (finish date drift, float erosion).
- **D10.07 Planned % complete / schedule % complete**: *Logic:* schedule % = elapsed planned duration to data date / planned duration (against baseline); Primavera Cloud computes planned % complete automatically.
- **D10.08 Project check-in/check-out**: offline editing. *Data:* checkout user, date, lock state. *Logic:* exclusive lock, then a merge/import on check-in (XML).

## D11 Earned Value and Performance Measurement

- **D11.01 EV fields**: *Data:* Planned Value (BCWS), Earned Value (BCWP), Actual Cost (ACWP), Budget at Completion (BAC), Estimate at Completion (EAC), Estimate to Complete (ETC), Variance at Completion (VAC), SV, CV, SPI, CPI, TCPI. *Logic:* PV = baseline budget × baseline schedule % at data date; EV = BAC × performance % complete; SV = EV − PV; CV = EV − AC; SPI = EV/PV; CPI = EV/AC; VAC = BAC − EAC; TCPI = (BAC − EV)/(BAC − AC) or against EAC.
- **D11.02 Performance % complete techniques**: per WBS EV setting. *Data:* technique (Activity % complete, 0/100, 50/50, custom percent X/Y, WBS milestones % complete, activity % complete using resource curves). *Logic:* computes performance % used for EV; values set at WBS level with an admin default.
- **D11.03 ETC/EAC techniques**: *Data:* ETC technique (ETC = remaining cost for activity, PF = 1, PF = custom, PF = 1/CPI, PF = 1/(CPI × SPI)). *Logic:* EAC = AC + ETC; ETC = (BAC − EV) × PF.
- **D11.04 EV rollups**: *Logic:* sums EV, PV and AC from assignments to activity, WBS, project and EPS; ratios are recomputed from sums, not averaged.
- **D11.05 Time-phased EV curves (S-curves)**: *Logic:* cumulative PV, EV and AC per period from the time-phased spread and stored period performance; earned schedule (ES) metrics: SPI(t) = ES/AT.
- **D11.06 Baseline selection for EV**: *Logic:* PV based on the project baseline or user baseline; "earned value calculation" option (budget at completion with current dates, planned values with planned dates, or with current dates).
- **D11.07 Labor/nonlabor/material splits**: *Data:* cost and unit fields per resource type. *Logic:* separate EV metrics for labor units versus cost.
- **D11.08 ANSI-748 compliance support**: *Data:* control accounts (WBS + OBS intersection), work packages, planning packages, management reserve, undistributed budget. *Logic:* budget logs (baseline change control), variance analysis reports with thresholds and explanations.

## D12 Project Monitoring: Thresholds, Issues, Work Products and Notifications

- **D12.01 Project thresholds**: rule-based monitoring. *Data:* threshold (parameter such as Start Date Variance, Total Float, CV, CPI, SPI, Cost % of budget, Duration % of original; lower and upper limits; WBS scope; tracking layout; responsible manager; status enabled/disabled; monitoring period). *Logic:* evaluated by the threshold monitor job; a breach generates an issue.
- **D12.02 Project issues**: tracked problems. *Data:* issue (name, priority, status Open/On Hold/Closed, responsible manager OBS, WBS/activity/resource link, identified-by, date identified, resolution date, history notes, threshold link, UDFs). *Logic:* lifecycle state machine and email notifications to the responsible manager.
- **D12.03 Work products and documents (WP&D)**: *Data:* document (title, version, author, status, reference/deliverable flag, private/public location, file), assignment to activities and WBS, document status list. *Logic:* review status lifecycle (Content Repository integration with check-in/out).
- **D12.04 Notifications engine**: *Data:* notification rule (event, recipient resolution, channel email/in-app/push, frequency immediate/daily/weekly digest). *Logic:* event bus → template rendering → delivery; per-user subscriptions.
- **D12.05 Status reporting / project status**: *Data:* status report (period, overall health RAG, narrative, KPIs snapshot). *Logic:* periodic snapshot of computed metrics.
- **D12.06 Change and decision logs (Primavera Cloud project logs)**: *Data:* log type, entries, owner, status.

## D13 Project Expenses and P6 Cost Management

- **D13.01 Expenses**: non-resource costs on activities. *Data:* expense item (activity, cost account, expense category, vendor, document number, budgeted/actual/remaining/at-completion cost, price/unit, units, unit of measure, accrual type (start, end, uniform), auto-compute actuals flag, PO number). *Logic:* time-phased accrual per accrual type; contributes to activity total cost.
- **D13.02 Cost accounts**: hierarchical cost accounts. *Data:* cost account (id, name, parent). *Logic:* cost rollups by account across assignments and expenses; default cost account per project.
- **D13.03 Project budget and budget change log**: *Data:* original budget, proposed budget, current budget (computed), budget changes (number, date, amount, responsible, status Proposed/Approved/Not Approved, reason), monthly spending plan, benefit plan, funding sources. *Logic:* current budget = original + approved changes; distributed versus undistributed variance; spending plan tally against the cost loaded schedule.
- **D13.04 Funding sources (P6)**: *Data:* funding source (hierarchy), project funding (amount, fund share %). *Logic:* allocation across funding sources.
- **D13.05 Cost totals per activity**: *Logic:* total cost = Σ labor + nonlabor + material + expenses (budgeted, actual, remaining, at-completion); actual this period.
- **D13.06 Summarization service**: precomputed rollups. *Data:* summary tables by EPS, project, WBS, resource, role, period (SUM* tables). *Logic:* a scheduled job aggregates spread data to summary tables for reporting performance.

## D14 Risk Management

- **D14.01 Risk register**: identified threats and opportunities. *Data:* risk (id, name, type threat/opportunity, category (RBS hierarchy), status (Proposed, Open, Active, Managed, Impacted, Closed, Rejected), owner, cause, effect, description, identified date, trigger, exposure start/finish, linked activities and WBS, response strategy, UDFs).
- **D14.02 Probability-impact scoring**: qualitative assessment. *Data:* probability-impact matrix (PxI scale 3x3..5x5 or custom), probability levels (range %), impact levels per category (schedule days or %, cost amount or %, performance, quality, safety, reputation), score thresholds (low/medium/high). *Logic:* risk score = P × max impact (or matrix lookup); pre-response versus post-response scoring.
- **D14.03 Risk responses**: mitigation plans. *Data:* response plan (strategy avoid/transfer/reduce/accept for threats, exploit/share/enhance/accept for opportunities), response actions (title, owner, cost, start/finish, status, linked activity). *Logic:* response cost added to the budget; post-response probability/impact used in analysis.
- **D14.04 Quantitative risk analysis (Monte Carlo)**: schedule and cost simulation. *Data:* uncertainty per activity (min/most likely/max duration, distribution type triangular, BetaPERT, uniform, normal, lognormal, trigen), cost uncertainty, risk-to-activity impact mapping (probability, schedule impact, cost impact), correlations, iteration count, seed. *Logic:* for each iteration sample durations (Latin hypercube or random), sample risk occurrence (Bernoulli with probability p) and add its impact to linked activities, run a CPM forward pass, record finish dates and costs; outputs are P-values (P10/P50/P80/P90) for finish date and cost, histogram/CDF distributions, criticality index (% of iterations where the activity is critical), duration sensitivity (Spearman rank correlation/tornado), cruciality, and joint confidence level (JCL scatter of cost versus date).
- **D14.05 Schedule risk templates and uncertainty templates**: *Data:* reusable estimate ranges by activity code (for example −10%/+25%). *Logic:* bulk apply to activities.
- **D14.06 Risk scoring rollup and exposure**: *Logic:* expected monetary value EMV = probability × impact; aggregated exposure by WBS/project/portfolio; risk heat map counts.
- **D14.07 Contingency determination**: *Logic:* contingency = P80 cost − deterministic cost (or another target confidence); schedule contingency = P-date − deterministic finish.
- **D14.08 Schedule health check prior to QRA**: *Logic:* open ends, constraints, lags and missing logic flagged as risky for simulation.
- **D14.09 Risk register data exchange**: *Logic:* import from Primavera Risk Analysis (.plan / XML), P6 XML risks, Excel.

## D15 Portfolio and Capital Planning

- **D15.01 Ideas and project proposals**: capture new investment requests. *Data:* idea (title, description, sponsor, workspace, proposed cost, benefit, scores, status (Draft, Submitted, Under Review, Approved, Rejected, Converted)). *Logic:* evaluation workflow, then conversion into a project (template-based).
- **D15.02 Scoring and prioritization**: *Data:* scoring criteria (weights, scales), scores per project. *Logic:* weighted score = Σ(weight × normalized score); ranking; efficient frontier (value versus cost).
- **D15.03 Capital plans**: multi-year budget planning. *Data:* capital plan (plan period, fiscal year start, planning horizon), plan line items per project (planned budget per year/period, funding source, priority, status included/excluded). *Logic:* time-phased budget spreads, totals versus targets.
- **D15.04 Portfolio scenarios and what-if analysis**: *Data:* scenario (included projects, shifted start dates, budget overrides). *Logic:* compare scenario totals against budget targets and resource capacity; constraint optimization (fit within budget per year, maximize score: knapsack-style selection); approve scenario → commit plan.
- **D15.05 Portfolio budget planning and approvals**: *Data:* budget plan, budget requests, approvals per period. *Logic:* approval workflow; approved amount pushed to the project budget (original budget).
- **D15.06 Portfolio measures / KPIs**: *Data:* measure definitions (formula on project fields), measure snapshots per period, targets. *Logic:* scheduled calculation and history.
- **D15.07 Programs**: groups of related projects. *Data:* program, member projects, program budget. *Logic:* program-level rollups of cost, schedule and risk.
- **D15.08 Benefits tracking**: *Data:* planned versus actual benefit per period. *Logic:* ROI, NPV, IRR, payback period calculations on cost and benefit streams.
- **D15.09 Unifier capital planning sheets**: *Data:* capital planning sheet (projects × fiscal years), planning items, planning BP. *Logic:* roll planning items into a capital program; auto-create shells from approved items.

## D16 Task and Lean Planning (Last Planner)

- **D16.01 Work plan tasks**: field-level tasks under schedule activities. *Data:* task (name, activity link, company/trade, owner, start, due date, proposed due date, duration, crew size, location, status (Not Started, In Progress, Committed, Completed, Blocked), task type), checklists. *Logic:* task dates are bounded by the parent activity; completion feeds activity % complete (optional).
- **D16.02 Look-ahead planning**: *Data:* look-ahead window (configurable weeks). *Logic:* surfaces tasks and activities within window; make-ready process.
- **D16.03 Constraints register**: blockers to tasks. *Data:* constraint (type: RFI, submittal, material, labor, equipment, permit, predecessor, design; owner, need date, status open/closed, linked task). *Logic:* a task becomes "ready" only when all constraints are closed; aging and reminders.
- **D16.04 Weekly commitments**: *Data:* commitment (task, week, committer, committed date). *Logic:* lock commitments at the weekly meeting.
- **D16.05 Percent Plan Complete (PPC)**: *Logic:* PPC = completed commitments / total commitments per week, by company and project; trend.
- **D16.06 Variance / reasons for non-completion**: *Data:* reason code list (weather, labor, prerequisite work, materials, design info, etc.). *Logic:* Pareto analysis of missed commitments.
- **D16.07 Pull planning / phase planning**: *Data:* milestones, handoffs between trades, sticky-note tasks with dependencies. *Logic:* backward planning from a milestone; conversion into activities.
- **D16.08 Takt planning (optional)**: *Data:* zones, takt time, train of trades. *Logic:* zone × wagon sequencing.
- **D16.09 Task notifications**: *Logic:* alerts on proposed due date or overdue; immediate/daily/weekly frequency.

## D17 Cost Controls: CBS, Budget, Cost Sheet and Forecast

- **D17.01 Project cost sheet**: matrix of CBS rows × configurable columns. *Data:* cost sheet (CBS rows), columns (data source: BP by status, e.g. Budget Approved, Commitments Pending/Approved, Changes, Spends; formula columns; manual entry columns; manager sheet links). *Logic:* columns auto-recompute from BP line items on status transitions; formulas such as Revised Budget = Original + Approved Budget Changes; Exposure = Pending; Forecast at Completion = Revised Commitment + Pending + Forecast Remaining.
- **D17.02 Company cost sheet rollup**: *Logic:* aggregates project cost sheets into company and program level by CBS or shell attributes.
- **D17.03 Original budget and budget distribution**: *Data:* budget BP line items (CBS, amount, distribution profile). *Logic:* distribute budget over time by curve (linear, bell, back-loaded, front-loaded, S-curve, manual) for cash flow.
- **D17.04 Budget transfers and budget changes**: *Data:* budget transfer BP (from CBS, to CBS, amount), budget change BP. *Logic:* zero-sum transfer validation; approval updates revised budget.
- **D17.05 Cost rules (validation)**: *Data:* rule (column A op column B, e.g. Revised Budget ≥ Approved Commitments; Invoice ≤ Approved PO; Pay App ≤ Contract + Change Orders; Budget > 0). *Logic:* evaluated when a BP moves to a status that triggers the rule, on manual load, via web services and auto-creation; hard block versus warning.
- **D17.06 Forecasting**: *Data:* forecast BP or forecast sheet (ETC by CBS by period). *Logic:* EAC = actuals to date + ETC; Forecast variance = Revised Budget − EAC; periodic forecast snapshots.
- **D17.07 Work packages**: *Data:* work package (subset of CBS, own budget). *Logic:* rollup of costs into packages and alternate views of the cost sheet.
- **D17.08 Worksheets**: ad hoc calculation sheets linked to cost sheet. *Data:* worksheet rows, columns, formulas. *Logic:* feed values back to cost sheet columns.
- **D17.09 Cost snapshots**: *Data:* snapshot of cost sheet at a point in time. *Logic:* period comparison and trend.
- **D17.10 Generic cost sheets (shells without CBS)**: *Logic:* summary rollups for program shells.
- **D17.11 Estimating linkage**: *Data:* estimate import (line items, quantities, unit costs, CBS mapping). *Logic:* estimate → original budget conversion.
- **D17.12 Actuals from ERP**: *Data:* actual cost transactions (cost code, amount, date, vendor, invoice ref). *Logic:* import and posting to the Spends column, reconciled against invoices.

## D18 Funding Management

- **D18.01 Fund codes and fund sheet**: *Data:* fund code (source, type: grant, bond, equity, loan; restrictions), company fund sheet (appropriated, allocated, consumed). *Logic:* allocation from company funds to projects.
- **D18.02 Project funding allocation**: *Data:* funding BP (fund code, CBS, amount). *Logic:* manual or automatic allocation to CBS by rule.
- **D18.03 Fund consumption**: *Logic:* when spends (invoices, payments) are approved, consume funds by priority (fund waterfall: consume fund A until exhausted, then B) or by ratio; unfunded amount tracking.
- **D18.04 Funding commitments**: *Logic:* reserve funds at commitment approval (encumbrance), release at payment.

## D19 Commitments and Contracts

- **D19.01 Base commitments**: subcontracts and purchase orders. *Data:* commitment (number, vendor, type, title, contract value, CBS line items, SOV lines, retainage %, start/finish, insurance, bonds, status (Draft, Pending, Approved, Closed, Terminated)). *Logic:* approval posts to Commitments Approved column; cost rule checks against budget.
- **D19.02 Commitment summaries**: *Data:* commitment summary (base + all change orders + invoices + payments + retainage held/released). *Logic:* Revised Commitment = Base + Approved Change Orders; Remaining = Revised − Invoiced; % billed.
- **D19.03 Purchase orders and PO amendments**: *Data:* PO, amendment line items, receipts. *Logic:* three-way match PO vs receipt vs invoice.
- **D19.04 Contract administration**: *Data:* contract clause library, key dates, milestones, notice periods, warranties, insurance certificates (with expiry), bonds. *Logic:* deadline reminders; contractual time-bar notices (e.g. NEC early warnings and compensation events with deadlines).
- **D19.05 Owner/prime contracts (revenue side)**: *Data:* prime contract, owner change orders, owner invoicing. *Logic:* margin = revenue − cost commitments.
- **D19.06 Contract types and pricing**: *Data:* lump sum, unit price (quantity × rate SOV lines), cost-plus (cost + fee %, GMP cap), T&M (rates). *Logic:* billing calculations per type; GMP savings share.
- **D19.07 Bid / procurement (RFB)**: *Data:* request for bid (bid package, invited vendors, bid items, due date, addenda), bid responses (line prices, qualifications), bid leveling sheet. *Logic:* bid comparison and normalization, award → auto-create commitment; Aconex Tenders with sealed bids (opened after closing time).

## D20 Change Management

- **D20.01 Change events / potential change orders**: track potential cost or schedule impacts. *Data:* change event (number, title, cause (owner request, design error, unforeseen condition, value engineering), scope, origin link (RFI, field issue), estimated cost per CBS, schedule impact days, status (Open, Pending, Approved, Rejected, Void)). *Logic:* exposure posted to Pending Changes column; roll into change orders.
- **D20.02 Change requests / proposals (PCO/COR)**: *Data:* request (vendor quote, markups, line items). *Logic:* markup calculation (overhead %, profit %, bond %, insurance %, tax compound or simple per contract rules).
- **D20.03 Change orders (commitment side)**: *Data:* CO (commitment ref, line items CBS/SOV, amount, days added). *Logic:* approval updates commitment value and cost sheet; adjusts SOV; rule Revised Budget ≥ Commitments.
- **D20.04 Owner change orders (revenue side)**: *Logic:* bundling PCOs into owner CO; billing via SOV.
- **D20.05 Trend management**: *Data:* trend items (early warnings of cost change). *Logic:* forecast adjustments before formal change.
- **D20.06 Schedule impact linkage**: *Logic:* change event linked to activities/fragnets; impact analysis via TIA in P6/Primavera Cloud.
- **D20.07 Change order log and aging**: *Logic:* aging days in status, approval cycle time, cumulative change % of contract.
- **D20.08 Allowance and contingency drawdown**: *Data:* contingency line, allowance line. *Logic:* transfers from contingency upon change approval; remaining contingency tracking.

## D21 Invoicing, Schedule of Values and Spends (Unifier)

- **D21.01 Schedule of Values (SOV) sheets**: *Data:* SOV lines (description, CBS, scheduled value, from contract and COs), two types: Payment Application SOV and General Spends SOV. *Logic:* SOV auto-built from contract and change order BPs.
- **D21.02 Payment applications (pay apps)**: *Data:* pay app (period, line items: previous work completed, this period, materials stored, total completed, % complete, balance to finish, retainage). *Logic:* AIA G702/G703 arithmetic; ≤ contract + approved COs rule; retainage computed per line or overall.
- **D21.03 Invoices and general spends**: *Data:* invoice (vendor, PO ref, lines, tax, amount). *Logic:* ≤ approved PO rule; posts to Spends.
- **D21.04 Payments**: *Data:* payment (invoice/pay app ref, amount, check/ACH number, date). *Logic:* paid-to-date, outstanding payable.
- **D21.05 Retainage tracking (Unifier)**: *Data:* retainage %, held, released amounts. *Logic:* retention held = Σ completed × %; retainage release BP.
- **D21.06 Payment-to-ERP**: *Logic:* approved invoice → AP in ERP; payment status back.

## D22 Cash Flow

- **D22.01 Cash flow curves**: *Data:* cash flow detail (CBS or summary level), curves: Baseline, Revised baseline, Spends/Actuals, Forecast, Commitments, Payments; period structure (month/quarter/year, fiscal calendar). *Logic:* time-phased amounts per period with cumulative and period views.
- **D22.02 Distribution profiles**: *Data:* profile (linear, bell, front-loaded, back-loaded, S-curve, custom percentages), start/end. *Logic:* spread amount across periods by profile; mixed profiles per CBS.
- **D22.03 Schedule-driven cash flow**: *Logic:* spread from P6/Primavera Cloud activity cost-loaded time-phased data (linked via CBS mapping) to cash flow.
- **D22.04 Forecast curve and auto-forecast**: *Logic:* Forecast = actuals to date + remaining spread of (EAC − actuals) by profile through forecast finish; reforecast by snapshot.
- **D22.05 Cash flow rollups**: *Logic:* aggregate project curves to program/company; filter by CBS/shell attribute.
- **D22.06 Cash flow snapshots and variance**: *Logic:* compare baseline vs forecast vs actual per period.
- **D22.07 Commitment-level cash flow**: *Logic:* per contract spread of committed value; retention release at end.

## D23 Payment Management (Textura-class)

- **D23.01 Project setup and payment structure**: *Data:* project (owner, GC, contract value, billing period, draw schedule), contracts tree (prime → subcontractor → sub-tier), budget/SOV per contract. *Logic:* tiered contract hierarchy; sub-tier billings roll up into sub draws.
- **D23.02 Draws (billing periods)**: *Data:* draw (number, period end, due dates for sub invoices, GC review, owner approval, payment). *Logic:* draw lifecycle: Open → Subs invoicing → GC review → Owner/lender approval → Funded → Paid → Closed; calendar of deadlines.
- **D23.03 Subcontractor invoices / pay requests**: *Data:* invoice (SOV lines: % complete or amount this period, stored materials, sub-tier payments, invoice number). *Logic:* auto-calc dollars from % complete × scheduled value; validation against remaining balance; billing for progress vs retention-only.
- **D23.04 Retention (retainage) management**: *Data:* retention % per contract/line, variable retention schedule (e.g. 10% until 50% complete then 5%), retention held to date, retention released. *Logic:* held = rate × work completed (including or excluding stored materials per rule); reduce rate at threshold; retention release request (Retention tab only when draw allows retention billing); final release at substantial completion.
- **D23.05 Lien waivers**: *Data:* waiver (type: conditional/unconditional, progress/final; state-statutory form templates; amount; through date; signer; sub-tier). *Logic:* auto-generate waiver amounts from approved payment; electronic signature; payment hold until waivers received; sub-tier must be included in a draw before requesting its waiver.
- **D23.06 Compliance documents**: *Data:* compliance requirement (insurance COI with expiry, W-9, licenses, certified payroll, bond), status per contract. *Logic:* deficient compliance → automatic payment hold/block and notifications; expiry tracking.
- **D23.07 Review and approval routing**: *Data:* reviewer roles (PM, project accountant, owner rep, lender, architect), approvals, rejections with comments. *Logic:* multi-step approval; rejection returns invoice to sub for revision; GC can adjust lines (approved amount vs requested).
- **D23.08 Owner/GC pay application assembly**: *Logic:* aggregate approved sub invoices plus GC's own costs into prime AIA G702/G703; compute GC fee, general conditions, insurance, retention.
- **D23.09 Electronic payments and disbursement**: *Data:* bank accounts, payment instructions, ACH transactions, joint checks. *Logic:* release payment only after approvals, waivers and compliance; funds flow owner → GC → subs; payment status tracking.
- **D23.10 Change orders in payment management**: *Data:* contract change orders (approved CO amounts added to SOV). *Logic:* SOV revision versioning.
- **D23.11 Signatures and audit**: *Logic:* e-signature on invoices and waivers by authorized signers; audit trail of user actions and documents; invoice number required before signature.
- **D23.12 ERP/accounting integration**: *Logic:* import contracts/budgets/COs from ERP; export approved invoices to AP; sync payment status (Textura connectors to Oracle, Viewpoint, CMiC, Sage etc.).
- **D23.13 Fees and billing of platform usage**: *Data:* fee schedule by contract value. *Logic:* per-contract fee calculation.

## D24 Business Process and Workflow Engine

- **D24.01 Business process (BP) definitions**: metadata-defined record types. *Data:* BP type (Simple, Line Item, Cost (with CBS/fund/asset code variants), Document, Text, Request for Bid, Resource Booking, Timesheet, Auto-create Shell/Project), upper form, detail line item forms, statuses, record number sequence. *Logic:* deploy BP configuration from uDesigner (design → deploy to production, versioned).
- **D24.02 Workflow schemas**: state machine graphs. *Data:* workflow (steps, links/actions (Approve, Reject, Revise, Send for Review), step assignees, conditions, due-date durations, end step and terminal statuses), workflow setup per shell. *Logic:* conditional routing (by field value, e.g. amount > threshold → executive step), parallel review with consensus (all, any, majority), sub-workflows, record status set on transition.
- **D24.03 Non-workflow BPs**: *Logic:* status-based lifecycle without routing.
- **D24.04 Tasks, due dates and escalation**: *Data:* task (step, assignee, due date, accepted). *Logic:* SLA timers; reminders; escalation; auto-advance on timeout.
- **D24.05 Auto-creation and linking**: *Logic:* auto-create downstream records on status (e.g. approved change event → draft change order; approved bid → contract); reference pickers; auto-populate fields; query-based field integration.
- **D24.06 Record numbering**: *Logic:* configurable sequence with prefix tokens (shell number, year), unique per shell.
- **D24.07 Comments, attachments and markups**: *Data:* general comments, attachment references, markup layers on attached documents. *Logic:* versioned markups per reviewer.
- **D24.08 Bulk actions and integration on BPs**: *Logic:* bulk create via CSV/web services; BP-level integration interface (create, update, getrecord, workflow action).
- **D24.09 Aconex workflows (document review)**: *Data:* workflow template (steps, reviewers, durations, step outcomes: Reviewed, Reviewed with comments, Rejected, Approved), workflow instance per document revision. *Logic:* sequential/parallel steps, final outcome determination, overdue tracking, auto-transmit on completion.
- **D24.10 Formula and validation engine**: *Logic:* expression evaluation for formula fields, date arithmetic, conditional required fields.

## D25 Document Management

- **D25.01 Document register**: *Data:* document (number, title, revision, version, type, discipline, status (e.g. For Information, For Review, For Construction, As-Built), category, author org, date, file (format, size, hash), confidentiality, custom metadata fields). *Logic:* metadata validation per project schema; number uniqueness per org.
- **D25.02 Revisions and supersede**: *Logic:* new revision supersedes previous; revision sequence rules (A, B, C → 0, 1, 2); version history immutable; current vs superseded flags.
- **D25.03 Folder structures (Unifier DM)**: *Data:* folder hierarchy (project and company documents), folder templates, folder permissions. *Logic:* inherited permissions; check-in/check-out locking.
- **D25.04 Bulk upload with metadata**: *Logic:* bulk import via spreadsheet metadata + files; validation errors report.
- **D25.05 Document search and indexing**: *Logic:* full-text indexing (OCR on PDFs), metadata search; saved searches.
- **D25.06 Markups and redlines**: *Data:* markup sessions per document version (annotations, user, timestamp). *Logic:* merge view of multiple markups; markups persisted as overlays.
- **D25.07 Drawing management and sheets**: *Data:* drawing sheet number, discipline, sheet title (OCR-extracted), sets. *Logic:* automatic sheet splitting and hyperlinking between sheets.
- **D25.08 Document distribution and access**: *Logic:* sharing outside org through transmittals; temporary links; download audit.
- **D25.09 Document retention, archive and handover**: *Data:* retention policy, archive packages. *Logic:* project archive export (Aconex "Project Completion" archive with documents + mail + metadata).
- **D25.10 Document control approval states**: *Logic:* status changes gated by workflow outcome; "approved for construction" only after review completion.
- **D25.11 File storage service**: *Logic:* object storage, virus scanning, thumbnails, file conversion (PDF rendering), checksum deduplication.

## D26 Correspondence and Transmittals

- **D26.01 Mail / correspondence**: formal project communication. *Data:* mail (number per org type, type (letter, RFI, transmittal, site instruction, notice, etc.), subject, from, to/cc, body, attachments (documents by revision, files), reference to other mail, status, response required + due date, confidential flag, mail templates). *Logic:* thread tracking (reply, forward), unique sequential numbering per mail type per org.
- **D26.02 Transmittals**: formal document issue. *Data:* transmittal (number, recipients, reason for issue, document revisions included, response required by, acknowledgement status). *Logic:* sending grants recipient org access to those revisions; receipt acknowledgment; overdue response tracking.
- **D26.03 Mail types and custom fields**: *Data:* mail type configuration (fields, numbering, response rules). *Logic:* configurable per project.
- **D26.04 Response tracking**: *Logic:* response required → due date → outstanding/overdue status; "awaiting response" registers.
- **D26.05 Meeting minutes**: *Data:* meeting (date, attendees, agenda items, action items with owner/due). *Logic:* carry-forward of open items to next meeting.
- **D26.06 Email ingestion**: *Logic:* inbound email to project address → correspondence record; outbound notifications.

## D27 RFIs and Submittals

- **D27.01 RFIs**: *Data:* RFI (number, subject, question, discipline, spec section, drawing refs, location, priority, cost impact flag, schedule impact flag, ball-in-court, due date, official response, status (Draft, Open, Answered, Closed, Void)). *Logic:* routing to design team; response → closes; aging; link to change events.
- **D27.02 Submittal register**: *Data:* submittal (number, spec section (CSI), type (shop drawing, product data, sample, O&M, warranty), package, required on-site date, lead time, review durations). *Logic:* back-calculated "submit by" date = required on-site − lead time − review time; schedule activity link.
- **D27.03 Submittal review workflow**: *Logic:* sub → GC review → architect/engineer review → return with code (A: No Exceptions Taken, B: Make Corrections Noted, C: Revise and Resubmit, D: Rejected); resubmission creates a new revision; ball-in-court tracking.
- **D27.04 Submittal packages and specifications**: *Data:* spec sections parsed from spec book. *Logic:* auto-generate register from specifications.
- **D27.05 Field issues → RFIs linkage**: *Logic:* create RFI from field issue; back-links.
- **D27.06 Design review / comment resolution**: *Data:* comment (reviewer, discipline, document, resolution, status). *Logic:* comment closeout matrix.

## D28 Field: Daily Logs and Site Diaries

- **D28.01 Daily reports**: *Data:* daily log (date, project, author, weather (temp, precipitation, wind; auto-fetched), manpower (company, trade, headcount, hours), equipment (type, hours, idle), deliveries, visitors, work performed by activity/location, delays, notes, photos). *Logic:* one log per day per company; approval/lock; aggregate manpower trends.
- **D28.02 Field progress quantities**: *Data:* installed quantities per activity/cost code, unit. *Logic:* % complete = installed/budget quantity; feeds schedule progress and EV.
- **D28.03 Photos and media**: *Data:* photo (geotag, timestamp, location, linked record). *Logic:* EXIF extraction; location pin on drawing.
- **D28.04 Field issues / observations**: *Data:* issue (type, location (drawing pin coordinates), assignee org, due date, status (Open, Ready for Inspection, Closed), photos). *Logic:* assign → fix → verify → close.
- **D28.05 Forms and checklists engine**: *Data:* form template (sections, questions, answer types, scoring), form instance. *Logic:* conditional questions; auto-create issue on failed item.
- **D28.06 Offline mobile sync**: *Logic:* conflict resolution (last-write-wins per field or record versioning), queued uploads.
- **D28.07 Timecards / crew time**: *Data:* crew, worker, hours by cost code, activity. *Logic:* labor actuals feed cost and resource actuals.

## D29 Quality: Punch Lists, Inspections and NCRs

- **D29.01 Punch lists**: *Data:* punch item (location, description, trade/assignee, due date, priority, photos, status (Open, Work Completed, Verified/Closed, Rejected)). *Logic:* sub marks complete → GC verifies; aging; completion % per area.
- **D29.02 Inspections and test plans (ITP)**: *Data:* inspection type, checklist, hold/witness points, inspector, result (pass/fail/NA), signatures. *Logic:* failed item generates deficiency; hold points block progress.
- **D29.03 Non-conformance reports (NCR)**: *Data:* NCR (description, cause, disposition (use as is, repair, rework, reject), corrective/preventive action). *Logic:* workflow raise → disposition → verify → close.
- **D29.04 Commissioning and handover**: *Data:* systems, components, checklists (pre-functional, functional), O&M documents, warranties. *Logic:* completion tracking per system; handover package compilation to facility (Aconex Handover).
- **D29.05 Quality KPIs**: *Logic:* first-time pass rate, defects per area, closure time.

## D30 Safety (HSE)

- **D30.01 Safety observations**: *Data:* observation (type safe/unsafe, category, location, company, photos, severity). *Logic:* trending; leading indicators.
- **D30.02 Incidents**: *Data:* incident (type: injury, near miss, property damage, environmental; date/time, persons, body part, OSHA recordable flag, days away, root cause, corrective actions). *Logic:* investigation workflow; OSHA 300/300A logs; TRIR = recordables × 200,000 / hours worked; LTIR, DART.
- **D30.03 Toolbox talks and training**: *Data:* talk (topic, attendees, signatures), worker certifications with expiry. *Logic:* expiry alerts; site access eligibility.
- **D30.04 Safety inspections and permits to work**: *Data:* permit (hot work, confined space, excavation), validity, approvals. *Logic:* permit state machine (Requested → Approved → Active → Closed).
- **D30.05 Job hazard analysis (JHA)**: *Data:* tasks, hazards, controls. *Logic:* risk rating.

## D31 Asset and Facilities Management (Unifier)

- **D31.01 Asset manager**: *Data:* asset (code, class, category, location, parent asset, acquisition cost, in-service date, useful life, salvage value, status, specs attributes). *Logic:* depreciation (straight line, double declining, sum-of-years-digits, manual) schedules.
- **D31.02 Space manager**: *Data:* building, level, space (area, type, occupancy, department), CAD/BIM references. *Logic:* space utilization, chargeback by area.
- **D31.03 Maintenance management**: *Data:* PM schedules (frequency by time or meter), work orders (asset, type, priority, labor, parts, cost, status), meter readings. *Logic:* auto-generate work orders from PM schedule or meter thresholds; work order lifecycle.
- **D31.04 Lease management**: *Data:* lease (landlord/tenant, terms, payment schedule, escalations (CPI, fixed %), options). *Logic:* payment schedule generation; ASC 842/IFRS 16 lease liability and ROU asset amortization.
- **D31.05 Facility condition assessment**: *Data:* condition index, deficiencies, renewal costs. *Logic:* FCI = deferred maintenance / current replacement value; capital renewal forecast.
- **D31.06 Real estate / portfolio of properties**: *Data:* property, ownership, valuation. *Logic:* rollups.
- **D31.07 Inventory and parts**: *Data:* item, stock levels, reorder point. *Logic:* reorder alerts.

## D32 Timesheets and Actuals Capture

- **D32.01 Timesheet periods**: *Data:* timesheet period (weekly/biweekly). *Logic:* auto-generated periods.
- **D32.02 Timesheets**: *Data:* timesheet (resource, period, rows by activity/assignment or overhead codes, hours per day, overtime, status (Active, Submitted, Approved, Rejected)). *Logic:* submit → resource manager approval → project manager approval; actuals applied to assignments.
- **D32.03 Overhead activities**: *Data:* nonproject activity codes (vacation, training). *Logic:* excluded from project cost or charged to overhead.
- **D32.04 Apply actuals**: *Logic:* approved hours → actual units on assignments → recalc remaining units and costs; update activity status if first hours.
- **D32.05 Unifier timesheet BPs**: *Data:* timesheet line items by project/shell. *Logic:* rate × hours to cost sheet actuals.

## D33 Reporting Data Layer and Analytics

- **D33.01 Operational reporting data (ODS) and star schema**: *Data:* data warehouse (P6 Analytics/Primavera Data Warehouse, Unifier Analytics), fact tables (activity spread, resource assignment spread, EV history), dimensions (project, WBS, resource, calendar date). *Logic:* nightly ETL; history captured at period/week/day granularity (slowly changing dimensions).
- **D33.02 Report definitions (backend)**: *Data:* report templates (tabular, BI Publisher data models), parameters. *Logic:* server-side report generation to PDF/XLS/CSV; scheduled reports.
- **D33.03 KPI calculations library**: *Logic:* SPI, CPI, PPC, float erosion, BEI, CPLI, change % of contract, RFI turnaround, submittal cycle time.
- **D33.04 Data views / database views for reporting**: *Logic:* published views of BP data for external BI tools.

## D34 Integrations and APIs

- **D34.01 P6 EPPM Web Services (SOAP)**: CRUD on all P6 business objects (projects, activities, relationships, resources, assignments, codes, UDFs, baselines, EPS). *Logic:* object-level services with field lists, filters, batch operations; respects security.
- **D34.02 P6 REST API**: *Logic:* REST endpoints for projects, activities, resources, schedules, with JSON; schedule/level jobs triggered via API.
- **D34.03 P6 Integration API (Java)**: *Logic:* local/remote mode Java library for business-object access.
- **D34.04 Primavera Cloud REST API**: *Logic:* OAuth/token auth; endpoints for workspaces, projects, activities, resources, risks, tasks, cost sheets; async jobs for scheduling and import.
- **D34.05 Unifier Web Services (REST/SOAP)**: *Logic:* create/update BP records, shells, cost sheets, CBS, user data, documents; integration interface per BP defined in uDesigner.
- **D34.06 Aconex API (REST/XML)**: *Logic:* documents (register, upload, supersede, download), mail (send, search), workflows, projects, users; event notifications.
- **D34.07 Textura APIs and ERP connectors**: *Logic:* contracts, budgets, draws, invoices, payment status; scheduled sync.
- **D34.08 P6 ↔ Unifier integration**: *Logic:* push WBS/activity to Unifier schedule sheet; pull cost-loaded spread; CBS mapping; activity sheets.
- **D34.09 P6 ↔ Primavera Cloud / Aconex / Textura / ERP links**: *Logic:* schedule sync, risk register link, document references, cost actuals from Fusion/EBS (Project Portfolio Management).
- **D34.10 Gateway / Oracle Integration Cloud**: *Logic:* field mapping, synchronization flows, scheduled sync jobs, error logs.
- **D34.11 Webhooks and event notifications**: *Logic:* outbound events (record created, status changed) to subscribers.
- **D34.12 Identity integration**: *Logic:* SAML/OIDC SSO, SCIM user provisioning, LDAP.
- **D34.13 Weather, map and e-signature services**: *Logic:* external providers called from daily logs, locations and approvals.

## D35 Import/Export Formats

- **D35.01 XER (P6 native)**: tab-delimited multi-table export (%T table, %F fields, %R rows) covering projects, WBS, activities, relationships, calendars, resources, codes, UDFs, baselines. *Logic:* import options per object (keep existing, update existing, insert new, do not import; delete activities not in XER); risks carried but not visible.
- **D35.02 P6 XML**: XML schema of full project and global data. *Logic:* import/export with baselines, optionally zipped; used for Primavera Cloud and check-in/out.
- **D35.03 Microsoft Project XML (MSPDI)**: *Logic:* import into new/existing project; multiple projects; field mapping (tasks → activities, resources, calendars, constraints, lag units, summary tasks → WBS).
- **D35.04 UN/CEFACT XML**: *Logic:* exporting projects in the UN/CEFACT schedule format for government compliance.
- **D35.05 Excel/CSV import-export**: *Logic:* activities, resources, expenses round-trip by spreadsheet template with field mapping and validation.
- **D35.06 Primavera Risk Analysis/other QRA formats**: *Logic:* risk data exchange (.plan / XML).
- **D35.07 IFC / BIM models**: *Data:* model files (IFC 2x3/IFC4), model elements (GUID, type, properties). *Logic:* model federation and viewing (Aconex Models), element-to-activity linking (4D), element-to-cost (5D), clash results (BCF).
- **D35.08 COBie**: *Logic:* asset data exchange from construction to operations (asset handover to Unifier).
- **D35.09 Document metadata spreadsheets**: *Logic:* bulk upload/export of document registers (CSV/XLS).
- **D35.10 Unifier configuration packages**: *Logic:* export/import of BP designs, data elements, workflows between environments (config package with versioning).

## D36 Platform Services

- **D36.01 Job services / background jobs**: *Logic:* scheduled schedule/level/summarize/apply-actuals/store-period-performance/send-to-Unifier jobs; job queue with status and logs.
- **D36.02 Multi-tenant and environment management**: *Logic:* tenant isolation, dev/test/prod environments, data refresh.
- **D36.03 Data retention and purge**: *Logic:* recycle bin (deleted records recoverable for N days), purge of audit/history.
- **D36.04 Localization**: *Data:* language packs, number/date formats. *Logic:* locale-aware formatting server-side.
- **D36.05 Search service**: *Logic:* global index across records and documents.
- **D36.06 Rate limiting and API throttling**: *Logic:* per-tenant quotas.
- **D36.07 Backup, restore and record versioning**: *Logic:* point-in-time recovery; record version history.

---

## Sources

- https://docs.oracle.com/cd/F88966_01/English/Admin/p6_eppm_application_admin/39102.htm (P6 EPPM data structures)
- https://docs.oracle.com/cd/E80480_01/help/en/user/233332.htm (P6 EPPM / Primavera Cloud data dictionary)
- https://docs.oracle.com/cd/G48897_01/English/Admin/p6_eppm_importing_exporting/101760.htm (XER import)
- https://docs.oracle.com/cd/G48897_01/English/Admin/p6_eppm_importing_exporting/7973.htm (P6 XML export)
- https://docs.oracle.com/cd/G18294_01/English/Admin/p6_eppm_importing_exporting/8010.htm (MSP XML import)
- https://docs.oracle.com/cd/F50962_01/English/User_Guides/proj_controls/10281943.htm (Unifier Cost Manager, cost rules, SOV, funding)
- https://docs.oracle.com/cd/F37375_01/English/User_Guides/udesigner/toc.htm (Unifier uDesigner: BP types, shells, asset/space managers)
- https://docs.oracle.com/cd/F25628_01/help/user/en/73139.htm (Unifier auto-create shells)
- https://docs.oracle.com/cd/F50962_01/help/admin/en/10301010.htm (Unifier admin managers)
- https://www.oracle.com/construction-engineering/primavera-unifier/
- https://www.oracle.com/construction-engineering/primavera-cloud-project-management/ (Primavera Cloud: risk/Monte Carlo, portfolio, field task management)
- https://www.oracle.com/ce-help/primavera-cloud/tasks-getting-started/task-management/ (work plan, look-ahead, notifications)
- https://www.oracle.com/ce-help/primavera-cloud/primavera-cloud-getting-started-schedulers/managing-field-schedule/
- https://www.oracle.com/construction-engineering/textura-construction-payment-management/datasheet/
- https://docs.oracle.com/cd/E97085_01/English/workflow_guides/sub_billing_guide_na/ (Textura subcontractor billing: retention tab, signing)
- https://docs.oracle.com/cd/E97085_01/English/workflow_guides/gc_lien_waiver_guide_na/ (Textura GC lien waivers)
- https://www.oracle.com/ce-help/textura-na/textura-subcontractor-onboarding/textura-subcontractor-checklist-2-na/
- https://help.aconex.com/ and https://help.aconex.com/aconex/our-main-application/using-aconex/ (Aconex documents, mail, workflows, field)
- https://help.aconex.com/field/ (Aconex Field: inspections and issues)
- https://planningplanet.com/blog/how-use-earned-value-management-primavera-p6 (P6 EV techniques, secondary)
- https://tensix.com/defining-activity-relationships-in-primavera-p6-eppm/ (relationship types, secondary)
