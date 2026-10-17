"""Tenancy, identity, audit journal and numbering (D01, D02, D24.06, D36)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String,
                        UniqueConstraint, func)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nsa.platform.core.db import Audited, Base, Keyed


class Company(Keyed, Audited, Base):
    __tablename__ = "company"

    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    cui: Mapped[str] = mapped_column(String(16), unique=True)
    trade_register_no: Mapped[str | None] = mapped_column(String(32))
    vat_payer: Mapped[bool] = mapped_column(Boolean, default=True)
    base_currency: Mapped[str] = mapped_column(String(3), default="RON")
    parent_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("company.id"))

    parent: Mapped[Company | None] = relationship(remote_side="Company.id")


class User(Keyed, Audited, Base):
    __tablename__ = "app_user"

    email: Mapped[str] = mapped_column(String(255), unique=True)
    full_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(16), default="active")

    __table_args__ = (CheckConstraint("status in ('active','locked','disabled')", name="status"),)


class Role(Keyed, Audited, Base):
    __tablename__ = "role"

    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    permissions: Mapped[list[str]] = mapped_column(JSONB, default=list)


class Membership(Keyed, Audited, Base):
    """Grants a role to a user in a company, optionally narrowed to one contract."""

    __tablename__ = "membership"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("app_user.id"), index=True)
    company_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("company.id"), index=True)
    role_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("role.id"))
    contract_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("contract.id"))

    __table_args__ = (UniqueConstraint("user_id", "company_id", "role_id", "contract_id"),)


class Journal(Keyed, Base):
    """Row snapshots with validity periods, for audit and as-of queries."""

    __tablename__ = "journal"

    table_name: Mapped[str] = mapped_column(String(64))
    row_id: Mapped[int] = mapped_column(BigInteger)
    version: Mapped[int] = mapped_column(Integer)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("app_user.id"))
    data: Mapped[dict] = mapped_column(JSONB)

    __table_args__ = (UniqueConstraint("table_name", "row_id", "version"),)


class Counter(Base):
    """One counter per resolved numbering prefix (e.g. 'SIT-<contract>-2026')."""

    __tablename__ = "counter"

    scope: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[int] = mapped_column(BigInteger, default=0)
