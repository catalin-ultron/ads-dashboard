# D29 Quality: Punch Lists, Inspections and NCRs

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D29.01 | Punch lists | OpenProject work package Type "Punch item" + BCF issue/viewpoint + author/assignee workflow | partial | Location (3D viewpoint), assignee, due date, priority, photos, role-gated statuses (sub completes, GC verifies via author-only transition); no completion % per area, no 2D pin |
| D29.02 | Inspections and test plans (ITP) | ERPNext Quality Inspection (+ Template, Parameter, Reading) + QualityInspectionService hold logic; LibrePlan TaskQualityForm | partial | Per-parameter numeric/formula/text acceptance, auto Accepted/Rejected, parent transaction blocked ("Stop") if inspection missing, unsubmitted or rejected = hold point; no witness points, signatures, or auto-deficiency |
| D29.03 | NCR | ERPNext Non Conformance + Quality Action (CAPA with resolution rows) + Quality Procedure | partial | NCR with procedure, status, corrective/preventive action; CAPA auto-completes when all resolutions complete; no disposition (use-as-is/repair/rework/reject) or verify step |
| D29.04 | Commissioning and handover | LibrePlan quality forms on tasks (checklist → progress); ERPNext Asset (handover target) | none | No system/component commissioning model, no pre-functional/functional checklists by system, no handover package compilation |
| D29.05 | Quality KPIs | ERPNext Quality Goal + scheduled Quality Review (objective pass/fail) | partial | Periodic objective reviews with targets; first-time pass rate etc. derivable from Quality Inspection status (inferred), not computed in code |

## Storage model

### ERPNext Quality Inspection (`erpnext/erpnext/stock/doctype/`)

| Doctype | Key fields | Relations |
|---|---|---|
| Quality Inspection (`quality_inspection/quality_inspection.json`, submittable, `MAT-QA-.YYYY.-`) | `report_date`*, `inspection_type`* (Incoming / Outgoing / In Process), `reference_type`* (Purchase Receipt, Purchase Invoice, Subcontracting Receipt, Delivery Note, Sales Invoice, Stock Entry, Job Card) + `reference_name`* Dynamic Link, `child_row_reference`, `item_code`*, `item_serial_no`, `batch_no`, `sample_size`* (>0), `inspected_by`* User, `verified_by`, `bom_no`, `quality_inspection_template`, `status`* (Accepted / Rejected / Cancelled), `manual_inspection`, `remarks`, `amended_from`, `company` | 1:N readings; N:1 template |
| Quality Inspection Reading (child) | `specification`* → Quality Inspection Parameter, `parameter_group`, `numeric`, `min_value`, `max_value`, `value` (expected text), `reading_value` (text result), `reading_1..reading_10`, `formula_based_criteria`, `acceptance_formula`, `manual_inspection`, `status` (Accepted / Rejected) | |
| Quality Inspection Template | `quality_inspection_template_name`*, `item_quality_inspection_parameter`* Table(Item Quality Inspection Parameter: same acceptance fields as reading) | Item.`quality_inspection_template`; Item flags `inspection_required_before_purchase` / `_before_delivery` |
| Quality Inspection Parameter / Parameter Group | `parameter`*, `description`, `parameter_group` / `group_name` | |

Row-level back reference: each referenced line (`<reference_type> Item`, `Stock Entry Detail`, or `Job Card.quality_inspection`) holds a `quality_inspection` link (`quality_inspection.py:287`).

### ERPNext Quality Management (`erpnext/erpnext/quality_management/doctype/`)

| Doctype | Key fields |
|---|---|
| Non Conformance (`non_conformance/non_conformance.json`, `QA-NC-{#####}`) | `subject`*, `procedure`* → Quality Procedure, `status`* (Open / Resolved / Cancelled), `details`, `process_owner` / `full_name` (fetched from procedure), `corrective_action`, `preventive_action` |
| Quality Action (`QA-ACT-{#####}`) | `corrective_preventive`* (Corrective / Preventive), `status` (Open / Completed), `date`, `goal`, `procedure`, `review` → Quality Review, `feedback` → Quality Feedback, `resolutions` Table(Quality Action Resolution: `problem`, `resolution`, `status` Open/Completed, `responsible` User, `completion_by` Date) |
| Quality Procedure (tree, NestedSet `lft`/`rgt`, name = `quality_procedure_name`) | `parent_quality_procedure`, `is_group`, `process_owner`, `processes` Table(Quality Procedure Process: `process_description`, `procedure` child link) |
| Quality Goal (name = `goal`) | `frequency` (None / Daily / Weekly / Monthly / Quarterly), `date` (1–31), `weekday`, `procedure`, `objectives` Table(`objective`*, `target`, `uom`) |
| Quality Review (`QA-REV-{#####}`) | `goal`*, `date`, `procedure`, `status` (Open / Passed / Failed), `reviews` Table(Quality Review Objective: `objective`, `target`, `uom`, `review`, `status` Open/Passed/Failed) |
| Quality Feedback / Template | template parameters → feedback rows with `rating` 1–5 |

