# D31 Asset and Facilities Management

## Coverage

| Feature id | Feature | Best OSS source | Coverage | Notes |
|---|---|---|---|---|
| D31.01 | Asset manager | ERPNext Asset + Asset Category + Asset Finance Book + Asset Depreciation Schedule | partial | Full asset register (category, location, custodian, cost, in-service date, salvage, status) and depreciation: Straight Line, Double Declining Balance, Written Down Value, Manual, daily pro-rata, shift-based; no sum-of-years-digits; no parent asset (only composite asset / split_from); spec attributes via Odoo equipment Properties |
| D31.02 | Space manager | ERPNext Location (nested tree with area, area_uom, lat/long, geolocation) | partial | Building/level/space hierarchy as a tree with area; no space type/occupancy/department, utilisation, chargeback, or BIM/CAD reference |
| D31.03 | Maintenance management | ERPNext Asset Maintenance (tasks, periodicity, logs, team) + Asset Repair; Odoo maintenance.request (preventive recurrence, MTBF/MTTR); ERPNext Maintenance Schedule/Visit | partial | Time-based PM generating logs/requests, overdue handling, repair cost capitalisation, downtime; no meter readings or meter-threshold triggers |
| D31.04 | Lease management | none | none | No lease, payment schedule, escalation, ASC 842/IFRS 16 model in cloned sources |
| D31.05 | Facility condition assessment | none | none | No condition index, deficiencies, renewal cost or FCI |
| D31.06 | Real estate portfolio | ERPNext Location tree (rollup container only) | none | No property, ownership, valuation model |
| D31.07 | Inventory and parts | ERPNext reorder_item (Item Reorder levels) + Odoo stock.warehouse.orderpoint | full | Reorder point/qty per warehouse with projected qty; Odoo min/max with lead-time horizon and multiples; repair consumes stock items |

## Storage model

### ERPNext assets (`erpnext/erpnext/assets/doctype/`)

