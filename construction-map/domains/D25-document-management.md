# D25 Document Management

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D25.01 | Document register | Mayan EDMS Document + DocumentType + MetadataType; OpenProject Document | partial | Typed documents with per-type required/validated metadata and SHA-256 checksum; no document number/revision/discipline/status columns (must be metadata), no per-org number uniqueness except via Mayan Sequence |
| D25.02 | Revisions and supersede | Mayan DocumentFile + DocumentVersion (`active` flag) | partial | Immutable file history, one active version per document, append/replace/keep actions; no revision code sequence (A,B,C→0,1,2) |
| D25.03 | Folder structures | Mayan Cabinet (MPTT) + IndexTemplate (rule-built tree) + ACL; OpenProject Storages project folders; Mayan checkouts | partial | Hierarchical folders, object ACLs with permission inheritance, check-out locks with expiry; no folder templates per project, folder ACLs do not cascade to documents |
| D25.04 | Bulk upload with metadata | Mayan Sources (staging/watch folders, compressed) + DocumentFileSourceMetadata | partial | Batch ingestion with captured source metadata; no spreadsheet-driven metadata mapping or error report |
| D25.05 | Search and indexing | OpenProject attachment fulltext (tsvector); Mayan OCR content per page | full | Plaintext extraction → PostgreSQL tsvector + GIN; OCR text per version page; saved searches not in backend read |
| D25.06 | Markups and redlines | Mayan converter ObjectLayer/LayerTransformation + redactions | partial | Per-page ordered transformation layers (redaction rectangles); no multi-user markup sessions/merge view |
| D25.07 | Drawing management and sheets | Mayan DocumentFilePage / DocumentVersionPage remap | partial | Page split of uploaded file, version pages remapped from file pages; no sheet-number OCR or sheet hyperlinking |
| D25.08 | Distribution and access | Mayan mailer (attachment/link), events; OpenProject Nextcloud permission sync | partial | Send as attachment or link, download/view events; no expiring public links in code read |
| D25.09 | Retention, archive, handover | Mayan DocumentType trash/delete periods; document_exports | partial | Time-based auto-trash and purge per type; no archive package (documents+mail+metadata) export |
| D25.10 | Approval states | Mayan Workflow (states, transitions, conditions, escalation, triggers) | full | Document-level state machine with role ACL, conditional transitions, entry/exit actions, timed escalation |
| D25.11 | File storage service | Mayan storage/file_caching/converter/duplicates + OpenProject ClamAV job | full | Pluggable storage, SHA-256, LRU page-image cache, ClamAV scan + quarantine, checksum duplicate detection, PDF/image conversion |

## Storage model

### Mayan EDMS (Django)

**DocumentType** `mayan-edms/mayan/apps/documents/models/document_type_models.py:32`
- `label` CharField (natural key), `filename_generator_backend` + `_arguments` (YAML), `trash_time_period` int + `trash_time_unit` (timedelta unit), `delete_time_period` + `delete_time_unit`, `document_stub_pruning_enabled` bool, `document_stub_expiration_interval` bigint seconds.
- **DocumentTypeFilename** (`:139`): quick labels, unique (`document_type`, `filename`).

**Document** `mayan-edms/mayan/apps/documents/models/document_models.py:26`
- `uuid` UUID (natural key, `:39`), `document_type` FK→DocumentType CASCADE, `label` (indexed, default = first filename), `description`, `datetime_created`, `language`.
- `in_trash` bool + `trashed_date_time` (`:74`) — soft delete; `is_stub` bool (`:85`) = DB row without uploaded file.
- `file_latest` 1:1→DocumentFile SET_NULL (`:33`); `version_active` 1:1→DocumentVersion SET_NULL (`:92`).
- `delete()` (`:111`) first trashes (sets `in_trash`), a second delete removes files and row.

**DocumentFile** (physical upload, immutable) `mayan-edms/mayan/apps/documents/models/document_file_models.py:30`
- `document` FK (related `files`), `timestamp`, `comment`, `file` FileField on defined storage `STORAGE_NAME_DOCUMENT_FILES`, `filename`, `mimetype`, `encoding`, `checksum` (indexed, `:92`), `size` bigint (`:99`). Natural key (`checksum`, document uuid). Ordered by `timestamp`.

**DocumentFilePage** (one row per page detected by converter): `document_file` FK, `page_number`.

**DocumentVersion** (logical, page-composed) `mayan-edms/mayan/apps/documents/models/document_version_models.py:23`
- `document` FK (related `versions`), `timestamp`, `comment`, `active` bool.
- **DocumentVersionPage** `mayan-edms/mayan/apps/documents/models/document_version_page_models.py:30`: `document_version` FK, `page_number`, generic FK (`content_type`, `object_id`) → usually a DocumentFilePage; unique (`document_version`, `page_number`).
- A version is therefore a page list that can mix pages from several files.

