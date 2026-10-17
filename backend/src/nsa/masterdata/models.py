"""Partners, units, cost indices and exchange rates (D01, D40.01)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from nsa.platform.core.db import Audited, Base, Keyed, Rate


class Partner(Keyed, Audited, Base):
    """Contracting authorities, JV partners, subcontractors, suppliers."""

    __tablename__ = "partner"

    name: Mapped[str] = mapped_column(String(255))
    cui: Mapped[str | None] = mapped_column(String(16), unique=True)
    country: Mapped[str] = mapped_column(String(2), default="RO")
    kind: Mapped[str] = mapped_column(String(24))
    public_authority: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        CheckConstraint("kind in ('authority','company','person')", name="kind"),
    )


class Unit(Base):
    __tablename__ = "unit"

    code: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(64))


class IndexSeries(Keyed, Base):
    """INS / CNSP cost indices: ICC total, ICC materials, forecast ICC, IPC."""

    __tablename__ = "index_series"

    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    publisher: Mapped[str] = mapped_column(String(32))
    base_year: Mapped[int | None]
    source_ref: Mapped[str | None] = mapped_column(String(64))  # e.g. "CNS107D:23295"


class IndexValue(Keyed, Base):
    __tablename__ = "index_value"

    series_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("index_series.id"))
    period: Mapped[date] = mapped_column(Date)
    value: Mapped[Decimal] = mapped_column(Rate)
    status: Mapped[str] = mapped_column(String(12), default="provisional")

    __table_args__ = (
        UniqueConstraint("series_id", "period"),
        CheckConstraint("status in ('provisional','revised','final')", name="status"),
    )


class FxRate(Base):
    """BNR daily reference rates."""

    __tablename__ = "fx_rate"

    currency: Mapped[str] = mapped_column(String(3), primary_key=True)
    on_date: Mapped[date] = mapped_column(Date, primary_key=True)
    ron_per_unit: Mapped[Decimal] = mapped_column(Rate)
