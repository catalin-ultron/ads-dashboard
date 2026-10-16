# D15 Portfolio and Capital Planning

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D15.01 | Ideas and project proposals | OpenProject `Projects::CreationWizard` (project initiation request → artifact work package); LibrePlan `OrderStatusEnum` (PRE_SALES, OFFERED); P6 `ProjectType.Status` (Requested, What-If) | partial | OpenProject submits an initiation request as a typed work package whose status workflow acts as evaluation; no idea entity with scores/conversion |
| D15.02 | Scoring and prioritization | OpenProject calculated-value project custom fields (formula) + `weighted_item_list`; P6 `StrategicPriority`, `OverallProjectScore` | partial | Formula engine (Dentaku) over project attributes gives weighted scores; no ranking/efficient frontier |
| D15.03 | Capital plans (multi-year budgets) | ERPNext `Budget` (against Project, from/to fiscal year, period distribution); P6 `ProjectSpendingPlanType`, `EPSSpendingPlanType` | partial | ERPNext time-phases a project budget per account across fiscal years; no plan-period/line-item entity |
| D15.04 | Portfolio scenarios and what-if | P6 `ProjectType.Status = What-If`, `ProjectPortfolioType.IncludeWhatIfProjects` | none | Flags only; no scenario comparison or optimisation |
| D15.05 | Portfolio budget planning and approvals | ERPNext `Budget` (submittable, revisions); P6 `EPSBudgetChangeLogType` | partial | Approval = document submit; no push of approved amount into project original budget |
| D15.06 | Portfolio measures / KPIs | OpenProject calculated values (recompute on change) | partial | Current value only; no periodic snapshots or targets |
| D15.07 | Programs | OpenProject `workspace_type` {project, program, portfolio} + nested set; budget aggregation over `self_and_descendants`; P6 `ProjectPortfolioType` | partial | Hierarchy and budget/spend rollups exist; no schedule or risk rollup |
| D15.08 | Benefits tracking (ROI, NPV, IRR, payback) | P6 `BenefitPlan` per month, `AnnualDiscountRate`, `TotalBenefitPlan` | partial | Data fields only; no financial-metric code in any source (grep for npv/irr/payback empty) |
| D15.09 | Capital planning sheets → project shells | OpenProject project templates + creation wizard; ERPNext project template copy | partial | Template-based project creation exists; no planning sheet |

## Storage model

### P6 portfolio fields (`mpxj/src/main/java/org/mpxj/primavera/schema/`)

| Type | Fields |
|---|---|
| `ProjectType` | `Status` {Planned, Active, Inactive, What-If, Requested, Template}, `StrategicPriority:int`, `OverallProjectScore:int`, `RiskScore:int`, `RiskLevel`, `RiskExposure`, `OriginalBudget`, `ProposedBudget`, `CurrentBudget`, `TotalFunding`, `TotalSpendingPlan`, `TotalSpendingPlanTally`, `TotalBenefitPlan`, `TotalBenefitPlanTally`, `AnnualDiscountRate:double`, `ProjectForecastStartDate`, `ProjectSpendingPlan[]`, `ProjectFunding[]`, `ProjectBudgetChangeLog[]` |
| `EPSType` | `Id:string(40)`, `Name:string(100)`, `ParentObjectId` (tree), `OBSObjectId`, `AnticipatedStartDate`, `AnticipatedFinishDate`, `OriginalBudget`, `ProposedBudget`, `CurrentBudget`, `DistributedCurrentBudget`, `CurrentVariance`, `UndistributedCurrentVariance`, `UnallocatedBudget`, `TotalFunding`, `TotalSpendingPlan(Tally)`, `TotalBenefitPlan(Tally)`, `LastSummarizedDate`, `Spread: EPSProjectWBSSpreadType` |
| `ProjectSpendingPlanType` / `EPSSpendingPlanType` | `Date` (month bucket), `SpendingPlan:double`, `BenefitPlan:double`, owner FK (project+WBS or EPS) |
| `EPSBudgetChangeLogType` | `EPSObjectId`, `ChangeNumber`, `Date`, `Amount`, `Reason`, `Responsible`, `Status` {Pending, Approved, Not Approved} |
| `EPSFundingType` | `EPSObjectId`, `FundingSourceObjectId`, `Amount`, `FundShare` |
| `ProjectPortfolioType` | `Name:string(40)`, `Description:string(255)`, `Type` {Manual, Auto-Maintained, Filtered}, `IncludeClosedProjects`, `IncludeWhatIfProjects`, `UserObjectId`, `PortfolioUserIdArray`, `MemberProject: PortfolioTeamMemberType[]` (`Id`, `Name`, `ObjectId`) |

