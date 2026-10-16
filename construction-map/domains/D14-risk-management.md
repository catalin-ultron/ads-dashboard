# D14 Risk Management

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D14.01 | Risk register | MPXJ P6 schema `RiskType`, `ActivityRiskType`, `RiskCategoryType` | partial | Full P6 register shape (threat/opportunity, RBS tree, exposure window, activity links); no MPXJ model class, reader or logic |
| D14.02 | Probability-impact scoring | P6 schema `RiskMatrixType`, `RiskMatrixScoreType`, `RiskThresholdType`, `RiskThresholdLevelType`, `RiskImpactType` | partial | Matrix up to 9 severities, scoring method enum; computation not implemented in OSS |
| D14.03 | Risk responses | P6 schema `RiskResponsePlanType`, `RiskResponseActionType`, `RiskResponseActionImpactType` | partial | Plan/action costs and post-response impacts as data; no budget push logic |
| D14.04 | Quantitative risk analysis (Monte Carlo) | `qsra_qcra_icsra` (cloned) `Project.simulate`, `Task.sample_*`; MPXJ `cpm.PrimaveraScheduler` for a network pass | partial | Three-point sampling (point/normal/uniform/PERT-beta/triangular), P10..P90, JCL, Pearson sensitivity; no network CPM per iteration, no risk events, no correlation, no criticality index |
| D14.05 | Uncertainty templates | none | none | Nothing in sources |
| D14.06 | Risk score rollup and exposure | P6 schema `RiskType.Exposure`, `ProjectType.RiskExposure/RiskScore/RiskLevel` | partial | Stored aggregates only |
| D14.07 | Contingency determination | `qsra_qcra_icsra` percentiles; LibrePlan `budgetMargin`/`hoursMargin` | partial | P-values available; contingency = P-target − deterministic not coded; LibrePlan applies flat % margin |
| D14.08 | Schedule health check before QRA | none in assigned sources | none | DCMA-style checks absent (see Gaps) |
| D14.09 | Risk register data exchange | MPXJ P6 PMXML JAXB binding of risk types | partial | Types bound for PMXML (de)serialization; MPXJ readers/writers do not map them to its model |

## Storage model

### P6 risk register (`mpxj/src/main/java/org/mpxj/primavera/schema/`)

