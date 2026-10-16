# D35 Import/Export Formats

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D35.01 | XER (P6 native) | MPXJ `PrimaveraXERFileReader` / `PrimaveraXERFileWriter` | partial | Full grammar, 43 tables read, 44 written; no per-object import options (keep/update/insert/delete), no RISK tables |
| D35.02 | P6 XML (PMXML) | MPXJ `PrimaveraPMFileReader` / `PrimaveraPMFileWriter` (JAXB, 160 schema classes) | partial | Projects + BaselineProject read/write; schema carries Risk*, Funding, Document, Timesheet but MPXJ ignores them; zip only via OPC/P6 REST export |
| D35.03 | MS Project XML (MSPDI) | MPXJ `MSPDIReader` / `MSPDIWriter`; IfcOpenShell `ifc4d/msp2ifc.py`, `ifc2msp.py` | full | Lag tenths-of-minute + LagFormat, outline hierarchy, cross-project links, summary tasks become WBS on XER write |
| D35.04 | UN/CEFACT XML | none for schedules; Odoo `account_edi_ubl_cii` (UN/CEFACT CII invoice), ERPNext `edi/code_list` (genericode code lists) | none | No UN/CEFACT schedule (XML) implementation anywhere; adjacent UN/CEFACT invoice + code-list infrastructure only |
| D35.05 | Excel/CSV import-export | Odoo `base_import` + `BaseModel.load/export_data` + `web/controllers/export.py`; IfcOpenShell `ifc4d/csv2ifc.py`, `ifc5d/csv2ifc.py`, `ifccsv` | full | Fuzzy column mapping, persisted mappings, dry-run, batch with row-by-row fallback, upsert by external id |
| D35.06 | Primavera Risk Analysis / QRA formats | MPXJ PMXML schema `RiskType`, `RiskImpactType` (unused by reader) | none | No .plan/.rsk reader; P6 risk register elements exist only as JAXB classes |
| D35.07 | IFC / BIM models | IfcOpenShell `api/sequence`, `api/cost`, `ifc4d`, `ifc5d`, `bcf`; OpenProject `modules/bim` | full | XER/PMXML/MSPDI/Powerproject to IFC4 schedule, IFC to PMXML/MSPDI, 5D cost CSV, BCF 2.1/3.0, IFC to XKT conversion pipeline |
| D35.08 | COBie | IfcOpenShell `ifcfm` (`cobie24.py`, `cobie24legacy.py`) | partial | IFC to COBie 2.4 export (CSV/XLSX/ODS/pandas); no COBie to IFC import |
| D35.09 | Document metadata spreadsheets | Odoo `base_import` (generic, any model incl. `ir.attachment`/documents) | partial | Generic mechanism only; no document-register-specific template |
| D35.10 | Configuration packages | Odoo `load()` with xml_id + `noupdate` mode | partial (inferred) | Module data loading semantics (external ids, update mode) are the closest analogue; no versioned BP-design package |

## Storage model

### MPXJ format registry (every format read/written)

Auto-detection order and fingerprints: `mpxj/src/main/java/org/mpxj/reader/UniversalProjectReader.java:384-524` (BOM, OLE, MSPDI, PP, MPX, XER `ERMHDR.*` :1211, Planner, PMXML `<BusinessObjects|APIBusinessObjects` :1215, MDB, SQLite, ZIP, Phoenix, FastTrack, ProjectLibre, GanttProject, TurboProject, DOS EXE, ConceptDraw, Synchro, GanttDesigner, SDEF, Sage, Project Commander, Edraw). ZIP is unpacked to a temp dir and every file in it is probed (`handleZipFile` :709, `handleDirectory` :737).

