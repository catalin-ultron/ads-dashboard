# D34 Integrations and APIs

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D34.01 | P6 EPPM Web Services (SOAP) | MPXJ `primavera/webservices/WebServicesReader` (REST variant only) | none | No SOAP client/server code; object CRUD with field lists modeled generically by Odoo `/json/2` + OpenProject API v3 |
| D34.02 | P6 REST API | MPXJ `WebServicesReader`; OpenProject `lib/api` (server pattern) | partial | Client: login cookie or bearer, `project?Fields=...`, `export/exportProjects`, `export/exportXERProject`; no schedule/level job endpoints |
| D34.03 | P6 Integration API (Java) | MPXJ `PrimaveraDatabaseReader` (direct JDBC on P6 schema) | partial | Read-only business-object access over P6 tables with `delete_date is null` soft-delete filter |
| D34.04 | Primavera Cloud REST API | MPXJ `opc/OpcReader` | partial | Token from `/primediscovery/apitoken/request`, workspaces/projects/baselines, async export job + poll + download; read only |
| D34.05 | Unifier Web Services | none | none | Only Unifier link fields in PMXML Project schema |
| D34.06 | Aconex API | IfcOpenShell `opencdeserver` (OpenCDE Documents 1.0, BCF 3.0, Foundation OAuth2) | partial | Multipart upload sessions, versions, download; no mail/transmittal API |
| D34.07 | Textura APIs and ERP connectors | ERPNext Plaid sync (pattern); LibrePlan connectors | none | No pay-application API; only generic connector/sync patterns |
| D34.08 | P6 <-> Unifier integration | MPXJ PMXML `ProjectType` Unifier fields | none | Only field names (UnifierProjectName/Number, UnifierScheduleSheetName, UnifierDataMappingName) |
| D34.09 | P6 <-> Cloud/Aconex/Textura/ERP links | MPXJ OPC/P6 REST readers; OpenProject storages | partial | Schedule pull via export jobs; document references via `Storages::FileLink` |
| D34.10 | Gateway / integration flows | LibrePlan `Connector` + `JobSchedulerConfiguration` + `OrderSyncInfo`; ERPNext `bulk_transaction`, Plaid sync; Odoo `ir.cron` | partial | Connector property bags, cron-driven jobs, last-sync watermark, failure logs and retry |
| D34.11 | Webhooks and event notifications | OpenProject `modules/webhooks`; Odoo `ir.actions.server` (webhook) + `base_automation` | full | Outbound with HMAC signature, per-project filter, delivery log, retry; inbound hook registry; Odoo inbound `/web/hook/<uuid>` |
| D34.12 | Identity integration | OpenProject warden strategies, `AuthProvider`, SAML/OIDC modules, `ScimClient`, `LdapAuthSource`, `ldap_groups` | full | API token, OAuth2 (Doorkeeper), OIDC JWT, basic api-key, SCIM 2.0 schema, LDAP bind + group sync |
| D34.13 | Weather, map, e-signature | none | none | Only lat/long on P6 LOCATION; no provider adapters |

## Storage model

### OpenProject webhooks (`openproject/modules/webhooks/db/migrate/tables/*.rb`)

| Table | Columns | Keys |
|---|---|---|
| webhooks_webhooks | name string (unique on LOWER(name), `20260105092419_add_uniqueness_for_webhook_names.rb`), url text, description text not null, secret string null, enabled bool, all_projects bool, timestamps | PK id |
| webhooks_events | name string (e.g. `work_package:updated`) | FK webhooks_webhook_id; N per webhook |
| webhooks_projects | project_id, webhooks_webhook_id | join webhook <-> project (N:M) |
| webhooks_logs | webhooks_webhook_id (FK, on_delete cascade), event_name, url, request_headers text (serialized Hash), request_body text, response_code int (-1 on exception), response_headers text, response_body text, timestamps | N per webhook |

Event catalogue (`lib/open_project/webhooks/event_resources/*.rb`): `project:created|updated`, `work_package:created|updated`, `work_package_comment:comment|internal_comment`, `time_entry:created`, `attachment:created`.

