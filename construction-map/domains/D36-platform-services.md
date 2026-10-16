# D36 Platform Services

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D36.01 | Job services / background jobs | frappe RQ `enqueue` + Scheduled Job Type/Log; Odoo `ir.cron` (SKIP LOCKED, failure deactivation); OpenProject good_jobs + job_statuses; MPXJ P6 `JobServiceType` | full | Queues with timeouts, dedup ids, retries, cron schedules, per-run logs, status per job; P6 job types only as schema |
| D36.02 | Multi-tenant and environment management | frappe multi-site (site = DB, per-site cache keys, per-site scheduler); Odoo per-database registry | partial | Database-per-tenant isolation; no dev/test/prod promotion or data-refresh tooling |
| D36.03 | Data retention and purge | frappe Deleted Document (restore) + Log Settings retention; Odoo autovacuum / user deletion queue | full | Recycle bin with restore, retention-day purge per log doctype |
| D36.04 | Localization | Odoo `res.lang`; frappe System Settings formats; OpenProject user language/time zone | full | Date/time/number format per language or system, currency precision, week start |
| D36.05 | Search service | frappe `__global_search` full-text table + queue; OpenProject `acts_as_searchable` + trigram GIN indexes | partial | Record index with permission filtering; no attachment content indexing in sources read |
| D36.06 | Rate limiting and API throttling | frappe `RateLimiter` (per-site time budget) + `@rate_limit`; OpenProject token bucket | full | Fixed-window budget, per-endpoint counters, persistent token bucket |
| D36.07 | Backup, restore and record versioning | OpenProject journals with `validity_period` + `at_timestamp`; frappe Version; OpenProject Backup export | partial | Per-record version history and as-of queries; no point-in-time database recovery |

## Storage model

### Background jobs
- **frappe Scheduled Job Type** (`frappe/frappe/core/doctype/scheduled_job_type/scheduled_job_type.py:34-55`): `method`, `frequency` ∈ {All, Hourly, Hourly Long, Hourly Maintenance, Daily, Daily Long, Daily Maintenance, Weekly, Weekly Long, Monthly, Monthly Long, Cron, Yearly, Annual}, `cron_format`, `last_execution`, `queue` (default/short/long), `stopped`, `create_log`, `server_script`, `scheduler_event`. **Scheduled Job Log** (`scheduled_job_type`, `status` Start/Complete/Failed, `details` traceback, `debug_log`). **RQ Job** virtual doctype over Redis (`core/doctype/rq_job/`).
- **Odoo ir.cron** (`odoo/odoo/addons/base/models/ir_cron.py:93-124`): `ir_actions_server_id` (code to run), `user_id` (run-as), `active`, `interval_number`, `interval_type` (minutes/hours/days/weeks/months), `nextcall`, `lastcall`, `priority` (0 high), `failure_count`, `first_failure_date`. **ir.cron.trigger** (`:930-937`): `cron_id`, `call_at` (ad-hoc wake-ups). **ir.cron.progress** (`:951`): `cron_id`, `done`, `remaining`, `timed_out_counter`, `deactivate`.
- **OpenProject good_jobs** (`openproject/db/migrate/tables/good_jobs.rb`): uuid `id`, `queue_name`, `priority`, `serialized_params` jsonb, `scheduled_at`, `performed_at`, `finished_at`, `error`, `active_job_id`, `concurrency_key`, `cron_key`, `cron_at`, `retried_good_job_id`, `batch_id`, `executions_count`, `job_class`, `error_event`, `labels[]`, `locked_by_id`, `locked_at`; partial indexes on unfinished jobs; plus `good_job_executions`, `good_job_processes`, `good_job_batches`, `good_job_settings`.
- **OpenProject job_statuses** (`openproject/modules/job_status/db/migrate/tables/job_statuses.rb`): polymorphic `reference` (unique), `message`, `status` CHECK ∈ {in_queue, error, in_process, success, failure, cancelled} (`app/models/job_status/status.rb:35-42`), `user_id`, `job_id` unique, `payload` jsonb — user-visible progress for long jobs (copy, export, backup).
- **LibrePlan JobSchedulerConfiguration** (`libreplan/libreplan-business/src/main/java/org/libreplan/business/common/entities/JobSchedulerConfiguration.java:42-52`): `jobGroup`, `jobName`, `cronExpression`, `jobClassName` (enum of import/export/notification jobs, `JobClassNameEnum.java:31-40`), `schedule` bool, `connectorName`.
- **P6 JobServiceType** (`mpxj/src/main/java/org/mpxj/primavera/schema/JobServiceType.java:155-167`): `JobType`, `JobTypeKey`, `JobStatus`, `JobRecurringType`, `LastRunDate`, `UserId`, `JobData`, `ProjectInfo`, `TargetWbsId`, import/export payload fields.

