# D26 Correspondence and Transmittals

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D26.01 | Mail / correspondence | OpenProject work packages + journals + IncomingEmails dispatch; ERPNext Issue | partial | Typed records with per-project sequential identifier, threaded replies via `References` header, attachments, watchers; no from/to/cc org model, no per-mail-type per-org numbering, no confidential flag |
| D26.02 | Transmittals | Mayan mailer (send documents as attachment/link) | none | No transmittal entity, no revision list, no access grant on send, no acknowledgement |
| D26.03 | Mail types and custom fields | OpenProject Type + custom fields + workflows; Mayan DocumentType + MetadataType | partial | Per-type field sets and status workflows; numbering is per project, not per type |
| D26.04 | Response tracking | ERPNext Service Level Agreement engine (generic, attachable to any doctype) | full | response_by / resolution_by from working-hours calendar and holidays, hold time excluded, agreement status First Response Due → Resolution Due → Fulfilled/Failed |
| D26.05 | Meeting minutes | OpenProject Meeting module; ERPNext Quality Meeting | full | Meetings with participants (invited/attended/RSVP), sections, agenda items, outcomes (information/decision/work package), recurring series with shared backlog for carry-forward |
| D26.06 | Email ingestion | OpenProject IncomingEmails::DispatchService; Mayan IMAP/POP3 sources; ERPNext Project Update reply collection | full | Inbound mail → new record or reply via encoded reference; attachments extracted; auto-submitted mail ignored; IMAP search/move/expunge |

## Storage model

### OpenProject — correspondence carrier (work packages)

**work_packages** `openproject/db/migrate/tables/work_packages.rb:35`: `type_id` FK, `project_id` FK, `subject`, `description`, `due_date`, `status_id` FK, `assigned_to_id`, `responsible_id`, `priority_id`, `author_id`, `category_id`, `version_id`, `parent_id`, `start_date`, `done_ratio`, `lock_version` (optimistic lock), CHECK `due_date >= start_date` (`:63`). Semantic identifier columns `sequence_number`, `identifier` (`openproject/app/models/work_package/semantic_identifier.rb:75`).
- **WorkPackageSemanticAlias** `openproject/app/models/work_package_semantic_alias.rb`: `identifier` unique → work_package; keeps old project prefixes resolvable.
- **relations** `openproject/app/models/relation.rb:34`: types relates, precedes/follows, blocks/blocked, duplicates/duplicated, includes/partof, requires/required (used for "reference to other mail").
- **journals** `openproject/db/migrate/tables/journals.rb:32`: one row per change (`version`, `notes` = reply body, `user_id`, `cause` jsonb, `validity_period` tstzrange non-overlapping per journable) with a snapshot row in `<model>_journals`. Replies to a record are journals with notes.
- **attachments** (see D25) and **watchers** (`openproject/app/models/watcher.rb`) give cc-like distribution.

### OpenProject — meetings `openproject/modules/meeting`

| Table | Key fields | Relations |
|---|---|---|
| meetings (`openproject/modules/meeting/db/migrate/tables/meetings.rb`) | `title`, `location`, `start_time`, `duration` float h, `state` int, `lock_version`, `type`, `template` bool, `recurring_meeting_id`, `recurrence_start_time`, `sharing`, `agenda_sorting_mode` | N:1 project, author; 1:N participants, sections, agenda_items; 1:1 own backlog section |
| meeting_participants (`openproject/modules/meeting/db/migrate/tables/meeting_participants.rb`) | `user_id`, `meeting_id`, `email`, `name`, `invited` bool, `attended` bool, `participation_status` (needs-action, accepted, declined, tentative, unknown; `openproject/modules/meeting/app/models/meeting_participant.rb:40`), comment | unique (user, meeting) (`meeting_participant.rb:35`) |
| meeting_sections (`openproject/modules/meeting/db/migrate/tables/meeting_sections.rb`) | `position`, `title`, `backlog` bool | N:1 meeting; 1:N agenda items |
| meeting_agenda_items (`openproject/modules/meeting/db/migrate/tables/meeting_agenda_items.rb`) | `title`, `notes`, `position`, `duration_in_minutes`, `item_type` (simple=0, work_package=1), `work_package_id`, `presenter_id`, `author_id`, `meeting_section_id`, `lock_version` | N:1 meeting, section; 1:N outcomes; emoji votes (`openproject/modules/meeting/app/models/meeting_agenda_item.rb:30`) |
| meeting_outcomes (`openproject/modules/meeting/db/migrate/tables/meeting_outcomes.rb`) | `notes`, `kind` (information=0, decision=1, work_package=2; `openproject/modules/meeting/app/models/meeting_outcome.rb:36`), `work_package_id`, `author_id` | N:1 agenda item |
| recurring_meetings (`openproject/modules/meeting/db/migrate/tables/recurring_meetings.rb`) | `start_time`, `end_date`, `title`, `frequency` (daily, working_days, weekly, monthly_day_of_month, monthly_nth_weekday; `openproject/modules/meeting/app/models/recurring_meeting.rb:87`), `interval`, `end_after`, `iterations`, `time_zone` | 1:1 template meeting; 1:N occurrence meetings |