| Format | Read class | Write class | Notes |
|---|---|---|---|
| Primavera P6 XER | `primavera/PrimaveraXERFileReader` | `primavera/PrimaveraXERFileWriter` | default charset CP1252 (`PrimaveraXERFileReader.java:351`, writer :1334) |
| Primavera P6 PMXML | `primavera/PrimaveraPMFileReader` | `primavera/PrimaveraPMFileWriter` | namespace forced to `http://xmlns.oracle.com/Primavera/P6/V25.12/API/BusinessObjects` (`NamespaceFilter.java:77`) |
| P6 EPPM database (JDBC) | `primavera/PrimaveraDatabaseReader` | none | `select * from <schema>task where proj_id=? and delete_date is null` (`DatabaseProjectReader.java:207`) |
| P6 SQLite database | `primavera/PrimaveraDatabaseFileReader` | none | same table layout |
| P6 EPPM REST API | `primavera/webservices/WebServicesReader` | none | export to XML/XER via REST (see D34) |
| Oracle Primavera Cloud | `opc/OpcReader` | none | async export job (see D34) |
| Primavera P3 (Btrieve dir, PRX) | `primavera/p3/P3DatabaseReader`, `P3PRXFileReader` | none | |
| SureTrak (dir, STX) | `primavera/suretrak/SureTrakDatabaseReader`, `SureTrakSTXFileReader` | none | |
| MS Project MPP (8/9/12/14) | `mpp/MPPReader` (+ `MPP8Reader`..`MPP14Reader`) | none | OLE compound document |
| MS Project MPX | `mpx/MPXReader` | `mpx/MPXWriter` | |
| MS Project XML (MSPDI) | `mspdi/MSPDIReader` | `mspdi/MSPDIWriter` | namespace `http://schemas.microsoft.com/project` (`mspdi/NamespaceFilter.java:45`) |
| MS Project database (MPD) | `mpd/MPDFileReader`, `MPDDatabaseReader` | none | |
| Project Server / PWA / Project Online | `pwa/PwaReader` | none | `/_api/` OData (`PwaReader.java:597`) |
| Microsoft Planner (Dataverse) | `msplanner/MsPlannerReader` | none | `msdyn_projects` entity set (`MsPlannerReader.java:106`) |
| Asta Powerproject PP (text / SQLite / MDB / JDBC) | `asta/AstaFileReader`, `AstaTextFileReader`, `AstaSqliteReader`, `AstaMdbReader`, `AstaJdbcReader` | none | |
| Phoenix Project Manager (PPX, v4/v5) | `phoenix/PhoenixReader` (`Phoenix4Reader`, `Phoenix5Reader`) | none | |
| Deltek Open Plan BK3 | `openplan/OpenPlanReader` | none | |
| Synchro SP | `synchro/SynchroReader` | none | |
| USACE SDEF | `sdef/SDEFReader` | `sdef/SDEFWriter` | fixed-width records |
| Sage 100 Contractor schedule grid | `sage/SageReader` | none | |
| GanttProject | `ganttproject/GanttProjectReader` | none | |
| GNOME Planner | `planner/PlannerReader` | `planner/PlannerWriter` | |
| ProjectLibre POD | `projectlibre/ProjectLibreReader` | none | serialized Java + embedded MSPDI |
| FastTrack FTS | `fasttrack/FastTrackReader` | none | |
| Merlin | `merlin/MerlinReader` | none | |
| ConceptDraw Project | `conceptdraw/ConceptDrawProjectReader` | none | |
| Edraw Project EDPX | `edrawproject/EdrawProjectReader` | none | |
| GanttDesigner | `ganttdesigner/GanttDesignerReader` | none | |
| TurboProject PEP | `turboproject/TurboProjectReader` | none | |
| Project Commander | `projectcommander/ProjectCommanderReader` | none | |
| MPXJ JSON | none | `json/JsonWriter` | |

Writer enum: `writer/FileFormat.java` = JSON, MPX, MSPDI, PLANNER, PMXML, XER, SDEF.

### XER file grammar (as parsed by `primavera/XerFile.java`)

```
file      := header-line { table-block } end-line
header    := "ERMHDR" TAB version TAB export-date TAB "Project" TAB user TAB user TAB db-name TAB "Project Management" TAB currency-short-name EOL
table     := "%T" TAB table-name EOL
             "%F" TAB col1 TAB col2 ... EOL
             { "%R" TAB v1 TAB v2 ... EOL }
end-line  := "%E" EOL
```

