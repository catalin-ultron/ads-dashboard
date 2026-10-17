# Backend Codebase Map

Inputs: [01-company-profile.md](01-company-profile.md), [02-coverage.md](02-coverage.md), [03-repo-inventory.md](03-repo-inventory.md), [../02-canonical-model.md](../02-canonical-model.md), [../03-gaps-and-rebuild.md](../03-gaps-and-rebuild.md), domain files D01–D36, new domains D37–D55.

## Sizing assumptions

| Dimension | Value | Basis |
|---|---|---|
| Legal entities | 6 operating (AG Construct, Pro Hart, Eurofor, Total NSA Invest, DPS Beton, Total N S A) | Profile |
| Live contracts | 15–25 concurrent, 5–40 M RON each, many multi-lot and in consortia | Profile (est.) |
| Users | 80–150 named (office, site engineers, RTE, lab, plant, dispatch, finance) | ≈650 staff cluster (est.) |
| Schedules | ≤ 5,000 activities per contract, ≤ 100k activities total | Public-works scale (est.) |
| Progress billing | 1 situație per contract per month, BoQ 500–5,000 lines | Profile (est.) |
| Concrete | 60–75k m³/yr, ~10k delivery notes/yr | Coverage (est.) |
| Aggregates | 1.5–2.5 Mt/yr, ~100k weighbridge tickets/yr | Coverage (est.) |
| Fleet | ≈ 300 units (trucks, plant, pumps, mixers) | Website |

Single PostgreSQL instance handles this volume comfortably; no sharding, no event-sourcing infrastructure required.

## Stack

| Concern | Choice | Reason |
|---|---|---|
| Language | Python 3.12 | Frappe (MIT) logic ports directly; IfcOpenShell and MPXJ have Python packages; team-neutral |
| Database | PostgreSQL 16 | Row-level scoping by company, JSONB for custom fields, exclusion constraints for validity periods, recursive CTEs for WBS/CBS trees |
| ORM / migrations | SQLAlchemy 2.0 + Alembic | Explicit schema ownership per module |
| API surface | FastAPI (internal service API only) | Typed contracts, OpenAPI for later frontend |
| Jobs | Procrastinate (Postgres-backed queue) | No extra broker; CPM runs, imports, e-Factura submissions, nightly rollups |
| Money / quantities | `Decimal` with currency column; RON base, EUR via BNR daily rates | Romanian public contracts are RON; EU funding reporting in EUR |
| Scheduling engine | MPXJ via PyPI `mpxj` 16.10.0 (bundled JARs, JPype) | LGPL-2.1+, used unchanged as a library; gives P6-clone CPM (`org.mpxj.cpm.PrimaveraScheduler`) and XER/PMXML/MSPDI I/O |
| IFC | `ifcopenshell` (LGPL-3.0+) | IFC4 schedule/cost exchange, quantity takeoff |
| Document storage | Object storage (Cloudflare R2, new bucket) | Content-addressed blobs; metadata in Postgres |
| Tests | pytest, hypothesis for engine invariants, golden files from MPXJ test schedules | |

Copyleft sources (OpenProject, ERPNext, HRMS, iDempiere, Mayan, TaskJuggler, LibrePlan) are specification sources only; every module citing them is a clean re-implementation from the domain files.

## Module layout