Meeting journals for meetings, sections, agenda items, outcomes, participants exist (`openproject/modules/meeting/db/migrate/20261012100000_create_meeting_outcome_journals.rb` etc.), so minutes are versioned.

### ERPNext — response tracking

**Service Level Agreement** `erpnext/erpnext/support/doctype/service_level_agreement/service_level_agreement.json`: `document_type` Link(DocType)* (any doctype), `service_level`, `default_priority`, `priorities` Table(Service Level Priority: `priority`, `response_time` Duration*, `resolution_time` Duration, `default_priority`), `support_and_resolution` Table(Service Day: `workday`, `start_time`, `end_time`), `holiday_list`*, `pause_sla_on` Table(status), `sla_fulfilled_on` Table(status)*, `apply_sla_for_resolution`, `condition` (Python expression), `entity_type`/`entity`, `start_date`/`end_date`, `enabled`.
- Fields injected into the target doctype (`service_level_agreement.py:254,287,929`): `service_level_agreement`, `priority`, `response_by`, `first_responded_on`, `on_hold_since`, `total_hold_time`, `agreement_status` (First Response Due | Resolution Due | Fulfilled | Failed), `sla_resolution_by`, `sla_resolution_date`, `service_level_agreement_creation`.
- **Issue** (`erpnext/erpnext/support/doctype/issue/issue.json`): `subject`, `raised_by`, `status` (Open | Replied | On Hold | Resolved | Closed), `priority`, `issue_type`, `project`, `email_account`, `issue_split_from`, plus the SLA fields and `first_response_time`, `avg_response_time`, `resolution_time`.

**Quality Meeting** `erpnext/erpnext/quality_management/doctype/quality_meeting/quality_meeting.json`: autoname `QA-MEET-{YY}-{MM}-{DD}-.###`, `status` (Open | Closed), `agenda` Table(`agenda` text), `minutes` Table(`minute` text, `document_type` Select(Quality Review | Quality Action | Quality Feedback)*, `document_name` Dynamic Link).

**Project Update** (`erpnext/erpnext/projects/doctype/project_update/project_update.json`): `project`, `date`, `time`, `sent`, `users` Table(Project User: `user`, `project_status` = parsed reply).

### Mayan — inbound/outbound mail plumbing

- Email sources: `mayan-edms/mayan/apps/source_emails/source_backends/imap_source_backends.py:20` (host, ssl, port, mailbox, `search_criteria`, `mailbox_destination`, `execute_expunge`, `store_body`), `pop3_source_backends.py:17`.
- Each extracted file stores email headers as `DocumentFileSourceMetadata` key/values `email_<header>` (`mayan-edms/mayan/apps/sources/models.py:16`).
- Outbound: `UserMailer` profiles (`mayan-edms/mayan/apps/mailer/models.py:18`), mailing actions attachment / link (`mailer/mailing_actions.py:74,91`).

## Algorithms and logic