### OpenProject identity

| Model | Fields / relations | File |
|---|---|---|
| AuthProvider (STI base for SAML/OIDC providers) | display_name unique, slug, available, options (json: additional_form_action_urls), creator; auth_url = `/auth/<slug>/`, callback_url = `/auth/<slug>/callback` | `app/models/auth_provider.rb` |
| UserAuthProviderLink | user_id (principal), auth_provider_id, external_id; identity url `slug:external_id` | `app/models/user_auth_provider_link.rb` |
| ScimClient | auth_provider_id, authentication_method enum {sso:0, oauth2_client:1, oauth2_token:2}, has_one Doorkeeper::Application (as integration), service_account via service_account_association | `app/models/scim_client.rb` |
| SCIM User schema | userName (unique server, required), name (complex), active, emails (multi, required), groups (multi, readOnly), externalId (unique, caseExact, required), id (readOnly) | `lib/open_project_scimitar/user.rb` |
| LdapAuthSource | name unique (<=60), host, port, tls_mode enum {plain_ldap:0, simple_tls:1, start_tls:2}, account, account_password (ciphered), base_dn, filter_string, attr_login/firstname/lastname/mail/admin, onthefly_register, tls_certificate_string | `app/models/ldap_auth_source.rb` |
| LdapGroups::SynchronizedGroup / Membership / SynchronizedFilter | LDAP group <-> OpenProject group with memberships (insert_all unique on user_id, group_id) | `modules/ldap_groups/app/models/ldap_groups/*.rb` |
| OpenIDConnect::Provider, UserToken, GroupLink, UserSessionLink | OIDC provider config, stored user tokens, group mapping | `modules/openid_connect/app/models/openid_connect/*.rb` |
| Saml::Provider | SAML IdP config | `modules/auth_saml/app/models/saml/provider.rb` |

### OpenProject external file storages (`modules/storages/app/models/storages/`)

| Model | Fields |
|---|---|
| Storage (STI: NextcloudStorage, OneDriveStorage, SharepointStorage) | name, host, provider config, automatic management flag |
| ProjectStorage | project_id, storage_id (unique per project), project_folder_mode enum {inactive, manual, automatic}, project_folder_id, creator |
| FileLink | storage_id, container (polymorphic, only `WorkPackage`), origin_id (required), origin_name, origin_mime_type, origin_created_by_name, origin_last_modified_by_name, transient origin_status {view_allowed, view_not_allowed, not_found, error} |

### OpenProject BIM/BCF (`modules/bim/app/models/bim/`)
`bcf_issues` (uuid unique, work_package_id required, markup XML, stage, labels, index, virtual reference_links, bim_snippet), viewpoints (issue_id, ordered by created_at), comments; `IfcModel` (project, uploader, title, is_default, conversion_status, attachments `ifc` and `xkt`).

### LibrePlan integration (`libreplan/libreplan-business/src/main/resources/org/libreplan/business/`)

| Table | Columns |
|---|---|
| connector | id, version (optimistic lock), name not null; child list `connector_property` (connector_id, connector_property_position, property_key, property_value) — `common/entities/Connector.hbm.xml` |
| job_scheduler_configuration | id, version, job_group, job_name, cron_expression, job_class_name (enum JobClassNameEnum), connector_name, schedule — `common/entities/JobSchedulerConfiguration.hbm.xml` |
| order_sync_info | id, version, last_sync_date not null, key not null (external id), connector_name not null, order_element_id FK — `orders/entities/Orders.hbm.xml:316-334` |

Predefined connectors (`java/.../common/entities/PredefinedConnectors.java:34-59`): Tim (Activated, Server URL, Username, Password, days timesheet 7, days roster 90, productivity factor 100, departments), Jira (labels, hours type), E-mail (protocol, host, port, sender, username, password). Jobs (`JobClassNameEnum.java:31-40`): ImportRosterFromTimJob, ExportTimesheetToTimJob, JiraOrderElementSynchronizerJob, SendEmailOn{TaskAssignedToResource, ResourceRemovedFromTask, MilestoneReached, TaskShouldStart, TaskShouldFinish, TimesheetDataMissing}Job.