| Doctype | Key fields | Relations |
|---|---|---|
| Asset (`asset/asset.json`, submittable, `ACC-ASS-.YYYY.-`) | `asset_name`*, `item_code`*, `asset_category`, `asset_owner` (Company / Supplier / Customer), `company`*, `location`* → Location, `custodian` → Employee, `department`, `cost_center`, `purchase_date`*, `available_for_use_date` (in-service), `disposal_date`, `net_purchase_amount`, `purchase_amount`, `total_asset_cost`, `additional_asset_cost`, `opening_accumulated_depreciation`, `opening_number_of_booked_depreciations`, `is_fully_depreciated`, `calculate_depreciation`, `value_after_depreciation`, `asset_quantity`, `asset_type` (Existing Asset / Composite Asset / Composite Component), `split_from` → Asset, `maintenance_required`, insurance fields (`policy_number`, `insurer`, `insured_value`, `insurance_start_date/end_date`), `status` (Draft, Submitted, Cancelled, Partially Depreciated, Fully Depreciated, Sold, Scrapped, In Maintenance, Out of Order, Issue, Receipt, Capitalized, Work In Progress), `journal_entry_for_scrap`, `purchase_receipt`/`purchase_invoice` | 1:N finance_books; 1:N depreciation schedules (one active per finance book); N:1 category, location |
| Asset Category (name = `asset_category_name`) | `finance_books` (defaults), `accounts` Table(Asset Category Account)*, `enable_cwip_accounting`, `non_depreciable_category` | 1:N Asset |
| Asset Finance Book (child) | `finance_book`, `depreciation_method`* (Straight Line / Double Declining Balance / Written Down Value / Manual), `total_number_of_depreciations`*, `frequency_of_depreciation`* (months), `depreciation_start_date`, `expected_value_after_useful_life` (salvage), `salvage_value_percentage`, `rate_of_depreciation`, `value_after_depreciation`, `daily_prorata_based`, `shift_based`, `total_number_of_booked_depreciations`, `increase_in_asset_life` (months) | |
| Asset Depreciation Schedule (submittable, `ACC-ADS-.YYYY.-`) | `asset`*, `finance_book`, `finance_book_id`, method/rate/number/frequency/salvage copies, `opening_accumulated_depreciation`, `status` (Draft / Active / Cancelled), `notes` | 1:N Depreciation Schedule rows (`schedule_date`*, `depreciation_amount`*, `accumulated_depreciation_amount`, `journal_entry`, `shift` → Asset Shift Factor) |
| Asset Shift Factor | `shift_name`*, `shift_factor`*, `default` | |
| Asset Value Adjustment (submittable) | `asset`*, `finance_book`, `date`*, `current_asset_value`*, `new_asset_value`*, `difference_amount`, `difference_account`*, `journal_entry` | |
| Asset Movement (submittable, `ACC-ASM-{YYYY}-{#####}`) | `purpose`* (Issue / Receipt / Transfer / Transfer and Issue), `transaction_date`*, `reference_doctype/name`, `assets` Table(Asset Movement Item: `asset`*, `source_location`, `target_location`, `from_employee`, `to_employee`) | |
| Location (tree, NestedSet, name = `location_name`) | `parent_location`, `is_group`, `is_container`, `latitude`, `longitude` (fetched from parent), `area` Float, `area_uom` → UOM, `location` Geolocation (GeoJSON), `lft`, `rgt` | self-tree; Asset.location |
| Asset Maintenance (name = asset) | `asset_name`* → Asset, `company`*, `maintenance_team`* → Asset Maintenance Team, `asset_maintenance_tasks`* Table | |
| Asset Maintenance Task (child) | `maintenance_task`*, `maintenance_type` (Preventive Maintenance / Calibration), `maintenance_status`* (Planned / Overdue / Cancelled), `start_date`*, `end_date`, `periodicity`* (Daily, Weekly, Monthly, Quarterly, Half-yearly, Yearly, 2 Yearly, 3 Yearly), `next_due_date`, `last_completion_date`, `assign_to` → User, `certificate_required` | |
| Asset Maintenance Log (submittable, `ACC-AML-.YYYY.-`) | `asset_maintenance`, `task`, `due_date` (← task.next_due_date), `completion_date`, `maintenance_status`* (Planned / Completed / Cancelled / Overdue), `has_certificate`, `certificate_attachement`, `actions_performed` | = PM work order |
| Asset Maintenance Team | `maintenance_team_name`*, `maintenance_manager`, `company`*, `maintenance_team_members`* | |
| Asset Repair (submittable, `ACC-ASR-.YYYY.-`) | `asset`*, `failure_date`*, `completion_date`, `repair_status` (Pending / Completed / Cancelled), `downtime`, `description`, `actions_performed`, `repair_cost`, `invoices` Table(Asset Repair Purchase Invoice), `stock_items` Table(consumed items), `consumed_items_cost`, `total_repair_cost`, `capitalize_repair_cost`, `increase_in_asset_life`, `project`, `cost_center` | = corrective work order |

ERPNext Maintenance module (`erpnext/erpnext/maintenance/doctype/`): Maintenance Schedule Item (`item_code`, `start_date`, `end_date`, `periodicity` Weekly…Yearly/Random, `no_of_visits`, `sales_person`, `serial_no`), Schedule Detail (`scheduled_date`, `actual_date`, `completion_status` Pending/Partially/Fully Completed), Maintenance Visit (`maintenance_type` Scheduled / Unscheduled / Breakdown, `completion_status`, `purposes`) — customer-side AMC servicing.

### Odoo maintenance (`odoo/addons/maintenance/models/maintenance.py`)