```
platform/
  core/            tenancy (group, company, branch), ids, money, units, calendars-of-record
  identity/        users, roles, memberships, permission evaluation, row scoping      D02
  audit/           journal with validity periods, versions, soft delete              D02, D36
  workflow/        state machines, transitions, approvals, assignment rules          D24
  numbering/       per-scope counters, document numbering schemes                    D24.06, D25
  customfields/    typed UDFs, formula fields, codes/classifications                 D09
  jobs/            queue, schedules, retries
  notify/          notifications, digests, escalations                               D12
  files/           blob store, checksums, virus-scan hook                            D25
masterdata/        partners (CUI, VAT status), items, materials, units, cost codes,
                   INS indices, BNR rates, norm catalogues                           D01, D39, D40
tendering/         opportunities, SICAP/TED watch, bids, DUAE, consortia, CNSC        D37, D55
contracts/
  contract/        contracts, lots, parties, consortium shares, clauses              D19, D41
  guarantees/      participation, good-execution, advance; retention ledger          D38
  modification/    addenda, extra-work orders, art. 221 limits, change events        D20, D40
  priceadjust/     OUG 64/2022 and contractual formulas over INS indices             D40
  subcontracts/    subcontract packages, declarations, direct payment                D41
estimating/        norm-based devize, F1–F5, BoQ, resource lists, deviz general      D39, D17.11
schedule/
  model/           EPS/WBS, activities, relationships, constraints, calendars        D03–D05
  engine/          CPM adapter over MPXJ, schedule options, logs, DCMA checks        D06
  leveling/        resource leveling (re-implemented from spec)                      D08
  baselines/       baselines, updates, progress, variance                            D10
  lean/            lookahead, weekly plans, PPC, constraints                         D16
  risk/            Monte Carlo over the CPM adapter                                  D14
resources/         resources, roles, rates, assignments, timesheets → actuals        D07, D32
billing/
  measurement/     measured quantities per BoQ line and period                       D39
  situatii/        monthly situații de lucrări, centralizator, certification          D39, D21
  invoices/        invoices to authority, e-Factura payloads, payments, retention     D21, D23, D49
cost/              CBS, budgets, commitments, actuals, forecast, EVM, cash flow       D11, D13, D17, D18, D22
procurement/       requisitions, RFQ, PO, receipts, three-way match                  D19
site/              daily logs, labour on site, plant usage, H&S, waste               D28, D51, D52
quality/           control programme, faze determinante, PVs, NCRs, punch,
                   reception, cartea tehnică                                        D29, D43
lab/               samples, tests, conformity (SR EN 206, 12350/12390)               D44
documents/         documents, revisions, transmittals, RFIs, submittals,
                   design phases, permits and authority correspondence               D25–D27, D42, D54
production/
  concrete/        mixes, batches, dispatch, delivery notes, conformity              D45
  quarry/          licences, extraction, weighbridge tickets, royalties, DoP         D46
fleet/             equipment register, hours, fuel, maintenance, ISCIR/RAR, hire      D47, D31
intragroup/        internal price lists, transfers, JV accounts, eliminations        D48
fiscal/            e-Factura, e-Transport, SAF-T D406 extracts, reverse charge        D49
hr/                employees, REGES-ONLINE and D112 exports                          D50
funding/           funded projects, reimbursement claims, PNRR milestones            D53
reporting/         snapshot tables, KPI library, as-of queries                       D33, D12
integration/       XER/PMXML/MSPDI (MPXJ), IFC, ANAF APIs, SICAP, accounting export  D34, D35
```

## Ownership and dependencies

