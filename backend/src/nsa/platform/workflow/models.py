from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from nsa.platform.core.db import Base, Keyed


class WorkflowLog(Keyed, Base):
    __tablename__ = "workflow_log"

    doc_type: Mapped[str] = mapped_column(String(64))
    doc_id: Mapped[int] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(64))
    from_state: Mapped[str] = mapped_column(String(32))
    to_state: Mapped[str] = mapped_column(String(32))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("app_user.id"))
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    comment: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (Index("ix_workflow_log_doc", "doc_type", "doc_id"),)