| Type | Fields | Keys / cardinality |
|---|---|---|
| `RiskType` | `ObjectId:int`, `Id:string(40)`, `Name:string(200)`, `Type` {Threat, Opportunity}, `Status` {Proposed, Open, Active, Rejected, Managed, Impacted}, `RiskCategoryObjectId`, `Cause`, `Effect`, `Description`, `Note` (each string(4000)), `IdentifiedDate`, `IdentifiedByResourceObjectId`, `ResourceObjectId` (owner), `ExposureStartDate`, `ExposureFinishDate`, `Exposure:double`, `Score:int`, `ScoreColor`, `ScoreText:string(40)`, `ProbabilityThresholdId`, `ScheduleThresholdId`, `CostThresholdId`, `ImpactThresholdValues:int`, `ResponseTotalCost:double`, `ProjectObjectId`, `UDF[]` | N : 1 project (`RiskType.java`) |
| `ActivityRiskType` | `ActivityObjectId`, `RiskObjectId`, `ProjectObjectId` | M : N risk ↔ activity (`ActivityRiskType.java`) |
| `RiskCategoryType` | `Name:string(40)`, `ParentObjectId`, `SequenceNumber` | self tree = RBS (`RiskCategoryType.java`) |
| `RiskThresholdType` | `Name:string(40)`, `Level:int` (number of levels), `ThresholdType` {Probability, Tolerance, Schedule, Cost, Relative Schedule, Relative Cost, User Defined} | global (`RiskThresholdType.java`) |
| `RiskThresholdLevelType` | `RiskThresholdObjectId`, `Level:int`, `Code:string(10)`, `Name:string(40)`, `Color`, `Range:string(100)`, `ProbabilityRange:double`, `ScheduleRange:double`, `CostRange:double`, `ToleranceRange:int`, `ThresholdType` | N : 1 threshold (`RiskThresholdLevelType.java`) |
| `RiskMatrixType` | `Name:string(40)`, `Description`, `ProbabilityThresholdLevel:int`, `ImpactThresholdLevel:int`, `RiskScoringMethod` {Highest, Average of Impacts, Average of Individual Scores} | global (`RiskMatrixType.java`) |
| `RiskMatrixScoreType` | `RiskMatrixObjectId`, `ProbabilityThresholdLevel:int`, `Severity1..Severity9:int`, `Severity1Label..Severity9Label:string(40)` | one row per probability level (`RiskMatrixScoreType.java`) |
| `RiskMatrixThresholdType` | `RiskMatrixObjectId`, `RiskThresholdObjectId` | M : N matrix ↔ impact thresholds (`RiskMatrixThresholdType.java`) |
| `RiskImpactType` (pre-response) | `RiskObjectId`, `RiskThresholdObjectId`, `RiskThresholdLevelObjectId`, `RiskThresholdLevelCode/Name` | one level per (risk, threshold) (`RiskImpactType.java`) |
| `RiskResponsePlanType` | `Id`, `Name:string(200)`, `RiskObjectId`, `ResponseType` {Avoid, Transfer, Reduce, Accept, Exploit, Facilitate, Enhance, Reject}, `IsActive:boolean`, `PlannedStartDate`, `PlannedFinishDate`, `StartDate`, `FinishDate`, `PlannedCost`, `ActualCost`, `RemainingCost`, `Score`, `ScoreColor`, `ScoreText` | N : 1 risk (`RiskResponsePlanType.java`) |
| `RiskResponseActionType` | `Id`, `Name:string(200)`, `RiskResponsePlanObjectId`, `RiskObjectId`, `ActivityObjectId` (linked activity), `ResourceObjectId` (owner), `Status` {Proposed, Sanctioned, Rejected, In Progress, Complete}, planned/actual dates, `PlannedCost`, `ActualCost`, `RemainingCost`, `Score`, `ScoreColor`, `ScoreText` | N : 1 plan (`RiskResponseActionType.java`) |
| `RiskResponseActionImpactType` (post-response) | `RiskResponseActionObjectId`, `RiskObjectId`, `RiskThresholdObjectId`, `RiskThresholdLevelObjectId` | one level per (action, threshold) (`RiskResponseActionImpactType.java`) |
| `ProjectType` risk aggregates | `RiskMatrixObjectId`, `RiskMatrixName`, `RiskExposure:double`, `RiskScore:int`, `RiskLevel` {Very High, High, Medium, Low, Very Low}; embeds `Risk[]`, `ActivityRisk[]`, `RiskImpact[]`, `RiskResponsePlan[]`, `RiskResponseAction[]`, `RiskResponseActionImpact[]` | (`ProjectType.java`) |

MPXJ grep finds no `getRisk`/`RiskType` use outside `primavera/schema/`, so risks survive only through raw JAXB objects.

### Quantitative analysis input (`qsra_qcra_icsra`, MIT, cloned)
`Task` (`qsra_qcra_icsra/qsra_qcra/task.py:9-35`): `task_id`, `name`, `a_dur`, `m_dur`, `b_dur` (optimistic/most likely/pessimistic duration), `a_cost`, `m_cost`, `b_cost`, `dist_type` ∈ {point, normal, uniform, beta, triangular}, `is_critical: bool`. Loaded from CSV/XLSX with required columns checked (`qsra_qcra_icsra/qsra_qcra/data.py:5-62`). `Project(tasks, n_iters=10_000, seed)` with `numpy.random.default_rng(seed)` (`project.py:20-32`).

## Algorithms and logic

### Distribution parameters and sampling (`qsra_qcra_icsra/qsra_qcra/task.py`)
- PERT mean = (a + 4m + b) / 6; σ = (b − a) / 6; min = a, max = b, for duration and cost (`:37-46`).
- PERT-beta shapes with λ = 4: α = 1 + 4(m − a)/(b − a), β = 1 + 4(b − m)/(b − a); sample u ~ Beta(α, β), value = a + u(b − a) (`:48-58,82-85`). Division by zero when a = b (edge case not guarded).
- normal: N(mean, σ) unbounded (can go negative); uniform: U(a, b); triangular: Tri(a, m, b); point: constant mean (`:60-92`). Cost sampling is a duplicate with cost parameters (`:96-123`). Duration and cost of the same task are sampled independently (zero correlation).

