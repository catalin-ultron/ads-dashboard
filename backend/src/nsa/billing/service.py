"""Build and persist a monthly situație from measured quantities (D39.04, D39.05, D38.02, D40.02)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from nsa.billing import situatii
from nsa.billing.models import PriceAdjustmentRun, Situatie, SituatieLine
from nsa.contracts import guarantees, priceadjust
from nsa.contracts.models import BoqItem, Contract, Guarantee, RetentionEntry


@dataclass(frozen=True)
class MeasuredInput:
    item_code: str
    quantity: Decimal
    pv_reference: str | None = None


class BillingError(ValueError):
    pass


def _previous_cumulative(session: Session, contract_id: int, period: date) -> dict[str, Decimal]:
    rows = session.execute(
        select(BoqItem.code, func.sum(SituatieLine.quantity))
        .join(SituatieLine, SituatieLine.boq_item_id == BoqItem.id)
        .join(Situatie, Situatie.id == SituatieLine.situatie_id)
        .where(Situatie.contract_id == contract_id, Situatie.period < period,
               Situatie.status != "rejected", SituatieLine.certified.is_(True))
        .group_by(BoqItem.code)
    ).all()
    return {code: qty for code, qty in rows}


def _retention_account(session: Session, contract: Contract) -> tuple[Guarantee, guarantees.RetentionAccount] | None:
    g = session.scalars(select(Guarantee).where(
        Guarantee.contract_id == contract.id, Guarantee.kind == "good_execution",
        Guarantee.instrument == "retention", Guarantee.status == "active")).first()
    if g is None:
        return None
    acct = guarantees.RetentionAccount(contract.price_excl_vat, g.target_share, g.planned_retention_share)
    for e in session.scalars(select(RetentionEntry).where(RetentionEntry.guarantee_id == g.id)
                             .order_by(RetentionEntry.id)):
        acct.entries.append(guarantees.Entry(guarantees.EntryKind(e.kind), e.amount, e.reference or ""))
    return g, acct


def build_situatie(session: Session, contract_id: int, period: date, number: str,
                   measured: list[MeasuredInput], *, advance_recovery: Decimal = Decimal("0"),
                   penalties: Decimal = Decimal("0"),
                   adjustment_indices: priceadjust.AdjustmentIndices | None = None,
                   indices_final: bool = False, adjustment_meta: dict | None = None) -> Situatie:
    contract = session.get(Contract, contract_id)
    if contract is None:
        raise BillingError(f"Contract {contract_id} not found")
    period = date(period.year, period.month, 1)

    items = {b.code: b for b in contract.boq}
    boq = {code: situatii.BoqItem(code, b.unit, b.unit_price, b.contract_quantity,
                                  b.approved_extra_quantity, b.hidden_works) for code, b in items.items()}
    lines = situatii.measure(boq, _previous_cumulative(session, contract_id, period),
                             [situatii.MeasuredLine(m.item_code, m.quantity, m.pv_reference) for m in measured])
    certified = sum((ln.value for ln in lines if ln.certified), Decimal("0"))

    run = None
    adjustment = Decimal("0")
    if adjustment_indices is not None and certified > 0:
        if contract.funding_source not in ("eu", "pnrr"):
            raise BillingError("OUG 64/2022 adjustment applies to EU-funded contracts; use the contract clause")
        if contract.materials_weight is None:
            raise BillingError("Contract has no materials weight (%cpm) for price adjustment")
        materials = sum((items[ln.item_code].materials_unit_price or Decimal("0")) * ln.quantity
                        for ln in lines if ln.certified)
        inp = priceadjust.AdjustmentInput(certified, materials.quantize(Decimal("0.01")), contract.advance_share,
                                          contract.materials_weight, adjustment_indices)
        res = priceadjust.adjust(inp)
        adjustment = res.adjustment
        run = PriceAdjustmentRun(
            method="oug64_2022", payment_value=inp.payment_value, materials_value=inp.materials_value,
            advance_share=inp.advance_share, profit_share=priceadjust.DEFAULT_PROFIT_SHARE,
            materials_weight=inp.materials_weight,
            icc_materials_current=adjustment_indices.icc_materials_current,
            icc_materials_reference=adjustment_indices.icc_materials_reference,
            icc_current=adjustment_indices.icc_current, icc_reference=adjustment_indices.icc_reference,
            indices_final=indices_final, adjusted_value=res.adjusted_value, adjustment=res.adjustment)
        if adjustment_meta:
            for key, value in adjustment_meta.items():
                setattr(run, key, value)

    retention = Decimal("0")
    account = _retention_account(session, contract)
    if account is not None:
        retention = account[1].retain(certified, number)

    shares = {str(p.partner_id): p.share for p in contract.parties if p.role in ("leader", "member") and p.share}
    result = situatii.centralize(lines, situatii.Deductions(advance_recovery, retention, penalties, adjustment),
                                 shares or None)

    sit = Situatie(contract_id=contract_id, number=number, period=period, status="draft",
                   gross=result.gross, certified=result.certified, advance_recovery=advance_recovery,
                   retention=retention, penalties=penalties, price_adjustment=adjustment, payable=result.payable)
    for ln in lines:
        sit.lines.append(SituatieLine(boq_item_id=items[ln.item_code].id, quantity=ln.quantity,
                                      cumulative_quantity=ln.cumulative_quantity, value=ln.value,
                                      certified=ln.certified, issue=ln.issue,
                                      pv_reference=next((m.pv_reference for m in measured
                                                         if m.item_code == ln.item_code), None)))
    session.add(sit)
    session.flush()
    if run is not None:
        run.situatie_id = sit.id
        session.add(run)
    if retention > 0:
        session.add(RetentionEntry(guarantee_id=account[0].id, kind="retention", amount=retention,
                                   on_date=period, situatie_id=sit.id, reference=number))
    session.flush()
    return sit