- `maintenance.equipment` (`:113`): `name`, `category_id`, `partner_id` (vendor), `partner_ref`, `model`, `serial_no` (unique constraint `:203`), `assign_date`, `cost`, `warranty_date`, `scrap_date`, `owner_user_id`, `technician_user_id`, `maintenance_team_id`, `effective_date`, `expected_mtbf`, computed `mtbf`, `mttr`, `latest_failure_date`, `estimated_next_failure`, `equipment_properties` (Properties typed by category definition, `:151`) — spec attributes.
- `maintenance.equipment.category` (`:23`): `technician_user_id`, `equipment_properties_definition` (PropertiesDefinition), counts.
- `maintenance.request` (`:240`): `name`, `equipment_id`, `category_id`, `user_ids` technicians, `stage_id` → maintenance.stage, `priority` (0–3), `state` (normal=In Progress, changes_requested, approved, done, cancelled; `:294`), `maintenance_type` (corrective / preventive), `schedule_date`, `schedule_end` (default +1 h), `duration` (h), `close_date`, `maintenance_team_id`*, `recurring_maintenance`, `repeat_interval` ≥1, `repeat_unit` (day/week/month/year), `repeat_type` (forever / until), `repeat_until`, `equipment_req_properties`.
- `maintenance.stage` (`:10`): `name`, `sequence`, `fold`, `maintenance_team_ids`; `maintenance.team` (`:505`) with email alias for request intake.

### Inventory

- ERPNext Item Reorder (child of Item: `warehouse`, `warehouse_group`, `warehouse_reorder_level`, `warehouse_reorder_qty`, `material_request_type`) and Bin `projected_qty` (`erpnext/erpnext/stock/reorder_item.py:118,181`).
- Odoo `stock.warehouse.orderpoint` (`odoo/addons/stock/models/stock_orderpoint.py:29-121`): `trigger` (auto/manual), `warehouse_id`, `location_id`, `product_id`, `product_min_qty`, `product_max_qty`, `min_max_based_on`, `daily_demand`, `replenishment_uom_id`, `route_id`, computed `qty_on_hand`, `qty_forecast`, `qty_to_order`, `lead_days`, `lead_horizon_date`, `deadline_date`, `snoozed_until`.

## Algorithms and logic

**Depreciation schedule generation** `erpnext/erpnext/assets/doctype/asset_depreciation_schedule/deppreciation_schedule_controller.py`
- Inputs: finance-book row (method, N periods, frequency months, start date, salvage, rate, pro-rata flags), asset (available-for-use date, net purchase amount, opening accumulated depreciation / booked periods).
- `initialize_variables` (`:125`): `pending = value_after_depreciation`; pending months = N × frequency + increase_in_asset_life − months already booked (`:243`); final count = N − opening booked, +1 if pro-rata (`:139`), extended when asset life increased (`:150`).
- Pro-rata detection (`:177`): days between available-for-use date and the period end preceding the first depreciation date < full period days → `has_pro_rata`; days ≤ 0 is an error.
- Loop (`create` `:49`) for each period: compute schedule date; keep already-booked rows; amount by method:
  - Straight Line / Manual (`depreciation_methods.py:16`): `depreciable = value_after_depreciation − salvage`; fixed = `depreciable / (pending_months / frequency)` (`:29`); daily pro-rata: daily = depreciable / pending days (or per-year / days in fiscal year) × days in period (`:33-45`); shift-based: `depreciable / Σ shift factors of unbooked rows × this row's shift factor` (`:47`).
  - WDV / DDB (`depreciation_methods.py:82-120`): at each fiscal-year change, `yearly = pending × rate / 100`; period amount = `yearly × frequency / 12` (constant within the fiscal year); daily variant = yearly / days in year × period days.
  - DDB rate `= 200 / (N × frequency / 12)` (`erpnext/erpnext/assets/doctype/asset/asset.py:1081`); WDV rate (when salvage given) `= 100 × (1 − (salvage / current_value)^(1 / pending_years))`, pending_years = (pending periods × frequency + life increase)/12 (`asset.py:1094-1119`).
  - First row: pro-rata amount = full amount × days / period days from available-for-use date (`set_depreciation_amount_for_first_row` `:400`, `_get_pro_rata_amt` `:237`); last row with pro-rata: remainder period to `available_for_use_date + N×frequency` months (`:424`).
  - Disposal date reached → partial amount and stop (`:379`).
  - Salvage adjustment (`:446`): on last row or when pending would drop below salvage, `amount += pending − salvage` and stop.
  - Rows with amount 0 stop; tiny assets that would produce zero first-row amount raise an error (`:462`).
