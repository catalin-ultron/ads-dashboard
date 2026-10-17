"""Public works contracts, parties, BoQ, guarantees and addenda (D19, D38, D40, D41)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import (BigInteger, Boolean, CheckConstraint, Date, ForeignKey, String, Text,
                        UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nsa.platform.core.db import Audited, Base, CompanyScoped, Keyed, Quantity, Rate

FUNDING_SOURCES = ("eu", "pnrr", "national", "local", "private")


class Contract(Keyed, Audited, CompanyScoped, Base):
    __tablename__ = "contract"
    __journaled__ = True

    number: Mapped[str] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(Text)
    authority_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("partner.id"))
    procedure_ref: Mapped[str | None] = mapped_column(String(64))  # SICAP notice / award id
    funding_source: Mapped[str] = mapped_column(String(12))
    design_build: Mapped[bool] = mapped_column(Boolean, default=False)
    bid_deadline: Mapped[date | None] = mapped_column(Date)
    signed_on: Mapped[date | None] = mapped_column(Date)
    start_order_on: Mapped[date | None] = mapped_column(Date)
    duration_months: Mapped[int | None]
    price_excl_vat: Mapped[Decimal]
    currency: Mapped[str] = mapped_column(String(3), default="RON")
    advance_share: Mapped[Decimal] = mapped_column(Rate, default=Decimal("0"))
    materials_weight: Mapped[Decimal | None] = mapped_column(Rate)  # %cpm for OUG 64/2022
    reference_month: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16), default="draft")

    parties: Mapped[list[ContractParty]] = relationship(back_populates="contract")
    boq: Mapped[list[BoqItem]] = relationship(back_populates="contract")

    __table_args__ = (
        UniqueConstraint("company_id", "number"),
        CheckConstraint(f"funding_source in {FUNDING_SOURCES}", name="funding_source"),
        CheckConstraint("status in ('draft','signed','in_execution','completed','final_reception','closed',"
                        "'terminated')", name="status"),
        CheckConstraint("price_excl_vat >= 0", name="price"),
    )


class ContractParty(Keyed, Audited, Base):
    """Consortium members and declared subcontractors with their shares."""

    __tablename__ = "contract_party"

    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contract.id"), index=True)
    partner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("partner.id"))
    role: Mapped[str] = mapped_column(String(16))
    share: Mapped[Decimal | None] = mapped_column(Rate)
    scope: Mapped[str | None] = mapped_column(Text)
    direct_payment: Mapped[bool] = mapped_column(Boolean, default=False)

    contract: Mapped[Contract] = relationship(back_populates="parties")

    __table_args__ = (
        UniqueConstraint("contract_id", "partner_id", "role"),
        CheckConstraint("role in ('leader','member','subcontractor','third_party_support')", name="role"),
    )


class BoqItem(Keyed, Audited, Base):
    """Bill of quantities line priced from the offer devize (D39.02)."""

    __tablename__ = "boq_item"
    __journaled__ = True

    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contract.id"), index=True)
    object_code: Mapped[str | None] = mapped_column(String(32))  # obiect / categorie de lucrări
    code: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    unit: Mapped[str] = mapped_column(String(16), ForeignKey("unit.code"))
    unit_price: Mapped[Decimal]
    materials_unit_price: Mapped[Decimal | None]
    contract_quantity: Mapped[Decimal] = mapped_column(Quantity)
    approved_extra_quantity: Mapped[Decimal] = mapped_column(Quantity, default=Decimal("0"))
    hidden_works: Mapped[bool] = mapped_column(Boolean, default=False)

    contract: Mapped[Contract] = relationship(back_populates="boq")

    __table_args__ = (UniqueConstraint("contract_id", "code"),)


class Addendum(Keyed, Audited, Base):
    __tablename__ = "addendum"
    __journaled__ = True

    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contract.id"), index=True)
    number: Mapped[str] = mapped_column(String(32))
    kind: Mapped[str] = mapped_column(String(24))
    signed_on: Mapped[date | None] = mapped_column(Date)
    value_delta: Mapped[Decimal] = mapped_column(default=Decimal("0"))
    duration_delta_days: Mapped[int] = mapped_column(default=0)
    legal_basis: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(16), default="draft")

    __table_args__ = (
        UniqueConstraint("contract_id", "number"),
        CheckConstraint("status in ('draft','approved','signed','cancelled')", name="status"),
        CheckConstraint("kind in ('price_adjustment','extra_works','unforeseen','de_minimis','duration',"
                        "'subcontractor','other')", name="kind"),
    )


class Guarantee(Keyed, Audited, Base):
    __tablename__ = "guarantee"
    __journaled__ = True

    contract_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("contract.id"), index=True)
    kind: Mapped[str] = mapped_column(String(16))
    instrument: Mapped[str] = mapped_column(String(16))
    issuer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("partner.id"))
    target_share: Mapped[Decimal | None] = mapped_column(Rate)
    planned_retention_share: Mapped[Decimal | None] = mapped_column(Rate)
    amount: Mapped[Decimal | None]
    valid_to: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(16), default="active")

    __table_args__ = (
        CheckConstraint("kind in ('participation','good_execution','advance')", name="kind"),
        CheckConstraint("instrument in ('bank_letter','insurance','deposit','retention')", name="instrument"),
        CheckConstraint("target_share is null or (target_share > 0 and target_share <= 0.10)",
                        name="target_share"),
    )


class RetentionEntry(Keyed, Base):
    __tablename__ = "retention_entry"

    guarantee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guarantee.id"), index=True)
    kind: Mapped[str] = mapped_column(String(24))
    amount: Mapped[Decimal]
    on_date: Mapped[date] = mapped_column(Date)
    situatie_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("situatie.id"))
    reference: Mapped[str | None] = mapped_column(String(128))

    __table_args__ = (
        CheckConstraint("kind in ('initial_deposit','retention','release_completion','release_final','call',"
                        "'restoration')", name="kind"),
    )