### Odoo automation and outbound webhooks
- `ir.actions.server`: state selection incl. `webhook`; webhook_url, webhook_field_ids (M2M ir.model.fields), computed webhook_sample_payload (`odoo/odoo/addons/base/models/ir_actions.py:585-693`).
- `base.automation`: trigger selection on_stage_set, on_user_set, on_tag_set, on_state_set, on_priority_set, on_archive, on_unarchive, on_create, on_create_or_write, on_write, on_unlink, on_change, on_time, on_time_created, on_time_updated, on_webhook; webhook_uuid (uuid4), url `/web/hook/<uuid>`, record_getter (safe_eval expression), log_webhook_calls, trg_date_id / trg_date_range / trg_date_range_type / trg_date_calendar_id, filter_pre_domain, filter_domain, trigger_field_ids, action_server_ids (`odoo/addons/base_automation/models/base_automation.py:149-278`).
- `ir.cron`: interval_number, interval_type, nextcall, lastcall, priority, failure_count, first_failure_date, active; `ir_cron_trigger(cron_id, call_at)` (`odoo/odoo/addons/base/models/ir_cron.py:114-123`).

### ERPNext integration records
- Bank Account `last_integration_date`, `integration_id`; Bank `plaid_access_token`; Bank Transaction `transaction_id` used as idempotency key (`erpnext/erpnext/erpnext_integrations/doctype/plaid_settings/plaid_settings.py:218-330`).
- Bulk Transaction Log Detail: transaction_name (Dynamic Link from_doctype), transaction_status, error_description, from_doctype, to_doctype, date, time, retried int (`erpnext/erpnext/bulk_transaction/doctype/bulk_transaction_log_detail/bulk_transaction_log_detail.json`).

## Algorithms and logic

**OpenProject API v3 request pipeline** (`openproject/lib/api/root_api.rb`, `lib/api/utilities/endpoints/bodied.rb`)
1. Content type `application/json; charset=utf-8`; mutating requests without an allowed Content-Type get 406/415 (`root_api.rb:99-123`).
2. `authenticate`: `warden.authenticate!(scope: authentication_scope)`; if login required and anonymous -> 401 with `WWW-Authenticate` (`root_api.rb:71-77, 279-311`).
3. Endpoint: `parse` (ParseParamsService + payload representer, camelCase -> snake_case via `PropertyNameConverter`) -> `instance_generator` -> `process_service.new(user:, model:, contract_class:).with_state(...).call(params)` (`bodied.rb:85-130`); contract = `<Namespace>::{Create,Update}Contract`; service = `{Create,Update}Service` (`modify.rb:88-95`).
4. Errors: contract errors -> `ErrorBase.create_and_merge_errors`; dependent-result errors are merged into base with "error in dependent" messages (`modify.rb:43-86`); `ActiveRecord::StaleObjectError` -> 409 `UpdateConflict` (`root_api.rb:304`, `lib/api/errors/conflict.rb`). Optimistic locking: payload must echo `lockVersion` (`lib/api/v3/work_packages/work_package_representer.rb:326`, `parse_params_service.rb:44`).
5. Collections: `offset` (1-based page) and `pageSize`; links `jumpTo`, `changeSize`, `previousByOffset`, `nextByOffset` (absent at bounds); `pageSize=0` returns only totals (`lib/api/decorators/offset_paginated_collection.rb`).
6. Filters: `filters=[{"<attr>":{"operator":"<op>","values":[...]}}]`, `sortBy=[["attr","asc"]]`, `groupBy=attr`, converted to AR names and applied to `<Model>Query` (`app/services/params_to_query_service.rb`).
7. Forms: `.../form` endpoints run the contract without saving and return schema + validation errors (`lib/api/decorators/form.rb`, `create_form.rb`, `update_form.rb`).
8. Mounted resources (`lib/api/v3/root.rb:45-95`): actions, activities, attachments, backups, capabilities, categories, configuration, custom actions/fields/options, days, grids, notifications, help texts, memberships, news, OAuth applications/client credentials, portfolios, principals, priorities, programs, projects, project phases, queries, relations, reminders, revisions, roles, shares, statuses, types, users, placeholder users, groups, versions, views, wiki pages, workspaces, work packages.

