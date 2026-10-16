# D09 Codes, User-Defined Fields and Classification

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D09.01 | Project codes | MPXJ `ProjectCode`/`ProjectCodeValue` (XER `PCATTYPE`/`PCATVAL`/`PROJPCAT`) | full | Hierarchical values, assignment per project; grouping/rollups not implemented |
| D09.02 | Activity codes (global/EPS/project scope) | MPXJ `ActivityCode` + `ActivityCodeScope` + `ActivityCodeValue` (XER `ACTVTYPE`/`ACTVCODE`/`TASKACTV`) | full | Scope, EPS/project owner, max length, secure flag, colored hierarchical values; one value per type per activity |
| D09.03 | Resource, role and assignment codes | MPXJ `ResourceCode`, `RoleCode`, `ResourceAssignmentCode` (XER `RCATTYPE`/`RCATVAL`/`RSRCRCAT`, `ROLECATTYPE`, `ASGNMNTCATTYPE`/`ASGNMNTACAT`) | full | Same type/value/assignment pattern |
| D09.04 | UDFs (subject areas, types, formulas, indicators, summaries) | MPXJ `UserDefinedField` + PMXML `UDFTypeType`/`UDFValueType`/`UDFCodeType`; OpenProject `CustomField` (calculated_value formulas, hierarchy, weighted items); MPXJ `GraphicalIndicator` | full | Storage from P6; working formula engine (Dentaku) with dependency closure in OpenProject; indicator criteria evaluation in MPXJ |
| D09.05 | Metadata-driven data elements/forms | OpenProject custom fields + sections + type/project activation; ERPNext `Accounting Dimension` (`create_custom_field`); Odoo `fields.Properties` | partial | Dynamic fields per entity type and per project; no picklist data sets with dependency, no BP form designer |
| D09.06 | Cost codes / CBS | MPXJ `CostAccount` (hierarchy); Odoo `account.analytic.plan` (tree, per-root dynamic column) + `analytic_distribution`; ERPNext `Cost Center` tree | partial | Hierarchies and multi-dimension tagging exist; no segment/delimiter CBS code parsing |
| D09.07 | Classification standards (MasterFormat, UniFormat, OmniClass) | IfcOpenShell `api/classification` (`IfcClassification`, `IfcClassificationReference`, `IfcRelAssociatesClassification`) | partial | Library/reference model and association; no standard code libraries or cross-standard mapping tables |

## Storage model

### P6 codes (MPXJ)
Paths relative to `mpxj/src/main/java/org/mpxj/`.

| Entity | Fields | Citation |
|---|---|---|
| `ActivityCode` (type) | `uniqueID` (`actv_code_type_id`), `scope` {GLOBAL, EPS, PROJECT} (`actv_code_type_scope`), `scopeEpsUniqueID` (`wbs_id`), `scopeProjectUniqueID` (`proj_id`), `sequenceNumber`, `name` (`actv_code_type`), `secure` (`super_flag`), `maxLength` (`actv_short_len`) | `ActivityCode.java:191-198`, `ActivityCodeScope.java:27-33`, `primavera/TableContextReader.java:494-512` |
| `ActivityCodeValue` | `uniqueID` (`actv_code_id`), FK type, `sequenceNumber`, `name` (`short_name`), `description` (`actv_code_name`), `color` (hex), `parentValue` (`parent_actv_code_id`) | `ActivityCodeValue.java:146-152`, `TableContextReader.java:514-532` |
| activity ↔ value | XER `TASKACTV` {task_id, actv_code_type_id, actv_code_id}; stored on `Task` as map type→value (one value per type) | `primavera/TableProjectReader.java:174-188` |
| `ProjectCode`/`ProjectCodeValue` + `PROJPCAT` {proj_id, proj_catg_type_id, proj_catg_id} | same shape | `TableContextReader.java:326-366`, `TableProjectReader.java:147-172` |
| `ResourceCode`/`RoleCode`/`ResourceAssignmentCode` + values | same shape; resource assignment via `RSRCRCAT` {rsrc_id, rsrc_catg_type_id, rsrc_catg_id}; assignment via `ASGNMNTACAT` {asgnmnt_catg_type_id, asgnmnt_catg_id} | `TableContextReader.java:368-492, 833-900`, `TableProjectReader.java:189-216` |
| PMXML `ActivityCodeTypeType` | adds `EPSCodeTypeHierarchy`, `RefProjectObjectIds`, `IsBaseline`, `IsTemplate`, `Length` | `primavera/schema/ActivityCodeTypeType.java` |