- `set_accumulated_depreciation` (`:493`): running sum from opening accumulated depreciation.
- Posting (`erpnext/erpnext/assets/doctype/asset/depreciation.py:46,81`): daily job selects schedule rows with no journal entry and `schedule_date ≤ date` for submitted assets in status Submitted/Partially Depreciated, excluding companies' frozen periods; creates depreciation Journal Entries per schedule, commits per asset, logs failures and sets `depr_entry_posting_status = Failed`.

**Asset status** `erpnext/erpnext/assets/doctype/asset/asset.py:808-860`: pending Asset Repair (repair_status Pending, not cancelled) → Out of Order; else draft → Draft (Composite → Work In Progress); submitted → Scrapped if scrap JE, Sold if disposal by sale, else compare default finance book `value_after_depreciation` with salvage: ≤ salvage → Fully Depreciated, < net purchase → Partially Depreciated, else Submitted; cancelled → Cancelled. Daily `update_maintenance_status` (`:1138`): maintenance-required assets → Out of Order (pending repair) / In Maintenance (`has_due_maintenance`: draft log Planned/Overdue with `due_date ≤ today`, `:1153`) / recomputed.

**Preventive maintenance (ERPNext)** `erpnext/erpnext/assets/doctype/asset_maintenance/asset_maintenance.py`
- `calculate_next_due_date(periodicity, start, end, last_completion)` (`:164`): base = last_completion if later than start (or no start); add 1 day / 7 days / 1, 3, 6 months / 1, 2, 3 years; empty if start ≥ end, last completion ≥ end, or result > end.
- `validate` (`:36`): fill `next_due_date` for tasks, reject next_due < start; `set_task_status` (`:72`): next_due < today → Overdue, back to Planned when no longer overdue; assignee must be a team member (`:56`).
- `on_update` → `sync_maintenance_tasks` (`:116`): for each non-cancelled task ensure one open log (Planned/Overdue) exists, created with `due_date = next_due_date` (`update_maintenance_log` `:201`); open draft logs of removed tasks set Cancelled; assignee gets a ToDo dated at next due (`assign_tasks` `:141`).
- Log submit (`asset_maintenance_log.py:69`): status must be Completed or Cancelled; Completed → task `last_completion_date = completion_date`, `next_due_date` recomputed, status Planned (`update_maintenance_task` `:111`); Cancelled → task Cancelled; asset status refreshed (`:130`). Cancel of a completed log reverts task dates only if that log drove the schedule (`:79,94`). Daily job: Planned logs with `due_date < today` → Overdue (`:136`).

**Preventive maintenance (Odoo)** `odoo/addons/maintenance/models/maintenance.py:450`: when a request is written to `state = done` and it is preventive + recurring, copy it with `schedule_date += repeat_interval × repeat_unit`, `schedule_end = schedule_date + duration` (default 1 h), default stage — only if `repeat_type = forever` or new date ≤ `repeat_until`; `close_date = today`. Changing stage without state resets changes_requested/approved → normal (`:452`). Leaving done clears `close_date`.

**Reliability metrics (Odoo)** `maintenance.py:95`: over corrective requests in state done: `MTTR = Σ (close_date − (schedule_date or create_date)) days / n`; `latest_failure_date = max(failure dates)`; `MTBF = (latest_failure − effective_date) days / n`; `estimated_next_failure = latest_failure + MTBF`.

**Repair** `erpnext/erpnext/assets/doctype/asset_repair/asset_repair.py`: `downtime = hours(completion − failure)` rounded 2 (`:268,433`); totals = repair cost from purchase invoices + consumed stock value; on submit with `capitalize_repair_cost`: `total_asset_cost`/`additional_asset_cost` += cost and every finance book `value_after_depreciation` += cost (or asset value if no depreciation), `increase_in_asset_life` extends schedule, depreciation rescheduled (`:216,275`); cancel reverses. Status refresh drives Out of Order.

**AMC visit schedule (ERPNext Maintenance Schedule)** `erpnext/erpnext/maintenance/doctype/maintenance_schedule/maintenance_schedule.py:166`: step = (end − start) days / no_of_visits; each visit date = previous + step, shifted backwards off holidays of the sales person's (or company) holiday list, and forwards if that falls before start; clamp to end date.

