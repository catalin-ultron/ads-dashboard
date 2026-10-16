# D27 RFIs and Submittals

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D27.01 | RFIs | OpenProject work package Type "RFI" + custom fields + role/author/assignee status workflow + relations; ERPNext SLA for due/aging | partial | All attributes expressible (custom fields), routing via assignee + workflow, aging via SLA; no first-class question/official-answer pair, ball-in-court, or cost/schedule-impact semantics |
| D27.02 | Submittal register | OpenProject work package Type "Submittal" + custom fields + `precedes` relation to schedule activity | partial | Register rows, CSI section as custom field, schedule link via relation; no back-calculated submit-by date |
| D27.03 | Submittal review workflow | Mayan document workflow (transition fields, ACL per transition, escalation) over document versions | partial | Multi-step routing with required return-code field on transition and resubmission as new document version; no ball-in-court per party, no review-duration clocks per step |
| D27.04 | Packages and spec parsing | none (OpenProject parent/child work packages for packages) | none | Packages as parent work packages only; no spec-book parsing |
| D27.05 | Field issues → RFIs | OpenProject BCF issue (1:1 work package) + relations | partial | BCF issue → work package (any type), relations `relates`/`requires` give back-links; no "convert issue to RFI" service |
| D27.06 | Design review / comment resolution | OpenProject BCF comments + viewpoints; Mayan document comments | partial | Threaded BCF comments linked to viewpoints and journals; no reviewer discipline, resolution status per comment, or closeout matrix |

## Storage model

### OpenProject — RFI/submittal carrier

**types** (`openproject/app/models/type.rb:36`): `name`, `position`, `is_milestone`, `color`; 1:N **type_variants** (`openproject/app/models/type_variant.rb`: `type_id`, `project_id` nullable, `workflow_id`, `enabled_in_new_projects` — only one variant per type may be enabled for new projects, `:88,205`). A project enables types through `project_types` (type + variant). Default status for a type = first `is_default` status of the variant's statuses (`openproject/modules/bim/app/services/bim/bcf/issues/default_work_package_attributes.rb:61`).

**statuses** (`openproject/db/migrate/tables/statuses.rb:35`): `name`, `is_closed`, `is_default` (single default enforced by `unmark_old_default_value`, `openproject/app/models/status.rb:61`), `is_readonly` (cannot be default, `:108`), `default_done_ratio` 0..100, `excluded_from_totals`, `position`, `color_id`.

**workflows / status transitions** (`openproject/app/models/workflow.rb`, `openproject/app/models/workflows/status_transition.rb`): named `Workflow` (`name` unique per project, nullable `project_id` = global) 1:N `StatusTransition(workflow_id, role_id, old_status_id, new_status_id, author bool, assignee bool)`; legacy table `openproject/db/migrate/tables/workflows.rb:35` had `type_id` in place of `workflow_id`, index (`role_id`,`type_id`,`old_status_id`).

**work_packages** (`openproject/db/migrate/tables/work_packages.rb:35`): `type_id`, `status_id`, `subject` (RFI subject), `description` (question), `assigned_to_id` (current responder), `responsible_id` (accountable), `author_id`, `due_date`, `start_date`, `priority_id`, `category_id` (discipline candidate), `version_id`, `parent_id` (package), `lock_version`. Per-project number `identifier = PROJ-n` (`openproject/app/models/projects/semantic_identifier.rb:37`).

**custom_fields** (`openproject/db/migrate/tables/custom_fields.rb:35`): `type` (WorkPackageCustomField, …), `field_format`, `regexp`, `min_length`, `max_length`, `is_required`, `is_for_all`, `multi_value`, `default_value`, `custom_field_section_id`; activated per type (`custom_fields_types`, unique (`custom_field_id`,`type_id`)) and per project (`custom_fields_projects`). Values in **custom_values** (`customized_type`, `customized_id`, `custom_field_id`, `value` text; `openproject/db/migrate/tables/custom_values.rb:35`). Spec section, drawing refs, cost-impact flag, schedule-impact flag, submittal type, required-on-site date, lead time map here.

