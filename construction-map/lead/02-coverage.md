# Total NSA Construction Cluster: Operational Activity Coverage

Inputs: [01-company-profile.md](01-company-profile.md), [research/](research/), [../00-feature-inventory.md](../00-feature-inventory.md), [../01-map.md](../01-map.md), [../03-gaps-and-rebuild.md](../03-gaps-and-rebuild.md), [../domains/](../domains/). Source paths are relative to the OSS clone root `/tmp/claude-0/-home-user-ads-dashboard/08bcb800-a6d2-545a-acb3-029a72aa1fba/scratchpad/oss/`. Research date 2026-10-17.

Entity key: **AGC** Total NSA AG Construct (general contractor, 149 staff); **PH** Pro Hart Group (MEP, JV partner, 200 staff); **EUF** Eurofor 2011 (stone quarry, 226 staff); **TNI** Total NSA Invest (gravel and sand pits, 47 staff); **DPS** DPS Beton (ready-mix, possibly asphalt, 25 staff); **TNSA** Total N S A (haulage, equipment rental, aggregates trading, 241 staff); **ALL** = every entity.

Status key: **covered** = OSS code implements the core logic; **partial** = OSS code exists but key logic or Romanian rules are missing; **spec-only** = no OSS logic, rebuild spec exists in 03-gaps-and-rebuild.md (gap register or core gaps #1–#14); **new gap** = outside D01–D36, defined below as D37+. *(est.)* = inference from turnover, staff, fleet and contract lists in the profile; unmarked volumes come from the research files.

## Activity map

### A01 Business development and tendering

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A01.01 | SEAP/SICAP and TED notice monitoring by CPV, county and value; bid/no-bid decision | AGC, PH | 150–300 notices screened/yr, 40–80 bids/yr *(est. from ≈10–15 awards/yr and ≈25–35% win rate)* | D15.01, D15.02; D37.01 | new gap | `erpnext/erpnext/crm/doctype/opportunity/opportunity.json` (pipeline record only) | No OSS ingests SICAP/TED; TED has an open API, SICAP only public pages and data.gov.ro dumps *(inference)* |
| A01.02 | Tender dossier intake: fișa de date, caiet de sarcini, clarifications, erate and deadline changes | AGC | 5–10 clarification rounds per bid *(est.)* | D25.01, D26.04; D37.02 | partial | `mayan-edms/mayan/apps/document_states/models/workflow_models.py` | Deadline recomputation on erată not modelled |
| A01.03 | Qualification evidence: DUAE per member, subcontractor and third-party supporter; similar experience, turnover, key staff, equipment, ISO certificates | AGC, PH | 1 DUAE per participant per bid; 3–9 participants per bid (research: up to 9 in waste tender) | D37.03 | new gap | — (files in D25.01) | Legea 98/2016 art. 193 (DUAE), art. 182–185 (third-party support) |
| A01.04 | Bid pricing: deviz ofertă per obiect from F3 quantities, resource lists (materials, labour, equipment, transport), indirect and profit %, check against estimated value | AGC, PH | 40–80 offers/yr, 200–2,000 items each *(est.)* | D17.11; D39.01, D39.02 | partial | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/util/cost.py` | Romanian norm-based resource explosion (norme de deviz) absent from OSS |
| A01.05 | Abnormally low price justification | AGC | 1–5 per yr *(est.)* | D37.06 | new gap | — | HG 395/2016 art. 210 (price < 80% of estimated value triggers justification) |
| A01.06 | Participation guarantee: issue (SGB or insurance), validity vs offer validity, release | AGC | ≈1 per bid; ≤1% of estimated value | D23.06; D38.01 | partial | `erpnext/erpnext/accounts/doctype/bank_guarantee/bank_guarantee.json` | HG 395/2016 art. 35–38 as amended by HG 336/2023 (verify current numbering) |
| A01.07 | Consortium (asociere) and subcontractor/supporter commitments at bid stage; shares per member | AGC, PH, TNSA | ≈60–80% of listed awards are JVs *(est. from research project tables)* | D01.07; D37.05, D48.04 | partial | `erpnext/erpnext/accounts/doctype/cost_center_allocation` | Recurring partners: Pro Hart, ING Proiect Management, Prenis, Prodial, Terra Building, Geiger |
| A01.08 | Electronic auction rounds and re-pricing | AGC | e.g. Șelimbăr–Roșia road (10 bids, e-auction) | D37.07 | new gap | — | Price must be redistributed to items after auction *(inference)* |
| A01.09 | Award communication, standstill, decision to contest or intervene | AGC | ≈40–80 results/yr *(est.)* | D37.08; D55.01 | new gap | — | Legea 101/2016 |
| A01.10 | Bid analytics: win rate, competitor prices from award notices, estimate vs award | AGC | 3–5 yrs of history | D33.03; D37.09 | partial | `erpnext/erpnext/crm/doctype/opportunity/opportunity.json` | TED award notices list all bidders and values |

### A02 Contract setup and consortia

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A02.01 | Contract register: works or design-build, value excl. VAT, duration, warranty period, penalty clauses, funding source | AGC, PH | 15–25 live contracts *(est.)*, 5–40 M RON each | D19.05, D01.03 | partial | `idempiere/org.adempiere.base/src/org/compiere/model/I_C_Project.java` | General conditions per HG 1/2018 (FIDIC-based red/yellow conditions) |
| A02.02 | JV internal split: share of works per member, leader billing, member-to-leader invoicing, joint account | AGC, PH, TNSA | ≈10–15 live JV contracts *(est.)* | D48.04 | new gap | `erpnext/erpnext/accounts/doctype/cost_center_allocation` (percentage split pattern) | Leader invoices the authority; members invoice through leader or directly per agreement |
| A02.03 | Good-execution guarantee: SGB/insurance or retention account (≥0.5% initial deposit, then successive retentions to target ≤10%) | AGC | 1 per contract; ≈15–25 live | D21.05, D23.04; D38.02 | spec-only | 03 core gap #2 + `erpnext/erpnext/accounts/doctype/tax_withholding_entry/tax_withholding_entry.py` | Legea 98/2016 art. 154 (Legea 208/2022) + HG 395/2016 art. 39–42; top-up when value rises by addendum |
| A02.04 | Advance payment and advance guarantee; recovery per situație | AGC | Some contracts *(inference)* | D21.04; D38.03 | partial | `erpnext/erpnext/accounts/doctype/advance_payment_ledger_entry` | %av is an input of the OUG 64/2022 formula |
| A02.05 | Insurance policies required by contract (CAR, professional liability for design) | AGC | 1–3 per contract | D23.06 | partial | `erpnext/erpnext/buying/doctype/supplier/supplier.json` | Validity tracking only |
| A02.06 | Ordin de începere, contract dates, suspensions, extensions | AGC | 15–25 contracts | D19.04, D05.01 | partial | `erpnext/erpnext/support/doctype/service_level_agreement/service_level_agreement.py` | Suspension stops duration clock and penalty clock |
| A02.07 | Delay penalties (contractual), and penalties owed by the authority for late payment | AGC | Disputed on SCJU contracts (research) | D55.04 | new gap | — | Legea 72/2013 (late-payment interest) |
| A02.08 | Contract budget from deviz general / offer per obiect as CBS | AGC | 1 CBS per contract | D17.03, D09.06 | partial | `erpnext/erpnext/accounts/doctype/budget/budget.py` | CBS must mirror deviz chapters (HG 907/2016) |

### A03 Design-build design management

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A03.01 | Design phase tracking SF/DALI → DTAC → PT → DE, deliverables per phase | AGC | ≈40–60% of contracts are design-build *(est. from research project tables)* | D42.01 | new gap | `mayan-edms/mayan/apps/sequences/managers.py` (register numbering) | HG 907/2016 phase content |
| A03.02 | Design subcontracts (Birou Proiectare Fleschin, RA Instal Proiect, ING Proiect Management, possibly Top Proiect) | AGC | 2–5 designers per D&B contract | D19.01, D19.04; D42.02 | partial | `erpnext/erpnext/buying/doctype/purchase_order` | Guarantee release for design tied to works reception (HG 395) |
| A03.03 | Technical verification of projects by atestat verifiers per fundamental requirement; expertiză tehnică for rehabs and monuments | AGC | 3–8 verifier reports per project *(est.)* | D27.06; D42.03 | new gap | `openproject/modules/bim/db/migrate/tables/bcf_comments.rb` | Legea 10/1995 (verification of projects); Maria Tereza is a historic monument (Ministry of Culture approval) |
| A03.04 | Certificat de urbanism, avize, acord de mediu, autorizație de construire | AGC (D&B), authority | 5–20 avize per project *(est.)* | D42.04, D54.02 | new gap | — | Legea 50/1991 |
| A03.05 | Beneficiary review of PT/DE, comment resolution | AGC | 1–3 review cycles per phase | D27.06, D24.09 | partial | `openproject/modules/bim/db/migrate/tables/bcf_comments.rb` | |
| A03.06 | Dispoziții de șantier from the designer during works | AGC | 10–50 per project *(est.)* | D20.01; D43.06 | spec-only | 03 core gap #4 | Each may trigger NCS (A08.06) |
| A03.07 | BIM/IFC models | AGC | Not observed (profile: no BIM) | D35.07 | covered | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/api/sequence/duplicate_task.py` | Low priority |
| A03.08 | Quantity take-off from PT into F3 quantity lists | AGC | Per D&B project | D17.11; D39.01 | partial | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/util/cost.py` | |

### A04 Planning and scheduling

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A04.01 | Grafic de execuție (works programme) in offer and contract | AGC, PH | 1 per bid and per contract; 50–300 activities *(est.)* | D03, D04, D05, D06 | covered | `mpxj/src/main/java/org/mpxj/cpm/PrimaveraScheduler.java` | |
| A04.02 | Monthly financial programme (eșalonare valorică) aligned to grafic and funding | AGC | Monthly per contract | D07.06, D22.03 | partial | `mpxj/src/main/java/org/mpxj/TimephasedUtility.java` | Must reconcile to deviz chapters |
| A04.03 | Baseline, monthly update, extensions of time via addenda | AGC | 15–25 schedules | D10.01–D10.04 | partial | `mpxj/src/main/java/org/mpxj/primavera/PrimaveraBaselineStrategy.java` | |
| A04.04 | Cross-contract crew and equipment planning incl. group fleet | AGC, TNSA | ≈170 major units, ≈350 site staff | D07, D08 | spec-only | 03 core gap #10 | |
| A04.05 | Weekly look-ahead | AGC | Weekly per site | D16.01–D16.04 | partial | `openproject/db/migrate/tables/work_packages.rb` | |
| A04.06 | Seasonal constraints: concreting below +5 °C, asphalt season, winter suspension | AGC, DPS | Nov–Mar each year | D05.03; D43.01 | partial | `mpxj/src/main/java/org/mpxj/primavera/TableProjectReader.java` | Weather-dependent calendars not modelled; cold-weather measures per NE 012/2 |
| A04.07 | Delay analysis / TIA for time claims | AGC | SCJU contracts delayed (research) | D06.12, D20.06 | spec-only | 03 core gap #14 | |

### A05 Estimating and bill of quantities

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A05.01 | Norm and resource catalogue: norme de deviz codes, consumption per unit, resource prices (materials, labour, equipment, transport) | AGC, PH | 5,000–20,000 norm lines, 2,000–5,000 resources *(est.)* | D39.01 | new gap | `erpnext/erpnext/manufacturing/doctype/bom` (explosion pattern) | Romanian norm system; licensing of the norm data to check |
| A05.02 | Deviz pe categorii de lucrări (F3) exploded to resource lists | AGC, PH | Per bid and per NCS | D39.02 | new gap | `odoo/addons/mrp/models/mrp_bom.py` | Ordin 863/2008 F1–F5 forms; offer resource lists (practice) |
| A05.03 | Deviz general (chapters 1–6) and deviz pe obiect | AGC (D&B), authority | Per D&B project | D39.03 | new gap | `idempiere/org.adempiere.base/src/org/compiere/model/I_C_ProjectPhase.java` | HG 907/2016 (deviz general structure) |
| A05.04 | Internal cost estimate vs offer price; target margin | AGC | Per contract | D17.03, D17.06 | partial | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java` | |
| A05.05 | Group product prices (aggregates, concrete, haulage, equipment hire) fed into estimates | AGC ← EUF, TNI, DPS, TNSA | Every bid | D48.01; D39.01 | new gap | `erpnext/erpnext/accounts/doctype/pricing_rule` | Must equal transfer-pricing policy (A18.02) |
| A05.06 | Estimate versions and comparisons | AGC | 2–5 versions per bid *(est.)* | D17.08, D17.09 | partial | `ifcopenshell/src/ifcopenshell-python/ifcopenshell/util/cost.py` | |

### A06 Cost control and forecasting

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A06.01 | Cost per contract / obiect / categorie de lucrări | AGC, PH | 15–25 contracts × 5–30 obiecte | D17.01, D09.06 | partial | `odoo/addons/analytic/models/analytic_plan.py` | |
| A06.02 | Actuals from accounting, payroll and internal fleet charges | AGC | Monthly | D17.12 | covered | `erpnext/erpnext/accounts/doctype/accounting_dimension/accounting_dimension.py` | Internal charges depend on A15.05 |
| A06.03 | Committed cost (subcontracts, POs) | AGC | 80–150 live subcontracts *(est.)* | D19.01, D19.02 | partial | `erpnext/erpnext/controllers/status_updater.py` | |
| A06.04 | Forecast at completion incl. expected price adjustment and unpriced NCS | AGC | Monthly per contract | D17.06, D11.03; D40.02 | partial | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java` | 2025 margin fell to 1.9% (profile) |
| A06.05 | Certified value vs cost vs plan (EV) | AGC | Monthly | D11.01–D11.05 | partial | `libreplan/libreplan-business/src/main/java/org/libreplan/business/planner/entities/OrderEarnedValueCalculator.java` | Earned = cumulative situații |
| A06.06 | Overhead allocation (site setup, HQ) | AGC | Monthly | D13.02, D32.03 | partial | `erpnext/erpnext/accounts/doctype/cost_center/cost_center.json` | |
| A06.07 | Contract cash flow incl. authority payment terms and funding lags | AGC | Monthly | D22.01–D22.07 | partial | `erpnext/erpnext/accounts/doctype/payment_schedule/payment_schedule.json` | Linked to A22.03 |

### A07 Progress measurement and billing (situații de lucrări)

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A07.01 | Measurement of executed quantities (foi de atașament, măsurători) per item, confirmed by diriginte de șantier | AGC, PH | 200–300 situații/yr *(est.: 15–25 contracts × 12)*, 50–500 lines each | D28.02; D39.04 | partial | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/workreports/entities/WorkReports.hbm.xml` | |
| A07.02 | Situație de lucrări: quantity × offer unit price, period and cumulative, per obiect | AGC, PH | As above | D21.01, D21.02; D39.04 | spec-only | 03 core gap #1 + `erpnext/erpnext/controllers/status_updater.py` | Must cap cumulative quantity at contract quantity unless NCS exists |
| A07.03 | Centralizator, deductions (advance recovery, GBE retention), diriginte certification, beneficiary approval | AGC | As above | D21.05, D23.04; D38.02, D39.05 | spec-only | 03 core gaps #1, #2 | |
| A07.04 | Invoice to the authority via e-Factura after acceptance of the situație | AGC, PH | 200–300/yr | D21.03; D49.01 | partial | `odoo/addons/account_edi_ubl_cii/models/account_edi_ubl_cen_en16931.py` | B2G e-Factura mandatory (Legea 139/2022); RO_CIUS absent from clone |
| A07.05 | Collection, late-payment interest | AGC | 200–300/yr | D21.04 | covered | `erpnext/erpnext/accounts/doctype/payment_entry`, `erpnext/erpnext/accounts/doctype/dunning` | Legea 72/2013 rate rules not configured |
| A07.06 | Hidden works (PV lucrări ascunse) gating billing of covered items | AGC | 20–100 PVs per contract *(est.)* | D43.03 | new gap | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/qualityforms/entities/QualityForms.hbm.xml` | |
| A07.07 | Final account (situație finală) and value reconciliation at reception | AGC | 5–10 closeouts/yr *(est.)* | D39.06 | new gap | — | Input to OUG 64 art. 11(6) final value addendum |

### A08 Price adjustment and addenda

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A08.01 | INS index ingestion: ICC total and materials (Buletin Statistic de Prețuri tab. 15/15A), forecast ICC (CNSP), IPC, IVUI; provisional vs final | AGC | Monthly series | D40.01 | new gap | — | OUG 64/2022 art. 17(4)–(8) |
| A08.02 | Adjustment per payment request (Vapl formula) and recalculation when indices become final | AGC, PH | Every situație on adjusted contracts | D40.02 | new gap | — | Addenda +15–70% on their contracts (profile) |
| A08.03 | Rest-de-executat baseline at addendum date (quantity, value, materials share) | AGC | 1 per adjusted contract | D40.03 | new gap | — | OUG 64/2022 art. 10, 17(9) |
| A08.04 | Contract adjustment clauses for national/local-budget contracts | AGC | Contracts outside EU funding | D40.04 | new gap | — | Legea 98/2016 art. 221(1)(a); HG 395/2016 art. 164 |
| A08.05 | Addenda register (acte adiționale) with cumulative-change limits | AGC | 2–15 addenda per contract (AA13/AA15 on SCJU) | D20.04; D40.05 | partial | `erpnext/erpnext/accounts/services/child_item_update.py` | Legea 98/2016 art. 221 limits; OUG 64 art. 8 50% cap |
| A08.06 | Note de comandă suplimentară / de renunțare / de modificare | AGC | 5–40 per contract *(est.)* | D20.01–D20.04; D40.06 | spec-only | 03 core gap #4 | Reference month for adjustment differs for NCS with/without offer equivalent |
| A08.07 | New unit prices for extra works from offer resource prices | AGC | Per NCS without offer equivalent | D39.02; D40.06 | new gap | `odoo/addons/mrp/models/mrp_bom.py` | |
| A08.08 | Duration addenda (extension of time) | AGC | 1–5 per contract | D20.06 | spec-only | 03 core gap #14 | |

### A09 Subcontractor management

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A09.01 | Subcontractor declaration (offer and execution), replacement and new-subcontractor approval | AGC | 3–8 subs per contract (research) | D41.01 | new gap | — | Legea 98/2016 art. 218–220; HG 395/2016 art. 151 |
| A09.02 | Subcontract register back-to-back with main-contract items | AGC | 80–150 live *(est.)* | D19.01, D19.04 | partial | `erpnext/erpnext/buying/doctype/purchase_order` | |
| A09.03 | Subcontractor situații and invoices | AGC | 800–1,500/yr *(est.)* | D23.03; D39.04 | spec-only | 03 core gap #1 | |
| A09.04 | Direct payment of subcontractors by the authority; contractor confirmation | AGC | On request | D41.03 | new gap | — | Legea 98/2016 subcontracting chapter (direct payment) |
| A09.05 | Retention from subcontractors | AGC | Per subcontract | D23.04 | spec-only | 03 core gap #2 | |
| A09.06 | Subcontractor compliance documents (ISC lab authorisation, ANRE for electrical, SSM, insurance) | AGC | Per subcontractor | D23.06 | partial | `erpnext/erpnext/buying/doctype/supplier/supplier.json` | |
| A09.07 | Reverse-charge VAT on construction services received and supplied | AGC, PH | Most B2B construction invoices | D49.04 | partial | `odoo/addons/account/models/account_tax.py` | Cod fiscal art. 331(2)(i); confirm validity after 31.12.2026 |
| A09.08 | Subcontractor performance scoring | AGC | Per subcontractor | D23.06 | partial | `erpnext/erpnext/buying/doctype/supplier_scorecard` | |

### A10 Procurement and materials

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A10.01 | Material requests, POs, framework agreements | AGC, PH | 3,000–8,000 PO lines/yr *(est.)* | D19.03 | covered | `erpnext/erpnext/stock/doctype/material_request` | |
| A10.02 | RFQ and supplier quotation comparison | AGC | 200–500 RFQs/yr *(est.)* | D19.07 | covered | `erpnext/erpnext/buying/doctype/request_for_quotation` | |
| A10.03 | Receipt on site: aviz de însoțire, NIR | AGC, PH | 5,000–15,000/yr *(est.)* | D19.03, D31.07 | partial | `erpnext/erpnext/stock/doctype/purchase_receipt` | OMFP 2634/2015 document forms |
| A10.04 | Material conformity at receipt: DoP, CE marking, certificat de conformitate, agrément tehnic | AGC, PH | Per product batch | D44.05 | new gap | `erpnext/erpnext/stock/doctype/quality_inspection/quality_inspection.py` | Reg. (UE) 305/2011; Legea 10/1995 (only certified products) |
| A10.05 | Site stores, bonuri de consum per contract, stock counts | AGC | 15–25 site stores | D31.07 | covered | `erpnext/erpnext/stock/doctype/stock_entry`, `erpnext/erpnext/stock/doctype/stock_reconciliation` | |
| A10.06 | Materials share per situație (Vm) for adjustment | AGC | Every situație | D40.03 | new gap | — | OUG 64/2022 art. 17(9) |
| A10.07 | Inbound e-Factura (SPV download) and 3-way match | ALL | 10,000–30,000 invoices/yr across cluster *(est.)* | D21.03; D49.02 | partial | `odoo/addons/account_edi_ubl_cii/models/account_edi_ubl.py` | |

### A11 Site operations (daily reports, labour, plant)

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A11.01 | Daily site report: weather, workforce, equipment, works, events | AGC, PH | 15–25 sites × 250 days ≈ 4,000–6,000/yr *(est.)* | D28.01 | partial | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/workreports/entities/WorkReports.hbm.xml` | |
| A11.02 | Attendance (condică) and crew time per site | AGC, PH | ≈350 workers | D28.07, D32.01–D32.04 | covered | `erpnext/erpnext/projects/doctype/timesheet/timesheet.py` | |
| A11.03 | Equipment hours per site (foaie de parcurs / foaie de lucru utilaj) | AGC, TNSA | ≈170 units × 250 days *(est.)* | D47.02 | partial | `odoo/addons/fleet/models/fleet_vehicle_odometer.py`, `hrms/hrms/hr/doctype/vehicle_log` | Internal charge-out missing |
| A11.04 | Delivery reconciliation: concrete tickets and aggregate weighbridge tickets vs designed quantities | AGC ← DPS, EUF, TNI | 10,000–20,000 tickets/yr *(est.)* | D45.04, D46.05 | new gap | `erpnext/erpnext/stock/doctype/delivery_note` | |
| A11.05 | Site registers: jurnal de șantier, condica de betoane, registers of PVs | AGC | 15–25 sites | D43.07 | new gap | — | Feed cartea tehnică |
| A11.06 | Photos and media | AGC | 50–200 per site per month *(est.)* | D28.03 | partial | `mayan-edms/mayan/apps/file_metadata/models.py` | |
| A11.07 | Site issues and instructions | AGC | | D28.04; D43.06 | partial | `openproject/db/migrate/tables/work_packages.rb` | |
| A11.08 | Site setup (organizare de șantier) cost and dismantling | AGC | Per contract | D17.01 | partial | `idempiere/org.adempiere.base/src/org/compiere/model/I_C_ProjectLine.java` | Deviz general chapter 5.1 |

### A12 Quality (control program, faze determinante, lab, reception, cartea tehnică)

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A12.01 | Program de control al calității per contract with faze determinante agreed with designer and ISC | AGC | 1 per contract; 5–30 phases | D29.02; D43.01 | new gap | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/qualityforms/entities/QualityForms.hbm.xml` | Legea 10/1995; Ordin 1370/2014 (PCF 002) |
| A12.02 | Faze determinante: convocation of ISC, designer, diriginte; PV fază determinantă as stop point | AGC | 100–400/yr *(est.)* | D43.02 | new gap | — | Successor works blocked until PV signed |
| A12.03 | PV lucrări ascunse, PV de trasare, PV predare-primire amplasament, PV recepție calitativă | AGC, PH | 1,000–3,000/yr *(est.)* | D28.05; D43.03 | partial | `erpnext/erpnext/stock/doctype/quality_inspection/quality_inspection.py` | |
| A12.04 | Laboratory tests on site and at plant (concrete, soils compaction, asphalt, aggregates) | DPS lab grade II, AGC | 500–2,000 test reports/yr *(est.)* | D29.02; D44.01–D44.04 | partial | `erpnext/erpnext/stock/services/quality_inspection_service.py` | Lab authorised by ISC |
| A12.05 | Non-conformities and remediation | AGC | 20–100/yr *(est.)* | D29.03 | partial | `erpnext/erpnext/quality_management/doctype/non_conformance` | |
| A12.06 | RTE and diriginte appointments, authorisation validity per specialty | AGC | ≈5–15 RTE *(est.)* | D43.05 | new gap | — | Legea 10/1995 (executant must employ RTE) |
| A12.07 | Reception at completion and final reception: notification, commission, PV with objections, remedy deadlines | AGC | 5–15 receptions/yr *(est.)* | D29.04; D43.08 | new gap | `libreplan/libreplan-business/src/main/resources/org/libreplan/business/qualityforms/entities/QualityForms.hbm.xml` | HG 343/2017; GBE 70% release depends on it |
| A12.08 | Cartea tehnică assembly (execution documents, certificates, PVs, as-built, dispoziții) | AGC | 1 per construction | D25.09; D43.09 | partial | `openproject/app/models/backup.rb`, `mayan-edms/mayan/apps/cabinets/models.py` | HG 273/1994 annex (verify still in force after HG 343/2017) |
| A12.09 | ISC quotas (0.5% Legea 10/1995 art. 40, 0.1% Legea 50/1991 art. 30) and CSC 0.5% (Legea 215/1997): declaration and regularisation at reception | Authority pays; AGC supplies values *(inference)* | Per contract | D43.10 | new gap | — | 50% at start notification, rest by reception |
| A12.10 | ISO 9001/14001/45001 records | AGC | Annual audits | D29.05 | partial | `erpnext/erpnext/quality_management/doctype/quality_procedure` | |
| A12.11 | Warranty-period defects and final reception | AGC | 20–60 contracts in warranty *(est.)* | D29.01; D43.11 | partial | `odoo/addons/project/report/project_task_burndown_chart_report.py` | Warranty 36 months typical (research: ULBS dorm) |

### A13 Health and safety

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A13.01 | Plan de securitate și sănătate, safety coordinator, registru/jurnal de coordonare | AGC | Per site | D51.01 | new gap | — | HG 300/2006 |
| A13.02 | Declarație prealabilă to ITM (>30 working days and >20 workers simultaneously, or >500 man-days) | Beneficiary/AGC | Most sites | D51.02 | new gap | — | HG 300/2006 annex 3 |
| A13.03 | SSM training (introductiv-generală, at workplace, periodic), fișe individuale | ALL | ≈650 people | D30.03 | partial | `hrms/hrms/hr/doctype/training_event/training_event.py` | Legea 319/2006; HG 1425/2006 |
| A13.04 | Accident and incident communication to ITM, investigation, registers | ALL | | D30.02 | spec-only | 03 core gap #12 | Legea 319/2006 (communication and investigation) |
| A13.05 | PPE issue | ALL | ≈650 people | D31.07 | partial | `erpnext/erpnext/stock/doctype/stock_entry` | |
| A13.06 | Permits to work (height, hot work, excavation, lifting) and inspections | AGC, EUF | | D30.04 | spec-only | 03 core gap #12 | |
| A13.07 | Medical fitness (medicina muncii) validity | ALL | ≈650 people | D50.05 | new gap | — | HG 355/2007 |
| A13.08 | Fire prevention (PSI/ISU) on sites and plants | ALL | | D51.05 | new gap | — | Legea 307/2006 |

### A14 Environment and waste

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A14.01 | C&D waste: management plan, sorting, transfer to authorised operators, monthly records by waste code (chapter 17) | AGC | 15–25 sites; rehab and demolition heavy | D52.01 | new gap | — | OUG 92/2021; HG 856/2002 annex 1 |
| A14.02 | Annual waste reporting to APM; Fondul pentru mediu declarations | ALL | Monthly/annual | D52.02 | new gap | — | OUG 196/2005 |
| A14.03 | Environmental permits and water permits for quarries, pits and plants; monitoring | EUF, TNI, DPS | 3–6 sites | D52.03 | new gap | — | |
| A14.04 | Excavated soil balance and reuse; haul to deposits | AGC, TNSA | Roads and networks | D52.04 | new gap | — | |
| A14.05 | Environmental incidents | ALL | | D30.02 | spec-only | 03 core gap #12 | |

### A15 Equipment and fleet

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A15.01 | Fleet and plant register with owning entity | TNSA, AGC, EUF, DPS | 80–100 tippers, 40 8x4 trucks, 20 excavators, 5 dozers, 13 loaders, 4 backhoes, 7 mixers, 3 pumps (research) | D31.01; D47.01 | partial | `odoo/addons/fleet/models/fleet_vehicle.py`, `erpnext/erpnext/assets/doctype/asset` | |
| A15.02 | Hours/km, fuel issue, consumption norms, anomaly detection | TNSA, AGC, EUF | ≈170 units; 1–3 M l diesel/yr *(est.)* | D47.02, D47.03 | partial | `odoo/addons/fleet/models/fleet_vehicle_odometer.py`, `hrms/hrms/hr/doctype/vehicle_log` | |
| A15.03 | Preventive maintenance by hours/km, repairs, parts | TNSA, EUF | ≈170 units | D31.03 | partial | `erpnext/erpnext/assets/doctype/asset_maintenance_task/asset_maintenance_task.json`, `odoo/addons/maintenance/models/maintenance.py` | ERPNext periodicity is calendar-only; meter-based triggers missing |
| A15.04 | Regulated inspections: RAR ITP, tachograph, ISCIR cranes/lifting (VTP), RCA, rovinietă, ARR licence copies | TNSA, AGC | ≈170 units × 3–6 obligations | D47.04 | new gap | — | Legea 64/2008 (ISCIR); OG 27/2011 (road transport); OG 15/2002 (rovinietă); Reg. (UE) 165/2014 |
| A15.05 | Allocation and dispatch between sites and group companies; internal hire rates | TNSA → AGC, EUF | Daily | D47.05, D48.02 | new gap | — | Drives intra-group invoicing |
| A15.06 | Equipment cost per hour for estimates and charge-out | TNSA, AGC | ≈30 equipment classes | D47.06; D39.01 | new gap | `erpnext/erpnext/manufacturing/doctype/workstation` (hour-rate pattern) | |
| A15.07 | Telematics/GPS and fuel-card import | TNSA | ≈170 units | D47.07; D34.13 | new gap | — | |
| A15.08 | Depreciation (accounting and fiscal useful lives) | ALL | | D31.01 | partial | `erpnext/erpnext/assets/doctype/asset/depreciation.py` | HG 2139/2004 catalogue |

### A16 Quarry and aggregates production

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A16.01 | Mining licences/permits, perimeters, validity, annual work programmes | EUF, TNI | 3–6 perimeters (Săliște, Balomiru de Câmp, Orlat, Beldiu) | D46.01 | new gap | — | Legea 85/2003 |
| A16.02 | Extraction, crushing and screening into fractions (0/4, 4/8, 8/16, 16/31.5, criblură, ballast) | EUF, TNI | EUF 1.5–2.5 Mt/yr, TNI 0.3–0.6 Mt/yr *(est. from turnover at 40–70 RON/t)* | D46.02 | partial | `erpnext/erpnext/manufacturing/doctype/bom_secondary_item`, `erpnext/erpnext/manufacturing/doctype/work_order` | Co-product yield split |
| A16.03 | Weighbridge tickets, dispatch, aviz de însoțire, e-Transport UIT | EUF, TNI, TNSA | 60,000–120,000 loads/yr *(est.)* | D46.05; D49.03 | new gap | `erpnext/erpnext/stock/doctype/delivery_note` | NC 2505/2517 are high-fiscal-risk goods (OPANAF 802/2022) |
| A16.04 | Stockpile inventory by fraction with survey reconciliation | EUF, TNI | Monthly | D46.04 | partial | `erpnext/erpnext/stock/doctype/stock_reconciliation` | |
| A16.05 | Royalty (redevență minieră) and mining activity tax: computation, quarterly payment, declarations | EUF, TNI | Quarterly | D46.06 | new gap | — | Legea 85/2003 art. 45–47 (€0.50 per unit for sand and gravel in consolidated text; verify rate for crushed rock) |
| A16.06 | Production reporting to the mining authority and INS | EUF, TNI | Quarterly/annual | D46.07 | new gap | — | Legea 85/2003 art. 46 |
| A16.07 | Product conformity: SR EN 12620 / 13242 / 13043, FPC, DoP, CE marking | EUF, TNI | Per product and FPC audit | D46.08 | new gap | `erpnext/erpnext/stock/doctype/quality_inspection_template` | Reg. (UE) 305/2011 |
| A16.08 | Environmental rehabilitation guarantee and closure plan | EUF, TNI | Per perimeter | D46.09 | new gap | — | Legea 85/2003 |
| A16.09 | Explosives and blasting records | EUF | Weekly *(inference: hard rock)* | D46.10 | new gap | — | Legea 126/1995 |

### A17 Concrete plant production and dispatch

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A17.01 | Mix designs by strength class, exposure, consistency, Dmax, with material sources | DPS | 30–80 active recipes *(est.)* | D45.01 | partial | `odoo/addons/mrp/models/mrp_bom.py`, `erpnext/erpnext/manufacturing/doctype/bom` | SR EN 206+A2; NE 012/1 |
| A17.02 | Order intake, pour scheduling, truck-mixer rotation, pump allocation | DPS | 60,000–75,000 m³/yr *(est. from 34.2 M RON at 450–550 RON/m³)*; 7 mixers, 3 pumps | D45.02 | new gap | `erpnext/erpnext/stock/doctype/delivery_trip` | Plant 60–80 m³/h |
| A17.03 | Batch records from plant controller (weights, w/c, admixtures, tolerances) | DPS | 7,000–9,000 loads/yr *(est.)* | D45.03 | partial | `erpnext/erpnext/manufacturing/doctype/work_order` | Controller integration absent |
| A17.04 | Delivery ticket per load with mandatory SR EN 206 content | DPS | 7,000–9,000/yr *(est.)* | D45.04 | partial | `erpnext/erpnext/stock/doctype/delivery_note` | |
| A17.05 | Conformity control of production (strength families, criteria) and FPC certification | DPS | Continuous | D44.03 | new gap | — | SR EN 206+A2 clause 8–9 |
| A17.06 | Fresh and hardened concrete tests (SR EN 12350-2/-6/-7, SR EN 12390-3/-8) | DPS lab | 300–1,000 sample sets/yr *(est.)* | D44.02 | partial | `erpnext/erpnext/stock/doctype/quality_inspection/quality_inspection.py` | |
| A17.07 | Pump services and billing (hours, m³) | DPS | 3 pumps | D45.05 | new gap | — | |
| A17.08 | Cement/aggregate/admixture consumption reconciliation | DPS ← EUF, TNI | Monthly | D45.06 | partial | `erpnext/erpnext/stock/doctype/stock_ledger_entry` | |
| A17.09 | Asphalt production (if DPS runs an asphalt plant) | DPS *(inference from registry heading)* | Unknown | D45.07 | new gap | — | SR EN 13108 series |

### A18 Intra-group transfers

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A18.01 | Inter-company sales: aggregates EUF/TNI → DPS/AGC, concrete DPS → AGC, haulage and rental TNSA → all, MEP PH ↔ AGC | ALL | Several thousand invoices/yr *(est.)* | D01.07; D48.01 | partial | `erpnext/erpnext/accounts/doctype/sales_invoice/mapper.py:168`, `erpnext/erpnext/stock/doctype/delivery_note/mapper.py:427` | Mirror purchase invoice exists; pricing policy does not |
| A18.02 | Transfer-pricing policy and file | ALL | Annual | D48.03 | new gap | — | Cod fiscal art. 11; OPANAF 442/2016 |
| A18.03 | Group management consolidation with eliminations | ALL | Monthly | D48.05 | new gap | — | |
| A18.04 | JV accounting between members | AGC, PH, TNSA | 10–15 JVs *(est.)* | D48.04 | new gap | — | |
| A18.05 | Shared-service recharges | ALL | Monthly | D48.06 | partial | `erpnext/erpnext/accounts/doctype/cost_center_allocation` | |
| A18.06 | Inter-company reconciliation and netting | ALL | Monthly | D48.07 | new gap | `erpnext/erpnext/accounts/doctype/payment_reconciliation` | |

### A19 Finance, accounting, fiscal compliance

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A19.01 | General ledger per Romanian chart of accounts per entity | ALL | 6 entities | D49.06 | partial | `odoo/addons/account/models/account_move.py` | OMFP 1802/2014; no l10n_ro in clone |
| A19.02 | e-Factura issue and receipt (RO_CIUS UBL), SPV status polling | ALL | 20,000–50,000 invoices/yr *(est.)* | D35.04; D49.01, D49.02 | partial | `odoo/addons/account_edi_ubl_cii/models/account_edi_ubl_cen_en16931.py` | OUG 120/2021; Legea 296/2023 |
| A19.03 | SAF-T D406 (monthly/quarterly; assets annual; stocks on request) | ALL | 6 entities | D49.05 | new gap | — | OPANAF 1783/2021 |
| A19.04 | e-Transport UIT for high-risk goods | EUF, TNI, TNSA, DPS | 60,000–120,000/yr *(est.)* | D49.03 | new gap | — | OUG 41/2022; OPANAF 802/2022 |
| A19.05 | VAT: D300, D394, reverse charge on construction | ALL | Monthly | D49.04 | partial | `odoo/addons/account/models/account_tax.py` | Cod fiscal art. 331(2)(i) |
| A19.06 | Treasury, guarantee lines, bank letters | ALL | | D21.04; D38 | partial | `erpnext/erpnext/accounts/doctype/payment_order` | |
| A19.07 | Fixed assets | ALL | ≈200+ major assets | D31.01 | partial | `erpnext/erpnext/assets/doctype/asset/depreciation.py` | |
| A19.08 | Receivables from public authorities, Legea 72/2013 interest | AGC, PH | | D21.04 | partial | `erpnext/erpnext/accounts/doctype/dunning` | |
| A19.09 | Annual financial statements and filings | ALL | Annual | D49.07 | partial | `erpnext/erpnext/accounts/doctype/period_closing_voucher` | |

### A20 HR and payroll

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A20.01 | Employee records, employment contracts, REGES-ONLINE submissions | ALL | ≈650 employees (≈890 with TNSA) | D50.01 | new gap | `erpnext/erpnext/setup/doctype/employee` | HG 295/2025; Revisal inactive since 31.12.2025 |
| A20.02 | Payroll with sector minimum wage and standard contributions | ALL | ≈650 payslips/month | D50.02 | partial | `hrms/hrms/payroll/doctype/salary_slip` | 4,582 RON sector minimum (2026); facilities abolished from 2025 (OUG 156/2024) |
| A20.03 | D112 monthly declaration | ALL | 6 entities × 12 | D50.03 | new gap | — | |
| A20.04 | Site timesheets to payroll, overtime, delegation allowances | AGC, PH | ≈350 site workers | D32.01–D32.04; D50.04 | partial | `hrms/hrms/payroll/doctype/salary_slip` | |
| A20.05 | Qualifications and authorisations (RTE, crane operators, welders, drivers' CPC, blasters) | ALL | ≈300 authorisations *(est.)* | D50.05 | new gap | — | |
| A20.06 | Cold-season stoppage indemnity via Casa Socială a Constructorilor | AGC, PH | Winter | D50.06 | new gap | — | Legea 215/1997 |
| A20.07 | Non-EU workers permits | AGC *(inference)* | Unknown | D50.07 | new gap | — | OG 25/2014 |

### A21 Documents and correspondence with authorities

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A21.01 | Correspondence register with authorities, registration numbers, response deadlines | AGC | 2,000–5,000 letters/yr *(est.)* | D26.01, D26.04 | partial | `erpnext/erpnext/support/doctype/service_level_agreement/service_level_agreement.py` | |
| A21.02 | Notifications: start and completion of works, ISC phase convocations | AGC, authority | Per contract | D54.01 | new gap | — | Legea 50/1991; Legea 10/1995 |
| A21.03 | Permit and authorisation register with expiries (AC, avize, ISC lab, mining licences, ISCIR, ARR) | ALL | 200–500 items *(est.)* | D54.02 | new gap | — | |
| A21.04 | Document control and revisions of PT/DE | AGC | | D25.01, D25.02 | spec-only | 03 core gap #7 | |
| A21.05 | Transmittals to authority and diriginte | AGC | | D26.02 | spec-only | 03 core gap #6 | |
| A21.06 | Qualified electronic signatures | ALL | | D02.14 | spec-only | 03 gap register D02.14 + `mayan-edms/mayan/apps/document_signatures/models.py` | Reg. (UE) 910/2014 |
| A21.07 | Archiving and retention | ALL | | D25.09, D36.03 | partial | `mayan-edms/mayan/apps/documents/models/document_version_models.py` | Legea 82/1991; Legea 16/1996 |

### A22 Funding and EU/PNRR reporting

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A22.01 | Funding source per contract and eligibility tagging (PNRR, regional programme, water programme, Anghel Saligny, CNI, local budget) | AGC | 15–25 contracts | D18.01, D18.02 | partial | `odoo/addons/analytic/models/analytic_distribution_model.py` | |
| A22.02 | Supporting packs for the beneficiary's payment requests | AGC | Per situație on funded contracts | D53.01 | new gap | — | OUG 124/2021; OUG 40/2015 |
| A22.03 | Payment-cycle tracking: beneficiary request → funds → payment to contractor | AGC | Per situație | D53.02; D22 | new gap | — | |
| A22.04 | PNRR end-date risk (activities due by 31.08.2026) and funding migration | AGC | ULBS dorm, Politehnica dorm, schools | D53.03 | new gap | — | OUG 124/2021 as amended |
| A22.05 | Audit trail for AM verifications, Court of Accounts, DNSH and double-funding declarations | AGC | Per funded contract | D53.04 | new gap | — | |
| A22.06 | Adjustment reserve ceilings at beneficiary level | AGC | Per adjusted contract | D40.05 | new gap | — | OUG 64/2022 art. 9 (reserve ≤23% + 10%) |

### A23 Disputes, claims and CNSC

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A23.01 | CNSC complaints as challenger, defendant-side intervenient or awardee | AGC | Several per year (Maria Tereza, research) | D55.01 | new gap | — | Legea 101/2016 |
| A23.02 | Court case register | AGC | ≈26 cases 2023–2026 | D55.02 | new gap | — | |
| A23.03 | Contractual claims for time and money | AGC | SCJU delays | D20.01; D55.03 | spec-only | 03 core gap #4 | HG 1/2018 claims clause |
| A23.04 | Penalties received or applied, set-off against payments | AGC | | D55.04 | new gap | — | |
| A23.05 | Audit findings affecting contracts (Court of Accounts on Săliște indexations) | AGC | | D55.05 | new gap | — | |
| A23.06 | Calls on guarantees | AGC | | D38.05 | new gap | — | HG 395/2016 (prior notice of claim) |

### A24 Reporting and management

| Activity id | Activity | Entity | Volume at their scale | Our coverage | Status | Best source (repo path) | Notes |
|---|---|---|---|---|---|---|---|
| A24.01 | Contract dashboard: initial/adjusted value, certified, invoiced, collected, cost, margin, progress | AGC | 15–25 contracts | D12.05, D33.01–D33.03 | partial | `openproject/modules/costs/app/models/costs/aggregated_costs.rb` | |
| A24.02 | Backlog and weighted pipeline | AGC, PH | | D15.06, D33.03 | partial | `erpnext/erpnext/crm/doctype/opportunity/opportunity.json` | |
| A24.03 | Quarry and plant KPIs (t/h, m³/day, yield, fuel/t, cost/t) | EUF, TNI, DPS | Daily | D45, D46 | new gap | — | |
| A24.04 | Fleet utilisation and cost KPIs | TNSA | Daily | D47 | new gap | — | |
| A24.05 | Statistical surveys to INS | ALL | Monthly/quarterly | D54.04 | new gap | — | |
| A24.06 | Permissions and audit per entity | ALL | 6 entities | D02.01, D02.13 | covered | `frappe/frappe` permission engine (D02) | |
| A24.07 | Migration from current accounting and spreadsheets | ALL | Unknown systems | D35.05 | partial | `odoo/addons/base_import/models/base_import.py` | Systems unknown (profile) |

## New domains required

### D37 Public Procurement and Tendering (Romania)

- **D37.01 Notice watch and bid/no-bid**: ingest SICAP and TED notices. *Data:* notice (source, notice no., authority CUI, CPV, NUTS, procedure type, estimated value, deadlines, lots, funding), watch rule, bid decision (go/no-go, reason, owner). *Logic:* match notices to watch rules; dedupe across SICAP/TED; create tender record on "go"; capacity check against live backlog. *Source:* Legea 98/2016 (procedures, art. 7 thresholds).
- **D37.02 Tender dossier and clarifications**: *Data:* dossier documents, clarification question/answer, erată, deadline history. *Logic:* recompute every downstream deadline when an erată moves the submission date; flag unanswered questions against the clarification cut-off. *Source:* Legea 98/2016; HG 395/2016.
- **D37.03 DUAE and qualification evidence**: *Data:* DUAE per participant role (leader, member, subcontractor, third-party supporter), evidence items (similar contracts with value and reception PV, turnover by year, key experts with CVs and certificates, equipment list, ISO certificates) with validity. *Logic:* select evidence that meets each qualification criterion; sum turnover and experience across JV members where allowed; expiry warnings. *Source:* Legea 98/2016 art. 193 (DUAE), art. 182–185 (third-party support).
- **D37.04 Offer assembly**: *Data:* technical proposal sections, financial proposal (forms), deviz ofertă link, grafic de execuție link. *Logic:* completeness check per fișa de date list; price cannot exceed estimated value without justification flag. *Source:* HG 395/2016.
- **D37.05 Consortium and supporters at bid**: *Data:* JV agreement (members, shares, leader, joint liability), subcontractor commitments, supporter commitments. *Logic:* shares sum to 100%; each declared subcontractor gets a D41.01 record on award. *Source:* Legea 98/2016 (association and third-party support).
- **D37.06 Abnormally low price**: *Data:* price justification request, response, cost breakdown. *Logic:* trigger when offer < 80% of estimated value; produce resource-level justification from D39. *Source:* HG 395/2016 art. 210.
- **D37.07 e-Auction**: *Data:* round, submitted total. *Logic:* redistribute final price to items pro rata or by rule, keeping resource prices consistent. *Source:* Legea 98/2016 (electronic auction).
- **D37.08 Award and standstill**: *Data:* communication of result, ranking, competitor offers, standstill end date. *Logic:* compute contest deadline by procedure value class; route to D55.01. *Source:* Legea 98/2016; Legea 101/2016.
- **D37.09 Bid analytics**: *Logic:* win rate by client/CPV/partner; estimate vs award ratio; competitor price distribution from award notices.

### D38 Contract Guarantees and Retention (Romania)

- **D38.01 Participation guarantee**: *Data:* instrument type (SGB, insurance, deposit), issuer, amount, validity, tender link. *Logic:* amount ≤1% of estimated value; validity ≥ offer validity; release after contract signature and constitution of the good-execution guarantee (losers: after award becomes final). *Source:* HG 395/2016 art. 35–38 (as amended by HG 336/2023; verify).
- **D38.02 Good-execution guarantee and retention account**: *Data:* instrument, target amount (≤10% of price excl. VAT), retention account (bank or Treasury), initial deposit, retention per situație, accrued interest owed to contractor. *Logic:* retention = min(planned % × situație value, target − balance); initial deposit ≥0.5% of price; target re-based on each value addendum; release 70% within 14 days of the reception-at-completion PV if no claims, 30% at final reception after the warranty period; for design services release on reception of the related works. *Source:* Legea 98/2016 art. 154 (Legea 208/2022); HG 395/2016 art. 39–42 (verify after HG 336/2023).
- **D38.03 Advance payment and advance guarantee**: *Data:* advance %, guarantee instrument, recovery schedule. *Logic:* recover advance pro rata per situație; guarantee reduces as advance is recovered; %av feeds D40.02.
- **D38.04 Guarantee lines and costs**: *Data:* bank/insurer limit, utilisation, fees. *Logic:* utilisation across all guarantees by issuer; fee accrual per contract.
- **D38.05 Calls on guarantees**: *Data:* claim notice (unmet obligations, damage computation), amount called, restoration. *Logic:* authority must notify contractor and issuer before calling; contractor must restore the guarantee after a call. *Source:* HG 395/2016.

### D39 Romanian Estimating, Devize and Situații de Lucrări

- **D39.01 Norm and resource catalogue**: *Data:* norm (code, unit, description, resource consumption lines), resource (type material/labour/equipment/transport, unit, price, effective date, source incl. group price list). *Logic:* unit price of a norm item = Σ(consumption × resource price) per resource class; equipment price from D47.06; labour from category rates. *Source:* Romanian norme de deviz practice; Ordin 863/2008.
- **D39.02 Deviz pe categorii and resource lists**: *Data:* deviz (obiect, categorie de lucrări, items with norm code, quantity, unit price split materials/labour/equipment/transport), indirect %, profit %. *Logic:* explode items to resource lists; sum by class; apply indirect and profit; materials share retained for D40.03. *Source:* Ordin 863/2008 F3/F4/F5.
- **D39.03 Deviz general and deviz pe obiect**: *Data:* chapters 1–6 with sub-chapters, obiecte, VAT. *Logic:* totals per chapter; link chapter 4 (investment) to contract CBS; chapter 5.1 site setup; diverse și neprevăzute share. *Source:* HG 907/2016.
- **D39.04 Measurement and situație de lucrări**: *Data:* situație (contract, period, obiect), line (deviz item, quantity this period, cumulative quantity, unit price, value), attachments (foi de atașament), diriginte certification. *Logic:* cumulative quantity ≤ contract quantity + approved NCS quantities; value = Σ(qty × price); separate lines for NCS items; block lines whose hidden-works PV (D43.03) is missing. *Source:* contract; HG 1/2018 measurement clauses.
- **D39.05 Centralizator and deductions**: *Logic:* gross certified − advance recovery − GBE retention − penalties ± adjustment (D40.02) = amount payable; per JV member split (D48.04).
- **D39.06 Final account**: *Logic:* reconcile cumulative situații, NCS, adjustments and penalties to the final contract value; produce input for the final-value addendum. *Source:* OUG 64/2022 art. 11(6) (EU-funded contracts).

### D40 Price Adjustment and Contract Modification

- **D40.01 Index store**: *Data:* index series (ICC total, ICC materials, forecast ICC from CNSP, IPC, IVUI), period, value, status provisional/final, %cpm weights by construction type (tab. 15A). *Logic:* ingest monthly; mark provisional; on final publication trigger recalculation of affected payments.
- **D40.02 Adjustment computation**: *Logic (works, EU-funded):* Vapl = Vm × [(%av + %p) + (1 − %av − %p) × ICCmr/ICCmlr] + (Vpl − Vm) + (1 − %cpm) × {(Vpl − Vm) × [(%av + %p) + (1 − %av − %p) × ICCr/ICCplr] − (Vpl − Vm)}; ICCr/ICCmr taken 60 days before the end of the submission month; reference month = month before bid deadline (or 30 days before signature), floored at January 2021; %p = profit in the payment, default 3% when not identifiable; sub-unit index ratios reduce the payment; adjustment SR = Vapl − Vpl, recalculated for the difference when indices become final; transport/major water infrastructure uses realised ICCRlr instead of forecast ICCplr. *Source:* OUG 64/2022 art. 17(3)–(8) as amended by OUG 109/2022.
- **D40.03 Rest-de-executat baseline**: *Data:* addendum date, remaining quantity and value by item, materials value. *Logic:* adjustment applies only to the remainder at the addendum date until reception at completion; contractor must split materials from other cost categories, otherwise statutory weights apply. *Source:* OUG 64/2022 art. 10, 17(1), 17(9).
- **D40.04 Contract clause adjustments**: *Data:* clause formula, indices, thresholds. *Logic:* evaluate the contract's own formula on each situație for national/local-budget contracts. *Source:* Legea 98/2016 art. 221(1)(a); HG 395/2016 art. 164.
- **D40.05 Addenda register and limits**: *Data:* addendum (type: adjustment, extra works, unforeseen, de minimis, duration, subcontractor), value delta, legal basis. *Logic:* cumulative value change vs Legea 98/2016 art. 221 limits (≤50% per modification for additional works/unforeseen; de minimis below threshold and ≤15% for works); OUG 64/2022 art. 8 cap 50%; adjustment reserve ≤23% of remainder, top-up ≤10% after 75% consumption (OUG 64/2022 art. 9). Direct awards must stay under the direct-award threshold after adjustment (art. 18).
- **D40.06 Notes de comandă**: *Data:* NCS / note de renunțare / note de modificare, items, quantities, price basis (offer price or new price), reference month. *Logic:* NCS items with an offer equivalent use the original reference month; new items priced from offer resource prices (D39.01) with their own reference month; renunțări reduce remaining quantities; aggregated into addenda (D40.05). *Source:* OUG 64/2022 art. 17(8) (extra works rule).

### D41 Subcontracting Compliance (Public Contracts)

- **D41.01 Subcontractor declaration**: *Data:* subcontractor, scope, value, % of contract, contract copy, declaration date, authority approval. *Logic:* subcontracts must be declared and approved before the subcontractor works; replacement allowed only in statutory cases; new subcontractor must meet the qualification criteria of the part it performs. *Source:* Legea 98/2016 art. 218–220; HG 395/2016 art. 151.
- **D41.02 Responsibility matrix**: *Logic:* contractor remains liable; flag subcontracted share vs any contractual cap.
- **D41.03 Direct payment**: *Data:* subcontractor request, contractor confirmation of the amount, authority payment. *Logic:* split contractor invoice into own share and directly paid share; reconcile with subcontractor invoice and remove from contractor receivable. *Source:* Legea 98/2016 (direct payment of subcontractors).
- **D41.04 Back-to-back flow-down**: *Logic:* GBE, penalties, retention and adjustment applied to subcontracts per subcontract terms, linked to the main-contract items.

### D42 Design-Build Design Management (HG 907/2016)

- **D42.01 Design phases**: *Data:* phase (SPF, SF, DALI, DTAC, PT, DE), deliverables, approval (HCL/HCJ approval of indicators for SF/DALI), status. *Logic:* PT cannot be submitted before DTAC/AC; DE per obiect before works on that obiect. *Source:* HG 907/2016.
- **D42.02 Design subcontract and fees**: *Logic:* fee milestones per phase; guarantee release for PT/DE tied to reception of the works (D38.02).
- **D42.03 Technical verification**: *Data:* verifier, specialty, fundamental requirement, referat, stamp date, expertiză tehnică. *Logic:* every PT section must carry the required verifications before issue for construction. *Source:* Legea 10/1995 (verification of projects).
- **D42.04 Permits and avize**: *Data:* certificat de urbanism, aviz list per CU, autorizație de construire with validity and works start deadline. *Logic:* AC validity and start obligation; extension request deadlines. *Source:* Legea 50/1991.

### D43 Construction Quality System (Legea 10/1995)

- **D43.01 Quality control programme**: *Data:* programme per contract, phases (type: determinantă, lucrări ascunse, verificare), participants (ISC, designer, diriginte, RTE). *Source:* Legea 10/1995; Ordin 1370/2014 (PCF 002).
- **D43.02 Faze determinante**: *Logic:* stop point; convocation sent to ISC and designer before the phase; PV signed by all required parties; successors in D06 cannot start (constraint injected). *Source:* Ordin 1370/2014 (PCF 002); Ordin 1369/2014 (PCE 001).
- **D43.03 Process PVs**: *Data:* PV lucrări ascunse, trasare, predare-primire amplasament, recepție calitativă, linked to elements and deviz items. *Logic:* PV status gates D39.04 billing.
- **D43.04 Product conformity at use**: *Logic:* every incorporated product links to DoP/certificate (D44.05).
- **D43.05 RTE and diriginte**: *Data:* person, authorisation number, specialties, validity, contract assignment. *Logic:* contract must have a valid RTE per specialty; expiry blocks PV signature. *Source:* Legea 10/1995.
- **D43.06 Dispoziții de șantier**: *Data:* issuer (designer/diriginte), content, impact. *Logic:* links to D40.06 when quantities change.
- **D43.07 Site registers**: jurnal de șantier, condica de betoane, register of PVs with sequential numbering per site.
- **D43.08 Reception**: *Data:* notification of completion, commission members (diriginte not a member), quorum 2/3, objections with deadlines, PV at completion, PV final. *Logic:* investor sets date within 5 days of notification, reception within 30 days; investor decision within 3 days; unremedied objections suspend final reception; final reception scheduled ≤10 days after warranty expiry; PVs trigger D38.02 releases. *Source:* HG 343/2017.
- **D43.09 Cartea tehnică**: *Logic:* assemble the execution section from D43.03, D44, D43.06, as-built drawings; handover at reception. *Source:* HG 273/1994 annex (verify current status).
- **D43.10 ISC and CSC quotas**: *Logic:* 0.5% (Legea 10/1995 art. 40) and 0.1% (Legea 50/1991 art. 30) of authorised value excl. VAT, 50% at start notification and the balance by reception, regularised on actual value; CSC 0.5% (Legea 215/1997).
- **D43.11 Warranty defects**: *Logic:* defects reported during warranty with remedy deadlines; open defects block final reception.

### D44 Construction Laboratory and Materials Testing

- **D44.01 Lab authorisation**: *Data:* lab grade, authorised tests, validity, equipment calibration. *Logic:* a test report is valid only if the test is in the lab's authorised scope and equipment is calibrated. *Source:* ISC laboratory authorisation regulation (verify act number).
- **D44.02 Samples and tests**: *Data:* sample (source: plant batch or site pour, element, date), tests (SR EN 12350-2 slump, -6 density, -7 air; SR EN 12390-3 compressive at 7/28 days, -8 water penetration; soil compaction; asphalt), results. *Logic:* schedule curing ages; compute results and conformity per test standard.
- **D44.03 Concrete production conformity**: *Logic:* SR EN 206+A2 conformity criteria by family (initial vs continuous production; mean of n results ≥ fck + margin; each result ≥ fck − 4), sampling rate by volume and period; FPC record for certification. *Source:* SR EN 206+A2; NE 012/1-2022 (verify title).
- **D44.04 Site acceptance testing**: *Logic:* acceptance per element/lot at delivery; link to D43.02 phases.
- **D44.05 Product declarations**: *Data:* DoP, CE, certificat de conformitate, agrément tehnic per product and batch. *Source:* Reg. (UE) 305/2011.

### D45 Ready-Mix Concrete (and Asphalt) Production and Dispatch

- **D45.01 Recipes**: *Data:* class, exposure class, consistency, Dmax, chloride class, cement type, w/c max, materials per m³ by source. *Logic:* recipe validity vs SR EN 206 limiting values per exposure class.
- **D45.02 Orders and dispatch**: *Data:* order (site, element, recipe, volume, rate m³/h, start), truck assignment, pump assignment. *Logic:* trucks needed = rate × cycle time / truck capacity; sequence loads; cold-weather flags.
- **D45.03 Batch records**: *Data:* per load actual weights, water, admixture, tolerances. *Logic:* tolerance check; consumption posting to stock.
- **D45.04 Delivery tickets**: *Data:* ticket per load with SR EN 206 delivery-ticket content (producer, ticket no., date/time of loading, truck, customer, site, recipe and properties, volume). *Logic:* ticket ↔ site receipt ↔ element; returns and waste.
- **D45.05 Pump services**: *Logic:* bill by hours and m³; link to orders.
- **D45.06 Materials reconciliation**: *Logic:* theoretical (Σ recipes × volume) vs actual stock movements; variance.
- **D45.07 Asphalt mixes** *(inference)*: *Data:* SR EN 13108 mix types, temperatures. *Logic:* same order/dispatch/ticket model.

### D46 Quarry and Aggregates (Legea 85/2003)

- **D46.01 Licences and perimeters**: *Data:* licence/permit, perimeter coordinates, reserves, validity, annual programme. *Logic:* production cannot exceed licensed annual quantity. *Source:* Legea 85/2003.
- **D46.02 Production**: *Data:* extraction volume, crusher runs, outputs by fraction. *Logic:* co-product yield split; cost per tonne by fraction.
- **D46.03 Products and prices**: *Data:* fraction catalogue, price lists (external, intra-group).
- **D46.04 Stockpiles**: *Logic:* book stock vs survey; adjustments.
- **D46.05 Weighbridge and dispatch**: *Data:* gross/tare/net, vehicle, driver, customer, site, aviz, UIT. *Logic:* each load > 500 kg or > 10,000 RON on a ≥2.5 t vehicle needs an e-Transport UIT before departure (D49.03).
- **D46.06 Royalty**: *Logic:* redevență = production units × statutory unit rate (€0.50 equivalent for sand and gravel in consolidated text; rate for crushed rock to verify), EUR converted at the rate of the first working day of October of the prior year; quarterly; annual mining activity tax per km². *Source:* Legea 85/2003 art. 45–47.
- **D46.07 Production reporting**: *Logic:* produce statutory production data for the mining authority and INS from D46.02.
- **D46.08 Aggregate conformity**: *Data:* FPC tests (grading, fines, LA, MDE), DoP, CE. *Source:* SR EN 12620, SR EN 13242, SR EN 13043; Reg. (UE) 305/2011.
- **D46.09 Rehabilitation guarantee**: *Data:* closure plan, financial guarantee amount.
- **D46.10 Explosives**: *Data:* receipts, consumption per blast, storage. *Source:* Legea 126/1995.

### D47 Fleet, Plant and Regulated Equipment

- **D47.01 Unit register**: *Data:* unit, class, owner entity, VIN/serial, capacity, meter type.
- **D47.02 Usage logs**: *Data:* daily hours/km per site and contract, operator. *Logic:* charge to contract cost (D17.12) at internal rate.
- **D47.03 Fuel**: *Data:* issue (tank, card), litres, meter reading. *Logic:* consumption norm per class (l/h, l/100 km); flag deviations.
- **D47.04 Regulated inspections**: *Data:* obligation (ITP, tachograph, ISCIR VTP, RCA, rovinietă, ARR licence copy), due date. *Logic:* block dispatch of non-compliant units. *Source:* Legea 64/2008; OG 27/2011; OG 15/2002; Reg. (UE) 165/2014.
- **D47.05 Allocation and dispatch**: *Logic:* reserve units per site/day; transfer between entities generates D48.02 charges.
- **D47.06 Cost rates**: *Logic:* hourly rate = (depreciation + financing + insurance + maintenance + fuel + operator) / planned hours; used in D39.01 and charge-out.
- **D47.07 Telematics import**: *Logic:* GPS hours/km and fuel-card lines matched to logs.
- **D47.08 Meter-based maintenance**: *Logic:* trigger by hours/km thresholds (extends D31.03).

### D48 Intra-Group Transfers and JV Accounting

- **D48.01 Inter-company price lists**: *Data:* product/service, seller entity, buyer entity, price, validity. *Logic:* auto-create mirror purchase invoice; price lookup from policy.
- **D48.02 Internal hire and haulage charges**: *Logic:* from D47.02/D47.05 logs to monthly inter-company invoice.
- **D48.03 Transfer-pricing file**: *Logic:* arm's-length range tests per transaction class; annual file content. *Source:* Cod fiscal art. 11; OPANAF 442/2016.
- **D48.04 JV accounting**: *Data:* JV, members, shares, leader. *Logic:* split each situație and cost by share or by executed scope; member-to-leader invoicing; JV-level P&L.
- **D48.05 Consolidation**: *Logic:* eliminate inter-company revenue/cost and unrealised margin in stock.
- **D48.06 Shared services**: *Logic:* recharge by driver.
- **D48.07 Reconciliation and netting**: *Logic:* match open inter-company balances; generate set-off documents.

### D49 Romanian Fiscal Compliance

- **D49.01 e-Factura outbound**: *Logic:* generate RO_CIUS UBL 2.1; upload to SPV within the statutory term; poll status; store signed XML and index. *Source:* OUG 120/2021; Legea 296/2023; Legea 139/2022 (B2G).
- **D49.02 e-Factura inbound**: *Logic:* download from SPV; parse; match to PO/receipt.
- **D49.03 e-Transport**: *Logic:* declare UIT for high-fiscal-risk goods (NC 2505, 2517) before transport; validity window; corrections. *Source:* OUG 41/2022; OPANAF 802/2022.
- **D49.04 VAT engine**: *Logic:* reverse charge on construction services (art. 331(2)(i)); D300, D394 generation. *Source:* Legea 227/2015 (Cod fiscal).
- **D49.05 SAF-T D406**: *Logic:* XML from GL, partners, invoices, payments; assets annually; stock on request. *Source:* OPANAF 1783/2021.
- **D49.06 Romanian chart of accounts**: *Source:* OMFP 1802/2014.
- **D49.07 Statutory reporting**: annual financial statements and fiscal declarations.

### D50 Romanian HR, Payroll and Labour Compliance

- **D50.01 REGES-ONLINE**: *Logic:* register contracts and changes before the effective date. *Source:* HG 295/2025.
- **D50.02 Payroll rules**: *Logic:* CAS 25%, CASS 10%, income tax 10%, CAM 2.25%; sector minimum wage check (4,582 RON in 2026); construction facilities ended 31.12.2024 (OUG 156/2024).
- **D50.03 D112**: monthly XML from payroll.
- **D50.04 Delegation and site allowances**: *Logic:* per-diem and travel from site timesheets.
- **D50.05 Authorisations and fitness**: *Data:* qualification type, issuer, validity; medical fitness. *Logic:* block assignment of expired staff to tasks requiring them.
- **D50.06 Cold-season indemnity**: *Source:* Legea 215/1997.
- **D50.07 Foreign worker permits**: *Source:* OG 25/2014.

### D51 Site H&S (HG 300/2006)

- **D51.01 Safety plan and coordinator**: *Data:* PSS, coordinator appointment, registru de coordonare. *Source:* HG 300/2006.
- **D51.02 Declarație prealabilă**: *Logic:* required when >30 working days and >20 simultaneous workers, or >500 man-days; filed with the ITM of the site's county; displayed on site. *Source:* HG 300/2006 annex 3.
- **D51.03 Dosar de intervenții ulterioare**: handed over at reception. *Source:* HG 300/2006.
- **D51.04 ITM accident communication**: *Source:* Legea 319/2006 (extends D30.02).
- **D51.05 Fire prevention**: *Source:* Legea 307/2006.

### D52 Environment and Construction Waste

- **D52.01 C&D waste records**: *Data:* waste code, quantity, generator site, transporter, receiving operator, documents. *Logic:* monthly record per waste type; retention ≥3 years. *Source:* OUG 92/2021; HG 856/2002.
- **D52.02 Environmental declarations**: *Source:* OUG 196/2005 (Fondul pentru mediu); annual APM reporting.
- **D52.03 Permits and monitoring**: environmental and water permits for EUF, TNI, DPS with conditions and monitoring schedules.
- **D52.04 Excavated soil balance**: *Logic:* cut/fill and reuse per site.

### D53 Funded-Project Reporting (EU, PNRR, National Programmes)

- **D53.01 Payment-request packs**: *Logic:* assemble invoice, situație, PVs, photos, staff lists per beneficiary request. *Source:* OUG 124/2021; OUG 40/2015.
- **D53.02 Cycle tracking**: *Logic:* states submitted → funds received by beneficiary → paid to contractor; ageing.
- **D53.03 Funding end-date risk**: *Logic:* compare programme end dates (PNRR activities by 31.08.2026) to schedule finish.
- **D53.04 Audit trail**: DNSH, double-funding and conflict-of-interest declarations; Court of Accounts findings.

### D54 Authority Interface and Permits Register

- **D54.01 Statutory notifications**: start and completion of works, ISC convocations. *Source:* Legea 50/1991; Legea 10/1995.
- **D54.02 Permits register**: all authorisations by entity with expiry and renewal tasks.
- **D54.03 Inspection visits**: ISC, ITM, ANAF, Garda de Mediu findings and deadlines.
- **D54.04 Statistical surveys**: INS submissions by entity.

### D55 Disputes, Claims and CNSC

- **D55.01 CNSC remedies**: *Data:* complaint, procedure, grounds, deadlines, decision, court appeal. *Logic:* deadline depends on procedure value class (above/below EU thresholds); decision due dates. *Source:* Legea 101/2016.
- **D55.02 Litigation register**: cases, courts, terms, provisions.
- **D55.03 Contractual claims**: notice, particulars, determination. *Source:* HG 1/2018 claims clause.
- **D55.04 Penalties and set-off**: *Logic:* contractual delay penalties; Legea 72/2013 interest on late payments.
- **D55.05 Audit findings**: Court of Accounts findings affecting contract values.

## Coverage summary

| Group | Activities | covered | partial | spec-only | new gap |
|---|---|---|---|---|---|
| A01 Business development and tendering | 10 | 0 | 5 | 0 | 5 |
| A02 Contract setup and consortia | 8 | 0 | 5 | 1 | 2 |
| A03 Design-build design management | 8 | 1 | 3 | 1 | 3 |
| A04 Planning and scheduling | 7 | 1 | 4 | 2 | 0 |
| A05 Estimating and bill of quantities | 6 | 0 | 2 | 0 | 4 |
| A06 Cost control and forecasting | 7 | 1 | 6 | 0 | 0 |
| A07 Progress measurement and billing | 7 | 1 | 2 | 2 | 2 |
| A08 Price adjustment and addenda | 8 | 0 | 1 | 2 | 5 |
| A09 Subcontractor management | 8 | 0 | 4 | 2 | 2 |
| A10 Procurement and materials | 7 | 3 | 2 | 0 | 2 |
| A11 Site operations | 8 | 1 | 5 | 0 | 2 |
| A12 Quality | 11 | 0 | 6 | 0 | 5 |
| A13 Health and safety | 8 | 0 | 2 | 2 | 4 |
| A14 Environment and waste | 5 | 0 | 0 | 1 | 4 |
| A15 Equipment and fleet | 8 | 0 | 4 | 0 | 4 |
| A16 Quarry and aggregates production | 9 | 0 | 2 | 0 | 7 |
| A17 Concrete plant production and dispatch | 9 | 0 | 5 | 0 | 4 |
| A18 Intra-group transfers | 6 | 0 | 2 | 0 | 4 |
| A19 Finance, accounting, fiscal compliance | 9 | 0 | 7 | 0 | 2 |
| A20 HR and payroll | 7 | 0 | 2 | 0 | 5 |
| A21 Documents and correspondence with authorities | 7 | 0 | 2 | 3 | 2 |
| A22 Funding and EU/PNRR reporting | 6 | 0 | 1 | 0 | 5 |
| A23 Disputes, claims and CNSC | 6 | 0 | 0 | 1 | 5 |
| A24 Reporting and management | 7 | 1 | 3 | 0 | 3 |
| **Total** | **182** | **9 (5%)** | **75 (41%)** | **17 (9%)** | **81 (45%)** |

New domains: 19 (D37–D55), 118 features.

### Top 15 gaps for this company

| # | Gap | Domains | Why it matters here |
|---|---|---|---|
| 1 | Situații de lucrări engine: measured quantities × offer prices, cumulative caps, centralizator with deductions | D39.04, D39.05; 03 #1 | Every leu of AGC's 132.5 M RON revenue passes through 200–300 situații/yr *(est.)*; no OSS has measured-quantity billing against a priced BoQ |
| 2 | OUG 64/2022 price adjustment: index store, Vapl per payment, recalculation on final indices, rest-de-executat | D40.01–D40.03 | Addenda add 15–70% on their contracts; 2025 net margin 1.9% leaves no room for formula errors; Court of Accounts already reviewed Săliște indexations |
| 3 | Good-execution guarantee retention account with 70%/30% release | D38.02; 03 #2 | Up to 10% of each contract's value is held until reception and warranty end; release depends on reception PVs (D43.08) |
| 4 | Romanian norm-based estimating and resource lists | D39.01, D39.02 | 40–80 bids/yr *(est.)*; NCS new prices and abnormally-low-price answers must come from the same resource lists |
| 5 | NCS and addenda register with Legea 98/2016 art. 221 limits | D40.05, D40.06; 03 #4 | AA13/AA15-type addendum chains on SCJU; exceeding limits exposes contracts to annulment and audit findings |
| 6 | Faze determinante and process PVs as stop points that gate billing | D43.01–D43.03 | Required by Legea 10/1995 on every contract; hidden-works PVs are a precondition for billing covered items |
| 7 | Reception and cartea tehnică | D43.08, D43.09 | Triggers guarantee release, warranty start, final value addendum and final reception; 5–15 receptions/yr *(est.)* |
| 8 | Intra-group pricing, inter-company invoicing, JV split | D48.01–D48.04 | Cluster ≈300 M RON (≈431 M with Pro Hart) with aggregates, concrete, haulage and rental flowing between entities; group has a history of tax and anti-fraud probes; most contracts are JVs |
| 9 | Weighbridge-to-e-Transport flow for aggregates | D46.05, D49.03 | NC 2505/2517 are high-fiscal-risk goods; 60,000–120,000 loads/yr *(est.)*; fines up to 100,000 RON per breach |
| 10 | Mining licences, production and royalties | D46.01, D46.06, D46.07 | EUF and TNI (≈133 M RON turnover) depend on licensed perimeters; quarterly royalty from production units |
| 11 | Concrete conformity, lab records and delivery tickets | D44.02, D44.03, D45.04 | Structural liability under Legea 10/1995; grade II lab and SR EN 206 conformity data feed cartea tehnică of every AGC building |
| 12 | Subcontractor declaration, replacement and direct payment | D41.01, D41.03 | 3–8 subcontractors per contract; turnover per employee ≈0.9 M RON shows heavy subcontracting; undeclared subcontractors are a procurement breach |
| 13 | Funded-project payment cycles and PNRR end-date risk | D53.01–D53.03 | PNRR activities were due by 31.08.2026; ULBS and Politehnica dorms and school rehabs depend on migrated funding; cash flow follows beneficiary reimbursement |
| 14 | Tender pipeline, DUAE and qualification evidence | D37.01–D37.05 | Near-100% public clients and expansion beyond Sibiu (Bucharest, Arad, Blaj) multiply bids; evidence reuse across JV members is manual |
| 15 | Fleet usage, regulated inspections and internal hire | D47.02–D47.05 | ≈170 major units; equipment cost reaches contracts only through internal hire; non-compliant units (ITP, ISCIR, tachograph) cannot legally work |

## Questions for the client

- Accounting software per entity (SAGA, WinMentor, Ciel, Nexus, SAP Business One or other), chart-of-accounts customisations, and who files e-Factura, SAF-T D406, D112 and e-Transport today.
- Estimating tool and norm database used for devize (e.g. a licensed norm catalogue), and export formats of past offers and situații.
- Situații de lucrări format per client (Primăria Sibiu, CJ Sibiu, Apa Canal, CNI, TURSIB, ULBS, UNSTPB): templates, attachments, approval steps, typical lead time from submission to payment.
- List of live contracts with value, funding source, JV structure and shares, subcontractors, addenda history and current price-adjustment formula.
- Price-adjustment workings already submitted: indices used, reference months, materials split, disputes with beneficiaries.
- Good-execution guarantees: instruments per contract (SGB, insurance, retention account), issuers, limits, current balances and pending releases.
- Group structure: shareholdings, which entity owns each equipment unit, inter-company price lists, transfer-pricing file status.
- Whether DPS Beton is the Cife Beton plant, whether it produces asphalt, plant controller make/model and data export.
- Laboratory: authorisation grade and scope, LIMS or spreadsheets, sampling plans, FPC certification body.
- Quarries and pits: licence/permit numbers, perimeters, annual programmes, production per fraction, weighbridge software, royalty declarations, environmental and water permits.
- Fleet: register with VIN/serials, telematics/GPS provider, fuel cards, maintenance system, ISCIR-registered equipment, internal hire rates.
- Payroll: provider or in-house, headcount per entity and site, use of foreign workers, delegation rules, REGES-ONLINE operator.
- Quality: sample programme de control al calității, PV templates, how cartea tehnică is assembled, RTE list and authorisations.
- H&S and environment: safety coordinators used, waste transporters and receivers, how monthly waste records are kept.
- Tendering: who monitors SICAP, archive of DUAE and qualification evidence, win/loss history, CNSC and court case files.
- Funded projects: beneficiary payment-request calendars, documents beneficiaries ask contractors for, PNRR contracts not completed by 31.08.2026 and their new funding.
- Document and correspondence practice: registration numbers, e-mail versus paper, qualified e-signature holders.
- Reports management uses today (per-contract margin, cash, backlog) and their sources.