- Tokenizer: `common/Tokenizer.java` with delimiter `\t` (`XerFile.java:95-96`); CR, LF, CRLF all end a record. A field may be double-quoted; inside quotes `""` is a literal quote and TAB/EOL are not delimiters, so quoted values can span lines. A record whose first token is empty is treated as a continuation DATA row (`RECORD_TYPE_MAP.put("", DATA)`, `XerFile.java:609`).
- First record must start with `ERMHDR` else INVALID_FILE (`XerFile.java:107-111`). Header field index 8 is the default currency short name, default `USD` (`processHeader`, :316-319). Writer emits version `20.12`, min project current-date, `admin`, `dbxDatabaseNoName`, default currency id (`PrimaveraXERFileWriter.java:226-240`).
- `%T` lowercases the table name; tables not in the required set are skipped wholesale (:251-265). `%F` lowercases column names and builds name->index map (:267-285). `%R` values beyond the `%F` count are dropped (:333-336). `%E` stops parsing (:296-300).
- Typing is by column name, not table: `FIELD_TYPE_MAP` (:619 onward). Only collision handled: `projcost.target_qty` is CURRENCY (:449). Empty string means null. DATE: fast path for `yyyy-MM-dd`, `yyyy-MM-dd HH:mm`, `yyyy-MM-dd HH:mm:ss` (:515), fallback pattern `yyyy-M-dd[ HH[:][.]mm[[:][.]ss]]` (:574). NUMERIC/CURRENCY/DURATION parsed with DecimalFormat whose decimal/grouping separators come from the `currtype` row matching the header currency (`processCurrency` :417); `currtype` rows are buffered and re-processed so later tables parse correctly (:133-138). Unparseable numbers fall back to the raw string.
- Encoding: reader and writer default `Cp1252` (`common/CharsetHelper.java:37`), overridable via `setCharset`. Notes/memos: newline is written as two DEL chars `\x7F\x7F` and content as HTML (`XerWriter.java:249-262`); read back by `NotesHelper.java:62`. Quotes in strings are doubled on write (`XerWriter.java:323-336`).
- Value formats on write (`XerWriter.java:348-383`): dates `yyyy-MM-dd HH:mm`, date-only `yyyy-MM-dd`, booleans `Y`/`N`, doubles `0.######`, rates/currency `0.0000`, max units `0.####` (stored as fraction: `MaxUnits/100`), durations always hours (`formatDuration` :306), GUIDs as P6 base64 of byte-swapped UUID with trailing `==` removed (:271-298), colours hex.
- Embedded calendar grammar in `calendar.clndr_data` (`StructuredTextParser.java`, writer `StructuredTextWriter.java`): `record := "(" number "||" name "(" key "|" value { "|" key "|" value } ")" "(" { record } ")" ")"`. Root `CalendarData` has children `DaysOfWeek` (child names `1`..`7`, 1 = Sunday, `common/DayOfWeekHelper.java:60`) each with hour records `s|HH:mm|f|HH:mm` (12-hour `h:mm a` also accepted, `TableContextReader.java:1198-1199`), and `Exceptions` whose children carry `d|<days since 1899-12-30>` (`EXCEPTION_EPOCH`, `TableContextReader.java:1254`, :793) plus optional hour records (no hours = non-working day). Missing `day/week/month/year_hr_cnt` are derived: minutes/day = weekly minutes / working days, month = week*4, year = month*12 (`TableContextReader.java:627-670`).

### XER tables and key columns

Read set: `PrimaveraXERFileReader.java:369-414`. Columns below are those the writer emits (`PrimaveraXERFileWriter.java` `*_COLUMNS` maps); PKs first, FKs named.

