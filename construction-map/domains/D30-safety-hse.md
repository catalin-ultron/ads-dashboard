# D30 Safety (HSE)

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D30.01 | Safety observations | OpenProject work package Type + custom fields (generic carrier) | none | No safety-specific model in any cloned source; a typed work package with category/severity custom fields is the only carrier |
| D30.02 | Incidents | ERPNext Quality Action / Non Conformance (CAPA pattern); OpenProject time_entries for hours worked | none | No incident, injury, body-part, OSHA recordable, days-away fields or TRIR/LTIR/DART computation; CAPA closure logic and hours source are reusable |
| D30.03 | Toolbox talks and training | HRMS Training Program / Training Event / Training Result / Employee Skill Map | partial | Sessions with attendee list, attendance, mandatory flag, per-attendee status, results (hours, grade); no signatures, no certification expiry, no site-access eligibility |
| D30.04 | Safety inspections and permits to work | Mayan document_states workflow engine; OpenProject role-based status workflow | partial | Generic state machines with guarded transitions, timed escalation and entry/exit actions can implement Requested → Approved → Active → Closed; no permit entity, validity window or permit types |
| D30.05 | Job hazard analysis (JHA) | none | none | No task/hazard/control/risk-rating model |

## Storage model

### HRMS training (`hrms/hrms/hr/doctype/`)

| Doctype | Key fields | Relations |
|---|---|---|
| Training Program (`training_program/training_program.json`, name = `training_program`) | `status` (Scheduled / Completed / Cancelled), `company`*, `trainer_name`, `trainer_email`, `supplier`, `description`* | 1:N Training Event |
| Training Event (`training_event/training_event.json`, submittable, name = `event_name`) | `event_status`* (Scheduled / Completed / Cancelled), `type`* (Seminar, Theory, Workshop, Conference, Exam, Internet, Self-Study), `level`, `has_certificate`, `location`*, `start_time`*, `end_time`*, `introduction`* (topic/content), `trainer_name`, `supplier`, `course`, `employee_emails` | N:1 program; 1:N Training Event Employee |
| Training Event Employee (child) | `employee` → Employee, `department`, `status` (Open / Invited / Completed / Feedback Submitted), `attendance` (Present / Absent), `is_mandatory` (default 1) | |
| Training Result (`training_result/training_result.json`, submittable, `HR-TRR-.YYYY.-.#####`) | `training_event`* | 1:N Training Result Employee (`employee`, `hours`, `grade`, `comments`) |
| Employee Skill Map (name = employee) | `employee_skills` Table(Employee Skill: `skill`*, `proficiency` Rating*, `evaluation_date`), `trainings` Table(Employee Training: `training` → Training Event, `training_date`) | |

### Generic carriers usable for HSE records