**Authentication strategies** (`openproject/lib_static/open_project/authentication/strategies/warden/`)
- `user_api_token.rb`: valid when API tokens enabled and bearer token starts with `Token::API.prefix`; lookup `find_by_plaintext_value`; user must be active.
- `doorkeeper_oauth.rb`: valid when bearer is not a decodable JWT; reject blank/expired/revoked/disabled-application tokens; require scope; user = resource_owner_id or application.client_credentials_user_id; active User or active ServiceAccount.
- `jwt_oidc.rb`: valid when bearer is a JWT; `OpenIDConnect::JwtParser(required_claims: ["sub"])` returns (payload, provider); scope must be listed in `payload["scope"]`; user = provider.user_auth_provider_links.find_by(external_id: sub).principal.
- `user_basic_auth.rb`: basic auth with username literal `apikey`, password = API key (needs `apiv3_enable_basic_auth`).
- `global_basic_auth.rb`: configured global user/password -> `User.system`; user must not be `apikey`, password non-empty.

**LDAP** (`app/models/ldap_auth_source.rb:126-150`): class-level `authenticate` iterates sources with `onthefly_register`; per source: fetch attributes by login (search with filter_string under base_dn), bind as returned DN with password, then `synchronize_user(login, attrs)` creates/updates the user. LDAP group sync: `modules/ldap_groups/app/services/ldap_groups/synchronize_groups_service.rb`, `synchronize_filter_service.rb`; membership add via `insert_all ... unique_by: [user_id, group_id]` (`synchronized_group.rb:58-90`).

**Outbound webhook delivery (OpenProject)**
1. Event bus `OpenProject::Notifications.subscribe(key)` per resource (`event_resources/base.rb`). Work package: on `AGGREGATED_WORK_PACKAGE_JOURNAL_READY`, action = `created` if journal.initial? else `updated`; actor = journal user (`event_resources/work_package.rb`).
2. Select `Webhook.enabled.joins(:events).where(events.name = event)`; enqueue one job per webhook id (`webhook.rb with_event_name`).
3. Job (`app/workers/represented_webhook_job.rb`): skip unless `enabled_for_project?(project_id)` (all_projects or listed; `project:created` always accepted, `project_webhook_job.rb`; attachment uses container's project, comments use journable's project). Body = JSON `{action: event, <payload_key>: API v3 representer(resource, embed_links: true), actor: UserRepresenter}` rendered as `User.system`. Headers `Content-Type`/`Accept: application/json`; if secret present `X-OP-Signature: sha1=HMAC_SHA1(secret, body)`.
4. POST via `OpenProject::SsrfProtection.post` (private IPs rejected unless allowlisted); every attempt logged to `webhooks_logs` (response_code -1 on exception); `Net::OpenTimeout/ReadTimeout` re-raised so `WebhookJob` retries (`retry_on Timeout::Error, Faraday::TimeoutError, wait: :polynomially_longer, attempts: 3`, `app/workers/webhook_job.rb`) (`app/services/webhooks/outgoing/request_webhook_service.rb`).
5. `CleanupWebhookLogsJob` deletes logs older than 7 days.
6. Inbound: `OpenProject::Webhooks.register_hook(name) { |hook, request, params, user| ... }`, served at `webhooks/<name>`; duplicate names raise (`lib/open_project/webhooks.rb`, `hook.rb`).

**Outbound/inbound webhooks (Odoo)**
- `_run_action_webhook` (`ir_actions.py:1058-1100`): payload `{_model, _id, _action: "name(#id)"} + record.read(webhook_field_ids)` serialized with `json.dumps(default=str)`; sent in `cr.postcommit` hook (never on rollback), timeout 1 s, fire-and-forget; failures only logged.
- Automation (`base_automation.py`): `_register_hook` patches `create`/`write`/`unlink` of target models; write path computes `filter_pre` before write, captures old values, then `filter_post` and `_process` (:844-900). `_process` skips records already processed in this context (`__action_done`) to stop recursion, keeps only records where a trigger field changed, runs each server action per record, logs duration (:759-823). Inbound `_execute_webhook(payload)`: record = safe_eval(record_getter, payload) else empty; missing record -> ValidationError; optional ir.logging trail (:594-637). Time triggers run from cron `_cron_process_time_based_actions` (:1161).