| Table | Entity | Key columns (PK; FKs; core) |
|---|---|---|
| CURRTYPE | Currency | curr_id; curr_short_name, curr_symbol, decimal_symbol, digit_group_symbol, base_exch_rate |
| PROJECT | Project | proj_id; clndr_id, acct_id, location_id, orig_proj_id, sum_base_proj_id; proj_short_name, plan_start_date, plan_end_date, scd_end_date, last_recalc_date (data date), next_data_date, critical_drtn_hr_cnt, critical_path_type, def_duration_type, def_task_type, task_code_prefix/base/step, guid, export_flag, baselines_to_export |
| SCHEDOPTIONS | Schedule options | schedoptions_id; proj_id; sched_outer_depend_type, sched_retained_logic, sched_progress_override, sched_float_type, sched_calendar_on_relationship_lag, sched_open_critical_flag, sched_lag_early_start_flag, level_* (leveling), enable_multiple_longest_path_calc, LevelPriorityList |
| CALENDAR | Calendar | clndr_id; proj_id (null for global), base_clndr_id; clndr_name, clndr_type (CA_Base/CA_Project/CA_Rsrc), default_flag, rsrc_private, day/week/month/year_hr_cnt, clndr_data |
| PROJWBS | WBS node | wbs_id; proj_id, parent_wbs_id, obs_id; wbs_short_name, wbs_name, seq_num, proj_node_flag (project root), status_code, est_wt, ev_compute_type, ev_etc_compute_type, orig_cost, guid |
| TASK | Activity | task_id; proj_id, wbs_id, clndr_id, rsrc_id (primary), location_id; task_code, task_name, task_type (TT_Task/TT_Rsrc/TT_LOE/TT_Mile/TT_FinMile/TT_WBS), duration_type (DT_FixedRate/DT_FixedDrtn/DT_FixedQty/DT_FixedDUR2), complete_pct_type (CP_Phys/CP_Drtn/CP_Units), status_code (TK_NotStart/TK_Active/TK_Complete), phys_complete_pct, target/remain_drtn_hr_cnt, total/free_float_hr_cnt, early/late/act/target/restart/reend/rem_late start+end dates, expect_end_date, cstr_type/cstr_date, cstr_type2/cstr_date2, priority_type, float_path, float_path_order, driving_path_flag, suspend/resume_date, external_early_start_date, external_late_end_date |
| TASKPRED | Relationship | task_pred_id; task_id (successor), pred_task_id, proj_id, pred_proj_id; pred_type (PR_FS/PR_FF/PR_SS/PR_SF), lag_hr_cnt, float_path, aref, arls, comments |
| RSRC | Resource | rsrc_id; parent_rsrc_id, clndr_id, role_id, shift_id, curr_id, unit_id, location_id; rsrc_short_name, rsrc_name, rsrc_type (RT_Labor/RT_Equip/RT_Mat), def_qty_per_hr, cost_qty_type, ot_factor, active_flag, guid |
| RSRCRATE | Resource price/units over time | rsrc_rate_id; rsrc_id, shift_period_id; start_date, max_qty_per_hr, cost_per_qty..cost_per_qty5 |
| ROLES / ROLERATE | Role and its rates | role_id; parent_role_id; role_short_name, role_name / role_rate_id; role_id; cost_per_qty..5, start_date, max_qty_per_hr |
| RSRCROLE | Resource-role link | rsrc_role_id; rsrc_id, role_id; skill_level |
| TASKRSRC | Assignment | taskrsrc_id; task_id, proj_id, rsrc_id, role_id, acct_id, curv_id; target/remain/act_reg/act_ot qty and cost, target/remain_qty_per_hr, cost_per_qty, rate_type, cost_per_qty_source_type, target/act/restart/reend/rem_late dates, target_lag_drtn_hr_cnt, relag_drtn_hr_cnt, guid |
| RSRCCURVDATA | Resource curve | curv_id; curv_name, default_flag, pct_usage_0..pct_usage_20 (21 points) |
| ACCOUNT | Cost account | acct_id; parent_acct_id; acct_short_name, acct_name, acct_seq_num |
| COSTTYPE | Expense category | cost_type_id; cost_type, seq_num |
| PROJCOST | Expense item | cost_item_id; proj_id, task_id, acct_id, cost_type_id; cost_name, target_cost, act_cost, remain_cost, cost_per_qty, target_qty (currency-typed), cost_load_type, po_number, vendor_name, auto_compute_act_flag |
| TASKPROC | Activity step | proc_id; task_id, proj_id; seq_num, proc_name, complete_flag, proc_wt, complete_pct |
| ACTVTYPE / ACTVCODE / TASKACTV | Activity code type / value (tree) / assignment | actv_code_type_id; proj_id, wbs_id; actv_code_type_scope (AS_Global/AS_EPS/AS_Project) / actv_code_id; parent_actv_code_id, actv_code_type_id; short_name, actv_code_name, color / (task_id, actv_code_type_id, actv_code_id, proj_id) |
| PCATTYPE / PCATVAL / PROJPCAT | Project codes | proj_catg_type_id / proj_catg_id, parent_proj_catg_id / (proj_id, proj_catg_type_id, proj_catg_id) |
| RCATTYPE / RCATVAL / RSRCRCAT | Resource codes | rsrc_catg_type_id / rsrc_catg_id, parent_rsrc_catg_id / (rsrc_id, rsrc_catg_type_id, rsrc_catg_id) |
| ROLECATTYPE / ROLECATVAL / ROLERCAT | Role codes | role_catg_type_id / role_catg_id / (role_id, role_catg_type_id, role_catg_id) |
| ASGNMNTCATTYPE / ASGNMNTCATVAL / ASGNMNTACAT | Assignment codes | asgnmnt_catg_type_id / asgnmnt_catg_id / (taskrsrc_id, asgnmnt_catg_type_id, asgnmnt_catg_id, proj_id) |
| UDFTYPE / UDFVALUE | UDF definition / value | udf_type_id; table_name (TASK/PROJWBS/RSRC/TASKRSRC/PROJECT), udf_type_name, udf_type_label, logical_data_type (FT_TEXT/FT_MONEY/FT_INT/FT_FLOAT/FT_FLOAT_2_DECIMALS/FT_START_DATE/FT_END_DATE/FT_STATICTYPE, `UdfHelper.java:129-136`) / (udf_type_id, fk_id = row id in table_name, proj_id; udf_date, udf_number, udf_text, udf_code_id) |
| MEMOTYPE / WBSMEMO / TASKMEMO | Notebook topic / WBS note / activity note | memo_type_id; eps/proj/wbs/task_flag / wbs_memo_id; wbs_id, proj_id, memo_type_id; wbs_memo / memo_id; task_id, proj_id; task_memo |
| UMEASURE | Unit of measure | unit_id; unit_abbrev, unit_name |
| SHIFT / SHIFTPER | Shift / shift period | shift_id; shift_name / shift_period_id; shift_id, shift_start_hr_num |
| LOCATION | Location | location_id; location_name, address fields, latitude, longitude |