- OpenProject work packages + custom fields + statuses/workflows (`openproject/db/migrate/tables/work_packages.rb:35`, `openproject/db/migrate/tables/custom_fields.rb:35`, `openproject/app/models/workflows/status_transition.rb`), attachments for photos, BCF viewpoint for location (`openproject/modules/bim/db/migrate/tables/bcf_viewpoints.rb`).
- ERPNext Quality Action (corrective/preventive, resolutions with responsible + completion_by) and Non Conformance (`erpnext/erpnext/quality_management/doctype/quality_action/quality_action.json`, `non_conformance/non_conformance.json`) for investigation actions.
- Hours worked denominator: OpenProject `time_entries.hours` by project/date (`openproject/modules/costs/db/migrate/tables/time_entries.rb:38`), LibrePlan `work_report_line.effort` (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/workreports/entities/WorkReports.hbm.xml`), ERPNext Timesheet Detail `hours`.
- Mayan workflow tables (`mayan-edms/mayan/apps/document_states/models/`) for permit documents: states with `initial`/`final`/`completion`, transitions with condition and required fields, escalations.

## Algorithms and logic

**Training event lifecycle** `hrms/hrms/hr/doctype/training_event/training_event.py`
- `validate` (`:45`): `employee_emails` = joined emails of attendees; `end_time > start_time` else error (`validate_period` `:55`).
- `on_update_after_submit` → `set_status_for_attendees` (`:59`): event Completed → every attendee with `attendance = Present` and status ≠ Feedback Submitted becomes Completed; event Scheduled → all attendees reset to Open; persisted with `db_update_all`.

**Training result** `hrms/hrms/hr/doctype/training_result/training_result.py`
- `validate` (`:29`): referenced Training Event must be submitted (docstatus 1).
- `on_submit` (`:36`): for each result employee, the matching event attendee row gets status Completed; the event is saved. The code assigns `training_event.status = "Completed"` while the doctype field is `event_status`, so the event header status is not changed by this path (observed in code).

**CAPA closure (reusable for incident actions)** `erpnext/erpnext/quality_management/doctype/quality_action/quality_action.py:31`: Completed iff all resolution rows are Completed.

**Permit-style state machine (Mayan, reusable)** `mayan-edms/mayan/apps/document_states/models/workflow_instance_model_mixins.py`
- Allowed transitions = origin transitions of active state ∩ user ACL ∩ condition true (`:98`).
- Escalation (`:17`): if the state is not final and `now > last transition time + (unit, amount)` and condition holds, auto-execute the escalation transition — models permit expiry (Active → Expired/Closed) (inferred use).
- Transition fields (required typed values) capture approver data, validity end, gas-test readings (`mayan-edms/mayan/apps/document_states/models/workflow_transition_field_models.py:22`).

**Rate formulas** — none in code. TRIR, LTIR, DART need recordable/lost-time/restricted case counts and hours worked; hours are available from the time sources above.

## State machines and workflows

- **Training Event**: docstatus Draft → Submitted → Cancelled; `event_status` Scheduled → Completed | Cancelled; attendee status Open → Invited → Completed → Feedback Submitted, recomputed on event status change.
- **Training Result**: Draft → Submitted (requires submitted event) → Cancelled.
- **Quality Action**: Open ⇄ Completed (derived).
- **Generic permit/observation**: any states via OpenProject (role/author/assignee guarded) or Mayan (ACL + condition + escalation) engines.

## Cross-domain links

- D28: observations and incidents originate in daily logs/field issues; hours from D28.07 timecards are the rate denominator.
- D29: safety inspections reuse checklist templates and NCR/CAPA patterns.
- D32: timesheet hours for TRIR/LTIR/DART.
- HR/resources: Employee, Department, Skill records from HRMS; contractor companies from supplier/partner records.
- D25: permit documents, signed toolbox-talk sheets as documents.

## Gaps

- **Observation**: `observation(type safe|unsafe, category, location, company, severity, photos, observer, date)`; leading-indicator trend = count by category/company/week, ratio safe:unsafe.
- **Incident**: `incident(type injury|near_miss|property_damage|environmental, occurred_at, location, description, root_cause, status)`, `incident_person(person, employer, injury_type, body_part, treatment, osha_recordable, days_away, days_restricted, fatality)`, corrective actions (Quality Action pattern). Investigation workflow Reported → Under Investigation → Actions Assigned → Closed.
- **OSHA logs and rates**: 300 log rows per recordable case, 300A annual summary (totals of cases, days away, restricted, hours worked); `TRIR = recordables × 200000 / hours`, `LTIR = lost-time cases × 200000 / hours`, `DART = (days-away + restricted/transfer cases) × 200000 / hours`.
- **Certifications**: `worker_certification(worker, type, number, issued, expires)`; daily job flags expiring within N days; site access eligibility = all required certification types for the role valid on date and toolbox-talk attendance within period.
- **Toolbox talk signatures**: per-attendee signature capture (Mayan `signature_captures` app exists upstream but was not read).
- **Permit to work**: `permit(type hot_work|confined_space|excavation|…, location, valid_from, valid_to, issuer, receiver, isolations, gas_tests)` with states Requested → Approved → Active → Suspended → Closed/Expired; Active requires all approvals and current time inside validity.
- **JHA**: `jha(activity)` → `jha_step` → `hazard(likelihood, severity)` → `control(type, residual_likelihood, residual_severity)`; risk rating = likelihood × severity matrix, residual rating after controls.