### OpenProject workspaces, phases, initiation, calculated fields

| Table / model | Fields | Notes |
|---|---|---|
| `projects` | `name`, `identifier` (unique lower), `parent_id`, `lft`, `rgt` (nested set), `active`, `templated`, `public`, `status_code` (0..5), `status_explanation`, `settings jsonb` | `openproject/db/migrate/tables/projects.rb:35-52` |
| `Project.workspace_type` | {project, program, portfolio}; allowed parents: project ← {portfolio, program, project}, program ← {portfolio}, portfolio ← none | `openproject/app/models/project.rb:44-54` |
| `project_phase_definitions` | `name` (unique), `position`, `color_id`, `start_gate bool`, `start_gate_name`, `finish_gate bool`, `finish_gate_name` | `openproject/db/migrate/tables/project_phase_definitions.rb` |
| `project_phases` | `project_id`, `definition_id`, `start_date`, `finish_date`, `active bool` (+ `duration`, per `RescheduleService`) | unique (project_id, definition_id) (`project_phases.rb`) |
| `Projects::CreationWizard` settings (jsonb store) | `project_creation_wizard_enabled`, `_artifact_name` ∈ {project_creation_wizard, project_initiation_request, project_mandate}, `_work_package_type_id`, `_status_when_submitted_id`, `_send_confirmation_email`, `_assignee_custom_field_id`, `_notification_text`, `_work_package_comment`, `_artifact_work_package_id`, `_artifact_export_type` (default attachment), `_artifact_export_storage` | `openproject/app/models/projects/creation_wizard.rb` |
| `custom_fields` (format `calculated_value`) | `formula` jsonb {`formula`: string, `referenced_custom_fields`: [ids]}; operators + - * / % ^ comparisons AND/OR; functions IF AND OR XOR NOT SWITCH MIN MAX SUM AVG ROUND ROUNDDOWN ROUNDUP ABS; CASE/WHEN; tokens `{{cf_N}}` | `openproject/app/models/custom_field/calculated_value.rb:37-148` |
| `hierarchical_items` (format `weighted_item_list`) | `label`, `short`, `weight` (renamed from `score`), `parent_id`, `sort_order`, `custom_field_id` | `openproject/db/migrate/tables/hierarchical_items.rb`, `db/migrate/20251103123548_rename_item_score_to_weight.rb` |
| `calculated_value_errors` | `customized` (project), `custom_field_id`, error payload | `openproject/app/models/acts_as_customizable/calculated_value.rb:103-126` |

### ERPNext capital-style budget (`erpnext/erpnext/accounts/doctype/budget/budget.json`)
`budget_against` {Cost Center, Project}, `project`, `cost_center`, `company`, `account` (required), `budget_amount`, `from_fiscal_year`, `to_fiscal_year`, `budget_start_date`, `budget_end_date`, `distribution_frequency` {Monthly, Quarterly, Half-Yearly, Yearly}, `distribute_equally`, child `budget_distribution` (`start_date`, `end_date`, `amount`, `percent`), `budget_distribution_total`, `revision_of`, Stop/Warn/Ignore actions per MR/PO/actual/cumulative; submittable.

### LibrePlan order pipeline state
`order_table.state` enum `OrderStatusEnum` {PRE_SALES 0, OFFERED 1, OUTSOURCED 2, ACCEPTED 3, STARTED 4, ON_HOLD 5, FINISHED 6, CANCELLED 7, STORED (ARCHIVED) 8}; with `work_budget`, `materials_budget`, `budget_margin`, `hours_margin` (`libreplan/libreplan-business/src/main/java/org/libreplan/business/orders/entities/OrderStatusEnum.java:34-44`, `libreplan/libreplan-business/src/main/resources/org/libreplan/business/orders/entities/Orders.hbm.xml:112-137`).

## Algorithms and logic

### Initiation request submission (OpenProject)
`SubmitArtifactService#call`: if the project's artifact work package exists, re-upload the artifact; else `CreateArtifactWorkPackageService` (`openproject/app/services/projects/creation_wizard/submit_artifact_service.rb:39-70`). Creation: `WorkPackages::CreateService` with type = wizard type (default first enabled type), status = configured submitted status (default first status of the type variant), subject from artifact name, assignee from a configured user custom field, journal comment, PDF attachment if export type is attachment; on success store the WP id on the project; then optional confirmation mail and upload to a project storage (`create_artifact_work_package_service.rb:49-105`). On each status change of that WP the PDF artifact is regenerated and re-uploaded (`reupload_artifact_on_status_changes_service.rb:43-69`). Evaluation workflow = the WP type's status workflow (D24).