Writer table order (parents first; `PrimaveraXERFileWriter.java:160-205`): ASGNMNTCATTYPE, COSTTYPE, CURRTYPE, SHIFT, SHIFTPER, LOCATION, MEMOTYPE, PCATTYPE, RCATTYPE, ROLECATTYPE, RSRCCURVDATA, UDFTYPE, UMEASURE, ACCOUNT, ASGNMNTCATVAL, PCATVAL, RCATVAL, ROLECATVAL, ROLES, PROJECT, ROLERATE, ROLERCAT, CALENDAR, PROJPCAT, SCHEDOPTIONS, PROJWBS, RSRC, ACTVTYPE, RSRCRATE, RSRCRCAT, RSRCROLE, TASK, WBSMEMO, ACTVCODE, TASKPROC, PROJCOST, TASKMEMO, TASKPRED, TASKRSRC, ASGNMNTACAT, TASKACTV, UDFVALUE, then `%E`. UDFVALUE rows sorted by (udf_type_id, fk_id) (:540-563). A table with zero rows is not emitted (header is written lazily on the first `%R`, `XerWriter.java:174-181`).

### PMXML structure

Root `APIBusinessObjects` (old files use `BusinessObjects`, renamed on read, `primavera/NamespaceFilter.java:34-41`). Global children (`schema/APIBusinessObjects.java`): Currency, UnitOfMeasure, CostAccount, UDFType, UDFCode, Location, ExpenseCategory, NotebookTopic, OBS, Shift/ShiftPeriod, Calendar, ProjectCodeType/ProjectCode, ResourceCodeType/ResourceCode, RoleCodeType/RoleCode, ResourceCurve, Role/RoleRate, Resource/ResourceRate, ResourceRole, ActivityCodeType/ActivityCode, ResourceAssignmentCodeType/Code, FinancialPeriod, EPS, RiskCategory/RiskMatrix*, FundingSource, Timesheet*, User*, then `Project` and `BaselineProject` (with `OriginalProjectObjectId`, `BaselineTypeObjectId`, `schema/BaselineProjectType.java:893-948`). `Project` children (`schema/ProjectType.java`): Code, UDF, Spread, ProjectResourceSpread, ProjectRoleSpread, Calendar, WBS, ProjectResource, ProjectBudgetChangeLog, WBSMilestone, ProjectNote, ProjectThreshold, ProjectSpendingPlan, ProjectFunding, ActivityCodeType, ActivityCode, Activity, ResourceAssignment, ActivityExpense, ActivityNote, ActivityStep, Relationship, ActivityPeriodActual, ProjectIssue, ResourceAssignmentPeriodActual, Document, ProjectDocument, ScheduleOptions, Risk, ActivityRisk, RiskImpact, RiskResponsePlan, RiskResponseAction, RiskResponseActionImpact. Project also carries Unifier link fields (UnifierProjectName/Number, UnifierScheduleSheetName, UnifierDataMappingName). Enumerations are text (`"Finish to Start"`, `"Start On or Before"`, `RelationTypeHelper.java:97-109`, `ConstraintTypeHelper.java:84-106`).

### MSPDI

JAXB model `mspdi/schema`; read entry points: calendars (base calendars, WeekDays, Exceptions, WorkWeeks; `MSPDIReader.java:410-900`), ExtendedAttributes and OutlineCodes (custom fields, :904, :1947), Resources incl. cost rate tables and availability (:946-1290), Tasks incl. baselines (:1290-1700), PredecessorLink (:1822), Assignments with baselines (:1930-2244).

### IFC4 schedule/cost as exchange format (IfcOpenShell)

