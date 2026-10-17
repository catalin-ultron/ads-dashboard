"""INS construction cost index feed (D40.01).

Source: TEMPO-Online matrix CNS107D "Indici de cost in constructii - an de baza 2021", monthly.
Value markup in the dataSet response: <u>…</u> latest provisional month, <strong>…</strong> revised,
plain = final (legend inferred from the data, see research/amendments-and-indices.md).
Indices on different base years must never be combined in one ratio.
"""

from __future__ import annotations

import calendar
import json
import os
import re
import http.client
import urllib.parse
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from nsa.billing.models import PriceAdjustmentRun
from nsa.contracts.priceadjust import AdjustmentIndices
from nsa.masterdata.models import IndexSeries, IndexValue

TEMPO_HOST = "statistici.insse.ro"
TEMPO_PORT = 8077
MATRIX = "CNS107D"
BASE_YEAR = 2021

# series code -> (TEMPO item id, label)
SERIES = {
    "ICC_TOTAL": (23295, "Total"),
    "ICC_NEW": (23296, "Constructii noi"),
    "ICC_CAPITAL_REPAIR": (23297, "Reparatii capitale"),
    "ICC_CURRENT_REPAIR": (23298, "Reparatii curente"),
    "ICC_RESIDENTIAL": (23299, "Cladiri rezidentiale"),
    "ICC_NON_RESIDENTIAL": (23300, "Cladiri nerezidentiale"),
    "ICC_ENGINEERING": (23301, "Constructii ingineresti"),
    "ICC_BUILDINGS": (23302, "Cladiri"),
    "ICC_MATERIALS": (23303, "TOTAL COST MATERIALE"),
}
_BY_LABEL = {label.lower(): code for code, (_, label) in SERIES.items()}

MONTHS_RO = {"ianuarie": 1, "februarie": 2, "martie": 3, "aprilie": 4, "mai": 5, "iunie": 6, "iulie": 7,
             "august": 8, "septembrie": 9, "octombrie": 10, "noiembrie": 11, "decembrie": 12}
_MONTH = re.compile(r"luna\s+(\w+)\s+(\d{4})", re.I)
_FLAG = re.compile(r"^<(u|strong)>(.*)</\1>$")


class IndexFeedError(ValueError):
    pass


@dataclass(frozen=True)
class Observation:
    series: str
    period: date
    value: Decimal
    status: str  # provisional | revised | final


@dataclass(frozen=True)
class Change:
    series: str
    period: date
    old_value: Decimal | None
    new_value: Decimal
    old_status: str | None
    new_status: str


def parse_month(label: str) -> date:
    m = _MONTH.search(label)
    if not m or m.group(1).lower() not in MONTHS_RO:
        raise IndexFeedError(f"Unrecognised month label {label!r}")
    return date(int(m.group(2)), MONTHS_RO[m.group(1).lower()], 1)


def parse_cell(cell: str) -> tuple[Decimal, str]:
    m = _FLAG.match(cell.strip())
    raw, status = (m.group(2), "provisional" if m.group(1) == "u" else "revised") if m else (cell.strip(), "final")
    try:
        return Decimal(raw.replace(",", ".")), status
    except Exception:
        raise IndexFeedError(f"Unparseable index value {cell!r}") from None


def parse_dataset(rows: list[list[str]]) -> list[Observation]:
    """Parse the 2-D array returned by POST /matrix/dataSet/CNS107D (first rows are headers)."""
    month_row = next((r for r in rows if any(_MONTH.search(c or "") for c in r[1:])), None)
    if month_row is None:
        raise IndexFeedError("No month header row in dataset")
    periods = [parse_month(c) for c in month_row[1:]]
    out = []
    for row in rows:
        code = _BY_LABEL.get((row[0] or "").strip().lower())
        if code is None or row is month_row:
            continue
        for period, cell in zip(periods, row[1:]):
            if cell in ("", "-", ":", None):
                continue
            value, status = parse_cell(cell)
            out.append(Observation(code, period, value, status))
    return out


def dataset_request(metadata: dict, series: list[str], months: int = 26) -> dict:
    """Build the dataSet POST body from matrix metadata, selecting series and the last `months` months."""
    dims = metadata["dimensionsMap"]
    wanted = {SERIES[s][0] for s in series}
    kinds = [o for o in dims[0]["options"] if o["nomItemId"] in wanted]
    if len(kinds) != len(wanted):
        raise IndexFeedError("Requested series missing from matrix metadata")
    return {"language": "ro", "arr": [kinds, dims[1]["options"][-months:], dims[2]["options"]],
            "matrixName": metadata["matrixName"], "matrixDetails": metadata["details"]}


