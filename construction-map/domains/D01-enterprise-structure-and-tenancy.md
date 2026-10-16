# D01 Enterprise Structure and Tenancy

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D01.01 | Enterprise Project Structure (EPS) | OpenProject `projects` nested set; MPXJ `EPS`/`EpsNode` + P6 `EPSType` schema | partial | Tree, re-parenting, subtree archive and visibility pruning exist; no EPS-level rollup of dates/costs/EV, no access inheritance down the tree |
| D01.02 | Organizational Breakdown Structure (OBS) | MPXJ P6 schema `OBSType`, `UserOBSType` | partial | Data model only (OBS tree, user+OBS+project profile triple, EPS/WBS `OBSObjectId`); no OSS evaluator of OBS-driven rights |
| D01.03 | Project entity | MPXJ `ProjectProperties` (P6 PROJECT/PREFER columns); OpenProject `projects` | partial | All P6 scheduling defaults are mapped by MPXJ; OpenProject gives status, active/archived, templated, settings JSONB; no check-out state machine |
| D01.04 | Programs / shells hierarchy | OpenProject `workspace_type` (project/program/portfolio) + parent rules | partial | Three fixed container types with allowed-parent matrix; no user-defined shell types, shell status set, or auto-create from BP |
| D01.05 | Project and shell templates | OpenProject `templated` flag + `Projects::CopyService` dependency pipeline | partial | Deep copy with id remapping of WPs, relations, versions, members, queries, wiki; no push-down propagation of template changes |
| D01.06 | Workspaces and portfolios | OpenProject portfolio workspaces; MPXJ `ProjectPortfolioType` (Manual / Auto-Maintained) | partial | Static hierarchical grouping only; no inherited/overridable configuration per workspace; dynamic filter portfolios only as schema |
| D01.07 | Multi-company and partner organizations | Odoo `res.company` (branches, `company_ids`, `check_company`, company-scoped `ir.access` domains); ERPNext Company tree | partial | Strong record ownership and consistency by company; no cross-organization project participation or "private until transmitted" model |
| D01.08 | Locations and geographic data | MPXJ `Location` (P6 LOCATION table) | partial | Address + lat/long attached to project/resource/activity; no location hierarchy, no geo rollup logic |
| D01.09 | Currencies and exchange rates | Odoo `res.currency` / `res.currency.rate`; ERPNext Currency Exchange; MPXJ `Currency` | full | Dated rates per company root, lookup algorithm, rounding/decimal places, stale-rate guard (ERPNext) |
| D01.10 | Admin preferences and categories | MPXJ PREFER hours-per-period + `Duration.convertUnits`; OpenProject `settings`; frappe System Settings | partial | Hours/day-week-month-year conversion implemented; lookup lists exist piecemeal (expense categories, notebook topics in MPXJ) |

## Storage model

### OpenProject project tree (Rails, PostgreSQL)

**projects** (`openproject/db/migrate/tables/projects.rb:32`)
- `id` bigint PK, `name` string not null, `description` text, `public` bool default true, `parent_id` bigint (self FK, nullable for roots), `identifier` string not null, unique on `LOWER(identifier)`, `lft`/`rgt` int (awesome_nested_set, indexed separately and as `(lft, rgt)`), `active` bool default true (false = archived), `templated` bool, `status_code` int, `status_explanation` text, `settings` jsonb not null default `{}`, timestamps.
- `workspace_type` enum string added later (`openproject/db/migrate/20250731144436_add_workspace_type_to_project.rb`; model enum at `openproject/app/models/project.rb:44`): `project | program | portfolio`.
- `status_code` enum (`project.rb:220`): `on_track 0, at_risk 1, off_track 2, not_started 3, finished 4, discontinued 5`.
- Associations (`project.rb:57-122`): `members` (non-locked principals), `enabled_modules` 1:N, `project_types` 1:N (`project_types(project_id, type_id, variant_id)` unique `(project_id, type_id)`, `db/migrate/20260804123419_create_project_types.rb:35`), `work_packages`, `versions`, `time_entries`, `budgets`, `phases`, `project_storages`, `belongs_to :template` (Project), `templated_projects`, `subproject_template_assignments`.
- `acts_as_customizable` (project attributes = custom fields), `acts_as_journalized` and `has_paper_trail` (audit, see D02).