Value hierarchies are topologically sorted before linking parents (`common/HierarchyHelper.sortHierarchy`, used at `TableContextReader.java:514`).

### P6 UDFs (MPXJ + PMXML schema)
| Entity | Fields | Citation |
|---|---|---|
| `UserDefinedField` | `uniqueID` (`udf_type_id`), `internalName` (`udf_type_name`), `externalName` (`udf_type_label`), `fieldTypeClass` from `table_name` (PROJWBS/TASK → TASK, RSRC → RESOURCE, TASKRSRC → ASSIGNMENT, PROJECT → PROJECT), `summaryTaskOnly` (table PROJWBS), `dataType` | `UserDefinedField.java:126-131`, `TableContextReader.java:291-318`, `primavera/FieldTypeClassHelper.java:108-122` |
| data types | XER `logical_data_type`: FT_TEXT→STRING, FT_MONEY→CURRENCY, FT_START_DATE/FT_END_DATE→DATE, FT_INT→INTEGER, FT_FLOAT/FT_FLOAT_2_DECIMALS→NUMERIC, FT_STATICTYPE (indicator)→STRING; PMXML "Text, Cost, Start Date, Finish Date, Integer, Double, Indicator" | `primavera/UdfHelper.java:129-158` |
| UDF value (XER `UDFVALUE`) | `udf_type_id`, `fk_id` (row in subject table), `udf_text`, `udf_number`, `udf_date`, `udf_code_id` | `TableContextReader.java:808-830`, `TableReaderHelper.java:140-205` |
| PMXML `UDFTypeType` | `SubjectArea`, `DataType`, `Title`, `Formula`, `IsCalculated`, `IsConditional`, `DisplayIndicatorFlag`, `SummaryMethod`, `IsSecureCode` | `primavera/schema/UDFTypeType.java` |
| PMXML `UDFValueType` | `UDFTypeObjectId`, `ForeignObjectId`, `ProjectObjectId`, `Text/Double/Integer/Cost/StartDate/FinishDate/Indicator`, `CodeValue`, `UDFCodeObjectId`, `ConditionalIndicator`, `Formula` | `primavera/schema/UDFValueType.java` |
| PMXML `UDFCodeType` | `CodeTypeObjectId`, `CodeValue`, `Description`, `SequenceNumber` (code-list UDFs) | `primavera/schema/UDFCodeType.java` |

MSP custom field metadata: `CustomField{field, alias, lookupTable, graphicalIndicator, masks}` (`CustomField.java:155-161`); `CustomFieldLookupTable{guid, enterprise, showIndent, resourceSubstitutionEnabled, leafOnly, allLevelsRequired, onlyTableValuesAllowed}` (`CustomFieldLookupTable.java:176-182`); `GraphicalIndicator{fieldType, nonSummaryRowCriteria, summaryRowCriteria, projectSummaryCriteria, inheritance flags}` (`GraphicalIndicator.java:324-331`).

### OpenProject custom fields
Paths relative to `openproject/`.

