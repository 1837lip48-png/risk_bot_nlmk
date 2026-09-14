from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.enums import RiskStatus


class AuditLog(Base):
    """AuditLog { id, riskId, actorId, fromStatus, toStatus, comment, timestamp } — раздел 5.

    Каждый переход статуса риска пишется сюда (CLAUDE.md, «Модель данных» и этап 8).
    from_status nullable — у самой первой записи (создание риска со статусом
    «Идентификация») предыдущего статуса не существует.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    risk_id: Mapped[str] = mapped_column(ForeignKey("risks.id"), nullable=False)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    from_status: Mapped[RiskStatus | None] = mapped_column(Enum(RiskStatus, name="risk_status"), nullable=True)
    to_status: Mapped[RiskStatus] = mapped_column(Enum(RiskStatus, name="risk_status"), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
