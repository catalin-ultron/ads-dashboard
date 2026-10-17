"""Declarative base and shared columns: bigint identity keys, company scoping, audit fields."""

from __future__ import annotations

import os
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, MetaData, Numeric, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

NAMING = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

Money = Numeric(18, 2)
Quantity = Numeric(18, 4)
Rate = Numeric(12, 6)


def database_url() -> str:
    return os.environ.get("NSA_DATABASE_URL", "postgresql+psycopg://nsa:nsa@localhost:5432/nsa")


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)
    type_annotation_map = {Decimal: Money}


class Keyed:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)


class Audited:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())
    lock_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    @declared_attr.directive
    def __mapper_args__(cls):
        return {"version_id_col": cls.lock_version}  # optimistic locking: stale updates raise


class CompanyScoped:
    @declared_attr
    def company_id(cls) -> Mapped[int]:
        return mapped_column(BigInteger, ForeignKey("company.id"), index=True)