**custom_fields / custom_values / project_custom_field_project_mappings** (project attributes, UDF-like)
- `custom_fields` (`tables/custom_fields.rb`): STI `type` (ProjectCustomField, WorkPackageCustomField, UserCustomField, ...), `field_format`, `regexp`, `min_length`, `max_length`, `is_required`, `is_for_all`, `is_filter`, `searchable`, `editable`, `admin_only`, `multi_value`, `default_value`, `custom_field_section_id`, `position_in_custom_field_section`.
- `custom_values(customized_type, customized_id, custom_field_id, value text)`; GIN trigram index on `value`.
- `project_custom_field_project_mappings(custom_field_id, project_id)` unique pair: activates a project attribute per project.

**settings** (`tables/settings.rb`): `name` string, `value` text, `updated_at`. Global key/value admin preferences (e.g. `journal_aggregation_time_minutes`, `brute_force_block_minutes`, `password_min_length` read in D02).

### MPXJ (P6 data model as read from XER/PMDB/PMXML)

**EPS** (`mpxj/src/main/java/org/mpxj/EPS.java:109`): maps `Integer → EpsNode` and `Integer → EpsProjectNode`.
- `EpsNode` (`EpsNode.java:112`): `uniqueID`, `parentUniqueID`, `name`, `shortName`; children computed.
- `EpsProjectNode` (`EpsProjectNode.java:88`): `uniqueID` (= `proj_id`), `parentEpsUniqueID`, `shortName`, `name`.
- Source rows: P6 stores EPS nodes in `PROJWBS` with `proj_node_flag='Y'`, joined to `PROJECT`; `project.project_flag` distinguishes a real project from an EPS node (`primavera/PrimaveraDatabaseReader.java:89`, `:388-428`).

**P6 PMXML schema classes** (`mpxj/src/main/java/org/mpxj/primavera/schema/`, JAXB, data only):
- `EPSType` (`EPSType.java:402`): `ObjectId`, `ParentObjectId`, `Id`, `Name`, `SequenceNumber`, `OBSObjectId` (responsible manager, `:419`), `ProjectObjectId`, budget fields (`OriginalBudget`, `CurrentBudget`, `ProposedBudget`, `UnallocatedBudget`, `TotalFunding`, `TotalSpendingPlan`, `TotalBenefitPlan`), `LastSummarizedDate`, plus ~120 `Summary*` rollup columns (actual/at-completion/baseline/remaining costs, units, EV indices, activity counts) written by the P6 summarizer.
- `OBSType` (`OBSType.java:86`): `ObjectId`, `ParentObjectId`, `Name`, `Description`, `SequenceNumber`, `GUID`.
- `UserOBSType` (`UserOBSType.java:92`): `UserObjectId`, `OBSObjectId`, `ProjectProfileObjectId` (+ names) — the user ↔ OBS ↔ project-security-profile assignment.
- `ProjectPortfolioType` (`ProjectPortfolioType.java:114`): `Name`, `Description`, `Type` enumeration `Manual | Auto-Maintained` (`:69-70`), `IncludeClosedProjects`, `IncludeWhatIfProjects`, `MemberProject` (N), `PortfolioUserIdArray`.
- `LocationType`, `CurrencyType`, `ExpenseCategoryType`, `NotebookTopicType`, `DocumentCategoryType`, `RiskCategoryType`, `WBSCategoryType` exist as lookup schemas.

**ProjectProperties** mapping of P6 `PROJECT` row (`primavera/TableProjectReader.java:94-131`): `proj_short_name`→ProjectID, `guid`, `create_date`, `sum_base_proj_id`→baseline project, `critical_path_type`, `def_duration_type`→default task type, `last_recalc_date`→**status (data) date**, `last_schedule_date`, `plan_start_date`→planned start, `scd_end_date`→scheduled finish, `plan_end_date`→**must finish by**, `critical_drtn_hr_cnt`→critical float limit, `location_id`, `name_sep_char` (WBS separator), `clndr_id`→default activity calendar, `task_code_prefix/base/step` (activity ID auto-numbering), `def_cost_per_qty`, `cost_qty_recalc_flag`, `step_complete_flag`, `fy_start_month_num`, `export_flag`, `proj_url`. Project UDFs via `populateUserDefinedFieldValues(... "PROJECT" ...)` (`:97`), project code assignments from `PROJPCAT` (`DatabaseProjectReader.java:148`).

**Location** (`Location.java:194-206`; read at `TableContextReader.java:140-160`): `location_id`, `location_name`, `address_line1..3`, `city_name`, `municipality_name`, `state_name`, `state_code`, `country_name`, `country_code`, `postal_code`, `latitude` double, `longitude` double. No parent field.