### LibrePlan quality forms (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/qualityforms/entities/QualityForms.hbm.xml`)

- `quality_form`: `name` unique, `description`, `quality_form_type` (BY_PERCENTAGE | BY_ITEMS), ordered `quality_form_items` (name, percentage, position), `report_advance` bool, `advance_type_id`.
- `task_quality_form`: N:1 `quality_form`, N:1 `order_element` (task); ordered `task_quality_form_items` (name, percentage, position, `passed`, `date`), `report_advance`. A form may be attached once per task (`java/org/libreplan/business/orders/entities/OrderElement.java:1437`).

### OpenProject punch items

Work package (type, status, assignee, responsible, due_date, priority, category) + BCF issue/viewpoint/comment tables (see D27/D28) + attachments.

## Algorithms and logic

**Inspection evaluation** `erpnext/erpnext/stock/doctype/quality_inspection/quality_inspection.py`
1. `validate` (`:76`): no readings → load from template (item template if none, `:197`); In-Process Job Card → copy acceptance criteria from template onto readings (`:92`); readings present → validate number format and evaluate.
2. Per reading unless `manual_inspection` (`inspect_and_set_status` `:340`):
   - formula: `frappe.safe_eval(acceptance_formula, {reading_1..reading_10 as floats (missing → 0.0), mean})` for numeric, `{reading_value}` for text (`:427,454`); invalid names or syntax → validation error.
   - numeric min/max: every non-empty `reading_i` must satisfy `min_value ≤ reading_i ≤ max_value`; at least one reading required (`min_max_criteria_passed` `:411`).
   - text: `reading_value == value` (`:400`).
   - `mean` = arithmetic mean of non-empty readings (`calculate_mean` `:471`).
3. Header status (if not manual): Accepted unless any reading Rejected → Rejected (`:350`).
4. `validate_inspection_required` (`:164`): QI only allowed when the item flag for that direction is set, unless "allow QI after purchase/delivery".
5. `before_submit`: `sample_size > 0`, every reading has a status (`:188,192,282`). `on_submit` writes the QI link into the reference rows when the "not submitted" action is Stop (`:236`). Cancel: blocked while a submitted reference document still links it (`:246`); cancel clears links and sets status Cancelled (`:273`).

**Hold point on parent transaction** `erpnext/erpnext/stock/services/quality_inspection_service.py:84`
- For each line whose item requires inspection (purchase/delivery flags; Stock Entry by purpose: manufacture → finished item, incoming → has target warehouse, outgoing → source ≠ target, `:67`):
  - missing QI → message on save, exception `QualityInspectionRequiredError` on submit (`:126`);
  - QI not submitted → Stop (exception) or Warn per Stock Settings `action_if_quality_inspection_is_not_submitted` (`:137`);
  - QI status ≠ Accepted → Stop or Warn per `action_if_quality_inspection_is_rejected` (`:152`).
- Invoked from every stock transaction `StockController.validate_inspection` (`erpnext/erpnext/controllers/stock_controller.py:410`). Construction analogue: activity/payment line cannot be posted until its ITP inspection is Accepted (inferred mapping).

**CAPA closure** `erpnext/erpnext/quality_management/doctype/quality_action/quality_action.py:31`: `status = Completed` iff resolutions exist and all have status Completed, else Open — recomputed on every save.