**Inbound email dispatch (OpenProject)** `openproject/app/services/incoming_emails/dispatch_service.rb`
1. `MailHandler.receive` parses raw RFC822 (`mail_handler.rb:35`) and calls DispatchService.
2. Ignore mail if sender is a system address, sender ignored, or an automation header matches (`Auto-Submitted: auto-*` etc., `dispatch_service.rb:38,233`).
3. Actor = user by sender address; unknown senders handled per option (reject / create user / anonymous) (`:152,163`).
4. Object reference from `References` header: last entry matching `^<?op\.([a-z_]+)-(\d+)@` (`:34,259`) — outgoing OpenProject mail embeds `op.<type>-<id>@` so replies thread to the right object even if the gateway rewrites Message-ID (`:86-95`).
5. First registered handler whose `handles?(email, reference:)` is true processes it: work package reply, journal reply, meeting response (iCal RSVP), forum message reply (`handlers/`). No reference → `receive_new_work_package` in the target project (`handlers/work_package.rb:73`).
6. Keyword lines in the body (`Status:`, `Assignee:`, `Due date:`, `Type:`, `Priority:`, `Version:` …) set attributes (`handlers/work_package.rb:154-242`); attachments created except ignored filename patterns (`handlers/base.rb:62,75`); sender/recipients added as watchers (`:102`); quoted text stripped (`:52`).

**Inbound email (Mayan)** `mayan-edms/mayan/apps/source_emails/source_backends/mixins.py:96`: recursive MIME walk; every header copied to source metadata; parts that are attachments or inline with non-empty content become document files (filename or `attachment-n`); body part stored as `email_body.txt|html` only if `store_body`. IMAP flow: `UID SEARCH <criteria>` → `UID FETCH (RFC822)` → after processing `COPY` to destination mailbox and/or flag deleted, optional `EXPUNGE` (`imap_source_backends.py:169,203,220`).

**Reply harvesting into status records (ERPNext)** `erpnext/erpnext/projects/doctype/project/project.py:746-870`: projects with `collect_progress` get a Project Update record and an email (`reply_to` = default incoming account) at the configured frequency (Hourly within from/to window that may cross midnight `:640`, Twice Daily, Daily, Weekly); holidays skipped. `collect_project_status` (`:787`) reads received Communications referencing the update, maps sender→user, parses reply text (EmailReplyParser), de-duplicates against already collected (user, text) pairs with a Counter, appends rows. Next day a summary email is sent and `sent=1`.

**Response due-date calculation (ERPNext SLA)** `erpnext/erpnext/support/doctype/service_level_agreement/service_level_agreement.py`
- `apply` on validate (`:521`): skip if doctype has no active SLA or the doc stays resolved (both previous and new status in fulfilled set and SLA/priority unchanged, `:544`). Select agreement by entity/condition/default (`:342`). Priority defaults to SLA default.
- `get_expected_time_for(parameter, priority, start)` (`:688`): allotted = response_time or resolution_time seconds; walk day by day: skip holidays and non-support weekdays; on the start day begin at max(now, day start); `time_left_today = end_time − start_time`; if `time_left ≥ allotted` → due = start + allotted; else subtract and continue next day. If allotted ≥ 1 day, due snaps to that day's `end_time`.
- `set_response_by`/`set_resolution_by` (`:895,908`) add accumulated `total_hold_time` seconds.
- Status transitions (`handle_status_change` `:580`), with three status classes — hold (pause_sla_on), fulfilled (sla_fulfilled_on), open (others):
  - open→not open or first reply: set `first_responded_on`, `first_response_time`; record assignees if late.
  - open→hold: `on_hold_since = now`, clear expected times.
  - hold→open: `total_hold_time += now − on_hold_since`; reset resolution metrics.
  - open→fulfilled: `sla_resolution_date = now`, compute resolution time.
  - fulfilled→open / fulfilled→hold: add hold time from `sla_resolution_date`, reset resolution.
  - hold→fulfilled: add hold time, set resolution if `apply_sla_for_resolution`.
- `update_agreement_status` (`:1009`): no first response → First Response Due; no resolution → Resolution Due; resolved by `sla_resolution_by` → Fulfilled else Failed (response-only mode compares `first_responded_on` vs `response_by`).
- Daily `check_agreement_status` disables SLAs past `end_date` (`:329`).