**MetadataType** `mayan-edms/mayan/apps/metadata/models/metadata_type_models.py:18`: `name` unique, `label`, `default` (template), `lookup` (template producing allowed options, `:39`), `validation` + `validation_arguments` (validator class path, `:45`), `parser` + `parser_arguments` (`:58`).
- **DocumentTypeMetadataType** `mayan-edms/mayan/apps/metadata/models/document_type_metadata_type_models.py:17`: (`document_type`, `metadata_type`) unique, `required` bool (`:26`).
- **DocumentMetadata** `mayan-edms/mayan/apps/metadata/models/metadata_instance_models.py:22`: `document` FK, `metadata_type` FK, `value` Text; unique (`document`, `metadata_type`) (`:44`).

**Sequence** `mayan-edms/mayan/apps/sequences/models.py:18`: `label`, `internal_name`, `position` bigint zero-based counter (`:37`), `value_is_unique`, `on_limit` (raise | wrap), M2M `document_types`; backend renders value for a position.

**Cabinet** (folder tree) `mayan-edms/mayan/apps/cabinets/models.py:24`: MPTT `parent` TreeForeignKey, `label`, M2M `documents`; unique (`parent`, `label`) (`:44`).

**IndexTemplate / IndexTemplateNode / IndexInstanceNode** `mayan-edms/mayan/apps/document_indexing/models/index_template_models.py:24,131`, `index_instance_models.py:39`: template node `expression` (Django template evaluated per document), `link_documents` bool, MPTT tree; instance nodes store evaluated `value` and linked documents; `IndexTemplateEventTrigger` (`:90`) rebuilds on chosen event types.

**DocumentCheckout** `mayan-edms/mayan/apps/checkouts/models.py:28`: `document` 1:1 (one active checkout), `checkout_datetime`, `expiration_datetime`, `user` FK, `block_new_file` bool (`:46`).

**AccessControlList** `mayan-edms/mayan/apps/acls/models.py:23`: generic FK (`content_type`, `object_id`) + `role` FK + M2M `permissions`; unique (`content_type`, `object_id`, `role`) (`:54`).

**Converter layers** `mayan-edms/mayan/apps/converter/models.py:92,112,140`: `StoredLayer` (`name`, `order`), `ObjectLayer` (generic FK to a page, `stored_layer`, `enabled`; unique per object+layer), `LayerTransformation` (`object_layer`, `order`, `name`, `arguments` YAML, `enabled`; unique (`object_layer`,`order`)). Redaction transformation `mayan-edms/mayan/apps/redactions/transformations.py:10` (`redaction_percent` rectangle).

**OCR** `mayan-edms/mayan/apps/ocr/models.py:18,40`: `DocumentTypeOCRSettings.auto_ocr`; `DocumentVersionPageOCRContent` 1:1 version page, `content` Text.

**Signatures** `mayan-edms/mayan/apps/document_signatures/models.py:30,73,135`: per DocumentFile `date_time`, `key_id`, `signature_id`, `public_key_fingerprint`; `DetachedSignature.signature_file` / `EmbeddedSignature`.

**Other**: `Comment` (`mayan-edms/mayan/apps/document_comments/models.py:20`: document, user, text, submit_date); `Tag` (M2M documents, `mayan-edms/mayan/apps/tags/models.py:14`); `DocumentFileSourceMetadata` (`mayan-edms/mayan/apps/sources/models.py:16`: key/value per file, unique (`document_file`,`key`)); `FileMetadataEntry` (`mayan-edms/mayan/apps/file_metadata/models.py:87`: driver output key/value per file, e.g. EXIF); `DuplicateBackendEntry` (`mayan-edms/mayan/apps/duplicates/models.py:37`); file cache `Cache`/`CachePartition`/`CachePartitionFile` (`mayan-edms/mayan/apps/file_caching/models.py:18,74,102`: `datetime`, `accessed`, `file_size`, `hits`).

### OpenProject

**documents** `openproject/modules/documents/app/models/document.rb:30`: `project_id`, `type_id`→DocumentType (counter cache), `title` ≤255, `description`, `kind` enum (classic | collaborative), timestamps; `acts_as_attachable`, `acts_as_journalized`, `acts_as_searchable` (title, description). Visibility = project permission `view_documents` (`:58`).
- **DocumentType** (`document_type.rb:30`): `name` unique case-insensitive, `position`, `is_default`, `documents_count`; last type cannot be deleted (`:66`); destroy can reassign documents (`:57`).