**Currency** (`Currency.java:144-153`; read at `TableContextReader.java:115-130`): `curr_id`, `curr_short_name` (ISO), `curr_type` (name), `curr_symbol`, `decimal_digit_cnt`, `decimal_symbol`, `digit_group_symbol`, `pos_curr_fmt_type`, `neg_curr_fmt_type`, `base_exch_rate` (single rate to base; P6 keeps no rate history).

**Admin preferences** (P6 `PREFER` table, `primavera/DatabaseProjectReader.java:154-167`): `day_hr_cnt`, `week_hr_cnt`, `month_hr_cnt`, `year_hr_cnt` (hours, stored by MPXJ as minutes ×60), `week_start_day_num`, `curr_id` (base currency), rows filtered `delete_date is null`.

### Odoo multi-company (`odoo/odoo/addons/base/models/`)

**res.company** (`res_company.py`): `_parent_store = True` (`:66`), `parent_id` Many2one res.company `ondelete=restrict` (`:87`), `child_ids` (branches) (`:88`), `parent_path` char indexed (`:90`), computed `parent_ids` and `root_id` = first id of `parent_path` (`:188-192`), `currency_id` required (`:109`), `active`.
- Invariant: fields returned by `_get_company_root_delegated_field_names()` (default `['currency_id']`, `:163-171`) must equal the parent's value (`_check_root_delegated_fields`, `:466`); writes on a root copy them to all branches (`:425-436`).
- Archiving a company archives its branches (`:420-422`); archiving is refused while active users have it as default company (`_check_active`, `:446-460`).

**res.users company fields** (`res_users.py:234-238`): `company_id` (current default) required, `company_ids` Many2many `res_company_users_rel(user_id, cid)` (allowed companies). Context key `allowed_company_ids` = companies activated in the session; feeds `company_ids` in access-rule eval (`ir_access.py:308-324`).

**res.currency / res.currency.rate** (`res_currency.py`)
- `res.currency` (`:51-82`): `name` char(3) ISO 4217 unique, `iso_numeric`, `symbol`, `rounding` float (default 0.01, > 0), `decimal_places` = `ceil(log10(1/rounding))` when 0<rounding<1 (`:239-244`), `position` before/after, `active`, `rate_ids` 1:N.
- `res.currency.rate` (`:396-440`): `name` Date (effective date), `rate` float (units of currency per 1 company currency), `company_rate`, `inverse_company_rate`, `currency_id`, `company_id` default `env.company.root_id`. Unique `(currency_id, company_id, name) NULLS NOT DISTINCT` — one rate per day per company; `CHECK (rate>0)`.

### ERPNext

- **Company** (`erpnext/erpnext/setup/doctype/company/company.json`): tree doctype (`is_tree=1`, `nsm_parent_field=parent_company`), `company_name`, `abbr`, `is_group`, `parent_company` Link Company, `lft`/`rgt`, `default_currency`, `country`, `default_holiday_list`, `cost_center`, `round_off_cost_center`.
- **Currency Exchange** (`setup/doctype/currency_exchange/currency_exchange.json`): `date`, `from_currency`, `to_currency`, `exchange_rate`, `for_buying`, `for_selling`; name autogenerated from date+pair+purpose (`currency_exchange.py:29-46`).

## Algorithms and logic