| Module | Owns entities | Depends on | Engine source |
|---|---|---|---|
| platform.* | Company, User, Role, Membership, Journal, WorkflowDef, Counter, CustomField, Blob | none | frappe (MIT, port): `frappe/permissions.py`, `frappe/model/workflow.py`, `frappe/model/naming.py`; OpenProject journals (spec) |
| masterdata | Partner, Item, Unit, CostCode, IndexSeries, FxRate, NormCatalogue | platform | Odoo/ERPNext rate lookup (spec) |
| contracts | Contract, Lot, Party, Guarantee, RetentionEntry, Addendum, ExtraWorkOrder, PriceAdjustmentRun, Subcontract | masterdata | ERPNext withholding pattern (spec), OUG 64/2022 formula (02-coverage D40.02) |
| estimating | Estimate, EstimateLine, NormApplication, ResourceList | masterdata | none (new) |
| schedule | Project, WBS, Activity, Relationship, Calendar, Baseline, ScheduleRun | platform, resources | MPXJ `org.mpxj.cpm` (library), IfcOpenShell sequence (library) |
| resources | Resource, Role(work), RateTable, Assignment, Timesheet | platform | MPXJ model (library); LibrePlan allocation (spec) |
| billing | MeasurementPeriod, MeasuredQty, Situatie, SituatieLine, Invoice, Payment | contracts, estimating, quality | none (new); retention from contracts.guarantees |
| cost | CBSNode, Budget, BudgetRevision, Commitment, Actual, Forecast, EVSnapshot, CashFlowCurve | contracts, procurement, billing, schedule | ERPNext budget control (spec), iDempiere commitments (spec), LibrePlan EV (spec, defects fixed) |
| procurement | Requisition, RFQ, PurchaseOrder, Receipt, Match | masterdata, contracts | ERPNext/iDempiere (spec) |
| site | DailyLog, LabourEntry, PlantEntry, HSEIncident, WasteRecord | schedule, fleet, resources | none (new) |
| quality | ControlProgramme, InspectionPoint, PV, NCR, Reception, TechnicalBookEntry | contracts, documents | ERPNext quality inspection (spec) |
| lab | Sample, Test, Result, ConformityAssessment | production, quality | none (new) |
| documents | Document, Revision, Transmittal, RFI, Submittal, DesignPhase, Permit | platform.files | Mayan versioning (spec), ERPNext response tracking (spec) |
| production | Mix, Batch, DeliveryNote, Licence, ExtractionRecord, WeighTicket, RoyaltyStatement | masterdata, fleet, intragroup | none (new) |
| fleet | Equipment, MeterReading, FuelEntry, MaintenancePlan, WorkOrder, Inspection, HireRecord | masterdata | ERPNext assets/maintenance (spec), Odoo maintenance (spec) |
| intragroup | InternalPriceList, Transfer, JVAccount, Elimination | all money modules | none (new) |
| fiscal | EInvoice, ETransportDeclaration, SaftExtract | billing, procurement, production | none (new; ANAF specs) |
| hr | Employee, Contract(employment), PayrollExport | platform | none (export-only; payroll stays in their payroll system) |
| funding | FundedProject, ReimbursementClaim, Milestone | contracts, billing, cost | none (new) |
| reporting | Snapshot, KPI | all | MPXJ timephased spreading (library), OpenProject as-of (spec) |
| integration | ImportJob, ExportJob, ExternalRef | all | MPXJ readers/writers, ifc4d/ifc5d (libraries) |

Accounting (general ledger) is not rebuilt: postings are exported to their accounting system; system identity is an open question for the client.

## Calculation pipeline

1. Calendars and working time (platform.core, schedule.model)
2. CPM forward/backward pass, float, critical path (schedule.engine via MPXJ)
3. Resource leveling (schedule.leveling) → re-run CPM
4. Resource and cost spreading over time (resources, reporting via MPXJ timephased)
5. Measured quantities per period (billing.measurement) gated by quality inspection points (quality)
6. Price adjustment per period (contracts.priceadjust) on INS indices
7. Situație de lucrări = measured qty × unit price + adjustment, minus retention and advance recovery (billing.situatii, contracts.guarantees)
8. Commitments and actuals (procurement, intragroup, site, fleet, production) → cost
9. Budget control checks (cost)
10. EVM snapshot (cost) from baseline, progress, actual cost
11. Cash flow forecast incl. funding reimbursement lag (cost, funding)
12. Fiscal documents (fiscal) and reporting snapshots (reporting)

## Build order

| Phase | Modules | Outcome |
|---|---|---|
| P0 | platform.*, masterdata | Tenancy, permissions, audit, workflow, numbering, master data |
| P1 | contracts, estimating, billing, contracts.priceadjust, contracts.guarantees | The public-works money loop: contract → BoQ → monthly situație → adjustment → retention → invoice |
| P2 | schedule.model, schedule.engine, resources, schedule.baselines, integration (XER/MSPDI) | CPM, P6/MSP import-export, baselines |
| P3 | cost, procurement, intragroup | Budgets, commitments, actuals, EVM, cash flow, JV and internal transfers |
| P4 | quality, lab, site, documents | Control programme, inspection gating of billing, reception, cartea tehnică, daily logs, H&S |
| P5 | production, fleet | Concrete dispatch, quarry weighbridge and royalties, fleet costs into contracts |
| P6 | fiscal, hr, funding, tendering, schedule.leveling, schedule.risk, schedule.lean, reporting | Compliance exports, funding claims, tender pipeline, advanced scheduling, KPIs |

## Infrastructure notes

- **Cloudflare (new resources only, none created yet):** R2 bucket for document blobs; optionally Queues for inbound integration webhooks. Not needed until P4.
- **Azure:** nothing required now. A managed PostgreSQL 16 and a JVM-capable worker host will be needed when an environment is wanted; flagged for when access is granted.
- **ANAF:** e-Factura / e-Transport / SPV APIs need the client's digital certificate (OAuth via ANAF); required in P6.
