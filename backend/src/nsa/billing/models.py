"""Situații de lucrări, lines and price adjustment runs (D39.04, D39.05, D40.02)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nsa.platform.core.db import Audited, Base, Keyed, Quantity, Rate


class Situatie(Keyed, Audited, Base):
    __tablename__ = "situatie"
    __journaled__ = True

    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contract.id"), index=True)
    number: Mapped[str] = mapped_column(String(32))
    period: Mapped[date] = mapped_column(Date)  # first day of the measured month
    status: Mapped[str] = mapped_column(String(16), default="draft")
    gross: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    certified: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    advance_recovery: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    retention: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    penalties: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    price_adjustment: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    payable: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    certified_by: Mapped[str | None] = mapped_column(String(255))  # diriginte de șantier
    certified_on: Mapped[date | None] = mapped_column(Date)

    lines: Mapped[list[SituatieLine]] = relationship(back_populates="situatie", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("contract_id", "number"),
        UniqueConstraint("contract_id", "period"),
        CheckConstraint("status in ('draft','submitted','certified','invoiced','paid','rejected')", name="status"),
    )


class SituatieLine(Keyed, Base):
    __tablename__ = "situatie_line"

    situatie_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("situatie.id"), index=True)
    boq_item_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("boq_item.id"))
    quantity: Mapped[Decimal] = mapped_column(Quantity)
    cumulative_quantity: Mapped[Decimal] = mapped_column(Quantity)
    value: Mapped[Decimal]
    certified: Mapped[bool] = mapped_column(Boolean, default=False)
    issue: Mapped[str | None] = mapped_column(Text)
    pv_reference: Mapped[str | None] = mapped_column(String(64))

    situatie: Mapped[Situatie] = relationship(back_populates="lines")

    __table_args__ = (UniqueConstraint("situatie_id", "boq_item_id"),)


class PriceAdjustmentRun(Keyed, Audited, Base):
    __tablename__ = "price_adjustment_run"

    situatie_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("situatie.id"), index=True)
    method: Mapped[str] = mapped_column(String(24))
    payment_value: Mapped[Decimal]
    materials_value: Mapped[Decimal]
    advance_share: Mapped[Decimal] = mapped_column(Rate)
    profit_share: Mapped[Decimal] = mapped_column(Rate)
    materials_weight: Mapped[Decimal] = mapped_column(Rate)
    icc_materials_current: Mapped[Decimal] = mapped_column(Rate)
    icc_materials_reference: Mapped[Decimal] = mapped_column(Rate)
    icc_current: Mapped[Decimal] = mapped_column(Rate)
    icc_reference: Mapped[Decimal] = mapped_column(Rate)
    indices_final: Mapped[bool] = mapped_column(Boolean, default=False)
    adjusted_value: Mapped[Decimal]
    adjustment: Mapped[Decimal]

    __table_args__ = (
        CheckConstraint("method in ('oug64_2022','contract_clause')", name="method"),
    )
