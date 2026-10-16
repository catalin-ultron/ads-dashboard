# Construction Platform Technical Map

## Contents

- [00-feature-inventory.md](00-feature-inventory.md): Primavera-class backend feature inventory, 36 domains
- [01-map.md](01-map.md): domain and feature index with coverage and sources
- [02-canonical-model.md](02-canonical-model.md): unified cross-domain entity model and calculation order
- [03-gaps-and-rebuild.md](03-gaps-and-rebuild.md): gap register, rebuild specs, defects found in sources
- [domains/](domains/): per-domain storage models, algorithms, state machines, links, gaps

## Coverage

| Features | Full | Partial | None |
|---|---|---|---|
| 291 | 68 (23%) | 182 (62%) | 41 (14%) |

## Domains

| Domain | Features | Full | Partial | None | Lead sources |
|---|---|---|---|---|---|
| [D01 Enterprise Structure and Tenancy](domains/D01-enterprise-structure-and-tenancy.md) | 10 | 1 | 9 | 0 | MPXJ, OpenProject, ERPNext |
| [D02 Security, Identity and Permissions](domains/D02-security-identity-and-permissions.md) | 14 | 3 | 9 | 2 | OpenProject, Frappe, MPXJ |
| [D03 WBS and Activities](domains/D03-wbs-and-activities.md) | 11 | 4 | 6 | 1 | MPXJ, LibrePlan, IfcOpenShell |
| [D04 Relationships and Constraints](domains/D04-relationships-and-constraints.md) | 5 | 3 | 2 | 0 | MPXJ, LibrePlan, TaskJuggler |
| [D05 Calendars and Time](domains/D05-calendars-and-time.md) | 7 | 4 | 3 | 0 | MPXJ, TaskJuggler, LibrePlan |
| [D06 CPM Scheduling Engine](domains/D06-cpm-scheduling-engine.md) | 12 | 4 | 6 | 2 | MPXJ, TaskJuggler, IfcOpenShell |
| [D07 Resources, Roles and Assignments](domains/D07-resources-roles-assignments.md) | 10 | 6 | 4 | 0 | MPXJ, LibrePlan, TaskJuggler |
| [D08 Resource Leveling and Capacity Planning](domains/D08-resource-leveling-capacity-planning.md) | 7 | 1 | 5 | 1 | LibrePlan, TaskJuggler, MPXJ |
| [D09 Codes, User-Defined Fields and Classification](domains/D09-codes-udfs-classification.md) | 7 | 4 | 3 | 0 | MPXJ, OpenProject, ERPNext |
| [D10 Baselines, Progress and Updating](domains/D10-baselines-progress-updating.md) | 8 | 2 | 5 | 1 | MPXJ, OpenProject, LibrePlan |
| [D11 Earned Value and Performance Measurement](domains/D11-earned-value-performance-measurement.md) | 8 | 0 | 8 | 0 | MPXJ, LibrePlan |
| [D12 Project Monitoring: Thresholds, Issues, Work Products and Notifications](domains/D12-project-monitoring.md) | 6 | 2 | 4 | 0 | OpenProject, MPXJ, ERPNext |
| [D13 Project Expenses and P6 Cost Management](domains/D13-project-expenses-p6-cost-management.md) | 6 | 1 | 5 | 0 | MPXJ, LibrePlan, ERPNext |
| [D14 Risk Management](domains/D14-risk-management.md) | 9 | 0 | 7 | 2 | MPXJ, qsra_qcra_icsra, LibrePlan |
| [D15 Portfolio and Capital Planning](domains/D15-portfolio-capital-planning.md) | 9 | 0 | 8 | 1 | OpenProject, ERPNext, LibrePlan |
| [D16 Task and Lean Planning (Last Planner)](domains/D16-task-lean-planning.md) | 9 | 0 | 7 | 2 | OpenProject, ERPNext, Odoo |
| [D17 Cost Controls: CBS, Budget, Cost Sheet and Forecast](domains/D17-cost-controls.md) | 12 | 2 | 10 | 0 | ERPNext, OpenProject, iDempiere |
| [D18 Funding Management](domains/D18-funding-management.md) | 4 | 1 | 3 | 0 | Odoo, ERPNext, iDempiere |
| [D19 Commitments and Contracts](domains/D19-commitments-and-contracts.md) | 7 | 2 | 5 | 0 | ERPNext, iDempiere, Odoo |
| [D20 Change Management](domains/D20-change-management.md) | 8 | 0 | 3 | 5 | ERPNext, OpenProject, Odoo |
| [D21 Invoicing, Schedule of Values and Spends](domains/D21-invoicing-sov-spends.md) | 6 | 2 | 2 | 2 | ERPNext, Odoo, iDempiere |
| [D22 Cash Flow](domains/D22-cash-flow.md) | 7 | 0 | 7 | 0 | ERPNext, OpenProject, MPXJ |
| [D23 Payment Management (Textura-class)](domains/D23-payment-management.md) | 13 | 0 | 7 | 6 | ERPNext, Odoo, Frappe |
| [D24 Business Process and Workflow Engine](domains/D24-business-process-workflow-engine.md) | 10 | 4 | 6 | 0 | Frappe, OpenProject, ERPNext |
| [D25 Document Management](domains/D25-document-management.md) | 11 | 3 | 8 | 0 | Mayan EDMS, OpenProject |
| [D26 Correspondence and Transmittals](domains/D26-correspondence-and-transmittals.md) | 6 | 3 | 2 | 1 | OpenProject, ERPNext, Mayan EDMS |
| [D27 RFIs and Submittals](domains/D27-rfis-and-submittals.md) | 6 | 0 | 5 | 1 | OpenProject, Mayan EDMS, ERPNext |
| [D28 Field: Daily Logs and Site Diaries](domains/D28-field-daily-logs-and-site-diaries.md) | 7 | 2 | 5 | 0 | OpenProject, LibrePlan, ERPNext |
| [D29 Quality: Punch Lists, Inspections and NCRs](domains/D29-quality-punch-lists-inspections-ncrs.md) | 5 | 0 | 4 | 1 | ERPNext, LibrePlan, OpenProject |
| [D30 Safety (HSE)](domains/D30-safety-hse.md) | 5 | 0 | 2 | 3 | OpenProject, ERPNext, Frappe HRMS |
| [D31 Asset and Facilities Management](domains/D31-asset-and-facilities-management.md) | 7 | 1 | 3 | 3 | ERPNext, Odoo |
| [D32 Timesheets and Actuals Capture](domains/D32-timesheets-actuals-capture.md) | 5 | 2 | 3 | 0 | ERPNext, LibrePlan, OpenProject |
| [D33 Reporting Data Layer and Analytics](domains/D33-reporting-data-layer-and-analytics.md) | 4 | 2 | 2 | 0 | Odoo, MPXJ, TaskJuggler |
| [D34 Integrations and APIs](domains/D34-integrations-and-apis.md) | 13 | 2 | 6 | 5 | MPXJ, OpenProject, LibrePlan |
| [D35 Import/Export Formats](domains/D35-import-export-formats.md) | 10 | 3 | 5 | 2 | MPXJ, IfcOpenShell, Odoo |
| [D36 Platform Services](domains/D36-platform-services.md) | 7 | 4 | 3 | 0 | Frappe, OpenProject, Odoo |

