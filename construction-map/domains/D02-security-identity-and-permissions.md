# D02 Security, Identity and Permissions

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D02.01 | Users and authentication | OpenProject users/passwords/LDAP/OIDC/SAML/2FA; frappe auth + System Settings | full | Statuses, hashed password history + expiry, policy rules, brute-force block, LDAP bind + group sync, TOTP/WebAuthn/backup codes, IP and hour restrictions, session expiry |
| D02.02 | Global security profiles | OpenProject global roles (`permissible_on: :global`, admin bypass); MPXJ `GlobalProfileType` + 65 `GlobalPrivilegesType` flags | full | Privilege catalogue from P6 schema, evaluation from OpenProject; `IsSuperUser` ↔ `admin` |
| D02.03 | Project security profiles | OpenProject members/member_roles/roles/role_permissions + `allowed_to`; MPXJ `ProjectProfileType`/`ProjectPrivilegesType`, `UserOBSType` | partial | Union-of-roles per project membership implemented; OBS-to-EPS/WBS responsibility mapping absent |
| D02.04 | Resource security | frappe User Permission on nested-set doctypes (descendants, `hide_descendants`); MPXJ `ResourceAccessType` | partial | Generic subtree restriction applied to every Link field; P6 resource access table is schema only |
| D02.05 | Cost-field security | frappe permlevel (field strip on read, reset on write) + `mask` permission; MPXJ `ViewProjectCostsAndFinancials` flag | partial | Server-side field hiding/masking for document reads and list queries; report/export masking not verified |
| D02.06 | Module access and license types | OpenProject enabled_modules gating; frappe Module Profile / User Type; MPXJ `UserLicenseType` | partial | Module enablement per project and module blocking per user; no named/concurrent license metering |
| D02.07 | Unifier permissions model | OpenProject group memberships with inherited member_roles; Odoo groups with transitive `implied_ids` | partial | Additive union through groups; no permission templates applied in bulk to shells |
| D02.08 | Workflow-role-based record access | OpenProject `workflows` (role, type, old/new status, assignee/author flags); frappe Workflow transition roles + self-approval; frappe DocShare | partial | Role- and assignee/author-gated transitions; access granted dynamically while assignee only via explicit shares |
| D02.09 | Aconex organization-scoped security | Odoo company restriction domains; OpenProject entity memberships (work-package shares), restricted journals | partial | Record visibility by company/share; no "private to org until transmitted" semantics |
| D02.10 | Primavera Cloud permission sets | OpenProject Role types per object (`permissible_on` project / work_package / project_query / global) and entity memberships | partial | Per-object-type permission sets and object-level grants; no workspace inheritance |
| D02.11 | Record-level and field-level access | Odoo `ir.access` domains; frappe if_owner / User Permission / permlevel / controller `has_permission` hooks | partial | Row-level fully implemented; per-workflow-step field editability not found |
| D02.12 | Delegation / proxy | frappe impersonation (logged, `impersonated_by` in Version) | none | No delegate/date-range routing; impersonation audit only |
| D02.13 | Audit trail | OpenProject journals (snapshot, validity_period) + paper_trail_audits; frappe Version/Access Log/Activity Log; MPXJ `PAuditXType` | full | Field-level old/new, user, timestamp, cause, impersonator, export audit, login audit |
| D02.14 | Electronic signatures | none | none | No signature records or hash in any source |

## Storage model

### OpenProject (principal / membership / role model)

