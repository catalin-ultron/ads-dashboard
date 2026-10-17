# Total NSA group: registry and financial research (construction focus)

*Compiled 2026-10-16. All amounts are in RON unless stated otherwise. "M" means millions of RON.*

## How the figures were sourced

- **Primary source (official).** Financial figures for 2019-2025 come straight from **ANAF's public balance-sheet web service** (the official filed statements that mfinante.gov.ro also shows): `https://webservicesp.anaf.ro/bilant?an=<YEAR>&cui=<CUI>`. Registration and VAT data come from **ANAF's VAT-registry API** (`https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva`), queried on 2026-10-15.
- **Second source.** For TOTAL NSA AG CONSTRUCT and TOTAL N S A, the full yearly tables on **totalfirme.ro**, which republishes MFinante data under the OGL licence, were checked line by line against ANAF. **Every 2019-2025 figure matches exactly.** For the other entities, the ANAF figures were checked against aggregator snippets (termene.ro, risco.ro, EMIS) as they appeared in search results. Where only one source was available, the figure is marked **[1 source]**.
- **Blocked sources.** listafirme.ro/.eu, termene.ro, risco.ro, confidas.ro, targetare.ro and sicap.ai all returned a Cloudflare or Vercel challenge, HTTP 403 or HTTP 429 to automated fetches. Their content appears here only as search-engine snippets, which are marked as such. ONRC and openapi.ro need an account or API key and were not queried. As a result, **full shareholder lists with percentages could not be retrieved**. What is published, mostly initials and administrator names, is given below.
- **Rankings** come from Coface **infoquick.ro**. Each is a national rank by turnover within the company's main CAEN code, "calculat pe baza celor mai recente date financiare disponibile", which here means FY2025. **[1 source]**
- **ANAF API coverage.** The API returned data only for FY2019 onward. AG Construct's 2016-2018 figures come from totalfirme.ro alone **[1 source]**.

---

## 1. Executive summary

- **The construction business sits in a separate legal entity, TOTAL NSA AG CONSTRUCT SRL** (CUI **36594214**, J2016001267324, founded 3-4 Oct 2016, Str. Podului nr. 131, Sibiu). This is the same address that totalnsa.ro gives for the transport HQ. Its main CAEN is 4120 (Rev. 2), shown as 4100 under CAEN Rev. 3: "Lucrări de construcții a clădirilor rezidențiale și nerezidențiale".
  - **FY2025:** turnover **132.46 M RON** (-6.1% y/y), net profit **2.49 M** (1.9% margin), **149 employees**, total assets about **38.2 M**, debts **14.7 M**, equity **23.5 M**.
  - **FY2024 peak:** turnover **141.0 M**, net profit **6.10 M**.
  - **Growth:** turnover rose from 39.8 M in 2020 to 141.0 M in 2024, a compound rate of about 37% a year. 2025 is the first decline.
  - **Rank:** **24th of 19,694** active CAEN 4120 companies in Romania by turnover. It ranks 30th by employees and 295th by net profit [infoquick, 1 source].
- **The logistics business is TOTAL N S A SRL** (CUI **9315010**, J1997000162324, Săliște, founded 1997, CAEN 4941 road freight).
  - **FY2025:** turnover **200.2 M**, net profit **20.7 M**, 241 employees, equity **160.1 M**.
  - **Rank:** **26th of 37,848** road-freight companies nationally.
  - This is the "Total NSA" brand on totalnsa.ro. Its registry objects also include construction codes (4100, 4211, 4350, 2363), but its main and reported activity is transport.
- **The construction value chain is vertically integrated** through sister companies linked to the same controlling businessman, **Ioan Domnariu** (named by press and by totalnsa.ro as founder and main associate):
  - **EUROFOR 2011 SRL** (CUI 29536210, Săliște, CAEN 0811 quarrying of building stone): FY2025 turnover **112.7 M**, 226 employees. It ranks **3rd nationally** in CAEN 0811.
  - **TOTAL NSA INVEST S.R.L.** (CUI 33469225, Beldiu/Teiuș, Alba county, CAEN 0812 gravel and sand): FY2025 turnover **20.7 M**, 47 employees. It ranks 29th of 807.
  - **DPS BETON S.R.L.** (CUI 33074365, formerly "DPS Beton&Asfalt", Sibiu, CAEN 2363 concrete): FY2025 turnover **34.2 M**, 25 employees. It ranks 33rd of 275. Press reports that Domnariu holds most of its shares, but the registry does not confirm this; see section 3.
- **Main subcontracting and JV partner: PRO HART GROUP SRL** (CUI 22170774, Sibiu, CAEN 4322 MEP installations). It partners on many public tenders and its logo appears on the "Companii in grup" page. FY2025 turnover **131.4 M**, net profit 14.1 M, 200 employees. It ranks **15th of 9,460** in CAEN 4322. Common ownership is **not confirmed** in any registry.
- **Combined size.** The construction-related perimeter, counting AG Construct, Eurofor, Total NSA Invest and DPS Beton without Pro Hart, had about **300 M RON** turnover in FY2025. Adding Pro Hart brings it to about 431 M.
- **Risk flags for AG Construct:**
  - No insolvency record (BPI) and no state-budget debts at 31.12.2025 [totalfirme].
  - VAT-registered since 31.10.2016. Not on cash-basis VAT, not on split VAT and not tax-inactive [ANAF].
  - About 26 court case numbers, mostly public-procurement disputes: CNSC appeals and contract-execution claims as defendant (pârât). In 2026 it is also named as civilly liable party in a criminal file (art. 296 NCP, "purtare abuzivă").
- **Public procurement is the core business.**
  - Press-documented wins include Spitalul Județean Sibiu (3 contracts, about 49.6 M lei rising to more than 85 M lei after addenda), Colegiul „Octavian Goga” (14.13 M), the Veterani district roads and lighting (13.82 M, JV with Pro Hart), the Sibiu creșă (18.14 M, JV), ULBS Engineering faculty (25.3 M, JV, under CNSC re-evaluation) and 17 Săliște town-hall contracts (more than 22 M).
  - sicap.ai claims 252 contracts worth 1.79 bn RON. **This total is implausible as company revenue and is not confirmed** (see section 6).