| IFC entity | Role | Created by |
|---|---|---|
| IfcWorkPlan > IfcWorkSchedule | project schedule container | `api/sequence/add_work_plan.py`, `add_work_schedule.py` |
| IfcTask (nested via IfcRelNests) | WBS node or activity; Identification, Name, Status, IsMilestone, PredefinedType | `api/sequence/add_task.py`, `edit_task.py` |
| IfcTaskTime | ScheduleStart/Finish/Duration, Actual*, Early*, Late*, TotalFloat, FreeFloat, IsCritical, Completion | `api/sequence/add_task_time.py` |
| IfcRelSequence + IfcLagTime | relationship type START_START/START_FINISH/FINISH_START/FINISH_FINISH + lag | `ifc4d/ifc4d/common.py:428-466`, `api/sequence/assign_lag_time.py` |
| IfcWorkCalendar + IfcWorkTime + IfcRecurrencePattern + IfcTimePeriod | calendar, working week, exceptions | `common.py:126-255` |
| IfcRelAssignsToControl | calendar controls task; cost item controls products | `common.py:338`, `api/cost/assign_cost_item_quantity.py:140` |
| IfcRelAssignsToProduct | task produces product (4D link) | `api/sequence/assign_product.py:83` |
| IfcRelAssignsToProcess | product/resource input to task | `api/sequence/assign_process.py:108` |
| IfcCostSchedule > IfcCostItem (nested) > IfcCostValue (Category, AppliedValue, unit basis) | 5D cost breakdown / schedule of rates | `api/cost/add_cost_schedule.py`, `add_cost_item.py`, `add_cost_value.py` |
| IfcElementQuantity / IfcQuantity* | quantities linked to cost items | `api/cost/assign_cost_item_quantity.py:215-242` |
| Pset `P6_UDF`, `P6_ActivityCodes` | carries P6 UDFs and activity codes (value + description) | `common.py:394-426` |
| IfcConstructionResource subtypes | LABOR/MATERIAL/EQUIPMENT from RT_* | `ifc4d/ifc4d/p6xer2ifc.py:44-50`, `common.py:468-490` |

### COBie 2.4 (ifcfm)

Sheets with key columns (`ifcfm/ifcfm/cobie24.py:1160-1560`): Contact (key Email; from IfcActor), Facility (Name; IfcBuilding), Floor (IfcBuildingStorey), Space (IfcSpace), Zone (IfcZone), Type (`util.fm.get_cobie_types`), Component (instances of types), System (IfcSystem/IfcDistributionSystem), Assembly (IfcRelAggregates/IfcRelNests, IfcMaterialLayerSet), Connection (IfcRelConnectsPorts), Spare (IfcConstructionProductResource), Resource (IfcConstructionEquipmentResource), Job (IfcTask), Document (IfcRelAssociatesDocument), Attribute (property sets), Coordinate. Each category = {keys, headers, colours, sort, get_category_elements, get_element_data}; output via `Writer.write_csv/write_ods/write_xlsx/write_pd` (`ifcfm/ifcfm/__init__.py:160-346`); `Parser.federate(paths)` merges several IFC files (:135).

### Odoo generic spreadsheet import/export

| Table/model | Fields |
|---|---|
| `base_import.mapping` | res_model, column_name, field_name (`addons/base_import/models/base_import.py:109-114`) |
| `base_import.import` (transient) | res_model, file (binary), file_name, file_type (:177-189) |
| `ir.exports` / `ir.exports.line` | name, resource (model), export_fields, export_language_ids (`odoo/addons/base/models/ir_exports.py`) |
| `ir.model.data` (inferred from `load`) | external id (module.name) -> (model, res_id), noupdate |

## Algorithms and logic

**XER read pipeline** (`PrimaveraXERFileReader.readAll`, :133-207)
1. Parse into `Map<table, List<Row>>` for required tables only.
2. `XerContextReader.read` builds shared context in dependency order: currencies, locations, shifts, UoM, expense categories, cost accounts, work contours, notebook topics, UDF definitions, project/resource/role/assignment/activity code definitions, calendars, UDF values, resource codes, resources, resource rates, role codes, roles, role rates (`XerContextReader.java:54-75`).
3. Per `project` row, `XerProjectReader` filters every table by `proj_id`: code assignments, role assignments, project properties + project codes + default currency + schedule options, WBS+tasks (+memos), predecessors, assignments, expenses, steps (`XerProjectReader.java:63-142`).
4. WBS and TASK share one MPXJ task-id space; `ClashMap.addID` renumbers a clashing id to the next free integer and `getID` translates later FKs (`ClashMap.java`, `TableProjectReader.java:237,325,604`).
5. Relationship with one end missing in this project becomes `ExternalRelation` (:626-641); if `linkCrossProjectRelations`, it is resolved across all projects in the file and added to both projects (`PrimaveraXERFileReader.java:163-204`).
6. Assignment with null `rsrc_id` but a `role_id` is an assignment to the role (`TableProjectReader.java:658-663`).
7. Projects with `export_flag` sort first (:161); `read()` returns the first or the one matching `setProjectID`.