- **users** (`openproject/db/migrate/tables/users.rb`): single table for principals, STI `type` (User, Group, PlaceholderUser, AnonymousUser, SystemUser, DeletedUser, ServiceAccount); `login` (256), `firstname`, `lastname`, `mail`, `admin` bool, `status` int, `last_login_on`, `language` (5), `ldap_auth_source_id` FK, `identity_url`, `first_login`, `force_password_change`, `failed_login_count` int, `last_failed_login_on`, `consented_at`. Status enum (`openproject/app/models/principal.rb:38-44`): `active 1, registered 2, locked 3, invited 4, deleted 5`; default scope hides `deleted`.
- **user_passwords** (`tables/user_passwords.rb`): `user_id`, `hashed_password` (128), `salt` (64), STI `type` (`UserPassword::Bcrypt`, legacy `UserPassword::SHA1`, `app/models/user_password/`), timestamps; N per user (history), newest first (`user.rb: current_password = passwords.first`).
- **group_users(group_id, user_id)** unique both orders.
- **roles** (`tables/roles.rb`): `name`, `position`, `builtin` int, STI `type` (Role, ProjectRole, GlobalRole, WorkPackageRole, ProjectQueryRole). Builtins (`openproject/app/models/role.rb:36-44`): `NON_BUILTIN 0, NON_MEMBER 1, ANONYMOUS 2, WORK_PACKAGE_VIEWER 3, _COMMENTER 4, _EDITOR 5, PROJECT_QUERY_VIEW 6, _EDIT 7, STANDARD_GLOBAL 8`.
- **role_permissions(role_id, permission string)**: one row per granted permission symbol (`role.rb:85-115`).
- **members** (`tables/members.rb`): `user_id` (any principal), `project_id` nullable (NULL = global membership), polymorphic `entity_type/entity_id` (NULL = project-wide; set = membership on one object, e.g. a WorkPackage share). Partial unique indexes: `(user_id, project_id)` where entity is NULL; `(user_id, project_id, entity_type, entity_id)` where entity is set.
- **member_roles** (`tables/member_roles.rb`): `member_id`, `role_id`, `inherited_from` (FK to the group's member_role it was copied from; NULL = directly granted); unique `(member_id, role_id, inherited_from)`.
- **enabled_modules(project_id, name)**: module switch per project.
- **workflows** (`tables/workflows.rb`): `type_id`, `old_status_id`, `new_status_id`, `role_id`, `assignee` bool, `author` bool; index `(role_id, type_id, old_status_id)`.
- **Permission definition** (in code, `openproject/lib/open_project/access_control/permission.rb:4-93`): `name`, `public` (granted to everybody), `require` (:member / :loggedin), `permissible_on` (subset of `global, project, work_package, project_query`), `project_module`, `grant_to_admin`, `dependencies`, `contract_actions`, controller actions.
- **ldap_auth_sources** (`tables/ldap_auth_sources.rb`): `host`, `port`, `account`, `account_password`, `base_dn`, `attr_login/firstname/lastname/mail/admin`, `onthefly_register`, `tls_mode`, `verify_peer`, `tls_certificate_string`, `filter_string`. LDAP groups module: `ldap_groups_synchronized_groups` (dn, group_id, ldap_auth_source_id, sync_users, filter_id) and `ldap_groups_memberships(user_id, group_id)` (`modules/ldap_groups/app/models/ldap_groups/`).
- **two_factor_authentication_devices** (`modules/two_factor_authentication/db/migrate/tables/two_factor_authentication_devices.rb`): STI `type` (Totp, Sms, Webauthn), `default`, `active`, `channel`, `phone_number`, `identifier`, `last_used_at` int (TOTP step), `otp_secret`, `user_id`, `webauthn_external_id` unique, `webauthn_public_key`, `webauthn_sign_count`. Backup codes and remembered-auth tokens are `tokens` rows (`tokens(user_id, type, value(128), created_at, expires_on, data json)`).
- **OAuth/OIDC/SAML**: `oauth_applications(uid unique, secret, redirect_uri, scopes, confidential, client_credentials_user_id, enabled, builtin)`; `remote_identities(user_id, auth_source_type/id, origin_user_id, integration_type/id)` unique per user+source+integration; OIDC provider, user tokens, group links (`modules/openid_connect/app/models/`), SAML provider (`modules/auth_saml/app/models/saml/provider.rb`).

### OpenProject audit
- **journals** (`tables/journals.rb`): polymorphic `journable_type/id`, `user_id` not null, `notes` text (GIN trigram), `created_at`, `updated_at`, `version` int, polymorphic `data_type/data_id` (snapshot row in `<type>_journals`, unique), `cause` jsonb, `validity_period tstzrange` (not empty, not null), `restricted` bool. Unique `(journable_type, journable_id, version)`; GiST exclusion constraint `journable_id WITH =, journable_type WITH =, validity_period WITH &&` (no overlapping validity per object).
- Satellite snapshot tables: `work_package_journals`, `project_journals`, `customizable_journals(journal_id, custom_field_id, value)`, `attachable_journals`, `storable_journals`, etc. (`app/models/journal.rb:124-150`).
- **paper_trail_audits** (`tables/paper_trail_audits.rb`): `item_type`, `item_id`, `event`, `whodunnit`, `stack` text, `object` jsonb, `object_changes` jsonb, `created_at` (used by `has_paper_trail` on Project, `project.rb:175`).

### frappe (role / DocPerm / row-level model; paths under `frappe/frappe/`)
- **Role** (`core/doctype/role/role.json`): `role_name` (PK), `disabled`, `is_custom`, `desk_access`, `two_factor_auth`, `restrict_to_domain`, `home_page`. Automatic roles `Guest`, `All`, `Desk User`, `Administrator` (`permissions.py:34-37`).
- **Has Role** child (`parenttype='User'`, `parent=user`, `role`). **Role Profile** (`role_profile`, `roles` Table Has Role) — bundle applied to users (`core/doctype/user/user.py:290-292`). **Module Profile** (`block_modules` Table Block Module). **User Type** (`role`, `user_doctypes`, `select_doctypes`, `apply_user_permission_on`, `user_id_field`).
- **DocPerm** (`core/doctype/docperm/docperm.json`, child of DocType; Custom DocPerm overrides): `role`, `permlevel` int, `if_owner`, and rights `select read write create delete submit cancel amend report export import share print email mask`.
- **User Permission** (`core/doctype/user_permission/user_permission.json`): `user`, `allow` (DocType), `for_value` (Dynamic Link → allow), `is_default`, `apply_to_all_doctypes`, `applicable_for` (DocType), `hide_descendants`. Validation forbids duplicates and >1 default per (user, allow) (`user_permission.py:48-75`).
- **DocShare** (`core/doctype/docshare/docshare.json`): `user`, `share_doctype`, `share_name` (Dynamic Link), `read`, `write`, `share`, `submit`, `everyone`, `notify_by_email`.
- **User** (`core/doctype/user/user.json`): `enabled`, `email`, `username`, `language`, `time_zone`, `roles`, `role_profiles`, `module_profile`, `block_modules`, `user_type`, `simultaneous_sessions`, `login_after`/`login_before` (hours), `restrict_ip` (prefix list), `bypass_restrict_ip_check_if_2fa_enabled`, `last_login`, `last_ip`, `last_active`, `api_key`, `api_secret` (Password), `last_password_reset_date`, `social_logins`.
- **__Auth** table (`utils/password.py:16`): `(doctype, name, fieldname, password, encrypted)`; `encrypted=0` rows hold passlib hashes (`pbkdf2_sha256`, `argon2`, `:18-23`); `encrypted=1` rows hold reversibly encrypted secrets (API secrets, OTP secret).
- **System Settings** security fields (`core/doctype/system_settings/system_settings.json`): `session_expiry`, `deny_multiple_sessions`, `force_user_to_reset_password` (days), `enable_password_policy`, `minimum_password_score` 1-4, `allow_consecutive_login_attempts`, `allow_login_after_fail` (s), `enable_two_factor_auth`, `two_factor_method` (OTP App | SMS | Email), `bypass_2fa_for_retricted_ip_users`, `apply_strict_user_permissions`, `disable_document_sharing`, `disable_user_pass_login`, `login_with_email_link`.
- **Version** (`core/doctype/version/version.json`): `ref_doctype`, `docname`, `data` JSON. **Access Log** (`core/doctype/access_log/access_log.json`): `user`, `export_from`, `reference_document`, `file_type`, `report_name`, `method`, `filters`, `columns`, `timestamp`. **Activity Log** (login/logout/impersonate). **Deleted Document** (D36).

### Odoo (`odoo/odoo/addons/base/models/`)
- **ir.access** (`ir_access.py:64-126`; this Odoo version merges ir.model.access and ir.rule): `name`, `active`, `model_id`, `group_id` (NULL ⇒ kind `restriction`, set ⇒ `permission`, `:129-137`), `operation` ∈ subsets of `crud` (`CRUD_SELECTION`, `:13-29`), `domain` char (Python-literal domain, may use `user`, `company_ids`, `company_id`, `time`).
- **res.groups** (`res_groups.py:14-90`): `name`, `user_ids` (`res_groups_users_rel(gid, uid)`), `implied_ids` (`res_groups_implied_rel(gid, hid)`), computed reflexive-transitive `all_implied_ids`, `implied_by_ids`, `disjoint_ids`, `access_ids`, `menu_access`, `view_access`, `share` (portal), `api_key_duration`, `privilege_id` → `res.groups.privilege(name, category_id, sequence)`.
- **res.users**: `group_ids` explicit, `all_group_ids = group_ids.all_implied_ids` (`res_users.py:251-253`, `:486-488`), `share`, `company_id`, `company_ids`.

### LibrePlan
- `user_table`, `profile_table(profile_name, roles)`, `roles_table(user, role)` (enum `UserRole`: `ROLE_SUPERUSER`, `ROLE_READ_ALL_PROJECTS`, `ROLE_EDIT_ALL_PROJECTS`, `ROLE_CREATE_PROJECTS`, module roles such as `ROLE_CALENDARS`, `ROLE_TIMESHEETS`, `ROLE_COST_CATEGORIES`, `ROLE_JOB_SCHEDULING`, web-service roles; `libreplan/libreplan-business/src/main/java/org/libreplan/business/users/entities/UserRole.java:36-83`).
- `order_authorization` single-table hierarchy (`resources/org/libreplan/business/users/entities/Users.hbm.xml:115-141`): `authorization_type` ∈ {`READ_AUTHORIZATION`, `WRITE_AUTHORIZATION`} (`OrderAuthorizationType.java`), `order_id`, discriminator `user` (→ `user_id`) or `profile` (→ `profile_id`). Per-project grants to users or profiles.

### P6 schema in MPXJ (`mpxj/src/main/java/org/mpxj/primavera/schema/`)
- `UserType` (`UserType.java:370`): `Name`, `PersonalName`, `EmailAddress`, `GlobalProfileObjectId`, `AllResourceAccessFlag`, currency/date/duration display preferences, `TeamMemberLocale`.
- `GlobalProfileType` / `ProjectProfileType` (`:78`): `Name`, `IsDefault`, `IsSuperUser`, `Privileges` (`GlobalPrivilegesType.java:172`, 65 booleans e.g. `AddEditDeleteOBS`, `AddEditDeleteSecurityProfiles`, `AddEditDeleteUsers`, `AddEditDeleteCurrencies`, `ViewResourceAndRoleCostsAndFinancials`, `ImportXML`; `ProjectPrivilegesType.java:150`, e.g. `ScheduleProjects`, `LevelResources`, `StorePeriodPerformance`, `ApplyActuals`, `CheckInAndCheckOutProjects`, `ApproveTimesheetsAsProjectManager`, `EditWBSCostsAndFinancials`, `ViewProjectCostsAndFinancials`, `AddEditDeleteProjectBaselines`, `SummarizeProjects`).
- `UserOBSType` (user, OBS, project profile), `ResourceAccessType` (`ResourceAccessType.java:94`: `UserObjectId`, `ResourceObjectId`, `AllResourceAccessFlag`), `UserLicenseType` (`UserObjectId`, `LicenseType`).
- `PAuditXType` (`PAuditXType.java:86`): `AuditTimestamp`, `PrmUserName`, `ApplicationName`, `HostName`, `Operation`, `BussinessObjName`, `TableColumnName`, `TablePrimaryKeys`, `BOFieldName`, `BOFieldType`, `OldValue`, `NewValue`, `OldValueName`, `NewValueName`, `ProjectObjectId`, `SubjectArea`.

## Algorithms and logic

### OpenProject: projects a user may act on (`Project.allowed_to(user, permission)`)
`openproject/app/models/projects/scopes/allowed_to.rb:37-200`:
1. Resolve permission objects; return none if user locked/deleted or no permission matches.
2. Admin and every permission `grant_to_admin?` ⇒ all active projects having the permission's module enabled.
3. Anonymous ⇒ non-member relation with builtin `ANONYMOUS`.
4. Otherwise `UNION ALL` of
   - member relation: `members` where `user_id = user.id` and `entity_type IS NULL` (project-wide), joined to active project, `enabled_modules.name IN (permission modules)`, `member_roles → roles → role_permissions.permission = name [AND enabled_modules.name = module]`;
   - non-member relation: project `active AND public`, role `builtin = NON_MEMBER`, and `NOT EXISTS` a membership of the user in that project, joined to the same permission/module conditions.
5. Public permissions skip the role_permission join entirely.
Effective rights are therefore the union over all roles of all memberships (direct and group-inherited); there is no deny rule.

### OpenProject: group role inheritance
`Groups::CreateInheritedRolesService#add_to_user_and_projects_cte` (`openproject/app/services/groups/create_inherited_roles_service.rb`): single SQL CTE: select group memberships and their non-inherited member_roles; find or `INSERT ... ON CONFLICT DO NOTHING` a `members` row per (user, project, entity); insert copied `member_roles` with `inherited_from = group member_role id`; touch `updated_at` of members that gained a new role; return those member ids (used for notifications). Removal (`cleanup_inherited_roles_service.rb`) deletes member_roles by `inherited_from` and members left without roles.

### OpenProject: LDAP group synchronisation
`LdapGroups::SynchronizeGroupsService` (`modules/ldap_groups/app/services/ldap_groups/synchronize_groups_service.rb`): bind with service account; for each synced group under an advisory lock: fetch members (forward lookup via member attribute, or reverse `memberOf`), optionally create missing users through `Users::CreateService` as system user (stops when enterprise user limit reached), map logins case-insensitively, delete memberships no longer present, insert new ones (`insert_all unique_by (user_id, group_id)`), reset counters. Group membership changes then fan out via inherited roles.

### OpenProject: login
- `User.try_to_login(login, password)` (`openproject/app/models/user.rb:259-285`): empty password → nil; existing user: activate invitation token if present, require `active?`, `check_password?` (LDAP bind via `ldap_auth_source.authenticate` or `current_password.matches_plaintext?` with legacy rehash, `:388-399`), and for non-LDAP users reject `force_password_change` or `password_expired?`; unknown login may be created on the fly from LDAP.
- Brute force (`user.rb:811-860`): on failure, if `last_failed_login_on` within `brute_force_block_minutes` increment `failed_login_count` else set 1; stamp `last_failed_login_on`. User is blocked while `failed_login_count >= brute_force_block_after_failed_logins` and last failure inside the block window (`:435-441`; SQL form `blocked_condition`, `:151-158`); a successful login outside the block resets the count. Threshold 0 disables.
- Password expiry `UserPassword#expired?` uses `Setting.password_days_valid` from password `created_at` (`user_password.rb:86`). New passwords are inserted as a new row; older rows beyond the banned-history count are cleaned (`update_password` / `clean_up_former_passwords`, `user.rb:215-229`).
- Password policy `OpenProject::Passwords::Evaluator` (`openproject/lib/open_project/passwords.rb`): rules `uppercase /[A-Z]/`, `lowercase`, `special /[^\da-zA-Z]/`, `numeric`; password conforms when length ≥ `password_min_length` and the number of matched active rules ≥ number of active rules (i.e. all active rules). Random passwords ≥15 chars and force change on next login (`user.rb: random_password!`).
- TOTP verify (`modules/two_factor_authentication/app/models/two_factor_authentication/device/totp.rb:54-93`): `ROTP::TOTP(otp_secret).verify(token, drift_behind: d, drift_ahead: d, after: last_used_at)` with `d = otp_drift_window || 60` s; on success store the returned timestep in `last_used_at` to prevent replay.

### frappe: permission evaluation (`frappe/frappe/permissions.py`)
`has_permission(doctype, ptype, doc, user)` (`:82-231`):
1. `Administrator` ⇒ allow. `ptype=share` with document sharing disabled ⇒ deny. Child tables delegate to parent (`has_child_permission`). Disabled module ⇒ deny.
2. With a document: `get_doc_permissions` (`:234-286`):
   - controller hooks `has_permission` may only deny (`has_controller_permissions`, `:488`);
   - `get_role_permissions(meta, user, is_owner)` (`:289-349`): applicable DocPerm rows = role ∈ user roles and `permlevel = 0`; each right = OR over rows. If any applicable row has `if_owner` and no row grants that right without `if_owner` (and right ≠ create), the right moves into `if_owner[right] = is_owner` and the base right becomes 1 only for `select/read` (so lists can be filtered by owner) else 0. Cached per (doctype, user, is_owner).
   - non-submittable ⇒ `submit=0`; non-importable ⇒ `import=0`; owner ⇒ overlay `if_owner` rights.
   - `has_user_permission(doc)` (`:358-485`) false ⇒ owner keeps only `if_owner` rights minus create; others get nothing.
3. Without a document: role permissions only (+ submittable/importable guards).
4. If still denied and ptype ∈ {read, write, share, submit, email, print, custom}: allowed when a DocShare grants it for that doc (email/print map to read) or, without doc, when any doc of the type is shared.
5. `select` falls back to `read`.

`has_user_permission` steps: (a) if the doctype itself is restricted, `docname` must be in allowed docs (for tree doctypes on create, an ancestor of the new parent must be allowed and not `hide_descendants`); (b) for every Link field (parent and child rows) not flagged `ignore_user_permissions`, if the linked doctype is restricted the value must be allowed; empty values pass unless `apply_strict_user_permissions`. Allowed docs come from `get_user_permissions(user)` (`core/doctype/user_permission/user_permission.py:97-151`): group User Permission rows by `allow`; for nested-set doctypes add all `get_descendants(for_value)` unless `hide_descendants`; filter by `applicable_for`; cached per user.

List queries apply the same rules as SQL (`model/db_query.py:1155-1285`): no read/select role perm and no user permission ⇒ only shared names; owner constraint ⇒ `owner = user`; otherwise for each restricted Link field (and `name`) add `(ifnull(field,'')='' or field in (allowed))` (without the empty branch when strict), AND-joined; `permission_query_conditions` hooks/server scripts are AND-ed; shared names are OR-ed onto the whole condition.

### frappe: field-level security (D02.05, D02.11)
- `permlevel` on DocField groups fields; DocPerm rows at permlevel > 0 grant read/write per group. Read: `apply_fieldlevel_read_permissions` deletes attributes whose permlevel is not in `get_permlevel_access('read')` for parent and child rows, then masks (`model/document.py:1255-1285`). Write: `validate_higher_perm_levels` resets values of high-permlevel fields the user cannot write back to the stored/default value (`document.py:1320-1340`).
- `mask` right: fields with `mask=1` whose permlevel lacks `mask` access are returned masked (`model/meta.py:197-216`); pattern by type (`model/utils/mask.py:21`): phone → first 3 + `XXXXXX`, email → `XXXXXX@domain`, date → `XX-XX-XXXX`, default `XXXXXXXX`. On save, masked placeholders are replaced by DB values before link checks (`_restore_masked_fields_from_db`, `document.py:1287`).

### Odoo: record rules (`odoo/odoo/orm/models.py:3603-3646`)
`_access_domain(operation)`: operations = CRUD codes containing the letter; collect active `ir.access` rows of the model whose operation matches and whose `group_id` ∈ user's `all_group_ids ∪ {False}`; domains are pre-parsed when literal else `safe_eval` with `{user, time, company_ids, company_id}`; result = `OR(permission domains) AND AND(restriction domains)`, plus `_inherits` parents' domains as `parent_field any (...)` restrictions. No matching permission ⇒ `OR([]) = FALSE` ⇒ model-level denial. `has_access` (`:3464-3500`): superuser bypass; read results cached per record id in `env._access_cache`; other ops check `origin == origin.sudo().filtered_domain(domain)`. Cache key includes `allowed_company_ids` (`ir_access.py:308`). Group closure: `_compute_all_implied_ids` = ids + supersets (`res_groups.py:341-346`); a group may not imply two disjoint groups (`:95-115`).
- Login throttling (`res_users.py:1335-1395`): per-registry, per-remote-IP `(failures, last_failure)`; on `AccessDenied` increment; cooldown after `base.login_cooldown_after` failures for `base.login_cooldown_duration` s; success clears.

### frappe: authentication
- `LoginManager.authenticate` (`frappe/frappe/auth.py:269-306`): reject empty or oversize password; `User.find_by_credentials`; per-IP and per-user `LoginAttemptTracker`; disabled user ⇒ fail; every failure writes an authentication Activity Log and commits (`fail`, `:335-341`).
- `LoginAttemptTracker` (`auth.py:543-640`): cache keys `login_failed_count`, `login_failed_time`; failure within `lock_interval` of the first failure increments, else resets to 1; locked while `count > max_consecutive_login_attempts` inside the interval; success clears. Parameters from `allow_consecutive_login_attempts` / `allow_login_after_fail`.
- `validate_hour` (`auth.py:347-365`): deny if current hour ≥ `login_before` or < `login_after`. `validate_ip_address` (`:477-515`): request IP must start with an entry of `restrict_ip`, unless 2FA is enabled and bypass flag set.
- Password storage: passlib verify, `is_password_reused` compares with current hash (`utils/password.py:107-122`); `force_user_to_reset_password` days since `last_password_reset_date` (`auth.py:308-325`).
- 2FA (`frappe/frappe/twofactor.py`): per-user secret `b32encode(os.urandom(10))` stored encrypted in defaults (`:130-139`); after password step cache user/pwd/secret under a tmp id for 180 s (OTP app) or 300 s (SMS/email) (`:94-110`); verify with HOTP (SMS/email counter) or TOTP (`:146-185`).
- Sessions: `simultaneous_sessions` per user (`sessions.py:80`), `session_expiry` default `240:00:00` (`:563`), `deny_multiple_sessions` clears other sessions (`auth.py:253-260`).

### Workflow-gated actions (D02.08)
- OpenProject `workflows` rows permit status change `old → new` for (role, type); `author`/`assignee` true rows apply only when the user is the WP author/assignee (columns in `tables/workflows.rb`; inferred from column semantics, evaluator not in sparse clone).
- frappe `get_transitions(doc)` (`frappe/frappe/model/workflow.py:76-110`): requires read; transitions from current state whose `allowed` role ∈ user roles and whose condition evaluates true. `has_approval_access` (`:364`): Administrator, or `allow_self_approval`, or user ≠ owner. Save validation rejects edits not allowed in the state and transitions not permitted (`:306-360`).
- ERPNext value-based approval `AuthorizationControl.validate_auth_rule` (`erpnext/erpnext/setup/doctype/authorization_control/authorization_control.py:63-116`): find Authorization Rules for transaction + `based_on` (Grand Total, discounts) with `value <= total`, company-specific first then global; item/item-group discount rules take precedence; then require the approving user/role.

### Audit capture
- OpenProject `Journals::CreateService#call` (`openproject/app/services/journals/create_service.rb:55-100`), run under an advisory lock per journable: one SQL statement snapshots the journable plus custom values, attachments, storages into the data tables only if something changed (`select_changed_sql`). Aggregation (`:589-626`) reuses the previous journal when aggregation is enabled (`journal_aggregation_time_minutes > 0`), the predecessor's `updated_at` is within the window, same user, same or empty cause, at most one of the two has notes, and same `internal` flag. New journal: previous journal's `validity_period` upper bound set to the new timestamp, new journal gets `[now, NULL)` (`:405-490`). `cause` jsonb records system causes (status change, parent change, working-day change, import; `app/models/journal/caused_by_*.rb`).
- frappe `Document.save_version` (`frappe/frappe/model/document.py:2038-2062`) when DocType `track_changes`: diff against `_doc_before_save` (or `amended_from`), skip Version doctype, installs and patches; `get_diff` (`core/doctype/version/version.py:104-230`) produces `changed [[field, old, new]]`, `added`/`removed` child rows, `row_changed [[table, idx, rowname, changes]]`, skips no-value fields and `ignore_versioning` fields, formats values, records `data_import`, `updater_reference`, `impersonated_by`, `audit_user` (`:41-49`). Insert events store `creation`, `created_by` only when an updater reference exists.
- frappe optimistic locking `check_if_latest` (`document.py:1387-1416`): `modified` of DB copy must equal the client's `_original_modified`, else `TimestampMismatchError`.
- Impersonation (`core/doctype/user/user.py:1647-1690`): requires `impersonate` right on User, writes Activity Log `operation=Impersonate`, notifies target by notification and email with the reason; subsequent Versions carry `impersonated_by`.

## State machines and workflows

- **OpenProject principal status**: `invited → active` (invitation token on first login, `user.rb:288-297`), `registered → active` (admin activation), `active ⇄ locked`, any → `deleted` (DeletedUser placeholder). Orthogonal derived state *blocked* = brute-force window condition, auto-expires.
- **frappe login**: credentials → (2FA required? → OTP pending with cached tmp id, expires 180/300 s → verified) → session; failure counters per IP and user → locked until interval passes.
- **frappe docstatus** (governs edit rights): `0 Draft → 1 Submitted → 2 Cancelled`; `0 → 2` only via discard; `1 → 0` forbidden; amend creates a new doc with `amended_from` (`model/document.py:1418-1480`). Submitted docs edit only `allow_on_submit` fields (`_validate_update_after_submit`).
- **Two-factor device**: `active=false` (registration started) → `active=true` (first token verified); one `default` per user.

## Cross-domain links

- Memberships/roles reference projects (D01.03) and, via `entity_type`, work packages (D03), project queries (D33).
- Workflows reference types and statuses (D24); frappe Workflow states drive D24 business processes.
- User Permissions restrict Company (D01.07), Project, Employee/Resource (D07), Cost Center (D17) links.
- Field masking/permlevel protects cost fields in D13/D17/D19.
- Audit journals cover D03 work packages, D10 progress, D25 documents, D28 meetings; P6 audit `PAuditXType` relates to D35 import/export.
- Login and job users feed D36 (job run-as user, rate limits).

## Gaps

- **OBS-based project security** (D02.03): implement `user_obs(user_id, obs_id, project_profile_id)`, `eps.obs_id`, `wbs.obs_id`; effective privileges on project P = union of profiles over OBS nodes assigned to the user whose subtree contains the OBS responsible for P's EPS/WBS nodes; Project Superuser short-circuits.
- **Resource security as a dedicated rule**: P6 `ResourceAccessType` (user → resource node, all flag) needs subtree filtering on resource pickers, leveling and timesheets; frappe User Permission on a nested-set Resource doctype is the closest reusable mechanism.
- **License metering**: named vs concurrent counts per module, login-time check against active sessions.
- **Permission templates** (Unifier): template entity of (group, module, rights), bulk apply to selected shells with overwrite/merge mode.
- **Dynamic assignee-based record access**: grant read/edit while a user is a current workflow step assignee or resolved from a shell attribute; needs a computed share table refreshed on step change.
- **Per-step field editability**: field × workflow-step matrix (hidden / read-only / editable / required) enforced on save like frappe `validate_higher_perm_levels`.
- **Organization privacy until transmittal** (Aconex): document `owner_org_id` + share/transmittal grants as row-level restriction.
- **Delegation/proxy**: `proxy(delegator, delegate, start, end, scope)`, task routing, and `acting_for_user_id` on audit rows.
- **Electronic signatures**: signature record (signer, role, document hash SHA-256, timestamp, certificate or envelope id), signer-authority check, hash re-verification on read.
- **DB-level audit levels and purge** (P6 0-3): no trigger-based audit in sources; retention handled only generically (D36.03).
