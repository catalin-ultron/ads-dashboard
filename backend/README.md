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
| Schema | `src/nsa/*/models.py`, `migrations/` | D01, D02, D19, D38–D41, D03–D06 | 26 tables, company-scoped, audit columns, journal with validity periods |

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

- P0: permission evaluation, journal writer, workflow engine, numbering service.
- P1: addenda limits (art. 221, OUG 64/2022 art. 8–9), NCS pricing, advance recovery, index store ingestion, invoice and e-Factura payload.
- P2: baselines, resource assignments, persisted import of XER into the schedule tables.