**Location / custodian tracking** `erpnext/erpnext/assets/doctype/asset_movement/asset_movement.py`: validation that source location/custodian equal the asset's current values (`:83,107`), source ≠ target; on submit/cancel the asset's location and custodian are recomputed from the latest submitted movement setting each (ordered by transaction_date, name) and an asset activity row is logged (`:134-170`).

**Revaluation** `erpnext/erpnext/assets/doctype/asset_value_adjustment/asset_value_adjustment.py:109,116`: `difference = new − current` (must be non-zero), revaluation Journal Entry, asset/finance book values updated and depreciation rescheduled.

**Reorder** ERPNext `erpnext/erpnext/stock/reorder_item.py:40-75`: per item × warehouse (or warehouse group summing child bins): if `projected_qty ≤ reorder_level`, order qty = max(reorder_qty, reorder_level − projected_qty) → Material Request of configured type grouped by company. Odoo `_get_qty_to_order` (`odoo/addons/stock/models/stock_orderpoint.py:499`): if `qty_forecast < min`: qty = max(min, max) − (virtual_available at lead-horizon date + qty in progress), rounded to replenishment multiples.

## State machines and workflows

- **Asset**: Draft → Submitted → Partially Depreciated → Fully Depreciated; any submitted → Sold | Scrapped (disposal, restorable via `restore_asset` `depreciation.py:466`); ↔ In Maintenance / Out of Order (derived from logs and repairs); → Cancelled.
- **Asset Depreciation Schedule**: Draft → Active (on asset submit, `convert_draft_asset_depr_schedules_into_active` `asset_depreciation_schedule.py:222`) → Cancelled; reschedule creates a new schedule with notes (`reschedule_depreciation` `:242`); only one non-cancelled schedule per asset+finance book (`validate_another_asset_depr_schedule_does_not_exist` `:60`).
- **Maintenance Task**: Planned ⇄ Overdue → Cancelled. **Maintenance Log**: Planned → Overdue (daily) → Completed | Cancelled (submit requires one of these).
- **Asset Repair**: Pending → Completed | Cancelled; Pending drives asset Out of Order.
- **Odoo request**: stage pipeline (configurable, per team) × state normal → changes_requested / approved → done | cancelled; done on recurring preventive spawns next occurrence.

## Cross-domain links

- Accounting domain: depreciation, revaluation, scrap and capitalised repair create Journal Entries against Asset Category accounts and cost centers.
- Procurement/stock: Asset from Purchase Receipt/Invoice; repairs consume stock items and link Purchase Invoices; reorder raises Material Requests.
- D29: handover/commissioning produce assets and initial maintenance plans; Quality Inspection can apply to received equipment.
- D25: certificates (`certificate_attachement`), warranties, O&M manuals as documents.
- HR: custodian Employee, maintenance team Users.
- Projects/cost: Asset Repair `project` and `cost_center` carry costs to projects.

## Gaps

- **Sum-of-years-digits** depreciation: `amount_k = (depreciable × (N − k + 1)) / (N(N+1)/2)` per year, split by frequency; not in ERPNext methods.
- **Parent asset hierarchy**: `parent_asset_id` tree with roll-up of cost and status; ERPNext only has composite capitalization and `split_from`.
- **Meter-based PM**: `meter(asset, unit)`, `meter_reading(value, read_at)`, PM rule `every X units` or threshold → generate work order when `reading − last_trigger_reading ≥ X`.
- **Space manager**: `space(location_id, type, area_gross, area_usable, occupancy, department, bim_guid)`; utilisation = occupied / capacity; chargeback = space area × rate allocated to department cost center.
- **Lease management**: `lease(landlord, tenant, commencement, term, payment frequency, escalation CPI|fixed%, options)`, payment schedule generator, IFRS 16/ASC 842: liability = PV(payments, discount rate), ROU asset = liability + initial direct costs − incentives, amortisation schedule (interest = opening liability × rate/period).
- **Facility condition assessment**: `condition_assessment(asset/space, date, rating)`, `deficiency(cost, priority, year)`; FCI = Σ deferred maintenance cost / current replacement value; renewal forecast by component life cycle.
- **Real estate portfolio**: property, ownership share, valuation history, rollups over the Location tree.