**Odoo external API** (`odoo/odoo/service/model.py:71-115`, `odoo/addons/rpc/controllers/json2.py`)
- XML-RPC/JSON-RPC `execute_kw(db, uid, password|api_key, model, method, args, kw)`: check uid/password, then `retrying(call_kw)` (retries serialization failures).
- JSON-2: `POST /json/2/<model>/<method>` with bearer auth scope `rpc`, body `{ids, context, ...kwargs}`; method must be public; `@api.model` methods reject ids (422); signature bound against kwargs (422 on mismatch); recordset results returned as ids; readonly cursor when method is marked `_readonly`.

**P6 REST client** (`mpxj/.../primavera/webservices/WebServicesReader.java`)
1. Auth: POST `{url}/restapi/login?DatabaseName=<db>` with header `authToken: base64(user:pass)`; keep `Set-Cookie` values; or use `Authorization: Bearer <token>`.
2. List: GET `/restapi/project?Fields=ObjectId,Id,Name,DataDate,CurrentBaselineProjectObjectId`.
3. Export: POST `/restapi/export/exportProjects` `{ProjectObjectId:[project, currentBaseline?], FileType: XML|ZIP}` or `/restapi/export/exportXERProject` `{FileType: XER|ZIP}`; response streamed (gzip-aware) into `UniversalProjectReader`.

**Primavera Cloud client** (`mpxj/.../opc/OpcReader.java`)
1. Token: `https://<host>/primediscovery/apitoken/request?scope=http://<host>/api` with Basic auth -> `TokenResponse` (access token + extra request headers), refreshed when invalid (:445-480).
2. Resources under `https://<host>/api/restapi/`: `workspace`, `project/workspace/{id}`, `action/baseline/project/{id}` (204 = empty).
3. Export: POST `action/exportP6xml` or `action/exportP6xer` (expects 201 + jobId) -> poll `action/jobStatus/{jobId}` with linear backoff `sleep(retryCount * pollInterval)` up to `pollCount`, done when `jobStatus == "COMPLETED"`, else `OpcExportJobTimeoutException` -> GET `action/download/job/{jobId}` (:305-395).

**OpenCDE Documents API (IfcOpenShell `opencdeserver/api/app/api/documents.py`)**: `upload-instructions` returns per-file part upload URLs for a session; `upload-part/{part_id}` stores bytes after checking the user owns the part, marks part uploaded; `upload-completion` verifies all parts flagged and present on disk, concatenates in order into the document, returns a DocumentVersion; `upload-cancellation`; `document-versions`, `document/{id}/version/{n}` (+ `/metadata`, `/download`, `/versions`); Foundation OAuth2 (`/foundation/oauth2/auth|code|token`, `/foundation/1.0/current-user`); BCF 3.0 projects/topics/comments/viewpoints/files/documents/events (`api/bcf.py:43-700`). BCF client with OAuth2 authorization code + refresh token (`bcf/bcf/v3/bcfapi.py:46-160`).

**External storage file links (OpenProject)** (`modules/storages/app/services/storages/file_link_sync_service.rb`): group links by storage, call adapter `files_info` with user-bound auth; per file: HTTP 200 -> update origin_* metadata, status view_allowed; 403 -> view_not_allowed; 404 -> not_found; other -> error; adapter failure marks all links error. Adapters resolved by key `"<storage>.queries.<name>"` / `"<storage>.authentication.user_bound"` (`project_storage.rb`).