**Periodic quality reviews (KPI cadence)** `erpnext/erpnext/quality_management/doctype/quality_review/quality_review.py`
- Daily scheduler `review()` (`:75`): per goal, Daily → create; Weekly → weekday matches; Monthly → `min(goal.date, last day of month) == today` (`is_review_date`); Quarterly → same and month ∈ {Jan, Apr, Jul, Oct}.
- `create_review` (`:98`) is idempotent per (goal, date). New review copies goal objectives with status Open (`set_objectives`).
- Status roll-up `set_status` (`:65`): any objective not Passed/Failed → Open; any Failed → Failed; else Passed. Objectives must belong to the goal (`validate_objectives` `:44`).

**Procedure tree integrity** `erpnext/erpnext/quality_management/doctype/quality_procedure/quality_procedure.py`: child listed in `processes` gets `parent_quality_procedure` set; a child may not have a different existing parent (`check_for_incorrect_child`); removing a child row clears its parent; changing parent removes the row from the old parent and appends to the new; NestedSet maintains `lft/rgt`.

**Checklist progress** `libreplan/libreplan-business/src/main/java/org/libreplan/business/qualityforms/entities/`
- BY_ITEMS: each item weight = floor(100/n, 2 decimals), remainder added to last item (`QualityForm.java:361`); percentage must be in (0,100) (`:277`).
- BY_PERCENTAGE: item percentages unique and increasing with position (`:248,266`); items passed strictly in order with non-decreasing dates (`TaskQualityForm.java:98-158`).
- `report_advance` + `advance_type` → passing items reports task progress through an AdvanceAssignment of that type (`QualityForm.java:406`; `qualityforms/daos/QualityFormDAO.java:137`).

**Punch verification** OpenProject `StatusTransition` rows with `assignee=true` (sub may move Open → Work Completed) and `author=true` (GC creator may move Work Completed → Verified/Closed or → Rejected) — evaluated by `from_status` (`openproject/app/models/workflows/status_transition.rb:53`) inside `new_statuses_allowed_from` (`openproject/app/contracts/work_packages/base_contract.rb:724`).

## State machines and workflows

- **Quality Inspection**: Draft (docstatus 0, status computed) → Submitted (docstatus 1; Accepted | Rejected) → Cancelled (docstatus 2, status Cancelled); `Cancelled` cannot be set manually (`quality_inspection.py:101`); amendment via `amended_from`.
- **Parent document with inspected items**: submit guarded by QI presence/submission/acceptance (Stop mode) — hold point.
- **Non Conformance**: Open → Resolved | Cancelled (select, no guards in code; `non_conformance.py` is empty).
- **Quality Action**: Open ⇄ Completed, derived from resolution rows.
- **Quality Review**: Open → Passed | Failed, derived from objectives.
- **Punch item (OpenProject)**: configurable statuses Open → Work Completed → Verified/Closed, with Rejected back to Open; role + author/assignee guards; blocked items cannot close.

## Cross-domain links

- D28: checklists (D28.05) are the same templates; field issues = punch items; progress from passed checklist items feeds D28.02/scheduling.
- D25: inspection reports, NCR attachments, O&M documents for handover.
- D27: NCR/punch may `relates` to RFI or submittal (design deficiency).
- Procurement/stock domain: incoming material inspections bind to Purchase Receipt lines.
- D31: handed-over assets become ERPNext Asset records with maintenance plans.
- D33: inspection status counts, NCR open/close dates for KPIs.

## Gaps

- **ITP structure**: `itp(spec_section, activity)` → `itp_step(seq, description, type hold|witness|review|surveillance, responsible_party, acceptance_criteria, reference_doc)`; inspection instance per step with `result pass|fail|na`, signatures (party, user, timestamp), and gating rule "hold step not passed ⇒ dependent activity cannot start/progress" (ERPNext Stop-mode check is the pattern).
- **Auto-deficiency**: failed reading/item ⇒ create punch item or NCR prefilled with location, item, inspector.
- **NCR disposition**: `disposition use_as_is|repair|rework|reject|return_to_supplier`, approver, cost, and states Raised → Dispositioned → Corrective Action → Verified → Closed with verification evidence.
- **Commissioning**: `system`/`subsystem`/`component(asset tag)` hierarchy, checklist templates per component type (pre-functional, functional), completion % per system = passed checks / total, handover package = documents + warranties + O&M + assets export.
- **Punch analytics**: completion % per area/location, aging = now − created for open items, first-time pass rate = inspections accepted on first attempt / total, defects per area, mean closure time.