**attachments** `openproject/db/migrate/tables/attachments.rb:32`: polymorphic `container_id/container_type`, `filename`, `disk_filename`, `filesize` bigint, `content_type`, `digest` (MD5, 40 chars), `downloads` int, `author_id`, `description`, `file`, `fulltext` text (≤4 MB), `fulltext_tsv` + `file_tsv` tsvector (GIN), `status` int. Status enum `uploaded|prepared|scanned|quarantined|rescan` (`openproject/app/models/attachment.rb:33`).
- Journaled copies: `attachment_journals`, `attachable_journals` (`journal_id`, `attachment_id`, `filename`).

**journals** `openproject/db/migrate/tables/journals.rb:32`: polymorphic `journable`, `user_id`, `notes`, `version` (unique per journable), polymorphic `data` (snapshot row in `<model>_journals`), `cause` jsonb, `validity_period` tstzrange with exclusion constraint forbidding overlap per journable (`:56`), `restricted`.

**Storages** `openproject/modules/storages/app/models/storages/project_storage.rb:34`: `project`↔`storage` unique pair, `project_folder_mode` enum inactive | manual | automatic (`:45`), `project_folder_id`. **file_links** (`openproject/modules/storages/db/migrate/tables/file_links.rb`): `storage_id`, `creator_id`, polymorphic container (only WorkPackage, `file_link.rb:38`), `origin_id`, `origin_name`, `origin_mime_type`, `origin_created_at/updated_at`, creator names; index (`origin_id`,`storage_id`).

## Algorithms and logic

**Upload pipeline (Mayan)** `mayan-edms/mayan/apps/documents/models/document_model_mixins.py:92` → `document_file_model_mixins.py:77,122`
1. `files_upload(file_object, action_name, comment)` creates DocumentFile; pre-create hooks run first (`:86`) — checkouts hook raises `NewDocumentFileNotAllowed` when another user holds a blocking checkout (`mayan-edms/mayan/apps/checkouts/hooks.py:25`).
2. `_create` saves, sets `document.file_latest = self`, `is_stub = False`, label = filename if empty (`:103`).
3. `_introspect` (`:122`): checksum (`:234`) = SHA-256 (`:38`) streamed in `setting_hash_block_size` chunks; MIME type/encoding via MIME backend (`:330`); size from storage (`:420`); page count via converter, deletes old page rows and bulk-creates `DocumentFilePage(page_number=1..n)` in batches (`:347`). Converter failure writes an error-log row instead of raising.
4. `versions_new(action_name)` (`:444`) dispatches a DocumentFileAction (`mayan-edms/mayan/apps/documents/document_file_actions.py`):
   - `append` (`:7`): new active version = active version pages + new file pages renumbered from `count+1`.
   - `replace` (`:66`): new active version = new file pages only.
   - `keep` (`:54`): file stored, no new version.
5. `pages_remap` (`document_version_model_mixins.py:251`) in one transaction deletes current version pages and bulk-creates new `DocumentVersionPage` rows; emits per-page events.

**Active version invariant** `document_version_model_mixins.py:52`: `active_set` sets `active=False` on all sibling versions, sets self active and `document.version_active`; `active_unset` (`:70`) clears the pointer. `DocumentVersion.save` (`document_version_models.py:92`) calls one of them on every save. Result: exactly one active version per document; file history is never rewritten (files only deleted explicitly, which recomputes `file_latest` = latest remaining by timestamp, `document_file_models.py:137`).

**Metadata validation** `mayan-edms/mayan/apps/metadata/models/metadata_type_models.py:105`: empty value → default template; still empty and required for the document type → error; `lookup` defined → value must be in rendered option list; `validation` class runs; `parser` normalises the stored value. `DocumentMetadata.save` rejects a metadata type not attached to the document type (`metadata_instance_models.py:98`); delete of a required entry is refused (`:64`).

**Numbering** `mayan-edms/mayan/apps/sequences/managers.py:33`: `SELECT … FOR UPDATE` on the sequence row, check `position + count` against backend limit; on limit either wrap to 0 or raise `SequenceExhausted`; values rendered for positions `[start, start+count)`; position advanced and saved inside the same transaction. Gives gap-free unique numbers per sequence; uniqueness per org needs one sequence per org (inferred).
- OpenProject per-project numbering for work packages: `UPDATE projects SET wp_sequence_counter = wp_sequence_counter + n RETURNING …` under a project advisory lock, identifier = `"#{project.identifier}-#{seq}"` (`openproject/app/models/projects/semantic_identifier.rb:37,135`).