def _request(method: str, path: str, body: dict | None = None):
    """HTTP to TEMPO (plain HTTP on port 8077); tunnels through an HTTP(S) proxy with CONNECT when one is set."""
    host, port = TEMPO_HOST, TEMPO_PORT
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if proxy:
        p = urllib.parse.urlsplit(proxy)
        conn = http.client.HTTPConnection(p.hostname, p.port or 80, timeout=60)
        conn.set_tunnel(host, port)
    else:
        conn = http.client.HTTPConnection(host, port, timeout=60)
    try:
        data = json.dumps(body).encode() if body is not None else None
        conn.request(method, f"/tempo-ins{path}", body=data,
                     headers={"Content-Type": "application/json"} if data else {})
        resp = conn.getresponse()
        payload = resp.read()
        if resp.status != 200:
            raise IndexFeedError(f"TEMPO {method} {path} returned {resp.status}")
        return json.loads(payload)
    finally:
        conn.close()


def fetch(series: list[str] | None = None, months: int = 26) -> list[Observation]:
    series = series or list(SERIES)
    metadata = _request("GET", f"/matrix/{MATRIX}")
    return parse_dataset(_request("POST", f"/matrix/dataSet/{MATRIX}", dataset_request(metadata, series, months)))


def ensure_series(session: Session) -> dict[str, IndexSeries]:
    existing = {s.code: s for s in session.scalars(select(IndexSeries).where(IndexSeries.code.in_(SERIES)))}
    for code, (item_id, label) in SERIES.items():
        if code not in existing:
            existing[code] = IndexSeries(code=code, name=label, publisher="INS", base_year=BASE_YEAR,
                                         source_ref=f"{MATRIX}:{item_id}")
            session.add(existing[code])
    session.flush()
    return existing


def upsert(session: Session, observations: list[Observation]) -> list[Change]:
    series = ensure_series(session)
    changes = []
    for ob in observations:
        s = series[ob.series]
        row = session.scalars(select(IndexValue).where(IndexValue.series_id == s.id,
                                                       IndexValue.period == ob.period)).first()
        if row is None:
            session.add(IndexValue(series_id=s.id, period=ob.period, value=ob.value, status=ob.status))
            changes.append(Change(ob.series, ob.period, None, ob.value, None, ob.status))
        elif row.value != ob.value or row.status != ob.status:
            changes.append(Change(ob.series, ob.period, row.value, ob.value, row.status, ob.status))
            row.value, row.status = ob.value, ob.status
    session.flush()
    return changes


def current_index_month(filing_month: date) -> date:
    """OUG 64/2022: index applicable 60 days before the last day of the filing month."""
    last = date(filing_month.year, filing_month.month, calendar.monthrange(filing_month.year, filing_month.month)[1])
    d = last - timedelta(days=60)
    return date(d.year, d.month, 1)


def lookup(session: Session, series: str, period: date) -> IndexValue:
    """Exact month, or the latest earlier month when the month is not yet published (to be recalculated)."""
    row = session.scalars(
        select(IndexValue).join(IndexSeries, IndexSeries.id == IndexValue.series_id)
        .where(IndexSeries.code == series, IndexValue.period <= period)
        .order_by(IndexValue.period.desc()).limit(1)).first()
    if row is None:
        raise IndexFeedError(f"No {series} value on or before {period}")
    return row


def runs_to_recalculate(session: Session, changes: list[Change]) -> list[PriceAdjustmentRun]:
    """Adjustment runs computed on provisional indices whose months changed in this feed."""
    touched = {(c.series, c.period) for c in changes if c.old_value is not None}
    if not touched:
        return []
    runs = session.scalars(select(PriceAdjustmentRun).where(PriceAdjustmentRun.indices_final.is_(False)))
    return [r for r in runs if (r.materials_series, r.current_period) in touched
            or (r.total_series, r.current_period) in touched
            or (r.materials_series, r.reference_period) in touched
            or (r.total_series, r.reference_period) in touched]


def adjustment_indices(session: Session, filing_month: date, reference_month: date,
                       total_series: str = "ICC_TOTAL", materials_series: str = "ICC_MATERIALS"
                       ) -> tuple[AdjustmentIndices, dict]:
    """Indices for one OUG 64/2022 run from the store, with the periods used and whether all are final.

    The realised ICC is used for the reference month (ICCRlr); the CNSP forecast annex (ICCplr) is not a feed.
    """
    current = current_index_month(filing_month)
    m_cur, m_ref = lookup(session, materials_series, current), lookup(session, materials_series, reference_month)
    t_cur, t_ref = lookup(session, total_series, current), lookup(session, total_series, reference_month)
    if m_ref.period != reference_month or t_ref.period != reference_month:
        raise IndexFeedError(f"Reference month {reference_month} is not published")
    meta = {"materials_series": materials_series, "total_series": total_series,
            "current_period": current, "reference_period": reference_month,
            "indices_final": all(v.status == "final" and v.period == p for v, p in
                                 ((m_cur, current), (t_cur, current), (m_ref, reference_month),
                                  (t_ref, reference_month)))}
    return AdjustmentIndices(m_cur.value, m_ref.value, t_cur.value, t_ref.value), meta