| Table | Columns | Citation |
|---|---|---|
| `custom_fields` | `type` (STI: WorkPackageCustomField, ProjectCustomField, TimeEntryCustomField, UserCustomField, VersionCustomField, GroupCustomField), `field_format` (formats referenced in the model: text, int, float, date, datetime, bool, list, user, version, hierarchy, weighted_item_list, calculated_value; the format registry initializer is not in the clone), `regexp`, `min_length`, `max_length`, `is_required`, `is_for_all`, `is_filter`, `searchable`, `editable`, `admin_only`, `multi_value`, `default_value`, `name`, `custom_field_section_id`, `formula` jsonb `{formula, referenced_custom_fields[]}` (GIN index) | `db/migrate/tables/custom_fields.rb`, `db/migrate/20250613141234_add_formula_to_custom_fields.rb`, `app/models/custom_field.rb:48-75, 106, 197-300, 372-403` |
| `custom_values` | `customized_type`, `customized_id` (polymorphic), `custom_field_id`, `value` text (trigram GIN) | `db/migrate/tables/custom_values.rb` |
| `custom_options` | `custom_field_id`, `position`, `default_value`, `value` | `db/migrate/tables/custom_options.rb` |
| `hierarchical_items` | `custom_field_id`, `label` (`db/migrate/tables/hierarchical_items.rb:37`), `short`, `weight` (decimal), `sort_order`, `children_count`, closure-tree hierarchy table | `app/models/custom_field/hierarchy/item.rb:30-34`, `db/migrate/20251103123548_rename_item_score_to_weight.rb` |
| `custom_fields_projects`, `custom_fields_types`, `project_custom_field_project_mappings` | activation of a field per project and per work-package type | `db/migrate/tables/` |
| `calculated_value_errors` | per customized record and field, last evaluation error | `db/migrate/20250908072653_create_calculated_value_errors.rb` |

### CBS / analytic dimensions
- MPXJ `CostAccount{uniqueID, id, name, notes, sequenceNumber, parent}` (`mpxj/src/main/java/org/mpxj/CostAccount.java:126-131`), referenced by assignments (`acct_id`).
- Odoo `account.analytic.plan` (`odoo/addons/analytic/models/analytic_plan.py:12-90`): `_parent_store` tree (`parent_id`, `parent_path`, `root_id`, `complete_name`), `default_applicability`, `applicability_ids`; each root plan materializes a column on analytic lines named `account_id` (project plan) or `x_plan<ID>_id` (`:116`) created via `ir.model.fields` (`:317-430`). `account.analytic.account{name, code, plan_id, root_plan_id, company_id, partner_id}` (`analytic_account.py:12-95`). `analytic.mixin.analytic_distribution` Json `{"<account ids>": percentage}` with GIN index on keys (`analytic_mixin.py:17-40`).
- ERPNext `Accounting Dimension` adds a Link custom field to every accounting doctype and Budget (`erpnext/erpnext/accounts/doctype/accounting_dimension/accounting_dimension.py:137-182`).

### IFC classification
`IfcClassification{Name, Edition, EditionDate, Source}` related to the project by `IfcRelAssociatesClassification`; `IfcClassificationReference{Identification (ItemReference in IFC2X3), Name, ReferencedSource → IfcClassification or parent reference}`; rooted products linked by `IfcRelAssociatesClassification`, non-rooted resources (e.g. cost items, materials) by `IfcExternalReferenceRelationship` (`ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/classification/add_classification.py:89-125`, `add_reference.py:127-270`).

## Algorithms and logic

### Calculated (formula) custom fields (OpenProject)
`app/models/custom_field/calculated_value.rb`:
- Grammar: operators `+ - * / % ^ < > <= >= <> != = == AND && OR ||`, functions `IF AND OR XOR NOT SWITCH MIN MAX SUM AVG ROUND ROUNDDOWN ROUNDUP ABS`, `CASE WHEN THEN ELSE END`, `TRUE FALSE`; operands only `{{cf_<id>}}` references and numeric literals (`:31-70`). Evaluated by Dentaku (`Dentaku::Calculator.new(case_sensitive: true)`).
- Referenceable formats: int, float, bool, calculated_value, weighted_item_list (`:78`).
- Validation: blank → error; tokens outside grammar → `invalid_tokens`; syntax check; referenced fields must be in `usable_custom_field_references_for_formula` (`:120-170`).
- Cycle prevention `can_be_referenced_by?(target)` (`:177-187`): recursive DFS with memo cache; a calculated field is referenceable only if neither it nor any field it transitively references is the target.
- Change propagation `affected_calculated_fields(changed_ids)` (`:96-112`): fixpoint loop over calculated fields, collecting those whose `referenced_custom_fields` intersect the changed set, then repeating with the newly affected ids (transitive closure).