### Project tree (EPS analogue), OpenProject
- **Nested set maintenance**: `acts_as_nested_set order_column: :lft, dependent: :destroy` (`openproject/app/models/projects/hierarchy.rb:185`); deleting a node deletes its subtree. A `before_save :remember_reorder` / `after_save :reorder_by_name` pair (`:188-209`) re-sorts siblings by name after renames so that `ORDER BY lft` yields name-sorted DFS order.
- **Tree build** `build_projects_hierarchy(projects)` (`hierarchy.rb:51-79`): sort by `lft`; maintain an ancestor stack; pop while the current project is not a descendant of the stack top; append to top's children; finally sort each level by name.
- **Visible roots with invisible ancestors** `nearest_visible_descendants(boundary)` (`hierarchy.rb:105-145`): over the visible scope compute `max(rgt) OVER (ORDER BY lft ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)`; a row is a "visible root" if that value is NULL or `rgt > max_preceding_rgt`. This surfaces children whose ancestors are hidden/archived.
- **Has visible children** `having_visible_descendants` (`:150-166`): EXISTS a visible+active project with `lft` and `rgt` strictly inside the candidate's interval.
- **Re-parenting** guard `Projects::BaseContract#validate_parent_assignable` (`openproject/app/contracts/projects/base_contract.rb:93-99`): new parent must be in `assignable_parents(user, project)` = projects where user has `:add_subprojects`, excluding `self_and_descendants` (cycle prevention), and whose `workspace_type` is in `ALLOWED_PARENT_WORKSPACE_TYPES[child.workspace_type]` (`openproject/app/models/projects/scopes/assignable_parents.rb`, matrix at `project.rb:50-54`): project → {portfolio, program, project}; program → {portfolio}; portfolio → {} (roots only).
- **Archive cascade** `Projects::ArchiveService#persist` (`openproject/app/services/projects/archive_service.rb`): sets `active=false` on the project and every `active_subprojects` member via `update_attribute` (skips validation, updates timestamps), then emits `PROJECT_ARCHIVED`.
- **Visibility**: `Project#visible?(user)` = `active && (public || user.admin? || user.access_to?(self))` (`project.rb:230`). Access is per-project membership, not inherited from the parent (see D02).

### EPS rollup (P6, data only)
- P6 stores pre-computed `Summary*` columns on EPS (`EPSType.java`) refreshed by "Summarize" jobs (`LastSummarizedDate`). No OSS source performs the rollup. (inferred) Rebuild: post-order traversal over EPS nested set aggregating project summaries: sums for costs/units/counts, min of start dates, max of finish dates, ratio indices recomputed from summed EV/PV/AC (not averaged).

### Project templates and copy, OpenProject
- `projects.templated` is admin-only to change (`base_contract.rb: validate_templated_set_by_admin`).
- `Projects::CopyService.copy_dependencies` (`openproject/app/services/projects/copy_service.rb:34-48`) runs, in order: Members, Versions, Categories, WorkPackages, Wiki, Forums, Queries, Boards, Overview, Phases, Storages. Each dependent service may be skipped by params (`skip_dependency?`, `:71`). Shared copy `state` carries id lookup maps (`version_id_lookup`, `work_package_id_lookup`) between steps.
- Work package copy (`openproject/app/services/projects/copy/work_packages_dependent_service.rb:48-135`): iterate source WPs in hierarchy order; `parent_id = work_packages_map[wp.parent_id] || wp.parent_id`; copy each WP with `bulk_duplicate_in_progress` state; record `old_id → new_id`; then a second pass copies relations, mapping both ends through the map (falls back to the original id if the other end was not copied, `relations_from_to`, `:184-195`). Versions remapped via `version_id_lookup`; assignee/responsible kept only if still a possible principal in the target.
- Copy is asynchronous via `Projects::EnqueueCopyService` (job, see D36).

### Multi-company consistency, Odoo
- `_check_company(fnames)` (`odoo/odoo/orm/models.py:3351-3420`): for every relational field declared `check_company=True`, take the origin's companies (`company_id`, or `company_ids`, or itself for res.company) and require each linked record to satisfy `_check_company_domain(companies)` = `company_id in companies + [False]` (`:3339-3349`). Company-dependent (property) fields are checked against `env.company`. Violations raise a UserError listing inconsistencies. Auto-invoked on create/write when `_check_company_auto = True` (`models.py:493`, `:3989`, `:4232`).
- Company scoping of visibility uses `ir.access` restriction domains evaluated with `company_ids` = session-allowed companies (D02).
- Accessible branches (`res_company.py:484-501`): BFS from each allowed root keeping only children also in `env.companies`.

### Currency conversion, Odoo
- `_get_rates(company, date)` (`res_currency.py:171-213`): resolve `company.root_id`; per currency, LATERAL subquery picks the latest rate with `name < date` and `company_id in (False, root)`, ordered by `company_id` then `name DESC`; fallback LATERAL picks the earliest rate if none before; `COALESCE(before, after, 1.0)`. Cached per `(company, date)` in cursor cache.
- `_compute_current_rate` (`:222-237`): `rate = rate(currency) / rate(to_currency)`; `inverse_rate = 1/rate`.
- `_convert(amount, to_currency, company, date, round=True)` (`:356-375`): `amount × _get_conversion_rate(...)` where conversion rate = `inverse_rate` computed with `to_currency` in context (`:345-354`); then `to_currency.round()` = `float_round(precision_rounding=rounding)` (`:286-293`). Zero amount short-circuits to 0.
- Edge: rate lookup uses strict `name < date` with the context date (as read); rates are only ever stored on root companies so branches inherit them.