### Simulation (`qsra_qcra_icsra/qsra_qcra/project.py:34-69`)
1. For each task draw `n_iters` duration and cost samples (vectorized), stack into task × iteration matrices.
2. Project duration per iteration = Σ durations of tasks flagged `is_critical` (fixed critical path, no network logic, no path switching).
3. Project cost per iteration = Σ all task costs.

### Outputs
- `summarise`: P50/P90 of duration and cost (`numpy.percentile`, linear interpolation) (`:73-89`); `percentiles`: P10..P90 deciles table (`:93-112`).
- `joint_probability(cost_target, duration_target)` = mean(cost ≤ target ∧ duration ≤ target) = JCL (`:115-123`).
- `correlation`: Pearson ρ(duration, cost), 0 on zero variance (`:127-136`).
- `sensitivity(top_n)`: Pearson ρ between each task's samples and total (duration only for critical tasks), ranked by |ρ| (`:141-185`). Not Spearman rank.

### Network forward pass for a rebuild
MPXJ exposes `org.mpxj.cpm.Scheduler.schedule(ProjectFile, LocalDateTime)` with `PrimaveraScheduler` and `MicrosoftScheduler` implementations and slack calculators that set `TaskField.CRITICAL` (`mpxj/src/main/java/org/mpxj/cpm/Scheduler.java:32`, `PrimaveraScheduler.java:61,3381,3570`); ifcopenshell offers `api/sequence/recalculate_schedule.py:28` and `cascade_schedule.py:27`. Either can be invoked per iteration with sampled durations (inferred integration; not done by any source).

### Contingency proxy (LibrePlan)
Budget with margin = budget + budget × `budgetMargin`/100 (HALF_EVEN, 2 dp); hours with margin = hours × (1 + `hoursMargin`/100) (`libreplan/libreplan-business/src/main/java/org/libreplan/business/orders/entities/OrderElement.java:1675-1720`). Flat percentage, not probabilistic.

## State machines and workflows
- Risk status (P6 enum): Proposed → Open → Active → Managed | Impacted; Rejected from Proposed/Open; feature inventory adds Closed (P6 PMXML enum has no Closed value). Transitions not implemented in OSS.
- Response action status: Proposed → Sanctioned → In Progress → Complete; Rejected.
- Response plan: `IsActive` flag selects the plan that drives post-response scores (inferred from field).

## Cross-domain links
- Risks link to activities (D03) and to resources as owner/identifier (D07); exposure window uses calendars (D05).
- QRA requires the CPM engine (D06), relationships/constraints (D04) and activity codes for templates (D09).
- Response costs flow to budgets (D13/D17) and response actions may link to activities (D03).
- Risk exposure rolls into portfolio scoring (D15) and dashboards (D33); PMXML exchange (D35).

## Gaps
- Scoring: P×I score = `RiskMatrixScoreType.Severity<impactLevel>` at the probability row; overall per `RiskScoringMethod` (Highest impact; average of impact levels; average of individual P×I scores); separate pre-response (`RiskImpact`) and post-response (`RiskResponseActionImpact`) scores; colour/text from score thresholds.
- EMV/exposure = probability × cost impact (and schedule days); aggregate by WBS/project/portfolio; heat-map counts per (P, I) cell.
- Monte Carlo engine to rebuild: per iteration sample activity durations (triangular, BetaPERT, uniform, normal, lognormal, trigen with percentile tails; Latin hypercube option), sample risk occurrence Bernoulli(p) and add schedule/cost impact to linked activities, apply correlation (Iman-Conover on ranks), run a full CPM forward/backward pass, record finish date, cost, per-activity criticality (critical in % of iterations), Spearman duration sensitivity, cruciality (criticality × sensitivity); store seed and iteration count for reproducibility.
- Uncertainty templates: rule rows (activity code value → min%/ML%/max%, distribution) bulk-applied to remaining durations.
- Contingency: cost = P_target(cost) − deterministic cost; schedule = P_target(finish) − deterministic finish.
- Schedule health check: open ends (no predecessor/successor), hard constraints, negative/large lags, missing logic, long durations, out-of-sequence progress flagged before simulation.
- Exchange: import Primavera Risk Analysis `.plan`/XML, P6 XML risk elements via the existing JAXB types, Excel.