**Meeting carry-forward and copy (OpenProject)**
- Backlog: `Meeting#backlog` (`openproject/modules/meeting/app/models/meeting.rb:336`) — for an occurrence of a recurring series the backlog is the series template's backlog section, so items parked there are shared across all occurrences. Moving items between an occurrence section and the series backlog is resolved in `MeetingAgendaItems::DropService#target_section` (`openproject/modules/meeting/app/services/meeting_agenda_items/drop_service.rb:152`); cross-meeting moves are journaled on the linked work package (`journalize_move_on_work_package`).
- Occurrence instantiation `RecurringMeetings::InitOccurrenceService` (`openproject/modules/meeting/app/services/recurring_meetings/init_occurrence_service.rb:120`): copy template with agenda and attachments, `recurrence_start_time = start_time`; restoring a cancelled occurrence re-opens it and re-sends invitations; interim RSVP responses moved to participants (`:138`). Template in `draft` cannot instantiate.
- `Meetings::CopyService` (`openproject/modules/meeting/app/services/meetings/copy_service.rb:79,122`): new meeting `start_time + 1 day`, `state = open`, participants copied, sections and items duplicated; attachment URLs in notes rewritten.
- Action items: outcome of kind `work_package` must reference a work package (`meeting_outcome.rb:44`); `MeetingOutcomes::CreateWithWorkPackageService` creates the WP (owner/due on the WP); open action items carry forward as open work packages (inferred).
- Duration check: `duration_exceeded_by_agenda_items?` compares sum of `duration_in_minutes` with meeting duration (`meeting.rb:324-334`).

**Numbering** `openproject/app/models/projects/semantic_identifier.rb:37,135`: atomic `UPDATE projects SET wp_sequence_counter = wp_sequence_counter + n RETURNING` under advisory lock `wp_sequence_<project_id>`; identifier `PROJ-<n>`; aliases inserted for all historical project slugs so renamed projects still resolve (`openproject/app/models/work_package/semantic_identifier.rb:231`). Mayan Sequence (D25) offers locked counters attachable per document type, i.e. per "mail type".

## State machines and workflows

**Meeting state** `openproject/modules/meeting/app/models/meeting.rb:145`: `open(0)`, `draft(1)`, `in_progress(3)`, `cancelled(4)`, `closed(5)`.
- Guards: meeting editable only if not closed and user has `edit_meetings` (`:272`); agenda items editable unless meeting closed (`meeting_agenda_item.rb:172`); outcomes editable only while `in_progress` (`meeting_outcome.rb:46`). Copies always start `open`. Occurrences can be cancelled and restored.

**Correspondence status (OpenProject)**: status set per type via named Workflow → `Workflows::StatusTransition(role, old_status, new_status, author, assignee)` (`openproject/app/models/workflows/status_transition.rb:53`); validation `status_transition_invalid` unless an allowed transition exists for the user's roles, author/assignee flags (`openproject/app/contracts/work_packages/base_contract.rb:364,724`).

**ERPNext Issue / SLA**: status Open → Replied/On Hold (hold) → Resolved/Closed (fulfilled); agreement_status First Response Due → Resolution Due → Fulfilled | Failed; reopen resets resolution and accumulates hold time.

**Quality Meeting**: Open ↔ Closed (plain select, no guards).

## Cross-domain links

- D25: attachments and document revisions referenced from mail; Mayan email sources create documents.
- D27: RFIs are correspondence of type RFI; SLA response tracking applies to RFI/submittal due dates; meeting agenda items link work packages (RFIs, issues).
- D28/D29/D30: meeting outcomes create work packages (field issues, punch items, safety actions).
- D33: response-time KPIs (first_response_time, resolution_time) feed RFI turnaround metrics.
- Calendars: SLA uses Holiday List and Service Day working windows (shared with scheduling calendars domain).

## Gaps

- **Transmittal entity**: rebuild `transmittal(number, project, from_org, reason_for_issue, response_required_by, status)` + `transmittal_item(document_revision_id, copies, format)` + `transmittal_recipient(org, user, acknowledged_at)`; on issue, insert ACL grants for recipient org on the listed revisions (Mayan ACL model is a fit), start SLA for response, record acknowledgement event.
- **Organisation-aware mail**: from/to/cc as organisations and users, confidential flag restricting visibility to addressed orgs, mail templates.
- **Per-mail-type per-org numbering**: combine a sequence row keyed (project, org, mail_type) with the locked increment pattern of `sequences/managers.py:33` / OpenProject `allocate_sequence_range!`.
- **Awaiting-response registers**: query layer over SLA fields (response_by < now and no first_responded_on).
- **Meeting item carry-forward for one-off meetings**: only recurring-series backlog exists; one-off series need explicit "copy open items" filtered by outcome status.