## Source repositories

| Repository | Language / stack | Domains referenced |
|---|---|---|
| MPXJ | Java; P6/MSP data model, readers/writers, P6-clone CPM | D01, D02, D03, D04, D05, D06, D07, D08, D09, D10, D11, D12, D13, D14, D22, D33, D34, D35, D36 |
| LibrePlan | Java/Hibernate; planning, allocation, EV, progress | D03, D04, D05, D07, D08, D10, D11, D13, D14, D15, D17, D22, D28, D29, D32, D33, D34 |
| TaskJuggler | Ruby; slot scheduler, leveling | D04, D05, D06, D07, D08, D16, D33 |
| IfcOpenShell | Python; IFC4 schedule/cost/resource, format converters | D03, D06, D09, D10, D17, D34, D35 |
| OpenProject | Ruby on Rails/PostgreSQL; projects, work packages, roles, journals, budgets, BIM/BCF, webhooks | D01, D02, D07, D09, D10, D12, D13, D15, D16, D17, D20, D22, D24, D25, D26, D27, D28, D29, D30, D32, D33, D34, D35, D36 |
| ERPNext | Python/Frappe; accounting, buying, stock, projects, assets, quality | D01, D04, D05, D09, D10, D12, D13, D15, D16, D17, D18, D19, D20, D21, D22, D23, D24, D26, D27, D28, D29, D30, D31, D32, D33, D34, D35 |
| Frappe HRMS | Python/Frappe; timesheets, HR, training | D30 |
| Odoo | Python; analytic, accounting, purchase, stock, maintenance, access rules | D01, D02, D05, D07, D09, D10, D12, D16, D17, D18, D19, D20, D21, D23, D31, D32, D33, D34, D35, D36 |
| Frappe | Python; DocType ORM, permissions, workflow, automation | D01, D02, D20, D23, D24, D36 |
| iDempiere | Java; project phases/lines, commitments, encumbrance, RfQ | D17, D18, D19, D21 |
| Mayan EDMS | Python/Django; document versions, workflows, checkouts, retention | D25, D26, D27, D28, D30 |
| qsra_qcra_icsra | Python; three-point Monte Carlo (weak) | D14 |