**XER write invariants** (`PrimaveraXERFileWriter.write`, :133-223): all ProjectFiles must share one ProjectContext; projects without unique id get temporary ids; if a project has 2+ root summary tasks a temporary single root WBS is inserted (`createValidWbsHierarchy` :1080) and removed afterwards; summary tasks are emitted as PROJWBS, non-summary non-null tasks as TASK (:1151-1164); resources exclude roles and id 0 (:1171-1174).

**PMXML read** (`PrimaveraPMFileReader.java:92-113, 288-345`): sniff `encoding="..."` from the first 512 bytes and decode with a lenient reader that drops invalid chars; strip `&lt;/HTML&gt;&#0;` NUL artefact; JAXB unmarshal through namespace filter; read Projects and BaselineProjects; attach baselines to the project whose ObjectId = `OriginalProjectObjectId`, the project's current baseline at index 0, others after (`populateBaselines` :231-256).
**PMXML write** (`PrimaveraPMFileWriter.java:95-180`): gather projects + baselines, JAXB marshal through an XSLT that drops `xsi:nil` elements (P6 omits them), optional `setWriteBaselines` emits each baseline as `BaselineProject`.

**MSPDI lag** (`MSPDIReader.java:1855-1872`): `LinkLag` is integer tenths of minutes; `LagFormat` code maps to units (3/35 min, 4/36 emin, 5/37 h, 6/38 eh, 7/39/53 d, 8/40 ed, 9/41 w, 10/42 ew, 11/43 mo, 12/44 emo, 19/51 %, 20/52 e%; `mspdi/DatatypeConverter.java:1234-1300`); non-percent lag = convert(lag/10 minutes -> lagUnits) using project minutes-per-day/week; percent lag kept raw. Missing Type = FS. `CrossProject=1` creates an external-task placeholder from `CrossProjectName` (`subproject\\taskUID`) (:1831-1900).

**P6 to IFC4 (`ifc4d/p6xer2ifc.py`, `common.py`)**: parse XER via `xerparser`; skip TT_LOE in the XER path (p6xer2ifc :140-142); WBS tasks created depth-first, siblings ordered by SequenceNumber (`common.py:257-274`); WBS Identification = parent Identification + "." + Code (:286-287); activity IsMilestone = start == finish unless source flags it; LOE -> PredefinedType ATTENDANCE; durations/floats converted hours -> days using calendar HoursPerDay (default 8) (:345-392); IsCritical = TotalFloat <= 0; Completion only if non-zero (IfcPositiveRatioMeasure); relationships deduplicated per (predecessor, successor, type) and lag stored as WORKTIME IfcLagTime using predecessor calendar (:428-466). Status map TK_NotStart/TK_Active/TK_Complete -> "Not Start"/"Progress"/"Completed".
**IFC to PMXML** (`ifc4d/ifc2p6.py`): builds `APIBusinessObjects` with OBS from IfcProject, Calendar per IfcWorkCalendar (fixed 8/40/172/2000 hours), Project per IfcWorkSchedule, WBS per summary IfcTask, Activity per leaf, StandardWorkWeek and HolidayOrExceptions auto-detected from IfcWorkTime.

**5D CSV to IFC** (`ifc5d/ifc5d/csv2ifc.py:161-330`): header row mandatory with Name and Unit; `Index` column = hierarchy depth (1-based; parent = last item at index-1); if `Value` column absent, every non-standard column is a cost category (suffix " Cost" stripped); `RateSchedule`+`RateID` link to schedule of rates; parent with no values and children gets a `*` sum cost value; schedule-of-rates rows get a unit basis from the Unit symbol.

**Odoo spreadsheet import** (`addons/base_import/models/base_import.py`)
1. Read CSV (separator/encoding/quoting options), XLS, XLSX, ODS (:376-670); `parse_preview` returns headers, preview rows, header types (:1081).
2. Column-to-field suggestion per header (:833-982): saved `base_import.mapping` wins (distance -1); exact match on technical name, translated label or English label (distance 0); else fuzzy match restricted to fields whose type fits the detected column type, distance = 1 - difflib ratio (:984-991), accepted if < `FUZZY_MATCH_DISTANCE` 0.2 (:184); `a/b` headers map to sub-fields; duplicates resolved keeping the smallest distance (:1046).
3. `execute_import(fields, columns, options, dryrun)` (:1534-1641): convert + parse dates/floats (locale-tolerant separators :1339-1390), multi-column-to-one-field merge, fallback values, then `model.load()` inside a savepoint that is rolled back when `dryrun`; on success store column->field mappings.
4. `BaseModel.load` (`odoo/orm/models.py:943-1120`): rows -> records (`_extract_records`, `_convert_records`); records with an external id are upserted through `_load_records` (create or write by xml_id; `mode=='update'`); batch create first, on failure retry row by row, collecting messages; stop after >= 10 errors and >= 1 error per 10 rows; any error rolls back the whole load (ids=False).
5. Export: `export_data` requires admin or `base.group_allow_export` (:924-941); `/web/export` produces CSV or XLSX (xlsxwriter, row limit check) with optional grouped output and aggregates (`addons/web/controllers/export.py:58-306`); field paths may carry `@lang` to export translations.