**relations** (`openproject/app/models/relation.rb:34`): `from_id`, `to_id`, `relation_type` ∈ relates, precedes/follows (with lag), blocks/blocked, duplicates, includes/partof, requires/required. `WorkPackage#blocked?` = has open blockers (`openproject/app/models/work_package.rb:243`).

**BCF** (`openproject/modules/bim/db/migrate/tables/`):
- `bcf_issues`: `uuid` unique, `markup` XML (original BCF markup), `work_package_id` unique FK CASCADE (1:1), `stage`, `index`, `labels` text[] (`bcf_issues.rb`).
- `bcf_viewpoints`: `uuid` + `issue_id` unique, `viewpoint_name`, `json_viewpoint` jsonb (camera, components, clipping planes), snapshot as attachment (`openproject/modules/bim/app/models/bim/bcf/viewpoint.rb:52-73`).
- `bcf_comments`: `uuid` + `issue_id` unique, `journal_id` (comment text lives in the work-package journal), `viewpoint_id` nullable, `reply_to` self-FK (`bcf_comments.rb`; `openproject/modules/bim/app/models/bim/bcf/comment.rb:37-43`).
- `ifc_models`: `title`, `project_id`, `uploader_id`, `is_default`, `conversion_status` pending|processing|completed|error (`openproject/modules/bim/app/models/bim/ifc_models/ifc_model.rb:40`).

### Mayan — submittal document review

Document (one per submittal item), DocumentFile (each upload), DocumentVersion (`active`), WorkflowInstance + WorkflowInstanceLogEntry with `extra_data` JSON from WorkflowTransitionField (`mayan-edms/mayan/apps/document_states/models/workflow_transition_field_models.py:22`: `field_type` char/integer, `name`, `label`, `default`, `lookup` template of allowed values, `required`, `widget`; unique (`transition`,`name`)). Comments: `mayan-edms/mayan/apps/document_comments/models.py:20` (document, user, text, submit_date).

### ERPNext — aging

SLA fields injectable into any doctype (`response_by`, `sla_resolution_by`, `agreement_status`, `first_responded_on`, `total_hold_time`), see D26 (`erpnext/erpnext/support/doctype/service_level_agreement/service_level_agreement.py:929`).

## Algorithms and logic

**Allowed status transitions for an RFI** `openproject/app/contracts/work_packages/base_contract.rb:724`
1. Current status always allowed (no-op).
2. If status is closed and any target version is closed → only current status (`closed_version_and_status?`, `:741`).
3. Otherwise statuses = new_status of `type_variant.workflows.from_status(status, user_roles, author: user == author, assignee: user was or is assignee)` (`:745`). `StatusTransition.from_status` (`openproject/app/models/workflows/status_transition.rb:53`): rows for those roles where (author ∧ assignee) → all; author ∨ assignee → rows flagged author or assignee per user's relation; neither → rows with both flags false.
4. If the WP is blocked (open blockers via `blocks`) → closed statuses removed (`:736`).
5. Validation error `status_transition_invalid` if the change is not in the set and type did not change (`:364`). Readonly statuses freeze other attributes (`already_in_readonly_status?`, `:768`; `readonly_attributes_unchanged`, `:656`).
- Mapping RFI states: Draft (author-only transitions), Open (assignee = design team), Answered (assignee transition), Closed/Void (closed statuses). Ball-in-court ≈ `assigned_to_id` (inferred).

**Aging / due** — ERPNext SLA `get_expected_time_for` working-hours walk and hold-time arithmetic (D26). Applied to an RFI doctype: response_by = creation + response_time in working hours; status in "pause" set (e.g. awaiting info) accumulates `total_hold_time`.