**Check-out / check-in** `mayan-edms/mayan/apps/checkouts/models.py`, `mayan-edms/mayan/apps/checkouts/managers.py`
- Create: refused if document already checked out (`models.py:97`); `expiration_datetime` must be in the future (`:63`).
- Check-in by owner needs `document_check_in`; others need `document_check_in_override` (`managers.py:28`). Event type distinguishes normal / forced / automatic check-in (`models.py:73`).
- Periodic `check_in_expired_check_outs` (`managers.py:52`) releases checkouts with `expiration_datetime <= now`.

**Permission evaluation** `mayan-edms/mayan/apps/acls/managers.py:253` `restrict_queryset(permission, queryset, user)`: global role permission → full queryset; otherwise OR of ACL filters for the user's roles on each object, plus inherited ACLs through registered model inheritance paths (e.g. document type → document, `_get_inherited_object_permissions` `:292`); unauthenticated → empty.

**Retention** `mayan-edms/mayan/apps/documents/managers.py:81,119,157`: per document type, `check_trash_periods` trashes documents with `datetime_created < now − trash_period`; `check_delete_periods` purges trashed documents with `trashed_date_time < now − delete_period`; `document_stubs_delete` hard-deletes stubs older than `document_stub_expiration_interval`.

**Fulltext indexing (OpenProject)** `openproject/app/workers/attachments/extract_fulltext_job.rb:68`: `Plaintext::Resolver` extracts text by content type; one UPDATE sets `fulltext`, `fulltext_tsv = to_tsvector(lang, normalized_text)`, `file_tsv = to_tsvector(lang, normalized_filename)`. Triggered from `Attachment#enqueue_jobs` (`openproject/app/models/attachment.rb:292`); backfill `extract_fulltext_where_missing` (`:308`).

**Virus scanning** `openproject/app/workers/attachments/virus_scan_job.rb:39`: only when scanning enabled and status `uploaded`; advisory lock per attachment; ClamAV response → success sets `scanned`; virus → setting `antivirus_scan_action` either deletes attachment and journals a note on the container, or journals and sets `quarantined` (`:74,91`); other responses raise and retry 3× at 5 s. Mayan equivalent: `mayan-edms/mayan/apps/file_metadata_clamav/drivers.py:19` stores the scan result as file metadata.

**Duplicates** `mayan-edms/mayan/apps/duplicates/duplicate_backends.py:7`: exact duplicate = other valid documents whose `file_latest.checksum` equals this document's; label backend matches by label. Results cached in `DuplicateBackendEntry`.

**Page-image cache eviction** `mayan-edms/mayan/apps/file_caching/model_mixins.py:85,134`: candidates ordered by (`accessed`, `hits`) ascending, preferring files older than a grace period; `prune` deletes until total size < `maximum_size`, skipping locked files, aborting after N lock failures.

**Rule-based folders** `document_indexing`: each IndexTemplateNode expression renders against document properties/metadata; resulting values become IndexInstanceNodes; documents linked where `link_documents`; rebuilt on configured events (`IndexTemplateEventTrigger`).

**External storage permissions (OpenProject → Nextcloud)** `openproject/modules/storages/app/services/storages/nextcloud_managed_folder_permissions_service.rb:109`: per automatic project folder, ACL = storage technical user (all file permissions) + group (none) + remote admins (all) + each project member's `all_permissions_for(project) ∩ FILE_PERMISSIONS`; public projects add non-member role permissions (`:144`); then group membership synced.

## State machines and workflows

**Document lifecycle (Mayan)**: stub (`is_stub`) → active → trashed (`in_trash`, restorable) → deleted. Trash/delete transitions are manual or time-driven per type.