### Indicator evaluation (MPXJ, MSP graphical indicators)
`GraphicalIndicator.evaluate(container)` (`GraphicalIndicator.java:58-135`): choose criteria list by row kind (project summary task uniqueID 0 / summary / non-summary) honoring inheritance flags, then return the index of the first `GraphicalIndicatorCriteria` (a `GenericCriteria` test: operator + value(s)) that matches the field value. This is the threshold traffic-light logic needed for P6 indicator UDFs.

### Hierarchy/code rollups
- OpenProject hierarchy items: ancestry path label `self_and_ancestors.label` joined by " / ", with short/weight suffix (`app/models/custom_field/hierarchy/item.rb:38-50`); tree flattening with depth (`app/services/custom_fields/hierarchy/hierarchical_item_aggregator.rb:33-48`).
- Odoo analytic plan applicability: score-based rule matching; default applicability unless a rule scores above baseline 0.5 (`analytic_plan.py:244-265`).

### UDF value binding (MPXJ)
UDF values are grouped by `(subject table, fk_id)` then assigned to the entity by data type: DATE → `udf_date`, CURRENCY/NUMERIC → `udf_number`, INTEGER → `udf_number` as int, else `udf_text` (`primavera/TableReaderHelper.java:140-205`).

### Classification reference reuse (IfcOpenShell)
`add_reference`: return existing reference if all products already reference it; reuse a reference with the same `Identification`; when copying from a library file, migrate the reference into the model and repoint `ReferencedSource` to an existing same-named `IfcClassification`; append products to the existing association relationship or create one (`add_reference.py:127-270`).

## State machines and workflows
None in code for codes or UDFs. OpenProject calculated values recompute on save of the customized record; the last failure is stored in `calculated_value_errors` (`app/models/custom_field.rb:55, 448-452`).

## Cross-domain links
- Activity codes and UDFs attach to D03 activities/WBS; project codes to D15 portfolio grouping; resource/role/assignment codes to D07.
- Cost accounts / analytic plans / cost centers are the D17 CBS and D13 expense classification; Odoo analytic lines are also D32 timesheet lines.
- Code- and UDF-based leveling priorities → D08; code-based grouping in reports → D33.
- IFC classification references on products/cost items → D17 cost items and D31 assets.
- OpenProject custom fields on time entries (`TimeEntryCustomField`) → D32.

## Gaps
- Summary aggregation of UDFs to WBS/project (sum/min/max/avg; P6 `SummaryMethod`): stored only. Rebuild: post-order traversal of WBS applying the method per UDF.
- Global change by code (P6): none. Rebuild as filtered bulk update over code assignments.
- Unifier data definitions with data sets and dependent picklists, upper/detail forms, auto-populate across BPs: none. Rebuild: data definition (type, size, picklist, data-set id), data element (label → DD), form layout per BP, dependency table (parent value → allowed child values), auto-populate rules (source BP field → target field on link/query).
- CBS segment parsing (delimiter, per-segment rollup): none. Rebuild: split code by delimiter, store segments as materialized path, roll up by prefix.
- MasterFormat/UniFormat/OmniClass libraries and mapping tables: none; IFC reference model can hold them as `IfcClassification` + nested `IfcClassificationReference` trees, with a mapping table (source ref, target ref) to add.