**SDEF** (`sdef/SDEFReader.java:134-172`): fixed-width ASCII; record id = first 4 chars: VOLM, PROJ, CLDR, HOLI, ACTV (Activity ID 10, Description 30, Duration 3, Constraint Date/Type, Calendar Code 1, Hammock, Workers/Day, Responsibility, Work Area, Mod/Claim, Bid Item, Phase, Category, Feature of Work), PRED (Activity ID, Preceding Activity, type, lag 4), UNIT, PROG (actuals, remaining duration, cost, cost to date, stored material, early/late dates, float sign, total float) (`ActivityRecord.java:66-80`, `PrecedenceRecord.java:54-57`, `ProgressRecord.java:102-114`).

## State machines and workflows

- XER parser: HEADER -> (TABLE -> FIELDS -> DATA*)* -> END; tables outside the required set enter a skip state until the next `%T` (`XerFile.java:239-309`).
- OpenProject IFC model conversion: `conversion_status` pending(0) -> processing(1) -> completed(2) | error(3) with `conversion_error_message` (`openproject/modules/bim/app/models/bim/ifc_models/ifc_model.rb`, `app/services/bim/ifc_models/view_converter_service.rb`): IfcConvert -> COLLADA2GLTF -> gltf2xkt + xeokit-metadata; uploading a new IFC deletes the existing XKT.
- Odoo import: preview -> (test = dryrun rollback) -> import; mapping persisted only after a run that produced ids.

## Cross-domain links

- XER/PMXML entities map onto D03 (PROJWBS, TASK, TASKPROC), D04 (TASKPRED, cstr_*), D05 (CALENDAR, SHIFT), D06 (SCHEDOPTIONS, float/critical fields), D07 (RSRC, ROLES, TASKRSRC, RSRCRATE, RSRCCURVDATA), D09 (ACTVTYPE/ACTVCODE, PCAT*, RCAT*, UDFTYPE/UDFVALUE), D10 (BaselineProject, target_* fields), D11 (ev_compute_type), D13 (PROJCOST, COSTTYPE, ACCOUNT), D14 (PMXML Risk*), D15 (EPS, ProjectFunding/SpendingPlan), D01 (OBS, LOCATION, CURRTYPE).
- IFC: IfcTask links to D03/D06, IfcCostItem to D17, IfcRelAssignsToProduct/Control to D31 (assets) and D25 (models as documents); BCF topics to D27/D29.
- COBie to D31 asset handover.
- Odoo import/export applies to any D13/D17/D19/D25 model; gated by D02 permission `base.group_allow_export`.
- Format readers that pull from remote services (OPC, P6 REST, PWA, Planner) are D34.

## Gaps

- XER import options (per-object keep/update/insert/do-not-import, delete activities not in file, "risks carried but not visible"): not implemented by MPXJ (read-only into a fresh ProjectFile). Rebuild needs: match keys per table (proj_short_name, wbs path, task_code, rsrc_short_name, code type+short_name, udf label+table), a per-table action enum, a diff/apply step in one transaction, and pass-through storage for unread tables (RISKTYPE/PROJRISK etc.) so re-export round-trips.
- Any XER table outside the 43-table read set (`PrimaveraXERFileReader.java:369-414`) is discarded at parse time (`XerFile.java:254`); a rebuild needs raw-table preservation for those (names such as financial periods, issues, thresholds, documents, OBS, EPS and risk tables are P6 conventions not present in MPXJ code, inferred).
- UN/CEFACT schedule XML: none. Rebuild needs XSD binding of the UN/CEFACT project schedule message plus mapping from D03/D04/D05; Odoo CII code shows the namespace/qualified-datatype pattern (`addons/account_edi_ubl_cii/models/account_edi_xml_cii_facturx.py:16-18, 459-462`).
- QRA (.plan/.rsk, Safran/Acumen formats): none; PMXML Risk elements exist only as schema classes.
- COBie import and validation rules (required fields per sheet, pick lists): only export exists.
- Configuration packages: no versioned design-package format; would need serialized metadata (BP definitions, data elements, workflows) with external ids and an `update`/`noupdate` merge like Odoo `load`.
- Document register template (D35.09): generic import exists, but supersede/revision semantics on import are absent.