### Weighted scoring via calculated values (OpenProject)
`calculate_custom_fields(fields)`: given = values of enabled referenced custom fields (excluding those being computed), converted with `as_calculable`; to_compute = {column_name → formula without patterns}; Dentaku `calculator.store(given)` then `solve(to_compute)` resolves inter-dependencies; non-numeric/boolean results become nil with errors persisted to `calculated_value_errors` (`openproject/app/models/acts_as_customizable/calculated_value.rb:41-126`). `affected_calculated_fields` computes the transitive closure of calculated fields referencing changed fields for recomputation (`openproject/app/models/custom_field/calculated_value.rb:96-117`). Weighted item list contributes the selected item's weight to formulas (inferred from `FIELD_FORMATS_FOR_FORMULA` including `weighted_item_list`, `:78`). A weighted score Σ wᵢ·sᵢ is expressible as one formula field.

### Program/portfolio rollups (OpenProject budgets)
`applicable_projects = project.self_and_descendants` (`openproject/modules/budgets/app/models/budgets/project_aggregation.rb:39-41`); budgeted base/material/labor/total and spent ratio across that subtree (`aggregated_budgets.rb:39-65`, `aggregated_budgets_with_spend.rb:48-54`).

### Phase-gate scheduling (OpenProject)
Activation upserts phases for the given definitions with `active` and reschedules following phases from the first definition by position (`openproject/app/services/project_phases/activation_service.rb:44-82`). Reschedule: for each active following phase, if both dates set and duration > 0, place `duration` working days starting at `from`, next `from` = finish + 1; partial phases snap start to next working day and finish to max(from, finish) on a working day (`openproject/app/services/project_phases/reschedule_service.rb:47-109`).

### Time-phased budget (ERPNext)
Periods and equal/manual distribution as in D13 (`erpnext/erpnext/accounts/doctype/budget/budget.py:242-375`); accumulated budget to date = Σ distribution rows starting on/before the posting date (`:813-830`). Multi-year span via `from_fiscal_year`/`to_fiscal_year` (`:86-110`).

## State machines and workflows
- LibrePlan order: PRE_SALES → OFFERED → ACCEPTED → STARTED → (ON_HOLD ↔ STARTED) → FINISHED → STORED; CANCELLED; OUTSOURCED (enum only; no transition guards found).
- P6 project status: Requested / What-If → Planned → Active → Inactive; Template.
- OpenProject initiation request: WP created in "submitted" status → type workflow transitions (role/author/assignee-guarded) → each transition re-exports the artifact.
- ERPNext Budget: Draft → Submitted → Cancelled; revise = cancel + amended copy with `revision_of`.
- OpenProject phase: inactive ↔ active; gates are flags on the definition (start/finish gate names), no gate approval state.

## Cross-domain links
- Portfolio hierarchy (EPS, workspace types) is the enterprise structure (D01) and permissions (D02).
- Budgets, spending/benefit plans and funding shared with D13, D17 (budget/forecast) and D18 (funding).
- Risk exposure and score inputs from D14; status codes from D12.05.
- Proposal workflow runs on the workflow engine (D24); artifacts stored in documents/storages (D25).
- Project templates and copy services relate to WBS templates (D03).
- Measures and snapshots feed analytics (D33).

## Gaps
- Idea entity (title, sponsor, proposed cost, benefit, scores, status Draft → Submitted → Under Review → Approved/Rejected → Converted) and conversion into a project from a template.
- Ranking and efficient frontier: sort by weighted score; frontier = non-dominated (cost, value) set.
- Capital plan: plan period, fiscal-year start, horizon, line items per project × year with funding source, priority, included/excluded; totals vs targets.
- Scenarios: copy of line items with shifted starts and budget overrides; compare totals and resource capacity (D08); 0/1 knapsack (max Σ score s.t. Σ cost_y ≤ budget_y ∀ years) via DP or MILP; approve → commit plan and push approved amounts to project original budget.
- Measure history: scheduled job storing (measure, project, period, value) with targets.
- Program rollups of schedule (min start / max finish), EV and risk.
- Benefits: NPV = Σ (Bₜ − Cₜ)/(1+r)^t with r = `AnnualDiscountRate` (monthly compounding of P6 monthly buckets), IRR = root of NPV(r)=0 (Newton/bisection), ROI = (ΣB − ΣC)/ΣC, payback = first t where cumulative B − C ≥ 0.
- Unifier-style planning sheet (projects × fiscal years) with auto-created project shells from approved items.