### Currency conversion, ERPNext
- `get_exchange_rate(from, to, transaction_date, args)` (`erpnext/erpnext/setup/utils.py:62-110`): same currency → 1; filter `date <= transaction_date`, pair match, optional `for_buying`/`for_selling`; unless Accounts Settings `allow_stale`, also require `date > transaction_date - stale_days`; take latest by `date desc, name desc`; if none and the external provider is enabled, fall back to pegged currencies and the configured API (Currency Exchange Settings); disabled provider returns 0.

### Hours-per-period conversion, MPXJ
- `Duration.convertUnits(duration, from, to, minutesPerDay, minutesPerWeek, daysPerMonth)` (`mpxj/src/main/java/org/mpxj/Duration.java:133-230`): normalise to minutes (`DAYS × minutesPerDay`, `WEEKS × minutesPerWeek`, `MONTHS × minutesPerDay × daysPerMonth`, `YEARS × minutesPerWeek × 52`; elapsed units use 24h/7d/30d/52w constants), then divide by the target unit factor. Defaults come from P6 PREFER hours per day/week/month/year (`DatabaseProjectReader.java:161-164`).

## State machines and workflows

- **Project lifecycle (OpenProject)**: `active=true` ⇄ `active=false` (archived). Archive cascades to active subprojects (`archive_service.rb`); `Projects::UnarchiveService` reverses; `Projects::ScheduleDeletionService` deletes asynchronously; destroy cascades to subtree (`dependent: :destroy`). Archived projects drop out of `allowed_to` (every join requires `projects.active = true`, D02).
- **Project health status** (`status_code`): free transitions among `on_track, at_risk, off_track, not_started, finished, discontinued`; contract only validates inclusion (`base_contract.rb: validate_status_code_included`).
- **P6 project status** (planned/active/inactive/what-if) and **check-out**: not modelled in the sources read; MPXJ portfolio flags `IncludeClosedProjects`/`IncludeWhatIfProjects` imply the status set (inferred).
- **Company lifecycle (Odoo)**: active → archived only when no active user has it as default; archiving cascades to branches.

## Cross-domain links

- Project → calendars (D05, `clndr_id`), default activity type/duration type (D03, D06), data date and last scheduled (D06, D10), baseline project (D10), codes/UDFs (D09), budgets (D17), locations (D01.08 used by D07 resources, D31 assets).
- EPS/OBS → security (D02.03): `EPSType.OBSObjectId`, `UserOBSType.ProjectProfileObjectId`.
- EPS summary columns ← EV and cost rollups (D11, D13, D17), funding (D18: `TotalFunding`, `EPSFundingType`).
- Company → currency (D01.09), cost centers (D17), accounting (D19-D23), employees (D32).
- Project memberships and roles → D02; project journals/paper_trail → D02.13; copy and archive jobs → D36.01.

## Gaps

- **EPS rollup engine**: no OSS summarizer; needs a post-order aggregation job writing summary columns per EPS node, with a `last_summarized` timestamp and incremental re-summarization on project change.
- **OBS-driven security**: only P6 schema; rebuild needs OBS tree, `user_obs(user, obs, project_profile)`, `eps.obs_id`/`wbs.obs_id`, and an evaluator that unions profiles of the user's OBS nodes (and their descendants) responsible for the project's EPS/WBS ancestors (D02.03).
- **Access inheritance down the EPS**: OpenProject memberships are project-local; need effective-permission materialisation over the nested set (ancestor membership applies to descendants).
- **Configurable shells** (Unifier): user-defined shell types, shell status enum `Active | On-Hold | View-Only | Inactive` with write guards, enabled managers per shell, auto-creation from template/BP.
- **Template propagation**: copy-only; push of template changes to derived shells needs template version ids and per-object provenance (`source_template_object_id`) for merge.
- **Workspace config inheritance and dynamic portfolios**: need owned codes/UDFs/calendars/currencies per workspace with override resolution along `parent_path`, and saved-filter portfolios re-evaluated on change (MPXJ `Auto-Maintained` is schema only).
- **Partner organizations on shared projects**: Odoo isolates by company within one database but has no org-on-project participation or document privacy until transmittal (D26).
- **Location hierarchy and geo rollups**: flat location records only.
- **Project currency with rate lock** (Unifier): no source stores a per-project locked rate; add `project.currency_id`, `project.rate_locked`, `project.locked_rate`.