### Retention / recycle bin
- **frappe Deleted Document** (`frappe/frappe/core/doctype/deleted_document/deleted_document.json`): `deleted_doctype`, `deleted_name`, `data` (full JSON incl. children), `restored`, `new_name`, `owner` = deleting user, `creation`.
- **frappe Log Settings** (`core/doctype/log_settings/log_settings.py:31-110`): child `logs_to_clear(ref_doctype, days)`; only doctypes whose controller implements `LogType.clear_old_logs(days)` are accepted (`_supports_log_clearing`, `:24`).
- **Odoo res.users.deletion** (`res_users_deletion.py:27`): `user_id`, `state` todo/done/fail — asynchronous deletion queue.

### Localization
- **Odoo res.lang** (`res_lang.py:103-139`): `code` (locale), `iso_code`, `url_code`, `active`, `direction` ltr/rtl, `date_format`, `time_format`, `week_start`, `grouping` (digit grouping pattern), `decimal_point`, `thousands_sep`.
- **frappe System Settings** (`core/doctype/system_settings/system_settings.json`): `language`, `time_zone`, `date_format`, `time_format`, `number_format` (10 patterns), `float_precision`, `currency_precision`, `rounding_method` (Banker's / Commercial), `first_day_of_the_week`, `currency`, `use_number_format_from_currency`. User-level `language`, `time_zone` on User.
- **OpenProject**: `users.language`, `user_preferences.settings` jsonb (`time_zone`, `workdays`, daily reminders; GIN indexes, `tables/user_preferences.rb`); time zone resolution defaults to `Etc/UTC` (`app/models/user.rb: time_zone`).
- **P6 user display prefs** in `UserType` (date format, separators, currency/duration decimals, `TeamMemberLocale`) (`primavera/schema/UserType.java`).

### Search
- **frappe `__global_search`** (created by `frappe.db.create_global_search_table`, `frappe/frappe/utils/global_search.py:21-26`): `(doctype, name, title, content, route, published)` with full-text index on `content` (MariaDB `MATCH ... AGAINST`), unique `(doctype, name)` upserted via `INSERT ... ON DUPLICATE KEY UPDATE` (`:225-240`, `:479-495`). Redis list `global_search_queue` buffers updates. Global Search Settings orders allowed doctypes.
- **OpenProject**: GIN `gin_trgm_ops` indexes on `journals.notes` and `custom_values.value` (`tables/journals.rb`, `tables/custom_values.rb`); `acts_as_searchable` declarations per model (e.g. `project.rb:136` over name, identifier, description).

### Rate limiting
- **OpenProject token_bucket_states** (`openproject/db/migrate/20260820101109_add_token_bucket_states.rb`): `identifier` unique, `microtokens` bigint, `refilled_at`, timestamps.
- frappe keeps counters in Redis only (keys `rate-limit-counter-<window>`, `rl:<method>:<identity>[:<seconds>]`).

### Versioning / backup
- **OpenProject journals** with `validity_period tstzrange` and non-overlap exclusion constraint per journable (`tables/journals.rb`), snapshot tables per type (D02).
- **OpenProject Backup** (`app/models/backup.rb`): STI on `exports`, attachment = the archive; settings `backup_include_attachments`, `backup_attachment_size_max_sum_mb` (default 1024); permission `:create_backup`.
- **frappe Version** (`ref_doctype`, `docname`, `data` diff JSON) (D02); System Settings `backup_limit`, `encrypt_backup`.

## Algorithms and logic

### frappe enqueue and execution
- `enqueue(method, queue, timeout, job_id, deduplicate, enqueue_after_commit, at_front, at_front_when_starved, ...)` (`frappe/frappe/utils/background_jobs.py:129-268`): with `deduplicate`, a job id is required and enqueue is skipped if a job with that id is QUEUED or STARTED (`:174-180`); queue length cap `MAX_QUEUED_JOBS = 500` (`:44`); if `at_front_when_starved` and queue count > 16 then push to front (`:245`); `enqueue_after_commit` defers the push into a post-commit callback list (`:262-268`). Queue timeouts: short/default 300 s, long 1500 s, overridable per custom worker (`get_queues_timeout`, `:99-127`).
- `execute_job(site, method, ..., user, retry)` (`:297-400`): init site, `set_user(user)`, run; on `QueryDeadlockError`/`QueryTimeoutError`/`RetryBackgroundJobError` rollback and re-run with `retry+1` after `sleep(retry+1)` up to 5 retries, then `log_error`; any other exception → rollback, Error Log, commit; success → commit.

### frappe scheduler
- Tick loop `start_scheduler` → `enqueue_events_for_all_sites` → per site, skip if scheduler inactive/disabled or site dormant (`schedule_jobs_based_on_activity`, `is_dormant` uses `dormant_days`) (`frappe/frappe/utils/scheduler.py:40-180`, `:223-262`).
- `enqueue_events` (`scheduler.py:155-178`): load non-stopped Scheduled Job Types (excluding disabled apps), shuffle, call `job.enqueue()`.
- `ScheduledJobType.enqueue` (`scheduled_job_type.py:81-101`): if due and not already queued under job id `scheduled_job||<name>`, enqueue `run_scheduled_job` on `long` queue for *Long*/*Maintenance* frequencies else `default` (`get_queue_name`, `:203-206`).
- `get_next_execution` (`:120-154`): `cron_format` from CRON_MAP (`Daily "0 0 * * *"`, `Hourly "0 * * * *"`, `Weekly "0 0 * * 0"`, `Monthly "0 0 1 * *"`, `Yearly/Annual "0 0 1 1 *"`, `All "*/(scheduler_interval/60 or 4) * * * *"`), next = `croniter(cron).get_next(after = last_execution or creation)`; due when next ≤ now. A per-site `sha1(site) % 60` minute offset is computed for Maintenance frequencies but the method returns a fresh `get_next` without it (as read, `:152-154`), so the offset is not applied.
- `execute` (`:156-177`): log Start (sets `last_execution`), run method or Server Script, commit, log Complete; on exception rollback, log Failed with traceback. Without `create_log`, only `last_execution` is updated.

### Odoo cron runner
- Worker loop `_process_jobs(db)` → `_process_jobs_loop` (`ir_cron.py:189-275`): list ready jobs (`nextcall <= now` or pending `ir.cron.trigger`) ordered `failure_count, priority, id` (`:306`); `_acquire_one_job` locks with `SELECT ... FOR NO KEY UPDATE SKIP LOCKED` so concurrent workers never run the same job (`:311-370`).
- `_process_job` (`:402-459`): environment as the cron's `user_id`; if `timed_out_counter >= 3` (`CONSECUTIVE_TIMEOUT_FOR_FAILURE`) and the progress is not done, status = FAILED and the counter resets; else `_run_job` returns FULLY_DONE / PARTIALLY_DONE / FAILED (batch jobs report `ir.cron.progress(done, remaining)` via `_notify_progress`, `:850`). Then `_update_failure_count`; FULLY_DONE or FAILED → `_reschedule_later`; PARTIALLY_DONE → `_reschedule_asap` (inserts an `ir_cron_trigger` at now).
- `_reschedule_later` (`:656-679`): add `interval_number × interval_type` to `nextcall` repeatedly (in the user's time zone, so daily jobs keep their wall-clock hour across DST) until it is in the future; set `lastcall = now`.
- `_update_failure_count` (`:574-640`): on failure `failure_count += 1`, `first_failure_date ||= now`; deactivate (`active=False`, counters reset) when `failure_count >= 5` **and** `first_failure_date + 7 days < now` (`MIN_FAILURE_COUNT_BEFORE_DEACTIVATION`, `MIN_DELTA_BEFORE_DEACTIVATION`, `:37-40`); warnings logged on the way; success resets both.
- `_trigger(at, coalesce)` (`:750-790`) inserts `ir.cron.trigger` rows and notifies the runner (`pg_notify`).

### OpenProject job processing
- good_job (Postgres-backed ActiveJob): unfinished jobs indexed by `scheduled_at` and `(queue_name, scheduled_at)`; workers lock rows (`locked_by_id`, `locked_at`); cron jobs identified by `cron_key`/`cron_at`; retries link via `retried_good_job_id` (from column semantics; scheduler code is the gem, not cloned).
- Long-running user jobs upsert a `job_statuses` row keyed by `job_id` and `reference`, moving `in_queue → in_process → success|failure|error|cancelled`, with `payload` (e.g. redirect or download link) (inferred from model + check constraint).

### Recycle bin and purge (frappe)
- `delete_doc` (`frappe/frappe/model/delete_doc.py:25-250`): permission `delete` (only Administrator deletes standard DocTypes), submitted docs must be cancelled first (`check_permission_and_not_submitted`, `:307-325`); `on_trash` hook; unless `force`, refuse when linked from live records (`check_if_doc_is_linked`, dynamic links) and suggest disabling if the doctype has `enabled/disabled`; delete row and children, attachments, passwords, global-search and tag entries; enqueue dynamic-link cleanup after commit; unless `delete_permanently`, insert **Deleted Document** with full JSON (`add_to_deleted_document`, `:253-262`).
- `restore(name)` (`core/doctype/deleted_document/deleted_document.py:43-95`): System Manager only; refuse if `restored`; user needs create on doctype and read on doc; `insert()` the JSON; if docstatus transition error (cancelled doc), restore as Draft and clear workflow state; then reset `owner`, `creation`, `modified`, `modified_by` to the originals without touching `modified`; comment "restored X as Y"; set `restored=1`, `new_name`.
- Retention: `DeletedDocument.clear_old_logs(days=180)` deletes rows older than N days (`:34-40`); `LogSettings.clear_logs` iterates `logs_to_clear` and calls each controller's `clear_old_logs(days)` (`log_settings.py:86-101`), scheduled via `run_log_clean_up` (`:115`); generic `clear_log_table(doctype, days)` deletes by `creation < now - days` (`:153-180`).
- Odoo `ir.autovacuum._run_vacuum_cleaner` (`ir_autovacuum.py:27-60`): daily, calls every model method decorated `@api.autovacuum`; `res.users.deletion._gc_portal_users` processes the deletion queue in batches of 50, marking done/fail (`res_users_deletion.py:37-90`).

### Global search (frappe)
- Indexing: on save `update_global_search(doc)` collects fields flagged `in_global_search` (and child table fields) into `content` joined with `" ||| "` and pushes JSON onto `global_search_queue` (`global_search.py:245-290`, `:446-450`); `sync_global_search` pops the queue, de-duplicates by (doctype, name) and bulk-upserts (`:374-445`); `rebuild_for_doctype` rebuilds one doctype (`:68-155`); delete removes the row (`:502-508`).
- Query `search(text, start, limit, doctype)` (`:512-580`): allowed doctypes = Global Search Settings ∩ user-readable doctypes; for each `&`-separated term run `MATCH(content) AGAINST(term)` as rank, filter by doctype set, order rank desc, limit/offset; then order results by doctype priority and keep only rows where `has_permission(doctype, doc)` passes, enriching title/image.

### Rate limiting
- frappe global limiter (`frappe/frappe/rate_limiter.py:32-100`): config `rate_limit = {limit, window}`; budget `limit × 10^6` **microseconds of request processing time** per fixed window; key `rate-limit-counter-<floor(now/window)>` with TTL = window; reject with 429 when counter > budget before handling; after the request add the request duration; headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`. Keys are site-namespaced by `cache.make_key` (per-tenant quota).
- frappe `@rate_limit(key, limit, seconds, methods, ip_based, user_based)` (`:104-195`): identity = user, IP, form key or combination; Redis key `rl:<counter>:<identity>[:seconds]`, `SETEX seconds 0` on first hit, `INCRBY 1`, raise `RateLimitExceededError` above limit (fixed window per endpoint).
- OpenProject `TokenBucketBasedRateLimiter::Base.consume!(tokens)` (`openproject/lib/open_project/token_bucket_based_rate_limiter/base.rb:52-111`): row lock on `token_bucket_states` by identifier; `available = min(microtokens + floor((now - refilled_at) × capacity / 86400), capacity)` with `capacity = limit × 10^6`; if `available ≥ tokens × 10^6` store `available - required`, `refilled_at = now`, return true; else false. `limit = 0` disables. Used for the daily email limit (`20260820101159_create_email_limit_per_day_token_bucket_state.rb`).
- Login throttles (frappe tracker, OpenProject brute force, Odoo cooldown) are in D02.

### Record versioning and as-of reads
- OpenProject `Journal.at_timestamp(t)` (`openproject/app/models/journal/timestamps.rb:66`): selects, per journable, the journal whose `validity_period` contains `t` (latest journal at or before `t`); powers baseline comparison of work packages at past timestamps. Validity intervals are contiguous `[created_at_i, created_at_{i+1})`, the latest open-ended, enforced by the exclusion constraint.
- frappe Version rows give forward diffs only; reconstructing a past state requires replaying diffs backwards from the current document (inferred).

### Multi-tenancy
- frappe: every request/job is bound to `frappe.local.site` (one database and config per site); jobs carry `site` (`execute_job(site, ...)`), the scheduler iterates sites, Redis keys go through `make_key` with site prefix, `scheduler_interval` and `rate_limit` are per-site config (inferred from `frappe.conf` usage). Maintenance offset hash on site name intended to spread multi-tenant load (`scheduled_job_type.py:120-125`).
- Odoo: registry and cron runner per database (`_process_jobs(db_name)`, login failure map on `env.registry`).

## State machines and workflows

- **frappe Scheduled Job Log**: `Start → Complete | Failed`. Scheduled Job Type: `stopped 0 ⇄ 1` (manual), `last_execution` advances on Start.
- **frappe RQ job**: `queued → started → finished | failed` (`JobStatus` in `background_jobs.py`; dedup checks QUEUED/STARTED), retries create a new execution of the same method.
- **Odoo ir.cron**: `active` → run (`nextcall` reached or trigger) → FULLY_DONE (reset failures, advance `nextcall`) | PARTIALLY_DONE (trigger at now) | FAILED (increment failures, advance `nextcall`) → after ≥5 failures spanning ≥7 days → `active=False`.
- **OpenProject job_status**: `in_queue → in_process → success | failure | error | cancelled`.
- **frappe Deleted Document**: `restored 0 → 1` (one-shot; second restore raises `DocumentAlreadyRestored`); purged after retention days.
- **Odoo res.users.deletion**: `todo → done | fail`.

## Cross-domain links

- Jobs run D06 scheduling, D08 leveling, D10 apply actuals/store period performance, D33 summaries, D34 sync connectors, D35 imports/exports (P6 `JobServiceType`, LibrePlan import/export jobs, OpenProject project copy D01.05).
- Recycle bin and Version reference any doctype/record (D03-D32); restore re-checks D02 permissions.
- Global search respects D02 read permissions; indexes D25 documents' metadata only.
- Localization formats drive D33 reporting output and D01.09 currency rounding.
- Rate limits and login throttling tie to D02.01 and D34 API.

## Gaps

- **Domain job catalogue** (schedule, level, summarize, apply actuals, store period performance, send-to-Unifier): define job types with parameters (project set, data date), run-as user, recurrence, per-run log and lock per project to prevent concurrent schedule/level; the frappe/Odoo runners provide the mechanics.
- **Environment management**: no dev/test/prod promotion, configuration package export/import, or production-to-test data refresh with anonymisation.
- **Point-in-time recovery**: needs DB-level WAL archiving/PITR; application sources only provide record histories and full exports.
- **Search over document content**: extract text from attachments (PDF/Office/OCR) into the index with ACL filtering; frappe indexes only declared fields.
- **Per-tenant API quotas**: frappe's limiter is a per-site time budget, OpenProject's bucket is a single global identifier; tenant/user/API-key quotas with plan-based limits need identifier = tenant+key and configurable refill.
- **Audit/history purge policy**: Version and journals have no retention purge in sources read; P6-style audit level and retention days per table need implementing alongside Log Settings.
