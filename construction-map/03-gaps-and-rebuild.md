# 03 Gaps and Rebuild Plan

## Gap register

| Feature id | Feature | Why no OSS covers it | Rebuild outline (entities + algorithm) | Nearest reusable pattern (source path) | Effort |
|---|---|---|---|---|---|
| D01.02 | OBS-driven project security | schema only: P6 `OBSType`/`UserOBSType` bound in MPXJ, no evaluator | OBSNode, UserOBS, EPSNode/WBSNode.obs_id; effective profile on P = ∪ profiles of user OBS nodes whose subtree contains the OBS responsible for any EPS/WBS ancestor of P; Project Superuser short-circuit; materialise per (user, project) on change | `mpxj/src/main/java/org/mpxj/primavera/schema/UserOBSType.java:92`; union evaluator `openproject/app/models/role.rb:85-115` | M |
| D01.04 | Configurable shells | core logic absent: OpenProject has three fixed workspace types | ShellType(name, allowed_parent_types, enabled_managers, status set Active/On-Hold/View-Only/Inactive with write guards); auto-create shell from template or BP transition task | `openproject/app/models/project.rb:44-54`; copy `openproject/app/services/projects/copy_service.rb:34-48` | M |
| D01.06 | Workspace config inheritance, dynamic portfolios | schema only (`ProjectPortfolioType.Type = Auto-Maintained`) | per-workspace owned codes/UDFs/calendars/currencies resolved nearest-ancestor along parent_path; Portfolio.filter_expr re-evaluated on project change events | root-delegated fields `odoo/odoo/addons/base/models/res_company.py:163-171,425-436` | M |
| D02.09 (+D01.07) | Organization privacy until transmitted | core logic absent: Odoo company rules isolate, cannot share selectively | ProjectParticipant, Document.owner_company_id; read rule = owner company ∨ ObjectACL grant; grants inserted by Transmittal issue | `mayan-edms/mayan/apps/acls/models.py:23-54`; `odoo/odoo/addons/base/models/ir_access.py:64-137` | M |
| D02.12 | Delegation / proxy | none: only frappe impersonation audit | Proxy(delegator, delegate, start, end, scope); WorkflowAction routing substitutes delegate inside window; Journal.acting_for_user_id | `mpxj/src/main/java/org/mpxj/primavera/schema/TimesheetDelegateType.java` | S |
| D02.14, D23.11 | Electronic signatures on approvals | none: Mayan signs files, nothing signs a workflow decision | ApprovalSignature(signer, role, subject, SHA-256 of canonical record JSON, signed_at, envelope id); signer-authority check; re-hash on read; provider adapter (DocuSign/Adobe) | `mayan-edms/mayan/apps/document_signatures/models.py:30-135` | M |
| D03.02 | WBS milestone % complete | schema only (`WBSMilestoneType`) | WBS % = Σ weight(completed) / Σ weight; feeds EV technique "WBS milestones" | `mpxj/src/main/java/org/mpxj/primavera/schema/WBSMilestoneType.java` | S |
| D03.04 | Duration-type equation solver | core logic absent: MPXJ stores `TaskType`, no solver | per assignment Units = Duration × Units/Time; on change of one variable hold the type's fixed variable(s) and recompute the free one; activity duration = max assignment duration for Resource Dependent | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/` (CalculatedValue allocation) | M |
| D03.06 | Weighted step % | core logic absent: steps stored, `step_complete_flag` read | physical % = Σ(weight × step %)/Σ weight when flag set; step templates copied on apply | `mpxj/src/main/java/org/mpxj/Step.java:54-137` | S |
| D03.08 | Global change | schema only (`GlobalReplaceType`) | rule = filter + ordered assignments (field = expr); preview diff set; commit in one transaction; journal cause = global_change_id | `mpxj/src/main/java/org/mpxj/primavera/schema/GlobalReplaceType.java`; restricted eval `frappe/frappe/model/workflow.py` | M |
| D03.09 | Activity ID generation and renumber | core logic absent: prefix/suffix/increment stored only | next code = prefix + (max suffix + increment); bulk renumber in WBS/seq order with collision check | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/add_task.py`; `mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java:121-124` | S |
| D03.11 | Feedback / status-update approval | schema only (Feedback, ReviewRequired, ReviewStatus) | PendingProgress rows per activity; PM approve applies to actuals, reject returns; WorkflowDefinition on PendingProgress | `frappe/frappe/workflow/doctype/workflow/workflow.json` | S |
| D04.05 | Logic validation report | core logic absent: loops detected, open ends tied silently, OOS never reported | open-start/open-finish lists, OOS (successor actual start before predecessor finish for FS etc.), constraint conflicts (hard constraint vs logic), dangling links; persisted in ScheduleRun.log | `mpxj/src/main/java/org/mpxj/cpm/DepthFirstGraphSort.java:89-117` | S |
| D05.04 | Resource availability per period | core logic absent: max units stored, never multiplied by calendar hours | capacity(r, day) = Σ working minutes(calendar r, day) × max_units(effective date, shift period); cache per day | `libreplan/libreplan-business/src/main/java/org/libreplan/business/calendars/entities/Capacity.java`; `taskjuggler/lib/taskjuggler/ResourceScenario.rb:830-905` | S |
| D05.06, D10.06 | Store period performance and history | schema only (`ActivityPeriodActualType`) | at period close insert ActivityPeriodActual/AssignmentPeriodActual = to-date − Σ prior periods; lock closed periods; trend = series over closes and schedule snapshots | `mpxj/src/main/java/org/mpxj/primavera/schema/ActivityPeriodActualType.java`; `taskjuggler/lib/taskjuggler/reports/TraceReport.rb:36-150` | M |
| D06.04 | Multiple float paths | core logic absent: `float_path`/`float_path_order` never computed | from end activity walk back driving (or min relationship free float) predecessors to build path 1; remove; repeat up to max paths; write float_path, float_path_order | `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java` (calculateLongestPath, PS:4056) | M |
| D06.05 | Progress override / actual-dates modes | core logic absent: option read, scheduler always retained logic | progress override: in-progress successor ES = data date ignoring incomplete predecessors; actual dates: remaining work from predecessors' actual dates; branch in forward pass per link | `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java` | M |
| D06.06 | Unhonoured schedule options | core logic absent: ignore-external, open-ends-critical, SS-lag-from-early-start, float-per-project-finish not read | implement each as a branch in link evaluation / LF seeding | `mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java:822-875` | M |
| D06.08 | Schedule log | core logic absent: only exception codes | ScheduleRun.log JSON: counts, open ends, constraints applied, OOS, loops with full path, external dates used | `taskjuggler/lib/taskjuggler/TaskScenario.rb` (postScheduleCheck) | S |
| D06.10 | DCMA 14-point | none | see Construction-specific core gaps | `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java` (engine output) + `mpxj/src/main/java/org/mpxj/primavera/schema/BaselineProjectType.java` | M |
| D06.11 | Scenarios diff/merge | core logic absent: scenario-indexed attrs, IFC baseline copy, no diff/merge | Scenario = copy-on-write project; diff by key (task_code, wbs path); merge selected changes | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/create_baseline.py:67-110`; `openproject/app/models/journable/with_historic_attributes.rb:145-200` | M |
| D06.12, D20.06 | Fragnet / TIA | none | see Construction-specific core gaps | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/duplicate_task.py` (copy primitive, D06) + `create_baseline.py:67-110` | L |
| D07.02 | Assign by role (staffing search) | schema only: `SkillLevel`, `RSRCROLE`; LibrePlan criterion match without proficiency | candidates = resources with role; free = capacity − booked DayAssignment over window; order by proficiency then free capacity | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/resources/entities/Resources.hbm.xml:155-178` | M |
| D07.07 | Resource teams and pools | carrier only: generic allocation by criteria | ResourceTeam(members), aggregated AvailabilityTable; allocation to team spreads to members by free capacity | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/resources/entities/Resources.hbm.xml:54-66` | S |
| D07.09, D13 | Auto-compute actuals | schema only (`auto_compute_act_flag`) | on progress update actual_units = planned × activity % (or planned-to-date), remaining = at-completion − actual, costs from rates; same for expenses | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/planner/entities/AdvanceConsolidations.hbm.xml:7-84` | S |
| D08.01–D08.03 | P6-style post-CPM leveler | core logic absent: TaskJuggler books serially during scheduling; P6 options stored, unread | see Construction-specific core gaps | `taskjuggler/lib/taskjuggler/ResourceScenario.rb:830-905`; `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/limiting/entities/LimitingResourceAllocator.java` | L |
| D08.05 | Activity-free portfolio demand plans | core logic absent: LibrePlan scenarios version allocations only | Demand(project, role/resource, period, units, scenario) vs capacity; overload report | `libreplan/libreplan-business/src/main/java/org/libreplan/business/scenarios/entities/Scenario.java:53-67` | M |
| D08.06 | Resource requests / booking | none | ResourceRequest (Draft → Submitted → Approved/Booked │ Rejected); booking writes soft DayAssignments | `frappe/frappe/workflow/doctype/workflow/workflow.json` | M |
| D08.07 | Persisted leveling log | core logic absent: TaskJuggler contention in memory | LevelingLog(activity, resource, contending activity, delay, reason, unresolved) per run | `taskjuggler/lib/taskjuggler/TaskScenario.rb:825-980` (`@competitors`, `@contendedResources`) | S |
| D09.06 | CBS segment parsing | core logic absent: trees exist, no delimiter semantics | split code by delimiter, store segments + materialised path, roll up by prefix | `odoo/addons/analytic/models/analytic_plan.py:12-90` (parent_path) | S |
| D09.07 | MasterFormat / UniFormat / OmniClass libraries and mapping | core logic absent: IFC reference model only | Classification + ClassificationReference trees loaded per edition; mapping(source_ref, target_ref) | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/classification/add_reference.py:127-270` | M |
| D10.02 | Update baseline merge | schema only (`UpdateBaselineOptionType`) | match current↔baseline on Activity code; per flag add new, delete missing, overwrite field groups; stamp last_baseline_update_date | `mpxj/src/main/java/org/mpxj/primavera/PrimaveraBaselineStrategy.java:54-75` | M |
| D10.03 | Baseline comparison (Claim Digger) | core logic absent: per-timestamp attribute diff, no report | field-by-field diff per entity type over matched keys → added/deleted/changed sets | `openproject/app/models/journable/with_historic_attributes.rb:145-200` | M |
| D10.04 | Update Progress / Apply Actuals | core logic absent | Update Progress: activities with planned dates before new data date get actuals = planned, RD from planned remaining; Apply Actuals = D32.04 then reschedule | `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java` (data date handling, PS:64-151) | M |
| D10.05 | Progress spotlight | none | query activities with planned/early start or finish in (old data date, new data date] | `mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java` (field set) | S |
| D10.08 | Project check-in / check-out | schema only (`CheckOutStatus/Date/User`) | exclusive lock row; reject writes from others; check-in imports file with diff/merge (D35.01) | `mayan-edms/mayan/apps/checkouts/models.py:28-46` | M |
| D11.02 | Performance % techniques | schema only (`EarnedValueComputeType`) | EV = BAC × f: 0/100, 50/50, custom X at start, WBS milestones, activity %, resource-curve % at performance %; WBS setting inherits project default | `mpxj/src/main/java/org/mpxj/primavera/schema/WBSType.java:52-103` | M |
| D11.03 | ETC/EAC techniques | schema only; LibrePlan hard-codes EAC = BAC/CPI | ETC = (BAC − EV) × PF, PF ∈ {1, user, 1/CPI, 1/(CPI·SPI)} or remaining cost; EAC = AC + ETC; TCPI both variants | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java:167-195` | S |
| D11.05 | Earned schedule | none | ES = t where cumulative PV(t) = EV(now), linear interpolation between periods; SPI(t) = ES/AT | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java:65-78` (series) | S |
| D11.06 | Baseline selection for EV | schema only | PV source = project baseline or current; global option at-completion vs planned values × planned vs current dates | `mpxj/src/main/java/org/mpxj/primavera/schema/ProjectType.java:794`; `GlobalPreferencesType.java:118-123` | S |
| D11.08 | ANSI-748 control accounts, MR, UB, VAR | schema only (budget log, unallocated budget) | ControlAccount(WBS×OBS), work/planning package flag, MR and UB ledgers, VarianceExplanation with thresholds and narrative per period | `mpxj/src/main/java/org/mpxj/primavera/schema/ProjectBudgetChangeLogType.java` | L |
| D12.01 | Threshold monitor job | schema only; ERPNext budget Stop/Warn only working breach evaluator | per enabled ProjectThreshold evaluate parameter per activity/WBS in window (dates or expressions); outside [lower, upper] → ProjectIssue (dedupe open per threshold+object) | `erpnext/erpnext/accounts/doctype/budget/budget.py:500-538` | M |
| D12.06 | Change / decision logs | carrier only | WorkItemType "log" with log type, owner, status workflow | `openproject/app/models/workflows/status_transition.rb:30-35` | S |
| D13.01 | Expense accrual spreading | core logic absent: `AccrueType` carried, unused | start → activity start period; end → finish period; uniform → by working minutes per period of activity calendar | `mpxj/src/main/java/org/mpxj/TimephasedUtility.java:48-266` | S |
| D13.02 | Cost-account rollups | core logic absent | Σ assignment + expense cost by cost account tree (nested set) per project/period | `erpnext/erpnext/accounts/doctype/cost_center/cost_center.json` (lft/rgt) | S |
| D13.04 | Funding allocation validation | schema only | Σ fund_share = 100 %, Σ amounts vs current budget; warn/stop | `odoo/addons/analytic/models/analytic_mixin.py:182-196` | S |
| D13.06 | Summarization service | schema only (P6 Summary*); LibrePlan incremental sums for expenses/effort | post-order job over WBS → project → EPS writing EVSummary and summary columns, last_summarized_at, incremental on change | `libreplan/libreplan-business/src/main/java/org/libreplan/business/orders/daos/SumExpensesDAO.java:69-184` | M |
| D14.01 | Risk register model and lifecycle | schema only (JAXB `RiskType`, no MPXJ model class) | Risk + ActivityRisk + RBS; status workflow Proposed → Open → Active → Managed/Impacted/Rejected | `mpxj/src/main/java/org/mpxj/primavera/schema/RiskType.java` | S |
| D14.02 | P×I scoring | schema only | score = RiskMatrixScore.severity[impact level] at probability row; overall by scoring method (highest, average impacts, average individual scores); pre and post response | `mpxj/src/main/java/org/mpxj/primavera/schema/RiskMatrixScoreType.java` | S |
| D14.03 | Response costs to budget | schema only | approved response plan cost → BudgetChangeLog (pending) and ExpenseItem on linked activity | `mpxj/src/main/java/org/mpxj/primavera/schema/RiskResponseActionType.java` | S |
| D14.04 | Monte Carlo schedule risk | core logic absent: qsra sums a fixed critical path, no network | see Construction-specific core gaps | `qsra_qcra_icsra/qsra_qcra/project.py:20-185` + `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java` | L |
| D14.05 | Uncertainty templates | none | rule rows (code value → min%/ML%/max%, distribution) bulk-applied to remaining durations | `mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java:174-188` (code assignments) | S |
| D14.06 | Exposure rollup | schema only | EMV = p × cost impact (and days); aggregate by WBS/project/portfolio; heat-map counts per (P, I) cell | `mpxj/src/main/java/org/mpxj/primavera/schema/RiskType.java` | S |
| D14.07 | Contingency determination | core logic absent: percentiles exist | cost contingency = P_target(cost) − deterministic cost; schedule = P_target(finish) − deterministic finish | `qsra_qcra_icsra/qsra_qcra/project.py:73-123` | S |
| D14.08 | Schedule health check before QRA | none | DCMA subset gate (open ends, hard constraints, leads/lags, long durations, OOS) | — (shares D06.10) | S |
| D14.09 | Risk register exchange | schema only: PMXML risk types bound but not mapped | map JAXB Risk* ↔ canonical; Excel and PRA XML import | `mpxj/src/main/java/org/mpxj/primavera/schema/APIBusinessObjects.java` | S |
| D15.01 | Ideas and conversion | carrier only (initiation request work package) | Idea (Draft → Submitted → Under Review → Approved/Rejected → Converted); convert = project copy from template | `openproject/app/models/projects/creation_wizard.rb` | M |
| D15.02 | Ranking and efficient frontier | core logic absent: formula scores only | sort by weighted score; frontier = non-dominated (cost, value) set | `openproject/app/models/custom_field/calculated_value.rb:37-148` | S |
| D15.03 | Capital plans | core logic absent: ERPNext time-phases one budget, no plan/line entity | CapitalPlan + lines per project × fiscal year with funding source, priority, included flag; totals vs targets | `erpnext/erpnext/accounts/doctype/budget/budget.json` | M |
| D15.04 | Portfolio scenarios and optimisation | none (What-If flags only) | scenario = line overrides (start shift, budget); compare totals and D08 capacity; 0/1 knapsack max Σ score s.t. Σ cost_y ≤ budget_y ∀y (DP or MILP); approve pushes original budgets | `libreplan/libreplan-business/src/main/java/org/libreplan/business/scenarios/entities/Scenario.java:53-67` | L |
| D15.06 | Measure history | core logic absent: calculated values recompute live only | scheduled job appends MeasureHistory(measure, project, period, value, target) | `frappe/frappe/core/doctype/scheduled_job_type/scheduled_job_type.py:34-55` | S |
| D15.08 | Benefits (NPV, IRR, ROI, payback) | schema only (BenefitPlan, AnnualDiscountRate) | NPV = Σ(Bt − Ct)/(1+r)^t monthly compounding; IRR by bisection/Newton; ROI = (ΣB − ΣC)/ΣC; payback = first t with cumulative ≥ 0 | `mpxj/src/main/java/org/mpxj/primavera/schema/ProjectSpendingPlanType.java` | S |
| D15.09 | Planning sheet → project shells | core logic absent | sheet rows (projects × fiscal years); approved row auto-creates project from template and pushes amounts | `openproject/app/services/projects/copy_service.rb:34-48` | M |
| D16.02 | Rolling look-ahead | core logic absent: fixed sprints | window = data date + N weeks over activities and tasks; make-ready status per task from PlanConstraint | `openproject/modules/backlogs/app/models/sprint.rb` | S |
| D16.03 | Constraint register | core logic absent: task-to-task blockers only | PlanConstraint typed (RFI, submittal, material, labor, equipment, permit, design) linked to source record; ready = all closed; aging and reminders before need date | `odoo/addons/project/models/project_task.py:85-88,280-285` | M |
| D16.04 | Weekly commitments | core logic absent: sprint scope lock only | WeeklyCommitment(task, week, committer, committed date, locked) immutable after lock | `openproject/modules/backlogs/app/services/backlogs/sprints/start_service.rb` | S |
| D16.05 | PPC | core logic absent: burndown replay exists | PPC(week) = completed commitments / commitments, by company and project; as-of evaluation via journals | `openproject/modules/backlogs/app/models/burndown.rb` | S |
| D16.06 | Reasons for non-completion | none | mandatory VarianceReason on missed commitment at week close; Pareto by reason | none in sources read | S |
| D16.07 | Pull planning | core logic absent: ALAP and milestones exist separately | backward pass from milestone over task network with trade handoffs; sticky-note tasks with duration and crew | `taskjuggler/lib/taskjuggler/TaskScenario.rb` (ALAP, `forward=false`) | M |
| D16.08 | Takt planning | none | zones × trades matrix; takt time; wagon sequence through zones; generated activities with FS by zone and trade | none in sources read | L |
| D17.01 | Configurable cost sheet | core logic absent: fixed Planned/Committed/Invoiced columns | CostSheetColumn registry (BP source / formula / manual), CostSheetPosting ledger keyed (project, CBS, column, period), dependency-ordered formula evaluation, repost on BP status transition | `idempiere/org.adempiere.base/src/org/compiere/model/I_C_ProjectLine.java`; `ifcopenshell/src/ifcopenshell-python/ifcopenshell/util/cost.py:63-128` | L |
| D17.04 | Budget transfers | core logic absent: revision by cancel-and-copy | BudgetTransfer(from CBS, to CBS, amount) with Σ = 0; approval posts Revised Budget | `erpnext/erpnext/accounts/doctype/budget/budget.py:887-898` | S |
| D17.05 | User-defined cost rules | core logic absent: hard-coded budget checks | Rule(column A op column B, scope, trigger statuses, hard/soft) evaluated on status change, API and auto-creation paths | `erpnext/erpnext/accounts/doctype/budget/budget.py:412-579` | M |
| D17.06 | Forecast sheet | core logic absent: EAC = BAC/CPI only | ETC by CBS × period (manual or from D11), periodic snapshot freeze, variance = Revised Budget − EAC | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java:183-195` | M |
| D17.08 | Worksheets | core logic absent: IFC formula trees per cost item | sheet cells with formulas; named outputs feed CostSheetColumn | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/util/cost.py:358-443` | M |
| D17.09 | Cost sheet snapshots | core logic absent: budget header journals only | snapshot = copy of CostSheetPosting aggregates per (CBS, column) with label; period compare | `openproject/db/migrate/tables/journals.rb` | S |
| D18.01 | Fund sheet | carrier only: fund as dimension with budget ceiling | FundingSource restrictions; company fund sheet columns appropriated / allocated / committed / consumed / available from ledgers | `erpnext/erpnext/accounts/doctype/accounting_dimension/accounting_dimension.py:137-182` | M |
| D18.02 | Funding BP | core logic absent | Funding record (fund, CBS, amount) with approval moving amount company → project fund sheet; zero-sum vs appropriation | `odoo/addons/analytic/models/analytic_distribution_model.py:10-99` | S |
| D18.03 | Waterfall fund consumption | core logic absent: ratio split only | on spend approval iterate eligible funds by priority, consume min(remaining fund, remaining spend), residual → Unfunded; FundConsumption ledger; re-run on reversal | `odoo/addons/analytic/models/analytic_mixin.py:182-275`; `idempiere/org.idempiere.acct/src/org/idempiere/acct/doc/Fact.java:78-84` | M |
| D19.01 | Subcontract attributes | core logic absent: PO lacks retainage, insurance, bonds, SOV | Commitment.commitment_type, retainage_policy, Bond, ComplianceRequirement with expiry, SOVLine per commitment | `erpnext/erpnext/accounts/doctype/bank_guarantee/bank_guarantee.json` | M |
| D19.02 | Commitment summary | core logic absent | revised = base + approved COs; pending COs; invoiced; paid; retainage held/released; remaining; % billed | `erpnext/erpnext/controllers/status_updater.py:85-108` | S |
| D19.04 | Contract administration and time bars | core logic absent | clause library, notice periods, time-bar calculators (e.g. notice within N days of awareness) with reminders | `erpnext/erpnext/support/doctype/service_level_agreement/service_level_agreement.py` | M |
| D19.05 | Prime contracts | core logic absent: margin = billed − cost only | PrimeContract with owner COs and SOV; margin = revenue commitments − cost commitments | `idempiere/org.adempiere.base/src/org/compiere/model/I_C_Project.java` | M |
| D19.06 | Cost-plus and GMP | core logic absent: T&M with ceiling only | billable = cost + fee %; GMP cap; savings = GMP − final cost split by share % | `idempiere/org.adempiere.base/src/org/compiere/model/X_C_Project.java:961-969` | M |
| D20.01–D20.04 | Change events → PCO → CO pipeline | none / core logic absent (PO amendment only) | see Construction-specific core gaps | `erpnext/erpnext/accounts/services/child_item_update.py:30-142`; `erpnext/erpnext/accounts/doctype/purchase_taxes_and_charges/purchase_taxes_and_charges.json` | L |
| D20.05 | Trend items | none | Trend(CBS, amount, probability) feeding forecast column before formal change | none in sources read | S |
| D20.07 | Change log metrics | none: generic audit only | days in status from StateMilestone; approval cycle time; cumulative change % = Σ approved COs / original contract | `frappe/frappe/automation/doctype/milestone_tracker/milestone_tracker.py:32-44` | S |
| D20.08 | Contingency / allowance drawdown | none | see Construction-specific core gaps | `erpnext/erpnext/accounts/doctype/budget/budget.py:887-898` | M |
| D21.01, D23.01 | SOV sheets and contract hierarchy | core logic absent: phase/line value breakdown only | see Construction-specific core gaps (SOV) | `idempiere/org.adempiere.base/src/org/compiere/model/I_C_ProjectPhase.java`; `ifcopenshell/src/ifcopenshell-python/ifcopenshell/util/cost.py:303-319` | M |
| D21.02, D23.03, D23.08 | Pay applications G702/G703 | none | see Construction-specific core gaps | `erpnext/erpnext/controllers/status_updater.py:492-541` | L |
| D21.05, D23.04 | Retainage | none | see Construction-specific core gaps | `erpnext/erpnext/accounts/doctype/tax_withholding_entry/tax_withholding_entry.py` | M |
| D22.01 | Cash-flow curve store | core logic absent: budget and actuals per period only | CashFlowEntry by curve type × period × CBS, fiscal period structure, period and cumulative views | `openproject/modules/costs/app/models/costs/aggregated_costs.rb:93-115` | M |
| D22.02 | Profile spreader | core logic absent: curves are data | map period overlap to normalised duration fraction; integrate 20-slice piecewise-constant curve; rescale to exact total, residual to last bucket | `mpxj/src/main/java/org/mpxj/WorkContour.java:127-135`; residual rule `odoo/addons/account/models/account_payment_term.py:169-266` | S |
| D22.04 | Auto-forecast | core logic absent | forecast = actuals for closed periods + (EAC − actuals) spread from data date to forecast finish | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java:183-195` | S |
| D22.06 | Cash-flow snapshots and variance | core logic absent: live variance only | CashFlowSnapshot freeze; per-period variance baseline vs forecast vs actual | `erpnext/erpnext/accounts/report/budget_variance_report/budget_variance_report.py:121-170` | S |
| D22.07 | Commitment cash flow with retention | core logic absent | spread committed value by profile or payment schedule; hold retention % per period; release at completion period | `erpnext/erpnext/accounts/doctype/payment_schedule/payment_schedule.json` | S |
| D23.02 | Draws | none | Draw (Open → Invoicing → GC Review → Owner/Lender Approval → Funded → Paid → Closed) with deadline reminders | `frappe/frappe/automation_engine/dispatch.py:22-175` | M |
| D23.05 | Lien waivers | none | see Construction-specific core gaps | `erpnext/erpnext/buying/doctype/supplier/supplier.json` (on_hold, hold_type) | M |
| D23.06 | Compliance register with auto-hold | core logic absent: certificates and supplier hold exist separately | ComplianceRequirement per contract; nightly expiry sweep sets Party.on_hold (hold_type Payments) and notifies | `erpnext/erpnext/regional/doctype/lower_deduction_certificate/lower_deduction_certificate.json`; `erpnext/erpnext/buying/doctype/supplier/supplier.json` | M |
| D23.09 | ACH / joint checks / funds flow | core logic absent: payment orders without file export | NACHA file generator from PaymentOrder; joint-check payee pairs; owner → GC → sub chain | `erpnext/erpnext/accounts/doctype/payment_order/payment_order.json` | M |
| D23.10 | Change orders in payment management | none: amend suffix only | CO approval versions SOVLine (version+1) and recomputes contract sum to date | `erpnext/erpnext/accounts/services/child_item_update.py:30-142` | M |
| D23.13 | Platform usage fees | none | fee schedule bands by contract value; fee invoice per draw | none in sources read | S |
| D24.01 | Versioned BP design → deploy | core logic absent: frappe mutates DocType in place | immutable published RecordTypeDefinition/WorkflowDefinition versions; instances pinned | `frappe/frappe/automation_engine/dispatch.py:106-175` (actions_snapshot) | L |
| D24.02, D24.09 | Parallel review with consensus, sub-workflows | core logic absent: one transition per action/role | StepInstance(mode all/any/majority, due_at) + StepAssignment outcomes; aggregation rule; child workflow linked to parent step, parent waits on completion | `frappe/frappe/automation/doctype/automation_event_subscription` (correlation wait) | L |
| D24.04 | Step SLA, escalation, auto-advance | core logic absent: no due on states | WorkflowState.due_duration; due_at on entry (working calendar); timer job escalates or applies default transition | `erpnext/erpnext/support/doctype/service_level_agreement/service_level_agreement.py` | M |
| D24.07, D25.06 | Markup sessions | core logic absent: single-owner page layers | Markup(version page, author, layer JSON, created_at, superseded_by); merged view = ordered overlay of non-superseded layers | `mayan-edms/mayan/apps/converter/models.py:92-140` | M |
| D24.10 | Server-side conditional validation | core logic absent: `mandatory_depends_on` client-only | evaluate depends_on / mandatory_depends_on / read_only_depends_on on save with the restricted evaluator | `frappe/frappe/model/base_document.py:1004-1048` | S |
| D25.01, D25.02 | Document numbering and revision schemes | core logic absent: metadata and single active version only | see Construction-specific core gaps | `mayan-edms/mayan/apps/sequences/managers.py:33`; `mayan-edms/mayan/apps/documents/models/document_version_models.py:23` | M |
| D25.03 | Folder templates, cascading folder ACLs | core logic absent: cabinet ACLs do not reach documents | folder template cloned per project; permission = nearest ancestor ACL union walking MPTT | `mayan-edms/mayan/apps/cabinets/models.py:24-44`; `mayan-edms/mayan/apps/acls/models.py:23-54` | M |
| D25.04, D35.09 | Bulk upload with spreadsheet metadata | core logic absent | row ↔ file match by filename; per-cell validation; error report; create revisions per D25.02 | `mayan-edms/mayan/apps/metadata/models/metadata_type_models.py:45-58`; `odoo/addons/base_import/models/base_import.py:109-189` | S |
| D25.07 | Drawing sheets | core logic absent: page split only | title-block OCR region → sheet number/title; sheet sets; cross-sheet hyperlinks from callout OCR | `mayan-edms/mayan/apps/ocr/models.py:18-40` | L |
| D25.08 | Expiring share links, external download audit | core logic absent | ShareLink(token, revision, recipient, expires_at); download events per party | `mayan-edms/mayan/apps/mailer/mailing_actions.py:74-91` | S |
| D25.09 | Archive / handover package | core logic absent: time-based trash only | export documents + correspondence + metadata manifest (JSON/CSV) as one package job | `openproject/app/models/backup.rb` | M |
| D26.01, D26.03 | Organisation-aware mail and numbering | core logic absent: per-project WP identifier | from/to/cc orgs and users, confidential flag, Sequence keyed (project, org, mail_type) | `mayan-edms/mayan/apps/sequences/managers.py:33` | M |
| D26.02 | Transmittals | none | see Construction-specific core gaps | `mayan-edms/mayan/apps/mailer/mailing_actions.py:74-91`; `mayan-edms/mayan/apps/acls/models.py:23-54` | M |
| D27.01 | RFI official answer and ball-in-court | carrier only | RFIDetail (question, official answer, impacts), ball_in_court_party per step with timestamps | `openproject/db/migrate/tables/work_packages.rb:35` + SLA fields | M |
| D27.02 | Submittal register with back-calculated dates | core logic absent | see Construction-specific core gaps | `erpnext/erpnext/support/doctype/service_level_agreement/service_level_agreement.py` | M |
| D27.03 | Submittal review clocks per party | core logic absent: Mayan logs steps, not party | StepAssignment with ball-in-court party, planned review days, actual days per party | `mayan-edms/mayan/apps/document_states/models/workflow_transition_field_models.py:22` | M |
| D27.04 | Spec-book parsing | none | MasterFormat section extraction (number, title, submittal paragraphs) → draft register rows | none in sources read | L |
| D27.06 | Comment closeout matrix | core logic absent: BCF comments lack status | comment(discipline, reviewer, response, status open/accepted/rejected/closed); closeout when all closed | `openproject/modules/bim/db/migrate/tables/bcf_comments.rb` | S |
| D28.01 | Daily log aggregate | core logic absent: work reports and emailed status only | DailyLog unique per (project, date, company) with sections; lock after approval; manpower trend Σ headcount by trade/day | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/workreports/entities/WorkReports.hbm.xml` | M |
| D28.03, D28.04 | Photos and 2D drawing pins | core logic absent: EXIF and 3D viewpoints only | DrawingPin(version page, x%, y%, record); EXIF GPS → georeferenced sheet → pin | `mayan-edms/mayan/apps/redactions/transformations.py:10`; `mayan-edms/mayan/apps/file_metadata/models.py:87` | M |
| D28.05 | Forms engine with logic | core logic absent: static templates | show_if on prior answers, scoring, signature fields, failed answer ⇒ create punch item / NCR | `erpnext/erpnext/stock/doctype/quality_inspection/quality_inspection.py` (acceptance formula) | M |
| D28.06 | Offline mobile sync | core logic absent: lock_version conflict only | client queue with idempotency keys; per-field LWW or 3-way merge against journal snapshot | `openproject/db/migrate/tables/journals.rb` | L |
| D29.01, D29.05 | Punch and quality analytics | core logic absent | completion % per area, aging, first-time pass rate, defects per area, mean closure time | `odoo/addons/project/report/project_task_burndown_chart_report.py:83-91` | S |
| D29.02 | ITP with hold/witness points and signatures | core logic absent: inspection hold of parent transaction only | ITP(spec section, activity) → steps (hold/witness/review/surveillance, party, criteria); inspection per step with signatures; hold step not passed ⇒ dependent activity cannot progress | `erpnext/erpnext/stock/services/quality_inspection_service.py:84` | M |
| D29.03 | NCR disposition and verification | core logic absent | disposition enum, approver, cost; Raised → Dispositioned → Corrective Action → Verified → Closed | `erpnext/erpnext/quality_management/doctype/quality_action/quality_action.py` | S |
| D29.04 | Commissioning and handover | none | system/subsystem/component hierarchy, checklist templates per component type, completion % per system, handover package export | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/qualityforms/entities/QualityForms.hbm.xml` | L |
| D30.01 | Safety observations | none | see Construction-specific core gaps (HSE) | `openproject/db/migrate/tables/work_packages.rb:35` + custom fields | S |
| D30.02 | Incidents, OSHA logs, TRIR | none | see Construction-specific core gaps (HSE) | `erpnext/erpnext/quality_management/doctype/quality_action/quality_action.py`; `openproject/modules/costs/db/migrate/tables/time_entries.rb:38` | M |
| D30.03 | Certifications and site eligibility | core logic absent: training records only | WorkerCertification with expiry; daily expiring flag; eligibility = required certs valid on date ∧ toolbox attendance in period | `hrms/hrms/hr/doctype/training_event/training_event.py` | M |
| D30.04 | Permits to work | carrier only: generic state engines | see Construction-specific core gaps (HSE) | `mayan-edms/mayan/apps/document_states/models/workflow_models.py` | M |
| D30.05 | Job hazard analysis | none | JHA → steps → hazards (L×S) → controls with residual rating | none in sources read | S |
| D31.01 | Sum-of-years-digits, parent assets | core logic absent | SYD amount_k = depreciable × (N − k + 1)/(N(N+1)/2) split by frequency; parent_asset_id tree with cost/status rollup | `erpnext/erpnext/assets/doctype/asset/depreciation.py` | S |
| D31.02 | Space management | core logic absent: location tree with area | Space(type, gross/usable area, occupancy, department, BIM GUID); utilisation; chargeback = area × rate to department cost center | `erpnext/erpnext/assets/doctype/location` (D31 tree) | M |
| D31.03 | Meter-based PM | core logic absent: time-based PM only | Meter, MeterReading; trigger work order when reading − last trigger ≥ X | `erpnext/erpnext/assets/doctype/asset_maintenance/asset_maintenance.py` | S |
| D31.04 | Lease management (ASC 842 / IFRS 16) | none | Lease, payment schedule generator with escalation; liability = PV(payments, rate); ROU = liability + IDC − incentives; interest = opening liability × rate/period | `odoo/addons/account/models/account_payment_term.py:169-266` (schedule generation) | L |
| D31.05 | Facility condition assessment | none | ConditionAssessment + deficiencies; FCI = Σ deferred maintenance / current replacement value; renewal forecast by component life | none in sources read | M |
| D31.06 | Real estate portfolio | none | Property, ownership share, valuation history, rollups over Location tree | `erpnext/erpnext/assets/doctype/location` | M |
| D32.02 | Two-stage timesheet approval | schema only (P6 Approved/Unapproved hours, TimesheetApprovingAs) | status per (timesheet, project) Active → Submitted → RM-Approved → PM-Approved │ Rejected; partial approval moves hours unapproved → approved; TimesheetAudit row per transition | `mpxj/src/main/java/org/mpxj/primavera/schema/TimesheetAuditType.java`; `erpnext/erpnext/projects/doctype/timesheet/timesheet.py:92-171` | M |
| D32.03 | Overhead exclusion from project cost | core logic absent: implicit internal project | lines with overhead_code and no project → overhead cost account; excluded from EV AC | `odoo/addons/hr_timesheet/models/res_company.py:26-66` | S |
| D32.04 | Apply actuals to assignments | core logic absent | see Construction-specific core gaps | `libreplan/libreplan-business/src/main/java/org/libreplan/business/orders/daos/SumChargedEffortDAO.java`; `taskjuggler/lib/taskjuggler/TimeSheets.rb:244-275` | M |
| D33.01 | Warehouse / star schema | core logic absent: as-of journals and spreads exist | SCD-2 dims via DimensionVersion; facts assignment spread, activity spread, EV history; nightly ETL job | `openproject/app/models/journable/historic_active_record_relation.rb`; `taskjuggler/lib/taskjuggler/reports/TraceReport.rb:79-140` | L |
| D33.03 | KPI library | core logic absent: CPI/CV/SV/EAC only | SPI, BEI, CPLI, float erosion, PPC, change % of contract, RFI turnaround, submittal cycle time from snapshots and state milestones | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java` | M |
| D34.01 | P6 SOAP services | none | WSDL-compatible facade over canonical services | `odoo/odoo/addons/base/models/` JSON-2 pattern (D34) | L |
| D34.02 | P6-compatible REST with schedule/level jobs | core logic absent: client only in MPXJ | object registry, `Fields=` projection, `Filter=` grammar, batch CRUD, async JobRun endpoints | `mpxj/src/main/java/org/mpxj/primavera/webservices/WebServicesReader.java`; `openproject/modules/job_status/db/migrate/tables/job_statuses.rb` | L |
| D34.05, D34.08 | Unifier web services, P6 ↔ Unifier mapping | none (PMXML link fields only) | mapping table (WBS/activity ↔ BP record / cost code) + push/pull jobs with watermarks | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/orders/entities/Orders.hbm.xml:316-334` (order_sync_info) | L |
| D34.06 | Aconex mail/transmittal API | core logic absent: OpenCDE documents only | REST for Transmittal, Mail, Document revisions over canonical services | `ifcopenshell` opencdeserver (D34) | M |
| D34.07 | Textura / ERP connectors | none | draw and payment sync, AP voucher export with idempotency keys, inbound payment status | `erpnext/erpnext/erpnext_integrations/doctype/plaid_settings/plaid_settings.py:218-330` | L |
| D34.10 | Integration flow designer | core logic absent: property bags and cron jobs | flow(source, mapping rules, transforms, target), per-run error log, retry | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/common/entities/JobSchedulerConfiguration.hbm.xml` | M |
| D34.13 | Weather, map, e-signature adapters | none | provider interfaces; weather snapshot per DailyLog from geocoded project location | none in sources read | M |
| D35.01 | XER import options and round-trip | core logic absent: MPXJ reads into a fresh ProjectFile | match keys per table, action enum per table (keep/update/insert/skip), delete-not-in-file, diff/apply in one transaction, RawTablePassthrough for unread tables | `mpxj/src/main/java/org/mpxj/primavera/PrimaveraXERFileReader.java:369-414`; `mpxj/src/main/java/org/mpxj/primavera/XerFile.java:251-336` | M |
| D35.02 | PMXML risk/funding/document/timesheet mapping | schema only (JAXB) | map Risk*, ProjectFunding, Document, Timesheet*, ProjectThreshold, ProjectIssue into canonical entities both ways | `mpxj/src/main/java/org/mpxj/primavera/schema/ProjectType.java` | M |
| D35.04 | UN/CEFACT schedule XML | none | XSD binding + mapping from D03/D04/D05 | `odoo/addons/account_edi_ubl_cii/models/account_edi_xml_cii_facturx.py:16-18,459-462` | M |
| D35.06 | QRA formats (.plan/.rsk) | none | reader/writer for PRA XML; uncertainty and risk events | `mpxj/src/main/java/org/mpxj/primavera/schema/RiskType.java` | M |
| D35.08 | COBie import and validation | core logic absent: export only | sheet parser, required-field and picklist rules, IFC/asset creation | `ifcopenshell` `ifcfm/ifcfm/cobie24.py:1160-1560` | M |
| D35.10 | Configuration packages | carrier only (Odoo load with xml ids) | versioned package of BP definitions, data elements, workflows with external ids; update/noupdate merge | Odoo `ir.model.data` + `load()` (D35) | L |
| D36.02 | Environment promotion and data refresh | core logic absent: database-per-tenant only | package export/import (D35.10) dev → test → prod; prod → test refresh with anonymisation | `frappe/frappe/core/doctype/scheduled_job_type/scheduled_job_type.py` (site jobs) | L |
| D36.05 | Attachment content search | core logic absent: declared fields only | text extraction (PDF/Office/OCR) into SearchIndexEntry with ACL filter at query | `openproject/db/migrate/tables/attachments.rb:32` (fulltext, tsvector); `mayan-edms/mayan/apps/ocr/models.py:18-40` | M |
| D36.07 | Point-in-time recovery | core logic absent: record histories only | WAL archiving + PITR at DB layer; journals for record-level restore | `openproject/app/models/backup.rb` | S |

### Legend
- Coverage class in "Why": **none** (no OSS code or schema), **schema only** (fields or JAXB/doctype definitions, no logic), **carrier only** (a generic record type could hold it, no domain semantics), **core logic absent** (adjacent mechanics exist, the defining algorithm does not).
- Paths are relative to `oss/`.
- Effort: S under 2 engineer-weeks, M 2–6, L over 6.

## Construction-specific core gaps

### 1. Schedule of Values and pay applications (AIA G702/G703) — D21.01, D21.02, D23.01, D23.03, D23.08
**Entities.**
- `SOVLine(id, contract_type{commitment,prime}, contract_id, code, description, cbs_id, scheduled_value dec, change_order_id null, version int, retainage_pct pct null, stored_materials_allowed bool)`; UK (contract, code, version). Initial lines generated from CommitmentLine/PrimeContract lines; each approved ChangeOrderLine inserts a new line or bumps version.
- `PayApplication(id, contract_type, contract_id, draw_id, number int, period_to d, status, original_sum, net_change_orders, contract_sum_to_date, total_completed_stored, retainage_work, retainage_stored, total_earned_less_retainage, previous_certificates, current_payment_due, balance_to_finish, submitted_at, certified_at, invoice_id)`.
- `PayApplicationLine(pay_app_id, sov_line_id, previous_completed (D), this_period (E), this_period_pct, materials_stored (F), total_completed_stored (G), pct_complete (G/C), balance_to_finish (H), retainage (I), approved_this_period, approved_stored, reviewer_note)`.
- GC owner application = aggregation PayApplication(contract_type=prime) whose lines reference prime SOV lines; each prime line can map to N sub SOV lines (`sov_map(prime_sov_line_id, sub_sov_line_id)`, proposed).

**State machine.** Draft → Submitted (sub) → Under Review (GC; per-line approved amounts may be reduced) → Approved → Certified (owner/architect) → Invoiced → Paid; Under Review → Rejected → Draft (revise and resubmit, same number). Guards: one open application per contract; `period_to` > previous period_to; Submitted requires compliance ok (D23.06) and, for numbers > 1, unconditional waiver for the previous payment (section 3).

**Algorithm.**
1. Open a new application: copy all active SOV lines; D = previous certified G − previous F (stored material installed this period moves into E), i.e. D(n) = D(n−1) + E(n−1).
2. Input per line E (amount or % of C: E = pct × C − D) and F (current stored balance).
3. G = D + E + F; reject when G > C (sub-line over-billing, same guard shape as `erpnext/erpnext/controllers/status_updater.py:492-541` allowance check with 0 tolerance); H = C − G.
4. I = rate(pct_complete) × (D + E) + rate_stored × F (rates from RetentionPolicy step function; section 2).
5. G702: L1 original sum = Σ original SOV values; L2 net COs = Σ approved CO values to period_to; L3 = L1 + L2; L4 = Σ G; L5a = Σ retainage on work; L5b = Σ retainage on stored; L5 = L5a + L5b; L6 = L4 − L5; L7 = L6 of the previous certified application; L8 current payment due = L6 − L7; L9 balance to finish incl. retainage = L3 − L6.
6. Invariants: Σ billed ≤ contract sum to date; L8 ≥ 0 unless a credit is explicitly allowed; rounding to currency at line level, totals summed from rounded lines.
7. On Certified: create payable Invoice (sub) or receivable Invoice (prime) for L8; post `this period` amounts to CostSheetPosting (actuals column) by SOV cbs_id; post retention held to RetentionEntry; update Commitment.per_billed.

### 2. Retainage — D21.05, D23.04, D22.07
**Entities.** `RetentionPolicy(id, rate_steps [{until_pct_complete, rate}], stored_rate pct, release_rule{substantial_completion,final,manual}, max_cap_pct null)`; `RetentionEntry(id, contract_id, sov_line_id, source_type{pay_app,release,adjustment}, source_id, held dec, released dec, status{held,partially_released,released})`; `RetentionRelease(id, contract_id, scope{partial,full}, amount, lines json, status, invoice_id)`.

**State machine.** RetentionRelease: Draft → Requested → Approved → Invoiced → Paid; Rejected → Draft. RetentionEntry status derives from Σ released vs Σ held per line.

**Algorithm.**
1. Rate at pay app n for a line = first step whose `until_pct_complete` ≥ line pct_complete (step-down, e.g. 10 % until 50 % then 5 %); apply either to cumulative work (recompute total held, entry = delta) or to new work only (policy flag, proposed).
2. Held(n) per line = rate × (D + E) + stored_rate × F; entry amount = Held(n) − Held(n−1) (can be negative on step-down or reduced F).
3. Cap: if `max_cap_pct`, held ≤ cap × C.
4. Release request validates amount ≤ Σ held − Σ released per line; on approval create an invoice of type retention release and RetentionEntry with released.
5. Cash flow: commitment curve holds `rate` share each period and releases total at the release period (D22.07).
6. Ledger shape reuses ERPNext Tax Withholding Entry semantics (taxable voucher ↔ withholding voucher, Under/Over/Settled; `erpnext/erpnext/accounts/doctype/tax_withholding_entry/tax_withholding_entry.py`).

### 3. Lien waivers — D23.05
**Entities.** `LienWaiverRequirement(contract_id, tier int, party_id, required_for{progress,final}, form_template_id)`; `LienWaiver(id, draw_id|payment_id, contract_id, sub_tier_party_id, conditionality{conditional,unconditional}, scope{progress,final}, jurisdiction_form, amount, through_date, signer_id, signed_at, document_id, signature_id, status)`.

**State machine.** Requested → Received → Signed (e-signature or uploaded notarised copy) → Accepted │ Rejected → Requested; Void.

**Algorithm.**
1. On pay app Approved, generate required waivers for the contract and every sub-tier party listed in requirements: conditional progress for `current_payment_due`, `through_date = period_to`.
2. When payment n is issued, generate unconditional progress waivers for payment n amount, due before release of payment n+1.
3. Final pay app: conditional final for the final amount; unconditional final after final payment.
4. Payment release guard: Payment for contract cannot be submitted while any required waiver for the draw is not Accepted, or any prior unconditional waiver is missing; implemented as Party/Invoice hold (`on_hold`, `hold_type = payments`, `erpnext/erpnext/buying/doctype/supplier/supplier.json`) set and cleared by the waiver state.
5. Amount check: waiver amount = payment amount (± tolerance), through_date ≥ period_to.

### 4. Change events → PCO/COR → change order pipeline — D20.01–D20.04, D23.10
**Entities.** ChangeEvent, ChangeEventLine (canonical model); `ChangeProposal(id, change_event_id, commitment_id|prime_contract_id, vendor_quote_ref, lines [{cbs_id, cost, markup_rows}], total, days, status{draft,requested,quoted,submitted,approved,rejected})` (PCO for subs, COR to owner); ChangeOrder, ChangeOrderLine; `markup_profile(contract_id, rows MarkupRow[], compound bool)`.

**State machine.**
- ChangeEvent: Open → Pending (estimates entered) → Approved │ Rejected │ Void; closes when all lines are realised by COs or voided.
- ChangeProposal: Draft → Requested (to vendor) → Quoted → Submitted (to owner for COR) → Approved │ Rejected.
- ChangeOrder: Draft → Pending → Approved │ Rejected │ Void; owner CO may bundle N CORs (N:1).

**Algorithm.**
1. ChangeEvent lines post `pending exposure` = Σ estimated cost to cost sheet column "Pending changes" per CBS (CostSheetPosting with source = event line).
2. Proposal total = Σ line cost + markups evaluated in row order: `on_net_total` = rate × net; `on_previous_row_total` = rate × running total (compound); `actual` fixed (ERPNext charge_type semantics, `purchase_taxes_and_charges.json`).
3. Commitment CO approval: commitment revised value += amount; SOV gets new/updated lines (version + 1); reverse pending exposure for the realised lines and post `approved commitment changes`; re-run budget control (revised budget ≥ commitments rule); contract dates += days.
4. Prime CO approval: prime SOV lines, revenue column, owner contract sum; margin recomputed.
5. Schedule impact: lines with days link to a fragnet (section 14); the CO carries the TIA result id.
6. Contingency: if CBS funding source is contingency, call section 5.
7. Log metrics from StateMilestone: days in each status, cycle time, change % = Σ approved / original contract.

### 5. Contingency and allowance drawdown — D20.08
**Entities.** ContingencyLine(project_id, cbs_id, kind{contingency,allowance}, original, drawn, remaining), ContingencyTransfer(contingency_line_id, change_order_id|budget_transfer_id, to_cbs_id, amount, posted_at), `contingency_owner_role` (proposed).

**State machine.** ContingencyTransfer: Proposed → Approved → Posted │ Rejected; Posted is immutable, reversal by negative transfer.

**Algorithm.**
1. On CO approval (or budget transfer) with funding = contingency: require remaining ≥ amount (hard rule) else route to owner approval.
2. Post −amount on contingency CBS "Revised budget" and +amount on target CBS (Σ = 0, same as budget transfer).
3. drawn += amount; remaining = original + adjustments − drawn.
4. Allowance lines: reconciliation at buyout, unused allowance returned to owner as deductive CO.
5. Forecast: projected contingency = remaining − Σ pending change exposure flagged to contingency − QRA P-target cost contingency shortfall (D14.07).

### 6. Transmittals — D26.02, D02.09
**Entities.** Transmittal(project_id, number, from_company_id, reason_for_issue, response_required_by, status, issued_at, cover_note), TransmittalItem(transmittal_id, document_revision_id, copies, format), TransmittalRecipient(transmittal_id, company_id, user_id, kind{to,cc}, acknowledged_at, responded_at, response_code).

**State machine.** Draft → Issued → Acknowledged (all `to` recipients) → Responded (if response required) → Closed; Draft → Cancelled; Issued → Superseded when a later transmittal re-issues the same document at a higher revision to the same recipient.

**Algorithm.**
1. Number from Sequence keyed (project, from_company, "TRN") under row lock (`mayan-edms/mayan/apps/sequences/managers.py:33`).
2. Issue: freeze item list; for each recipient company insert ObjectACL grants (view/download) on each listed revision (`mayan-edms/mayan/apps/acls/models.py:23-54`); send mail with links (`mayan-edms/mayan/apps/mailer/mailing_actions.py:74-91`); write Journal.
3. Start SLA clock `response_required_by` (working-day calendar, ERPNext SLA pattern); awaiting-response register = issued, response required, now > due, not responded.
4. Acknowledgement via link click or explicit action stamps `acknowledged_at`.
5. Review-workflow completion may auto-issue a transmittal (WorkflowTransition task).

### 7. Document numbering and revision schemes — D25.01, D25.02, D26.03
**Entities.** `NumberingScheme(project_id, document_type_id, pattern, unique_scope{project,project_org})` with tokens `{project}{org}{discipline}{type}{zone}{seq:n}`; Document.number; DocumentRevision(document_id, rev_code, rev_seq, phase{pre_issue_alpha,post_issue_numeric}, status_code, issued_at, version_id, superseded_by, supersede_reason); `RevisionScheme(alpha_sequence, skip_letters, numeric_start, transition_status)`.

**State machine (revision).** WIP → Issued for Review (rev A, B, C…) → Issued for Construction (rev 0) → revised IFC (1, 2, …) → As-Built; each new revision sets previous `superseded_by`; only one current revision per document.

**Algorithm.**
1. On document creation render pattern; `{seq}` from Sequence keyed by the rendered prefix; enforce UK per unique_scope; reject manual numbers that do not match pattern regex.
2. Next revision code: if phase alpha and target status is not IFC → next letter skipping configured letters (e.g. I, O); on first IFC status switch phase to numeric at `numeric_start`; numeric phase increments.
3. Each revision references an immutable DocumentVersion/DocumentFile set (Mayan); checksum duplicates rejected.
4. Supersede: new current revision marks previous superseded; transmittals of superseded revisions flagged to recipients.
5. Bulk import (D25.04) runs the same steps per row and reports per-cell errors.

### 8. Submittal register with back-calculated dates — D27.02, D27.03
**Entities.** SubmittalDetail (canonical model) + `SubmittalReviewStep(submittal_id, seq, party_id, planned_days int, started_at, returned_at, outcome)`; WorkItemRelation `precedes` to the linked Activity.

**State machine.** Pending (register row) → In Preparation → Submitted → Under Review (ball-in-court per step) → Returned: A (approved) / B (approved as noted) → Closed; C (revise and resubmit) / D (rejected) → Resubmission Required → In Preparation with revision + 1. Return code mandatory on the Returned transition (Mayan transition field pattern).

**Algorithm.**
1. required_on_site = linked activity early start (option: late start or a fixed date).
2. submit_by = required_on_site − lead_time_days (fabrication/delivery, working days of the supplier calendar) − Σ planned review days of all steps − buffer; subtraction walks the project calendar backwards (working-day walk, as SLA working-window computation run in reverse).
3. Recompute on every CPM run (D06) and on step edits; flag `late` when today > submit_by and status ∈ {Pending, In Preparation}; float = submit_by − forecast submit date.
4. Ball-in-court: current step party; days held per party = returned_at − started_at in working days; register aging by party.
5. Activity gating (optional): activity cannot start while linked submittal not Closed with A/B (ERPNext Stop-mode check shape, `erpnext/erpnext/stock/services/quality_inspection_service.py:84`).

### 9. Monte Carlo schedule risk analysis — D14.04, D14.07, D14.08
**Entities.** UncertaintyEstimate, QRARun(project_id, iterations, seed, sampling, correlation_matrix, data_date, status), QRAResult(run_id, activity_id, metric, percentiles, value), `RiskEventImpact(risk_id, activity_id, schedule_days_min/ml/max, cost_min/ml/max)` (proposed).

**State machine.** QRARun: Queued → Validating (schedule health gate, section 13 subset) → Running → Completed │ Failed │ Cancelled.

**Algorithm.**
1. Freeze network: activities, relationships, calendars, constraints, data date from the latest ScheduleRun.
2. Per activity remaining-duration distribution from UncertaintyEstimate (triangular, BetaPERT α = 1 + 4(m − a)/(b − a), β = 1 + 4(b − m)/(b − a) guarded for a = b, uniform, truncated normal ≥ 0, lognormal, trigen with percentile tails); uncertainty templates fill missing estimates by code value.
3. Sampling: seeded RNG (`numpy.random.default_rng(seed)` as `qsra_qcra_icsra/qsra_qcra/project.py:20-32`); Latin hypercube optional; correlation by Iman–Conover rank reordering using the correlation matrix.
4. Per iteration: sample durations; for each risk sample occurrence ~ Bernoulli(p) and if it occurs add sampled schedule/cost impact to linked activities; run full CPM forward/backward (same engine as D06, no leveling); record finish date, cost, per-activity critical flag.
5. Outputs: P-curves (P10…P90) for finish and cost; JCL = P(cost ≤ c ∧ finish ≤ t); criticality index = fraction of iterations critical; Spearman rank correlation of activity duration with finish (sensitivity); cruciality = criticality × sensitivity.
6. Contingency = P_target − deterministic (cost and schedule) written to QRAResult and proposed to ContingencyLine/BudgetChangeLog.
7. Reproducibility: store seed, iteration count, input snapshot hash.

### 10. P6-style resource leveler — D08.01–D08.03, D08.07
**Entities.** ScheduleOptions level_* fields; ResourceAssignment.leveling_delay, Activity.leveling_delay, remaining early dates; `LevelingLog(run_id, activity_id, resource_id, contending_activity_id, delay dur, reason{over_capacity,float_limit,priority}, unresolved bool)` (proposed).

**State machine.** Leveling run: Requested → CPM refreshed → Leveling → Completed (with log) │ Failed; project lock held throughout (JobDefinition.project_lock_key).

**Algorithm.**
1. Run CPM (D06) to obtain early dates and total float; build capacity per resource/day = calendar minutes × max_units × (1 + max_overalloc_pct) (D05.04).
2. Fixed load: in-progress work remaining, activities with actuals/constraints that cannot move, assignments in other projects with priority ≥ `other_project_priority` when `consider_other_projects`.
3. Candidate list = unstarted (and remaining of in-progress per option) activities with leveled resources, sorted by `leveling_priority_list` keys (activity priority, early start, total float, code/UDF values), ties by activity code.
4. Serial pass in time order: for each candidate whose predecessors are already placed, earliest start = max(logic-driven date from placed predecessors, early start); test the time-phased demand (DayAssignment spread for that start, curve-aware) against remaining capacity for every leveled resource; if infeasible, advance to next window where the resource frees capacity (scoreboard search, TaskJuggler `ResourceScenario.rb:830-905` idea).
5. If `level_within_float`, cap delay at total float − `preserve_min_float`; when exceeded keep earliest start, mark unresolved and log over-allocation.
6. Commit placement: book demand; leveling_delay = leveled start − early start; set remaining early start/finish; successors become eligible.
7. Afterwards recompute late dates from unleveled backward pass (or leveled per `preserve_scheduled_dates` option) and floats; persist LevelingLog and Project.last_level_date.

### 11. Timesheet → assignment actuals posting — D32.04, D10.04, D07.09
**Entities.** Timesheet, TimeEntry (approved/unapproved hours split), TimesheetAudit, ResourceAssignment actual fields, `ActualsPosting(time_entry_id, assignment_id, regular_hours, overtime_hours, cost, posted_at, reversed_by)` (proposed, idempotency).

**State machine.** Timesheet per (resource, period, project): Active → Submitted → RM-Approved → PM-Approved (or single-level) │ Rejected → Active; PM-Approved lines become postable; posted lines are locked; reopen requires reversal postings.

**Algorithm.**
1. Select PM-Approved TimeEntry lines with assignment_id not yet posted (or lines with activity_id only: resolve assignment by (activity, resource), create one if the activity allows).
2. Per line: actual_regular_units += approved_hours; actual_overtime_units += approved_ot_hours.
3. Cost: actual_regular_cost += hours × effective rate (rate source/index/override on the assignment, effective-dated ResourceRate at entry date); overtime × overtime_factor.
4. Remaining: if `auto_compute_actuals`, remaining = at-completion − actual (≥ 0) per duration type; else keep remaining units unless the resource reported remaining (TaskJuggler time-sheet record pattern `taskjuggler/lib/taskjuggler/TimeSheets.rb:244-275`).
5. Activity: actual start = min entry date if not set, status In Progress; actual finish only when the resource marks finished and all assignments complete (LibrePlan `work_report_line.finished`).
6. Write ActualsPosting rows; overhead-code lines post to overhead cost account and skip project cost; then trigger Apply Actuals reschedule (D10.04) and EV refresh.

### 12. HSE: observations, incidents, permits, TRIR — D30.01, D30.02, D30.04
**Entities.** SafetyObservation, Incident, IncidentPerson, CorrectiveAction (reused), WorkPermit (+ `permit_approval(permit_id, role, approver_id, approved_at)`, `gas_test(permit_id, taken_at, o2, lel, h2s, co, ok)`), `OSHALogEntry(incident_person_id, case_no, classification{death,days_away,restricted,other_recordable}, days_away, days_restricted)` (proposed), hours denominator from TimeEntry/DailyLog manpower.

**State machines.**
- Incident: Reported → Under Investigation → Actions Assigned → Closed (all CorrectiveAction resolutions completed, ERPNext CAPA auto-complete pattern) │ Reopened.
- WorkPermit: Requested → Approved (all required approvals) → Active (only within valid_from..valid_to and latest gas test ok when type requires) → Suspended (gas test fail, stop-work) → Active │ Closed │ Expired (valid_to passed, timer job).

**Algorithm.**
1. Recordability per IncidentPerson: osha_recordable if treatment beyond first aid, days away, restricted, loss of consciousness, or fatality.
2. Period hours H = Σ TimeEntry hours for project/company in period (fallback Σ DailyLog manpower hours).
3. TRIR = recordable cases × 200 000 / H; LTIR = lost-time cases × 200 000 / H; DART = (days-away + restricted/transfer cases) × 200 000 / H; severity rate = days away × 200 000 / H.
4. OSHA 300 rows per recordable case, 300A annual totals (cases by class, days, hours).
5. Leading indicators: observations by category/company/week, safe:unsafe ratio.
6. Permit guard: Active transition condition evaluated server-side (WorkflowTransition.condition) on time window and approvals; Expired set by scheduled job.

### 13. DCMA 14-point assessment — D06.10, D14.08
**Entities.** `ScheduleQualityRun(id, schedule_run_id, baseline_id, data_date, results json)`, `ScheduleQualityFinding(run_id, check_no, activity_id, relationship_id, value)` (proposed).

**State machine.** None beyond run status (Queued → Completed │ Failed).

**Algorithm.** Population = incomplete activities excluding LOE, WBS summary and (for checks 1, 6, 8) milestones; working days from activity calendars.
1. Logic: activities missing predecessor or successor ≤ 5 %.
2. Leads: relationships with negative lag = 0.
3. Lags: relationships with positive lag ≤ 5 %.
4. Relationship types: FS ≥ 90 %.
5. Hard constraints (must start/finish on, start/finish on or before, mandatory) ≤ 5 %.
6. High float: total float > 44 working days ≤ 5 %.
7. Negative float: count = 0.
8. High duration: remaining/original duration > 44 working days ≤ 5 %.
9. Invalid dates: actual dates after data date or forecast dates before data date = 0.
10. Resources: activities with duration > 0 and no resource/cost assignment (report).
11. Missed tasks: of activities with baseline finish ≤ data date, finished after baseline finish or not finished ≤ 5 %.
12. Critical path test: add a large delay (e.g. 600 working days) to one critical activity in a scratch copy, rerun CPM; project finish must slip by the same amount, else the critical path is broken.
13. CPLI = (critical path length + total float of the end) / critical path length ≥ 0.95.
14. BEI = activities actually completed / activities with baseline finish ≤ data date ≥ 0.95.
Write per-check value, threshold, pass flag and offending objects.

### 14. Fragnet and time impact analysis — D06.12, D20.06
**Entities.** `Fragnet(id, project_id, change_event_id, name, activities json, relationships json, tie_ins [{existing_activity_id, new_activity_ref, type, lag}])`, `TIA(id, fragnet_id, scenario_project_id, data_date, unimpacted_finish, impacted_finish, delta_days, milestone_deltas json, status)` (proposed).

**State machine.** Fragnet: Draft → Ready → Analysed → Accepted (CO days granted) │ Rejected. TIA run: Queued → Completed │ Failed.

**Algorithm.**
1. Unimpacted: copy-on-write scenario of the project statused to the event data date (actuals and remaining as of that date), run CPM; record finish and key milestones.
2. Impacted: same scenario + fragnet activities and tie-in relationships (and changed durations), run CPM with identical options.
3. Delta = impacted − unimpacted finish (working days on project calendar) and per milestone; float consumption per path.
4. Concurrency check: delays already present in the unimpacted run on the driving path are reported to separate excusable vs non-excusable (windows analysis optional: repeat per update window).
5. Accepted TIA writes CO.days and, on approval, merges fragnet into the live schedule (scenario merge, D06.11) and updates contract dates.

## Known defects found in OSS sources

| # | Source location | Defect | Impact on reuse |
|---|---|---|---|
| 1 | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java:65-78` with `HoursCostCalculator.java:82-102` | Advance measurements are already cumulative progress; `accumulateResult` accumulates them again, so BCWP is a sum of cumulative values (overstated; marked inferred in D11) | Do not re-accumulate cumulative advances |
| 2 | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/HoursCostCalculator.java:82-102` | BCWP computed with `MathContext(2, HALF_UP)` (two significant digits): 1 234 h becomes 1 200 h | Use full precision |
| 3 | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java:131-148` | `getValueAt` returns the first later point when the date has no key, not the previous point | Carry previous value forward |
| 4 | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/CompanyEarnedValueCalculator.java:142-154` | Company BCWP returned without `accumulateResult` while BCWS/ACWP are accumulated (`:53-65,117-139`): curve mixes cumulative and per-day series | Accumulate consistently |
| 5 | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/HoursCostCalculator.java:114-183` | BCWS adds whole hours per day and sums leftover minutes across all assignments onto the last assignment day (+1 h if 30–60 min, +min/60 if > 60) | Daily BCWS distorted; spread minutes per day |
| 6 | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/HoursCostCalculator.java:207-232` | ACWP is hours, so CPI/EAC compare hours, not money | Apply cost rates before EV |
| 7 | `libreplan/libreplan-business/src/main/java/org/libreplan/business/orders/daos/SumExpensesDAO.java:69-184` | Incremental expense sums compute the edit delta from a previous value fetched in another transaction (possible race / stale delta, inferred) | Recompute from lines or lock |
| 8 | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/cost/copy_cost_item_values.py:54` | Removes destination values using `source` as parent (observed defect, D17) | Fix before reuse |
| 9 | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/recalculate_schedule.py:170-178` | Open ends silently tied to dummy start/finish nodes, never reported | Report open ends explicitly |
| 10 | `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java:535-539,772-790,932-935` | External early start / late finish always applied; "ignore relationships to/from other projects" option never consulted | Branch on option |
| 11 | `mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java:845-858` (read) vs `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java` | Retained logic / progress override / actual dates, open-ends-critical, SS-lag-from-early-start, float-per-project-finish read but not used: scheduler always behaves as retained logic | Results diverge from P6 when options set |
| 12 | `mpxj/src/main/java/org/mpxj/cpm/DepthFirstGraphSort.java:89-117` (TODO at `:96`) | Cycle detection throws `CycleException` without the cycle path; no loop breaking | Report full cycle |
| 13 | `mpxj/src/main/java/org/mpxj/primavera/PrimaveraXERFileWriter.java:1553-1563` | XER writer emits constant WBS EV settings (`ev_compute_type="EC_Cmp_pct"`, `ev_etc_compute_type="EE_PF_cpi"`, `ev_user_pct=6`, `ev_etc_user_value=0.88`); no reader maps them | Round-trip loses EV settings |
| 14 | `mpxj/src/main/java/org/mpxj/primavera/XerFile.java:254` (read set `PrimaveraXERFileReader.java:369-414`) | Tables outside the 43-table read set are discarded at parse time | Preserve raw tables |
| 15 | `mpxj/src/main/java/org/mpxj/primavera/XerFile.java:333-336` | `%R` values beyond the `%F` column count silently dropped | Data loss on malformed files |
| 16 | `mpxj/src/main/java/org/mpxj/primavera/XerFile.java:449,619` | Field typing by column name across all tables; only `projcost.target_qty` collision handled (other same-named columns with different types would be mis-typed, inferred) | Type per (table, column) |
| 17 | `mpxj/src/main/java/org/mpxj/AccrueType.java:35-39` / `mpxj/src/main/java/org/mpxj/ExpenseItem.java:285-304` | `AccrueType` carried but never used to time-phase expenses | Implement accrual spreading |
| 18 | `mpxj/src/main/java/org/mpxj/primavera/TableContextReader.java:943-986` | Max units per time effective-dated but never multiplied by calendar hours; the P6 scheduler ignores max units (D05) | Resource-dependent durations and leveling need capacity |
| 19 | `qsra_qcra_icsra/qsra_qcra/task.py:48-58` | PERT-beta shape parameters divide by (b − a); a = b not guarded | Guard degenerate estimates |
| 20 | `qsra_qcra_icsra/qsra_qcra/task.py:60-92` | Normal distribution unbounded, can sample negative durations/costs | Truncate at 0 |
| 21 | `qsra_qcra_icsra/qsra_qcra/task.py:96-123`, `project.py:34-69` | Duration and cost sampled independently (zero correlation); project duration = Σ durations of tasks pre-flagged critical (no network, no path switching) | Unusable for schedule QRA as is |
| 22 | `qsra_qcra_icsra/qsra_qcra/project.py:141-185` | Sensitivity uses Pearson ρ, not Spearman rank | Use rank correlation for skewed inputs |
| 23 | `frappe/frappe/model/base_document.py:1004-1048`, `frappe/frappe/model/document.py:1499-1520` | Server enforces `reqd` only; `mandatory_depends_on` evaluated client-side (inferred) | API writes bypass conditional mandatory rules |
| 24 | `openproject/app/workers/represented_webhook_job.rb` (D34 cites file, no line) | Outbound webhook signature is `X-OP-Signature: sha1=HMAC_SHA1(secret, body)` only; no status-change or delete events | Weak signature algorithm for integrations |
