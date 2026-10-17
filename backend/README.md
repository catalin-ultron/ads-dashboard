# NSA Construction Backend

Backend for a public-works contractor of Total NSA's scale. Design: [../construction-map/lead/04-codebase-map.md](../construction-map/lead/04-codebase-map.md).

## Implemented

| Module | Path | Domains | Basis |
|---|---|---|---|
| CPM engine adapter | `src/nsa/schedule/engine/mpxj_adapter.py` | D06 | MPXJ `org.mpxj.cpm.PrimaveraScheduler` (LGPL-2.1+, used unchanged via PyPI `mpxj` + JPype) |
| Schedule types | `src/nsa/schedule/model/types.py` | D03–D05 | Canonical model |
| Schedule service | `src/nsa/schedule/service.py` | D06 | Loads a stored schedule, runs CPM, writes dates/float/criticality, logs the run |
| Schedule file I/O | `src/nsa/integration/schedule_files.py` | D35 | MPXJ UniversalProjectReader / UniversalProjectWriter: reads XER, PMXML, MSPDI, MPP, MPX and more; writes XER, PMXML, MSPDI, MPX, Planner, SDEF, JSON |
| Price adjustment | `src/nsa/contracts/priceadjust.py` | D40.02 | OUG 64/2022 art. 17(8) formula and reference-month rule |
| Good-execution retention | `src/nsa/contracts/guarantees.py` | D38.02 | Legea 98/2016 art. 154, HG 395/2016 art. 39–42: ≤10% target, ≥0.5% initial deposit, 70/30 release, calls and restoration |
| Situație de lucrări | `src/nsa/billing/situatii.py` | D39.04–05 | Cumulative cap against contract + approved NCS quantity, hidden-works PV gate, centralizator, JV split |
| Billing service | `src/nsa/billing/service.py` | D39, D38, D40 | Builds and persists a monthly situație: prior cumulative quantities, retention ledger, OUG 64/2022 run for EU/PNRR contracts |
| Permissions | `src/nsa/platform/identity/permissions.py` | D02 | Role-union grants, company-wide or contract-scoped memberships, wildcard patterns, query scoping; design inspired by Frappe (MIT) and OpenProject memberships (spec) |
| Audit journal | `src/nsa/platform/audit.py` | D02, D33 | Per-flush row versions with validity periods, acting user, as-of reads, delete closure; optimistic locking on `lock_version` |
| Numbering | `src/nsa/platform/numbering.py` | D24.06 | Atomic counter per resolved prefix (e.g. `SIT-{contract}-{year}-{n:03d}`) |
| Workflow engine | `src/nsa/platform/workflow/engine.py` | D24 | Declarative states and transitions, permission and condition guards, four-eyes rule, effects, locked states, transition log |
| Situație workflow | `src/nsa/billing/workflows.py` | D39 | draft → submitted → certified (not by submitter) → invoiced → paid; reject/rework |
| Modification limits | `src/nsa/contracts/modification.py`, `thresholds.py` | D40.05 | Legea 98/2016 art. 221 (cumulative 50% for (b)+(c) and OUG 64 art. 8, de minimis net cumulative < 26,960,556 lei and < 15%/10%, 221(7) tests, 221(10) indexed base), OUG 64 art. 9 reserve, art. 18 ceilings, SEAP/JOUE obligations |
| Addendum workflow | `src/nsa/contracts/workflows.py` | D40.05 | Approval and signature blocked beyond legal limits; signing updates the contract price and keeps the initial value |
| INS index feed | `src/nsa/masterdata/indices.py` | D40.01 | TEMPO matrix CNS107D (base 2021): live fetch through CONNECT proxy, provisional/revised/final flags, upsert with change log, 60-day current-month rule, fallback lookup, runs to recalculate |
| Schema | `src/nsa/*/models.py`, `migrations/` | D01, D02, D19, D24, D38–D41, D03–D06 | 27 tables, company-scoped, audit columns, journal with validity periods |

## Run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
export NSA_DATABASE_URL=postgresql+psycopg://nsa:nsa@localhost:5432/nsa
alembic upgrade head
pytest
```

Requires a JVM (Java 17+) for MPXJ. Database tests skip when PostgreSQL is unreachable.

## Licensing

- MPXJ and IfcOpenShell are LGPL libraries, called unchanged.
- No code from GPL/AGPL sources (OpenProject, ERPNext, HRMS, iDempiere, Mayan, TaskJuggler, LibrePlan) is copied; their behaviour is re-implemented from the domain specifications.
- Frappe (MIT) logic may be ported with its notice retained.

## Next

- e-Factura: already done in an existing project; integrated as an external adapter, not rebuilt.
- National-budget contracts: OUG 47/2022 adjustment (total ICC, January 2019 floor) next to the OUG 64/2022 engine.
- NCS pricing (offer-equivalent items keep the original reference month), advance recovery schedule.
- P2: baselines, resource assignments, persisted XER import into the schedule tables.
- Legal values marked "unverified" in `construction-map/lead/research/amendments-and-indices.md` (2021-base %cpm table 15A, CNSP forecast annex after 2023, HG 395/2016 art. 164 status, 2026 direct-award thresholds).