**Scheduled sync patterns**
- LibrePlan: `JobSchedulerConfiguration(cron_expression, job_class_name, connector_name)` binds a job to a connector; `Connector.isActivated()` and `areConnectionValuesValid()` gate execution (`Connector.java:118-127`); `OrderSyncInfo(key, connector_name, last_sync_date)` records which external issue/order maps to an order element and when it last synced.
- ERPNext Plaid (`plaid_settings.py:218-262`): start = `last_integration_date` or today-12 months; fetch; per transaction savepoint, skip and log failures; idempotent on `transaction_id`, skip pending; watermark = date of the last inserted transaction. Scheduled `hourly_maintenance` (`erpnext/erpnext/hooks.py:518`).
- ERPNext bulk transaction (`erpnext/erpnext/utilities/bulk_transaction.py`): enqueue conversion job; per document create Success/Failed log; `retry(date)` re-enqueues Failed with retried = 0; scheduled hourly (`hooks.py:515`).
- Odoo `ir.cron` (`ir_cron.py:189-690`): jobs acquired with `FOR NO KEY UPDATE SKIP LOCKED` ordered by failure_count, priority, id; next call advanced by interval in the user's timezone until > now; failure_count++ per failure, deactivate when failure_count >= 5 AND first failure > 7 days ago, admin notified; reset on success; `ir_cron_trigger` rows schedule ad-hoc runs.

## State machines and workflows

- Webhook delivery: enqueued -> (filtered out by project) | POST -> logged (2xx/4xx/5xx) | timeout -> retry (max 3 attempts) -> logged; log expires after 7 days.
- OPC export job: requested (201) -> polled (jobStatus != COMPLETED) -> COMPLETED -> downloaded | timeout exception.
- OpenCDE upload session: instructions issued -> parts uploaded (each flagged) -> completion (all flagged + present) -> DocumentVersion | cancellation.
- IFC model conversion: pending -> processing -> completed | error (`ifc_model.rb`).
- ScimClient authentication_method: sso | oauth2_client | oauth2_token; only oauth2_token exposes access tokens (`scim_client.rb`).
- ProjectStorage.project_folder_mode: inactive | manual | automatic; automatic + storage automatic management enabled + active project selects folders for `managed_folder_sync_service.rb`.
- Odoo cron job: active -> failing (count, first_failure_date) -> warned -> deactivated; success resets.
- ERPNext bulk log: Failed (retried 0) -> retried -> Success | Failed (retried 1).

## Cross-domain links

- Webhook payloads are API v3 representers of D03 work packages, D15 projects, D32 time entries, D25 attachments; actor is a D02 user.
- Identity (D34.12) feeds D02 users/groups/roles; SCIM service accounts and OAuth applications are D02 principals.
- File links connect D25 documents to D03 work packages; BCF issues link D27/D29 to D03 and D35.07 IFC models.
- LibrePlan connectors sync D32 timesheets (Tim) and D03 order elements (Jira); email jobs are D12 notifications.
- Plaid sync feeds D23/D22 bank transactions; bulk transaction converts D19 orders into D21 invoices.
- P6/OPC readers deliver D35 XER/PMXML payloads.
- Cron and automation engines are shared with D24 workflow and D36 platform jobs.

## Gaps

- P6 SOAP services and a P6-compatible REST surface (CRUD per business object with `Fields=` projection, `Filter=` expressions, batch create/update, schedule/level async jobs): no OSS server. Rebuild: object registry from D03/D07/D09 entities, field-list projection and filter grammar (OpenProject filters JSON is a model), async job table (job id, type, status, result URL) like OPC `action/jobStatus`.
- Unifier BP record APIs, cost-sheet/CBS endpoints and the P6 <-> Unifier schedule-sheet mapping: none; needs a mapping table (P6 WBS/activity id <-> BP record/cost code) plus push/pull jobs with OrderSyncInfo-style watermarks.
- Aconex mail/transmittal APIs, Textura draw/payment APIs, ERP actuals connectors (Fusion/EBS): none; OpenCDE Documents and Plaid sync are the closest reusable patterns.
- Integration-flow designer (field mapping, transformation, per-run error log): none beyond connector property bags and per-record logs.
- Webhook gaps in OpenProject: no status-change-specific events (only created/updated), no delete events, SHA-1 HMAC only.
- Weather/map/e-signature provider adapters: none.