**Workflow engine (Mayan document_states)** — the approval-state mechanism for D25.10.
- Template: `Workflow` (`mayan-edms/mayan/apps/document_states/models/workflow_models.py:23`: `internal_name`, `label`, M2M `document_types`, `auto_launch`, `ignore_completed`), `WorkflowState` (`workflow_state_models.py:21`: `label`, `initial`, `final`, `completion` int %), `WorkflowTransition` (`workflow_transition_models.py:23`: `origin_state`, `destination_state`, `condition` template; unique (workflow,label,origin,destination)), `WorkflowTransitionField` (`workflow_transition_field_models.py:22`: typed form fields required on transition, `lookup`, `required`), `WorkflowTransitionTriggerEvent` (`workflow_transition_trigger_models.py:22`: transition fires on event type), `WorkflowStateAction` (`workflow_state_action_models.py:25`: `when` on-entry=1 / on-exit=2, backend class + args), `WorkflowStateEscalation` (`workflow_state_escalation_models.py:26`: `transition`, `priority`, `unit`+`amount`, condition, comment).
- Runtime: `WorkflowInstance` (`workflow_instance_models.py:28`: `workflow`, `document`, `state_active`, JSON `context`; unique (document, workflow)), `WorkflowInstanceLogEntry` (`:98`: `transition` nullable = initial entry, `user`, `comment`, `extra_data` JSON, `datetime`).
- Launch: on document create or type change, auto-launch workflows for the type (`mayan-edms/mayan/apps/document_states/handlers.py:21,37`); `launch_for` (`mayan-edms/mayan/apps/document_states/models/workflow_model_mixins.py:160`) creates instance in `initial` state and an initial log entry.
- Valid transitions (`mayan-edms/mayan/apps/document_states/models/workflow_instance_model_mixins.py:98`): `state_active.origin_transitions`, restricted by ACL permission `workflow_instance_transition` for the user, minus transitions whose condition evaluates false.
- `do_transition` (`:46`): must be in valid set; merges `extra_data` into instance context; `do_execute` (`workflow_transition_model_mixins.py:38`) atomically sets `state_active = destination` and writes a log entry; log entry save (`workflow_instance_models.py:162`) runs origin exit actions then destination entry actions (`workflow_state_model_mixins.py:20,26`). `clean` validates transition fields (`workflow_instance_models.py:138`).
- Event triggers (`mayan-edms/mayan/apps/document_states/managers.py:27`): on any event whose target or action object is a document, find instances with a matching trigger transition that is currently valid and execute the first; instances in a final state of `ignore_completed` workflows are skipped.
- Escalation (`mayan-edms/mayan/apps/document_states/models/workflow_instance_model_mixins.py:17`): for non-final states, when `now > last_log_entry.datetime + escalation delta` and condition true, execute the escalation transition (periodic task every 5 min, `mayan-edms/mayan/apps/document_states/literals.py:17`).
- Built-in actions include document property edit, launch other workflows, HTTP request (`mayan-edms/mayan/apps/document_states/workflow_actions.py:26,98,168`), metadata edit (`mayan-edms/mayan/apps/metadata/workflow_actions.py`).

**Checkout**: checked-in ↔ checked-out (create checkout / delete checkout by owner, override, or expiry).

**OpenProject attachment status**: uploaded → scanned | quarantined | (deleted); `prepared` = direct-upload pending; `rescan` re-queues.

## Cross-domain links

- D26 Transmittals/Correspondence: Mayan mailer sends documents as attachment or link (`mayan-edms/mayan/apps/mailer/mailing_actions.py:74,91`); OpenProject incoming email attaches files to work packages (see D26).
- D27 RFIs/Submittals: Mayan workflows provide review routing over document versions; OpenProject attachments and file_links attach documents to work packages (RFI/submittal records).
- D28 Field: EXIF metadata via `file_metadata_exif` drivers feeds photo records; BCF viewpoints carry snapshots (D28.04).
- D29 Quality: commissioning/handover packages need D25 document sets.
- D31 Assets: O&M manuals and warranties attach to assets (ERPNext Asset `image`/attachments, inferred).
- Platform: ACLs/roles (Mayan acls, OpenProject roles) shared with the access-control domain; journals/events feed audit.

## Gaps

- **Document number + revision code scheme**: no OSS entity stores `number`, `revision` (A,B,C then 0,1,2), `status code` (For Review / For Construction / As-Built) as first-class columns. Rebuild: `document(number unique per project/org, title, discipline, type, current_revision_id)`, `revision(document_id, rev_code, rev_seq, status, issued_at, superseded_by)` with a revision-sequence state (alpha pre-issue → numeric post-IFC) and Mayan-style immutable files under each revision.
- **Supersede semantics**: Mayan's single `active` version is the closest; need explicit `superseded` flag and reason, and transmittal linkage per revision.
- **Folder templates and cascading folder permissions**: Cabinets have no ACL inheritance to contained documents; rebuild needs folder-template cloning per project and permission resolution walking the MPTT ancestors.
- **Bulk metadata import**: spreadsheet row ↔ file matching, per-row validation report (Mayan's `validate_value` can be reused per cell).
- **Markup sessions**: multi-user annotation overlays per version page with author/timestamp and merged view; Mayan layers give storage shape (ordered transformations per page) but are not per user.
- **Drawing sheets**: title-block OCR to extract sheet number/title, sheet sets, automatic cross-sheet hyperlinks.
- **Expiring share links and download audit per external party**; **archive package export** (documents + correspondence + metadata manifest).