---

## 2. Legal entities: identification

All data in this table comes from the ANAF VAT-registry API on 2026-10-15, unless stated otherwise.

| # | Entity | CUI | Reg. Com. (ONRC) | Registered | Main CAEN (ANAF) | Registered office | VAT payer since | Role in group | Link to Total NSA |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **TOTAL NSA AG CONSTRUCT SRL** | **36594214** | J2016001267324 (J32/1267/2016) | 2016-10-03/04 | **4100 / 4120** building construction | Str. Podului nr. 131, Mun. Sibiu, 550263 | 2016-10-31 | **Construction general contractor** | Confirmed: name, same HQ as totalnsa.ro, logo on group page, press |
| 2 | TOTAL N S A SRL | 9315010 | J1997000162324 | 1997-04-03 | 4941 road freight | Str. Andrei Șaguna nr. 61, Săliște | 1997-06-01 | **Logistics / transport** (the totalnsa.ro brand) | Confirmed |
| 3 | EUROFOR 2011 SRL | 29536210 | J2012000012327 | 2012-01-12/13 | 0811 quarrying of building stone | Calea Amnașului nr. 6, Săliște | 2013-09-19 | Aggregates: quarry at Valea Rece–Dealul Furcilor (Săliște) and gravel pit at Cristian on DN1 | Press: "societate controlată tot de Ioan Domnariu" (Turnul Sfatului 2023, 2026). **Not on the group logo page** |
| 4 | TOTAL NSA INVEST S.R.L. | 33469225 | J2020000822011 (moved to Alba 2020; first registered 2014-08-11 in Sibiu) | 2014-08-11 | 0812 gravel and sand extraction | Calea Beldiului FN, sat Beldiu, Teiuș, jud. Alba | 2014-09-05 | Aggregates (gravel pit) | Confirmed: name, logo on group page, phone "0269553549" is the Total NSA HQ number |
| 5 | DPS BETON S.R.L. (formerly DPS BETON&ASFALT) | 33074365 | J2014000393321 (J32/393/2014) | 2014-04-16/17 | 2363 ready-mix concrete | Str. Henri Coandă nr. 59, Sibiu | yes | Concrete and asphalt supply | Press only: "cele mai multe părți sociale îi aparțin omului de afaceri Ioan Domnariu"; photo caption "Betonul a fost luat din grupul de firme Total NSA" (Turnul Sfatului, 2026-05-17). **[unconfirmed in registry]** |
| 6 | PRO HART GROUP SRL | 22170774 | J2007001277325 (J32/1277/2007) | 2007-07-26 | 4322 plumbing, HVAC (4120 in FY2019) | Str. Triajului nr. 46, Sibiu | yes | MEP / installations; standing JV partner of AG Construct | Logo on group page ("sigla-prohart-group"). Press snippet: "Ioan Domnariu a adus firma PROHART GROUP Sibiu la o cifra de afaceri de circa 30 milioane" **[unconfirmed]** |
| 7 | TOTAL N.S.A. GRUP SRL | 21244962 | J2007000394324 | 2007-03-01 | 4683 (ANAF registry) / 4673 (balance sheet) wholesale | Str. Andrei Șaguna nr. 61, Săliște (same as #2) | yes | Small trading / holding vehicle (1-2 employees) | Confirmed: same address as Total N S A, logo "Total NSA Grup" |
| 8 | GETICA SRL | 13884286 | J32/280/2001 | 2001-05-15 | 0812 gravel and sand | Str. Foltești nr. 3, Săliște | yes | Dormant gravel licence holder (no revenue) | Logo "sigla-getica" on group page. Săliște match; **ownership unconfirmed** |
| 9 | OLIMPIA SERVICII INTERNATIONALE SRL | 15619510 | J2016000517321 (registered 2003; moved to Sibiu 2016) | 2003-07-25 | 7020 consulting (6820 real-estate rental in FY2024-25) | Șelimbăr nr. 1, DC 56, jud. Sibiu | yes | Property-holding / rental (1 employee) | Logo on group page; exact-name match is the only such company in Romania. **Ownership unconfirmed** |
| 10 | TOP PROIECT SRL | 15391152 | J2003001059127 | 2003-04-22 | 7112 engineering / design | Str. Copernicus nr. 7, Cluj-Napoca | yes | Possibly design / engineering partner | Logo "sigla-top-proiect" on group page. This is the only exact "TOP PROIECT SRL" in the registry, **but it is based in Cluj. The link is unconfirmed**, so treat this match as tentative |
| - | "PC Privat Consulting" | not found | - | - | - | - | - | Logo on group page | No exact registry match found on infoquick. Closest is "PRIVAT CONSULTING S.R.L." (15733867, Deva), which was struck off in 2011 and is not relevant |
| - | "Total NSA Imobiliare" | not found as a legal entity | - | - | - | - | - | Real-estate brand (Facebook page "TOTAL NSA Imobiliare", Sibiu) | Probably a trade name used by Total N S A, Total NSA Invest or Olimpia. **Unresolved** |
| - | "Total NSA Truks" | not found as a legal entity | - | - | - | - | - | Truck sales / service brand | **Unresolved**. May be a trade name of Total N S A or Total N.S.A. Grup |

The group page itself is <https://www.totalnsa.ro/ro/companii/>. Its logo files include sigla-total-nsa, -total-nsa-ag-construct, -total-nsa-invest, -total-nsa-imobiliare, -total-nsa-grup, -total-nsa-truks, -top-proiect, -prohart-group, -getica, -pc-privat-consulting and -olimpia-servicii-internationale.

### Activity codes of TOTAL NSA AG CONSTRUCT (registry objects, via totalfirme.ro)

- **Main:** 4100 (formerly 4120): construction of residential and non-residential buildings.
- **Secondary codes shown (43 of 81 authorised):**
  - Materials: 2363, 2364
  - Waste: 3811, 3812, 3821
  - Civil engineering: 4211, 4212, 4213, 4221, 4222, 4291, 4299
  - Specialised works: 4311, 4312, 4313, **4321, 4322**, 4323, 4324, 4331-4335, 4341, 4342, 4350, 4391, **4399**
  - Trade and transport: 4613, 4683, 4932, 4939, 4941, 5210, 5224
  - Real estate and consulting: 6811, 6812, 6820, 7020, **7112**
  - Other: 8130, 9130
- **Reading:** this is a full-scope general contractor licence covering buildings, roads (4211), utilities (4221/4222), MEP (4321/4322), restoration (9130) and in-house engineering (7112).

### Shareholders and administrators (as published)

| Entity | Associates (published) | Administrators (published) | Source / confidence |
|---|---|---|---|
| TOTAL NSA AG CONSTRUCT | 5 associates. termene.ro shows initials **R.M.E., D.I., P.D.C.** (others hidden). D.I. corresponds to **Ioan Domnariu**, called "principalul asociat" by Turnul Sfatului (2022, 2026) | 2 administrators: **ROMAN Eugen Mihai** and **PĂSCUȚIU Cristian Ștefan** (sicap.ai representatives; Roman also appears in court records) | Search-engine snippets of termene.ro and sicap.ai; press. **Percentages not available** |
| TOTAL N S A | 3 associates. termene.ro initials **D.I., D.D.E., D.A.I.** (Domnariu family) | 1 administrator | termene snippet. In 2012 Ana Domnariu became sole associate and Ioan Domnariu stayed administrator (Turnul Sfatului 2012-07-12); the structure has changed since |
| EUROFOR 2011 | 3 associates, controlled by Ioan Domnariu (press) | 1 administrator: **Iosif Cristian Petruța** (Turnul Sfatului 2023) | Press plus termene snippet |
| Others | not retrieved | not retrieved | ONRC extract needed |

Capital: TOTAL NSA AG CONSTRUCT has 500,000 RON subscribed share capital (ANAF I11 FY2024). TOTAL N S A has 11,000,000 RON (totalfirme).

---

## 3. Group structure: who does what

```
                         Ioan Domnariu (founder / main associate, per press)
                                              |
   -----------------------------------------------------------------------------------------
   |                    |                       |                  |                        |
 LOGISTICS          CONSTRUCTION           AGGREGATES          CONCRETE              REAL ESTATE / OTHER
 TOTAL N S A        TOTAL NSA AG           EUROFOR 2011        DPS BETON (*)         Total N.S.A. Grup
 (9315010)          CONSTRUCT (36594214)   (29536210, quarry)  (33074365)            Olimpia Servicii Int. (*)
 trucks, bulk,      general contractor,    TOTAL NSA INVEST    + "Cife Beton" mixer  "Total NSA Imobiliare" brand
 tippers, mixers    public works, roads    (33469225, gravel)    trucks run by        Getica (*) dormant gravel
                    + JV partner           GETICA (*) dormant    Total N S A
                    PRO HART GROUP (*)
                    (22170774, MEP)
                    + TOP PROIECT (*) design?
(*) = link based on group-page logo or press only, not confirmed in a registry
```

- **Construction entity:** **TOTAL NSA AG CONSTRUCT SRL** carries the construction activity. It is the company that bids and signs public works contracts. Total N S A (logistics) does **not** appear as the contractor on any of the construction contracts found.
- **Materials and equipment flow:**
  - Total N S A's fleet supplies the tippers (100), ballast trucks (7) and "Cife Beton" concrete mixers (5) (totalnsa.ro fleet page).
  - Eurofor 2011 and Total NSA Invest supply crushed stone, sand and gravel, which fits the coordinator's "7 gravel pits / Balomir" lead. Balomiru de Câmp is near Beldiu/Teiuș in Alba county, where Total NSA Invest is registered.
  - DPS Beton supplies ready-mix concrete and asphalt.
- **Developer side:** Total N S A itself bought a 27 ha site in Săliște (2016, 1.98 M lei). It is building a cross-dock logistics park there (more than 28.8 M lei, 2024-2027), and the halls are rented to a logistics operator. The likely contractor for these halls is AG Construct, but this is not confirmed. "Total NSA Imobiliare" is the consumer-facing real-estate brand.

---

## 4. Per-entity yearly financials (official ANAF filings)

- **Columns:** amounts in **M RON**. Turnover is "cifra de afaceri netă" (I13). Total revenue is I14. Net profit is I18 minus I19. Average employees is I20.
- **\*Total assets** = fixed assets (I1) + current assets (I2) + prepaid expenses (I6).
- **Source:** `https://webservicesp.anaf.ro/bilant?an=YYYY&cui=CUI`.
- **Confirmation:** AG Construct and Total N S A rows were cross-checked line by line with totalfirme.ro and match exactly (2 sources). Other entities have ANAF as the official single source. Their FY2024-25 headline figures agree with the termene, risco and EMIS search snippets where those appeared (Pro Hart 2024: 104.27 M / 12.0 M per risco; 2025: 131.4 M / 14.1 M per termene; Eurofor 2025: 112.7 M / 3.4 M / 226 per termene; DPS 2025: 34.16 M per search snippet; Total NSA Invest 2021: 7.23 M / 3,640 per confidas).

### TOTAL NSA AG CONSTRUCT SRL (construction) - CUI 36594214

| Year | Turnover (CA neta) | Total revenue | Net profit (loss) | Net margin | Avg. employees | Total assets* | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 71.36 | 71.68 | 1.06 | 1.5% | 117 | 15.36 | 12.62 | 2.74 |
| 2020 | 39.76 (-44.3%) | 40.55 | 1.48 | 3.7% | 128 | 15.26 | 11.15 | 4.12 |
| 2021 | 51.66 (+29.9%) | 52.82 | 2.59 | 5.0% | 133 | 26.24 | 19.88 | 6.36 |
| 2022 | 93.10 (+80.2%) | 93.19 | 4.70 | 5.0% | 135 | 32.42 | 23.59 | 8.83 |
| 2023 | 111.66 (+19.9%) | 115.00 | 6.13 | 5.5% | 147 | 54.87 | 39.91 | 14.96 |
| 2024 | 141.00 (+26.3%) | 142.51 | 6.10 | 4.3% | 136 | 49.89 | 28.83 | 21.06 |
| 2025 | 132.46 (-6.1%) | 135.92 | 2.49 | 1.9% | 149 | 38.23 | 14.68 | 23.55 |

### TOTAL N S A SRL (logistics / transport) - CUI 9315010

| Year | Turnover (CA neta) | Total revenue | Net profit (loss) | Net margin | Avg. employees | Total assets* | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 178.58 | 199.21 | 4.21 | 2.4% | 414 | 152.08 | 101.60 | 48.57 |
| 2020 | 139.43 (-21.9%) | 154.27 | 8.58 | 6.2% | 380 | 150.97 | 91.61 | 57.15 |
| 2021 | 172.40 (+23.6%) | 194.16 | 11.36 | 6.6% | 393 | 183.33 | 113.96 | 68.51 |
| 2022 | 212.89 (+23.5%) | 257.90 | 25.74 | 12.1% | 318 | 222.27 | 126.19 | 94.24 |
| 2023 | 174.05 (-18.2%) | 204.01 | 17.19 | 9.9% | 245 | 252.54 | 139.17 | 111.39 |
| 2024 | 221.17 (+27.1%) | 271.05 | 28.01 | 12.7% | 248 | 303.37 | 161.41 | 139.40 |
| 2025 | 200.24 (-9.5%) | 198.77 | 20.70 | 10.3% | 241 | 308.93 | 144.76 | 160.10 |

### EUROFOR 2011 SRL (quarry / crushed stone) - CUI 29536210

| Year | Turnover (CA neta) | Total revenue | Net profit (loss) | Net margin | Avg. employees | Total assets* | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 6.16 | 6.97 | 2.20 | 35.8% | 16 | 4.94 | 2.85 | 2.09 |
| 2020 | 8.08 (+31.3%) | 8.74 | 2.00 | 24.7% | 24 | 13.25 | 9.16 | 4.09 |
| 2021 | 27.27 (+237.4%) | 28.76 | 2.99 | 11.0% | 61 | 26.62 | 19.53 | 7.08 |
| 2022 | 55.43 (+103.3%) | 64.81 | 3.15 | 5.7% | 180 | 48.34 | 38.10 | 10.24 |
| 2023 | 75.17 (+35.6%) | 91.51 | 0.10 | 0.1% | 244 | 82.96 | 72.62 | 10.34 |
| 2024 | 97.26 (+29.4%) | 120.70 | 2.12 | 2.2% | 245 | 94.46 | 82.00 | 12.46 |
| 2025 | 112.68 (+15.9%) | 138.12 | 3.45 | 3.1% | 226 | 117.39 | 100.79 | 15.91 |

### TOTAL NSA INVEST S.R.L. (gravel and sand) - CUI 33469225

| Year | Turnover (CA neta) | Total revenue | Net profit (loss) | Net margin | Avg. employees | Total assets* | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 7.41 | 11.73 | 1.85 | 25.0% | 21 | 7.41 | 4.06 | 3.35 |
| 2020 | 7.19 (-3.0%) | 11.48 | 1.34 | 18.7% | 22 | 9.59 | 4.93 | 4.66 |
| 2021 | 7.23 (+0.6%) | 12.59 | 0.00 | 0.1% | 27 | 17.55 | 12.89 | 4.66 |
| 2022 | 14.06 (+94.4%) | 19.32 | 0.24 | 1.7% | 37 | 15.94 | 11.84 | 4.10 |
| 2023 | 17.66 (+25.7%) | 24.92 | 1.29 | 7.3% | 43 | 18.98 | 13.59 | 5.39 |
| 2024 | 20.38 (+15.4%) | 28.59 | 1.28 | 6.3% | 47 | 24.28 | 17.61 | 6.67 |
| 2025 | 20.72 (+1.7%) | 30.71 | 1.01 | 4.9% | 47 | 25.10 | 17.42 | 7.68 |

### DPS BETON S.R.L. (concrete and asphalt) - CUI 33074365

| Year | Turnover (CA neta) | Total revenue | Net profit (loss) | Net margin | Avg. employees | Total assets* | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 0.00 | 0.24 | -0.17 | n/a | 0 | 5.14 | 5.44 | -0.30 |
| 2020 | 9.49 | 10.10 | 0.91 | 9.6% | 9 | 8.85 | 8.24 | 0.60 |
| 2021 | 19.82 (+108.8%) | 19.90 | 2.06 | 10.4% | 19 | 13.89 | 11.22 | 2.66 |
| 2022 | 23.53 (+18.7%) | 23.61 | 0.94 | 4.0% | 22 | 11.18 | 7.57 | 3.61 |
| 2023 | 25.37 (+7.8%) | 25.64 | 2.67 | 10.5% | 20 | 16.01 | 9.73 | 6.28 |
| 2024 | 35.71 (+40.8%) | 35.79 | 3.40 | 9.5% | 23 | 18.00 | 8.33 | 9.68 |
| 2025 | 34.16 (-4.4%) | 34.61 | 1.63 | 4.8% | 25 | 18.45 | 7.15 | 11.31 |

### PRO HART GROUP SRL (MEP installations; recurring JV partner) - CUI 22170774

| Year | Turnover (CA neta) | Total revenue | Net profit (loss) | Net margin | Avg. employees | Total assets* | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 31.84 | 32.67 | 2.41 | 7.6% | 77 | 10.76 | 6.92 | 3.83 |
| 2020 | 31.40 (-1.4%) | 34.54 | 4.40 | 14.0% | 94 | 28.81 | 21.55 | 7.03 |
| 2021 | 44.02 (+40.2%) | 48.35 | 1.76 | 4.0% | 122 | 33.67 | 25.07 | 8.57 |
| 2022 | 65.57 (+48.9%) | 64.79 | 2.27 | 3.5% | 120 | 29.94 | 20.66 | 9.24 |
| 2023 | 61.31 (-6.5%) | 64.41 | 9.18 | 15.0% | 130 | 51.36 | 32.89 | 18.42 |
| 2024 | 104.27 (+70.1%) | 117.77 | 12.00 | 11.5% | 168 | 72.90 | 49.32 | 23.29 |
| 2025 | 131.36 (+26.0%) | 131.34 | 14.06 | 10.7% | 200 | 89.24 | 56.86 | 32.35 |

### TOTAL N.S.A. GRUP SRL - CUI 21244962

| Year | Turnover (CA neta) | Total revenue | Net profit (loss) | Net margin | Avg. employees | Total assets* | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 1.87 | 2.22 | 0.26 | 14.0% | 2 | 3.90 | 0.34 | 3.56 |
| 2020 | 1.84 (-1.3%) | 2.02 | 0.28 | 15.3% | 2 | 3.52 | 0.28 | 3.23 |
| 2021 | 1.81 (-1.6%) | 1.82 | 0.92 | 50.7% | 2 | 4.33 | 0.17 | 4.15 |
| 2022 | 0.92 (-49.1%) | 1.02 | 0.52 | 56.0% | 2 | 5.76 | 2.29 | 3.47 |
| 2023 | 0.52 (-43.6%) | 2.57 | 2.17 | 416.4% | 1 | 6.22 | 1.10 | 5.12 |
| 2024 | 0.17 (-68.1%) | 0.34 | -0.00 | -2.4% | 1 | 6.16 | 1.05 | 5.12 |
| 2025 | 0.03 (-81.4%) | 1.01 | 0.55 | 1782.2% | 1 | 6.89 | 1.18 | 5.71 |

### GETICA SRL - CUI 13884286

| Year | Turnover (CA neta) | Total revenue | Net profit (loss) | Net margin | Avg. employees | Total assets* | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 0.00 | 0.00 | -0.03 | n/a | 1 | 1.95 | 1.78 | 0.18 |
| 2020 | 0.00 | 0.00 | -0.03 | n/a | 0 | 1.94 | 1.80 | 0.14 |
| 2021 | 0.00 | 0.00 | -0.03 | n/a | 0 | 2.04 | 1.92 | 0.12 |
| 2022 | 0.00 | 0.00 | -0.06 | n/a | 0 | 2.39 | 2.33 | 0.05 |
| 2023 | 0.00 | 0.02 | -0.04 | n/a | 0 | 2.45 | 2.44 | 0.02 |
| 2024 | 0.00 | 0.07 | -0.04 | n/a | 0 | 2.42 | 2.45 | -0.02 |
| 2025 | 0.01 | 0.06 | -0.03 | -244.8% | 0 | 2.30 | 2.36 | -0.05 |

### OLIMPIA SERVICII INTERNATIONALE SRL - CUI 15619510

| Year | Turnover (CA neta) | Total revenue | Net profit (loss) | Net margin | Avg. employees | Total assets* | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 0.31 | 0.33 | 0.24 | 75.2% | 1 | 1.69 | 0.09 | 1.61 |
| 2020 | 0.35 (+11.0%) | 0.36 | 0.28 | 80.1% | 1 | 1.88 | 0.51 | 1.36 |
| 2021 | 1.51 (+333.2%) | 4.51 | 3.16 | 208.6% | 0 | 4.61 | 0.38 | 4.23 |
| 2022 | 0.74 (-50.9%) | 0.96 | 0.59 | 79.2% | 1 | 4.88 | 0.82 | 4.06 |
| 2023 | 0.33 (-55.9%) | 4.82 | 0.18 | 54.0% | 1 | 12.32 | 8.08 | 4.24 |
| 2024 | 0.47 (+44.7%) | 1.12 | 0.30 | 63.5% | 1 | 13.12 | 8.93 | 4.19 |
| 2025 | 0.55 (+16.9%) | 0.62 | 0.00 | 0.8% | 1 | 10.68 | 6.49 | 4.19 |

### TOP PROIECT SRL (Cluj-Napoca) - CUI 15391152

| Year | Turnover (CA neta) | Total revenue | Net profit (loss) | Net margin | Avg. employees | Total assets* | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 0.80 | 0.86 | 0.33 | 40.9% | 5 | 0.98 | 0.15 | 0.82 |
| 2020 | 0.55 (-32.1%) | 0.57 | 0.13 | 23.0% | 6 | 1.09 | 0.14 | 0.95 |
| 2021 | 1.17 (+115.0%) | 1.18 | 0.37 | 31.8% | 7 | 1.78 | 0.74 | 1.04 |
| 2022 | 1.14 (-3.0%) | 1.14 | 0.42 | 36.9% | 7 | 2.09 | 0.63 | 1.46 |
| 2023 | 1.25 (+9.7%) | 1.25 | 0.08 | 6.2% | 7 | 2.24 | 0.87 | 1.37 |
| 2024 | 1.24 (-0.7%) | 1.24 | 0.22 | 17.3% | 7 | 2.74 | 1.02 | 1.57 |
| 2025 | 1.34 (+7.8%) | 2.29 | 0.67 | 49.9% | 5 | 3.47 | 1.09 | 2.24 |

### TOTAL NSA AG CONSTRUCT: early years (FY2016-2018) [1 source: totalfirme.ro / MFinante]

| Year | Turnover | Total revenue | Net profit | Employees | Fixed assets | Current assets | Debts | Equity |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2016 (3 months) | 0.11 | 0.37 | 0.0008 | 59 | 0.01 | 0.44 | 0.46 | 0.001 |
| 2017 | 11.83 | 11.73 | 0.32 | 79 | 0.34 | 3.30 | 3.33 | 0.32 |
| 2018 | 18.25 | 18.60 | 1.79 | 108 | 1.39 | 5.45 | 4.77 | 2.11 |

**Currency caveat.** listafirme.eu shows AG Construct's 2025 turnover as about "25.98 million" and risco.ro shows 26.27 M EUR. Both are **EUR conversions** of the same 132.46 M RON. They are not a different figure.

### TOTAL N S A: long series FY2010-2018 (turnover / net profit / employees, M RON) [1 source: totalfirme.ro]

2010: 72.97 / 2.17 / 190 · 2011: 98.23 / 0.02 / 250 · 2012: 142.03 / 1.81 / 305 · 2013: 173.52 / 10.72 / 338 · 2014: 197.48 / 2.23 / 368 · 2015: 235.63 / 9.49 / 397 · 2016: 205.41 / 1.88 / 407 · 2017: 194.69 / 0.29 / 455 · 2018: 168.99 / 0.74 / 424

Turnul Sfatului (2017) separately reports 2016 turnover of "peste 205 milioane lei" (about 13% below 2015), which confirms the 2016 figure.

---

## 5. Growth trends and analysis (construction entity)

| Metric | TOTAL NSA AG CONSTRUCT |
|---|---|
| Turnover CAGR 2017→2024 | 11.8 M → 141.0 M, about **+43% a year** |
| Turnover CAGR 2020→2024 | 39.8 M → 141.0 M, about **+37% a year** |
| Turnover CAGR 2019→2025 | 71.4 M → 132.5 M, about **+11% a year** |
| 2019 spike / 2020 dip | 71.4 M in 2019, then -44% in 2020. This points to large one-off contract(s) in 2019, such as the ANL blocks contract signed Nov 2019 and county works |
| Peak | FY2024: 141.0 M turnover, 6.10 M net profit |
| FY2025 | -6.1% turnover. Net profit -59% to 2.49 M. Margin fell to 1.9%, the lowest since 2019 |
| Net margin range | 1.5%-5.5% (2019-2024). Thin, which is typical of public-tender general contracting |
| Headcount | 117 → 149 (2019-2025), only +27% while turnover nearly doubled. This implies heavy subcontracting (for example Pro Hart for MEP) and use of group equipment |
| Revenue per employee FY2025 | about 0.89 M RON |
| Balance sheet FY2025 | Total assets about 38.2 M. Debts fell from 39.9 M (2023) to 14.7 M. Equity rose to 23.5 M, about **62% equity ratio**. Cash 5.2 M. Inventories 10.8 M, the highest yet (materials or work in progress) |
| Receivables | Fell from 30.7 M (2023) to 12.2 M (2025). Collections improved, or the backlog is smaller |
| Fixed assets | About 9.6-10.9 M. Equipment is light because heavy fleet sits in Total N S A and Eurofor |

**Related entities, in brief:**

- **Total N S A (logistics):** flat to slightly growing turnover (139 M to 221 M), with high and rising profitability (10-13% net margin since 2022). Equity has tripled since 2019 to 160 M and fixed assets are 214 M, so it is the group's asset-heavy core.
- **Eurofor 2011:** grew 18× from 2019 to 2025 (6.2 M to 112.7 M), a fast expansion with a thin margin of 3.1%. It is highly leveraged, with debts of 100.8 M against equity of 15.9 M. It is the second-largest entity linked to construction.
- **Pro Hart Group:** grew 4× from 2019 to 2025 (31.8 M to 131.4 M) with strong margins of 10-15%. It is now roughly the same size as AG Construct, with 200 employees.
- **DPS Beton:** grew from 9.5 M to 34.2 M (2020-2025).
- **Total NSA Invest:** grew from 7.4 M to 20.7 M.

### National rankings (infoquick.ro, latest data FY2025) [1 source]

| Entity | CAEN | Rank by turnover | By total revenue | By net profit | By employees |
|---|---|---|---|---|---|
| TOTAL NSA AG CONSTRUCT | 4120 building construction | **24 / 19,694** | 27 | 295 | 30 |
| TOTAL N S A | 4941 road freight | **26 / 37,848** | 31 | 5 | 51 |
| EUROFOR 2011 | 0811 stone quarrying | **3 / 225** | 3 | 19 | 2 |
| TOTAL NSA INVEST | 0812 gravel and sand | 29 / 807 | 18 | 80 | 22 |
| DPS BETON | 2363 concrete | 33 / 275 | 33 | 31 | 61 |
| PRO HART GROUP | 4322 MEP | **15 / 9,460** | 16 | 11 | 13 |
| TOP PROIECT (Cluj) | 7112 engineering | 2,089 / 16,646 | 1,358 | 1,257 | 1,433 |

**County rankings.**

- **Total N S A:** Turnul Sfatului (2024) calls it "cea mai mare firmă de transport mărfuri din județ" by turnover, profit and employees.
- **AG Construct:** a county-level CAEN 4120 ranking was not retrievable (listafirme.ro and termene.ro were blocked). A turnover of 132-141 M RON almost certainly puts it in the **top 3 building contractors in Sibiu county**, but this is an estimate, not confirmed.

---

## 6. Public procurement (SEAP/SICAP) presence: TOTAL NSA AG CONSTRUCT

AG Construct is a very active public-works bidder, mainly with Sibiu municipality, Sibiu county council (CJ Sibiu), Săliște town hall, CNI and ULBS.

| Contract / tender | Authority | Value | Year | Status | Source |
|---|---|---|---|---|---|
| Two new ANL blocks of flats, Sibiu | ANL / Primăria Sibiu | n/a | 2019 (signed) | signed | turnulsfatului.ro 2019-11-11 |
| 3 of 5 works at Spitalul Clinic Județean Sibiu: Neurology ward (JV with Pro Hart), "spitalul nou"/Maternity rehabilitation, UPU extension | CJ Sibiu | about 49.6 M lei initially, rising to more than 85 M lei (+70%) via addenda | 2020-2022 | delays reported; UPU inaugurated Nov 2022 | turnulsfatului.ro 2022-11-13 |
| Energy efficiency, Colegiul „Octavian Goga” | Primăria Sibiu | 14.13 M lei | Feb 2024 | awarded | transilvaniabusiness.ro 2024-02-07 |
| Roads and public lighting, Veterani district (JV with Pro Hart) | Primăria Sibiu | 13.82 M lei | Nov 2024 | signed | turnulsfatului.ro 2024-11-07 |
| Waste collection centre, Dealul Gușteriței (PNRR) | Primăria Sibiu | est. 25.7 M lei excl. VAT | Nov 2024 | bidder (with Terra Building, Prenis) | turnulsfatului.ro 2024-11-07 |
| County waste management system (SMID) modernisation | CJ Sibiu | n/a | - | bidder (vs Con-A) | tribuna.ro |
| Largest creșă in Sibiu, Str. Viitorului 28A (JV with ING Proiect Management and Pro Hart), design and build, 50 months | CNI | **18.14 M lei** excl. VAT | Mar 2025 | awarded | turnulsfatului.ro 2025-03-10 |
| Extension of ULBS Faculty of Engineering (JV with Pro Hart) | ULBS | 25.3 M lei | May-Jul 2025 | awarded, then CNSC ordered re-evaluation ("preț neobișnuit de scăzut") | turnulsfatului.ro 2025-07-24 |
| 17 contracts, mostly roads | Primăria Săliște | more than 22 M lei (initial, excl. VAT) | about 2020-2025 | executed; Court of Accounts audit; AG Construct paid 2.95 M lei damages | turnulsfatului.ro 2026-02-01 |
| Parks Vasile Aaron and Tineretului (JV leader, with Pro Hart and Well Plast) | Primăria Sibiu | n/a | Oct 2026 | tender cancelled | turnulsfatului.ro 2026-10-08 |

**Aggregate figure from sicap.ai (search snippet):** "252 contracte atribuite în valoare de 1.790.432.488,99 RON / 358.086.497,80 EUR". The same snippet lists 6 contracts not awarded, worth 15.7 M RON.

- **This total is NOT confirmed and is very likely inflated.** It is about 2.7 times AG Construct's cumulative 2016-2025 turnover of about 671 M RON.
- **Likely reasons:** it probably counts full JV contract values, framework-agreement ceilings and duplicate or addendum entries. Use it only as a sign of high SEAP activity.
- **Not checked further:** the sicap.ai pages (/firma/36594214 and /achizitii/firma/161219) returned HTTP 403 or 429.

Total N S A (CUI 9315010) also has a SICAP profile: sicap.ai/achizitii/firma/71341 and /licitatii/firma/71341. Its contents were not retrievable.

---

## 7. Litigation, insolvency, tax status

| Check | TOTAL NSA AG CONSTRUCT | TOTAL N S A | Source |
|---|---|---|---|
| Insolvency (BPI) | **Not listed** | Not listed | totalfirme.ro; juridice.consultanti.ro (no insolvency file with AG Construct as debtor) |
| Insolvency-risk score | 9.27% "Foarte scăzut" | 37.46% "Ușor" | totalfirme.ro [1 source] |
| State-budget debts at 31.12.2025 | None | None | totalfirme.ro (ANAF list) [1 source] |
| VAT | Registered since 31.10.2016. No TVA la încasare, no split VAT, **not inactive** | VAT since 01.06.1997, same flags | ANAF API (official) |
| Tax office | AF Contribuabili Mijlocii Sibiu (mid-size taxpayer) | same | ANAF |
| RO e-Factura register | statusRO_e_Factura = false (field in ANAF API) | false | ANAF |
| Court cases | **About 26 case numbers (29 records), 2023-2026**, never as plaintiff | not checked | juridice.consultanti.ro |

**AG Construct court-case themes:**

- **Public-procurement contract-execution suits as defendant (pârât):** Tribunalul Sibiu 2565/85/2023 (as JV leader), 1238/85/2024 (appealed at CA Alba Iulia 2025-2026), 102/85/2026.
- **Many CNSC-decision challenges at CA Alba Iulia (2025-2026),** both as petitioner and as respondent. These are typical of an aggressive bidder.
- **Contractual-damages claims:** Judecătoria Sibiu 2452/306/2024 and 18376/306/2025.
- **Administrative-act annulment and suspension (2026)** and contravention complaints.
- **Criminal file:** 15185/306/2026, "purtarea abuzivă" (art. 296 NCP). The company appears only as *parte responsabilă civilmente*, which suggests an employee incident.

**Press / reputational flags (not legal findings):**

- Turnul Sfatului has published investigations into contract cost overruns at Spitalul Județean (2022) and into a preferential rent linked to the Domnariu family and the CJ president (2022, denied).
- Its Săliște "Oraș la stăpân" article (2026) covers the concentration of town-hall contracts and Court of Accounts findings.
- It also reported on Eurofor's quarry access onto the DN1 and excavation-tax disputes (2023, 2026).
- In 2021 it reported a DNA-requested inquiry involving trucks on the unfinished motorway; the group's involvement is not established.

---

## 8. Source URLs

**Official (ANAF):**

- Balance sheets: `https://webservicesp.anaf.ro/bilant?an={2019..2025}&cui={36594214, 9315010, 29536210, 33469225, 33074365, 22170774, 21244962, 13884286, 15619510, 15391152}`
- VAT / registry: `https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva` (POST, queried 2026-10-15)

**Aggregators:**

- https://www.totalfirme.ro/total-nsa-ag-construct-srl-36594214
- https://www.totalfirme.ro/total-nsa-srl-9315010
- https://www.infoquick.ro/verificare-firme/total-nsa-ag-construct-srl-36594214 (and the matching slugs for 9315010, 29536210, 33469225, 33074365, 22170774, 21244962, 13884286, 15619510, 15391152)
- https://termene.ro/firma/36594214-TOTAL-NSA-AG-CONSTRUCT-SRL (snippet only)
- https://termene.ro/firma/9315010-TOTAL-N-S-A-SRL (snippet only)
- https://termene.ro/firma/29536210-EUROFOR-2011-SRL (snippet only)
- https://termene.ro/en/firma/22170774-PRO-HART-GROUP-SRL (snippet only)
- https://www.risco.ro/en/verifica-firma/total-nsa-ag-construct-cui-36594214 (snippet only)
- https://www.risco.ro/en/verifica-firma/pro-hart-group-cui-22170774 (snippet only)
- https://listafirme.eu/total-nsa-ag-construct-srl-36594214/ (snippet only; EUR figures)
- https://www.confidas.ro/profil/33469225/total-nsa-invest-srl (snippet only)
- http://www.firme.info/total-nsa-ag-construct-srl-cui36594214/
- https://www.emis.com/php/company-profile/RO/Total_Nsa_Ag_Construct_SRL_en_13026982.html
- https://www.emis.com/php/company-profile/RO/Pro_Hart_Group_SRL_en_4290226.html
- https://sicap.ai/firma/36594214 (snippet only)
- https://sicap.ai/achizitii/firma/71341 (blocked)
- https://juridice.consultanti.ro/parte-total-nsa-ag-construct-srl

**Company:**

- https://www.totalnsa.ro/ro/companii/ (group logos)
- https://www.totalnsa.ro/ro/parc-auto/cife-beton
- https://www.totalnsa.ro/en/team/

**Press:**

- https://www.turnulsfatului.ro/2022/11/13/secretul-presedintei-cimpean-sta-in-chirie-preferentiala-la-familia-care-a-primit-contracte-de-milioane-de-euro-la-spitalul-judetean-198130
- https://www.turnulsfatului.ro/2025/03/10/o-asociere-condusa-de-total-nsa-ag-construct-va-construi-cea-mai-mare-cresa-din-sibiu-aceasta-se-va-afla-pe-strada-viitorului-218241
- https://www.turnulsfatului.ro/2024/11/07/asocierea-total-nsa-si-pro-hart-group-va-reabilita-drumurile-si-iluminatul-public-din-cartierul-veterani-lucrarile-incep-in-primavara-215414
- https://www.turnulsfatului.ro/2024/11/07/terra-building-total-nsa-ag-construct-din-sibiu-si-prenis-din-blaj-vor-sa-construiasca-centrul-de-colectare-a-deseurilor-din-dealul-gusteritei-215385
- https://www.turnulsfatului.ro/2025/07/24/extinderea-facultatii-de-inginerie-blocata-la-licitatie-ulbs-obligata-sa-reevalueze-oferta-total-nsa-pretul-pentru-organizarea-de-santier-considerat-neobisnuit-de-scazut-221622/
- https://www.turnulsfatului.ro/2026/10/08/a-treia-mare-licitatie-anulata-la-sibiu-cea-pentru-noile-parcuri-din-vasile-aaron-si-cartierul-tineretului-concurau-aceiasi-constructori-ca-si-la-sub-arini/
- https://www.turnulsfatului.ro/2026/02/01/saliste-oras-la-stapan-226189
- https://www.turnulsfatului.ro/2026/05/17/in-spatele-mamei-legaturile-fiilor-lui-astrid-fodor-cu-firme-interesate-de-banii-si-bunavointa-administratiei-sibiului/
- https://www.turnulsfatului.ro/2023/11/22/cu-n-primar-care-inchide-ochii-balastiera-lui-domnariu-a-transformat-drumul-national-intr-o-balta-de-noroi-207302
- https://www.turnulsfatului.ro/2024/02/12/cea-mai-mare-firma-de-transport-marfuri-din-judet-investeste-28-de-milioane-de-lei-in-dezvoltarea-unei-zone-industriale-si-logistice-langa-autostrada-209041
- https://www.turnulsfatului.ro/2019/11/11/a-fost-semnat-contractul-pentru-ridicarea-a-doua-noi-blocuri-anl-in-sibiu-157323
- https://www.turnulsfatului.ro/2017/07/02/cele-mai-mari-afaceri-romanesti-din-sibiu-cum-au-inceput-sa-semene-cu-multinationalele-87525
- https://www.turnulsfatului.ro/2012/07/12/ioan-domnariu-a-cedat-actiunile-de-la-total-nsa-rdquo-chestii-personale-rdquo-15958
- https://www.transilvaniabusiness.ro/2024/02/07/total-nsa-ag-construct-srl-contract-de-1413-milioane-lei-cu-primaria-sibiu/
- https://www.tribuna.ro/con-a-operations-si-total-nsa-ag-construct-au-depus-oferte-pentru-licitatia-privind-modernizarea-sistemului-de-management-integrat-al-deseurilor-din-judetul-sibiu/

## 9. Open items / next steps

1. **ONRC "Certificat constatator"** (paid, through recom.onrc.ro or openapi.ro with an API key) for 36594214, 22170774, 33074365, 29536210 and 15391152. This would confirm shareholder percentages and whether Pro Hart, DPS Beton and Top Proiect are owned by Domnariu.
2. **Legal entities behind "Total NSA Imobiliare", "Total NSA Truks" and "PC Privat Consulting".** Not found under those names. They may be trade names, or the companies may have been renamed.
3. **SICAP contract list for CUI 36594214** from e-licitatie.ro or data.gov.ro open procurement datasets, to replace the unverified 1.79 bn RON aggregate.
4. **County CAEN 4120 ranking for Sibiu** from listafirme.ro or topfirme.com (blocked from this environment).