**BCF issue import → work package** `openproject/modules/bim/app/services/bim/bcf/issues/transform_attributes_service.rb`
- Title missing on import → "(Imported BCF issue contained no title)" (`:47`); author = project user by email or System (`:55`); assignee by email in project or `InexistentUser` placeholder unless `invalid_people_action = anonymize` (`:59,194`).
- Type/status/priority resolved by name; unknown values: `use_default` → project default type / type's default status / default priority, `chose` → selected id, else Inexistent* placeholder that fails validation (`:73-172`).
- Defaults when no import options: default create type = first project type whose variant is *not* enabled in new projects, else first (`default_work_package_attributes.rb:37`).

**Submittal review via document workflow (Mayan)**
- Template example (inferred configuration): states Submitted(initial) → GC Review → A/E Review → Returned(final); transitions carry a required `return_code` field with lookup `A,B,C,D` (`WorkflowTransitionField.lookup/required`); transition ACL per role restricts who can execute each step (`workflow_instance_model_mixins.py:98`); condition on a transition can read instance context, e.g. only allow "Approve" when return_code ∈ {A,B} (`WorkflowTransition.condition`, `workflow_transition_models.py:27`).
- `do_transition` merges transition field values into instance `context` JSON and logs them in `extra_data` (`mayan-edms/mayan/apps/document_states/models/workflow_instance_model_mixins.py:46`).
- Resubmission: upload new file with action `replace` → new active DocumentVersion (`mayan-edms/mayan/apps/documents/document_file_actions.py:66`); an event trigger on `document_version_created` can move the workflow back to GC Review (`WorkflowTransitionTriggerEvent`, `document_states/managers.py:27`).
- Review clocks: `WorkflowStateEscalation` (unit+amount after last log entry) auto-executes an escalation transition (`workflow_instance_model_mixins.py:17`).

**Comment threads on BCF** `openproject/modules/bim/app/models/bim/bcf/comment.rb`: comment uuid unique per issue; optional `viewpoint`; `reply_to` builds a tree; text stored in work package journal so it shares audit/notifications.

## State machines and workflows

- **RFI (OpenProject)**: per-type named workflow; states = statuses; transitions = (role, old, new, author?, assignee?) rows; guards: role membership, author/assignee flags, blocked relation, closed version, readonly status.
- **Submittal (Mayan)**: initial → … → final states with `completion` %; transitions guarded by ACL + condition + required fields; side effects via state entry/exit actions (metadata edit, HTTP call, launch workflow) (`mayan-edms/mayan/apps/document_states/workflow_actions.py:26,98,168`); event-triggered and time-escalated transitions.
- **IFC model conversion**: pending → processing → completed | error.

## Cross-domain links

- D25: submittal files and versions; review states are D25.10 workflows.
- D26: RFI/submittal numbering and SLA response tracking; inbound email replies thread to the RFI (OpenProject References dispatch).
- D28.04/D29: BCF issues/field issues relate to RFIs (`relates`), punch items.
- Scheduling domain: `precedes`/`follows` relations link submittals to schedule activities (OpenProject relations carry lag; inferred use).
- Change management domain: RFI `relates` to change event work packages (cost/schedule impact).

## Gaps

- **Submit-by date**: `submit_by = required_on_site − lead_time − Σ review_durations` (working days) with recomputation when the linked activity's early start moves; no OSS implementation. Needs a calendar-aware subtraction (SLA working-day walk run backwards).
- **Ball-in-court**: explicit `ball_in_court_party(org/user)` per step with timestamps, and duration per party; Mayan log entries give step timestamps but not party.
- **Official response**: a distinct answer record (text, responder, date, attachments) closing the RFI; today only journal notes.
- **Return codes**: A/B/C/D semantics with rule "C/D ⇒ resubmission revision required, A/B ⇒ close"; implement as transition field + condition (pattern exists, codes do not).
- **Spec-book parsing**: CSI MasterFormat section extraction (section number/title, submittal requirement paragraphs) to auto-create register rows.
- **Comment closeout matrix**: per comment `discipline`, `reviewer`, `response`, `status (open/accepted/rejected/closed)`; BCF comments lack status.
