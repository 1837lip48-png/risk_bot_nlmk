from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.enums import RiskDependencySource, RiskDependencyType


class RiskDependency(Base):
    """RiskDependency { ... } — process_full_v4.md, раздел 5 + этап 6.

    source: manual|ai_suggested — обязателен, разделяет ручную Карту связей и AI Knowledge
    Graph в одной и той же таблице (раздел 4.7: AI-связи требуют подтверждения риск-менеджером
    перед тем как стать «ручными» — то есть после подтверждения source меняется на manual,
    сама сущность не дублируется в отдельную таблицу).
    """

    __tablename__ = "risk_dependencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_risk_id: Mapped[str] = mapped_column(ForeignKey("risks.id"), nullable=False)
    to_risk_id: Mapped[str] = mapped_column(ForeignKey("risks.id"), nullable=False)
    type: Mapped[RiskDependencyType] = mapped_column(
        Enum(RiskDependencyType, name="risk_dependency_type"), nullable=False
    )
    source: Mapped[RiskDependencySource] = mapped_column(
        Enum(RiskDependencySource, name="risk_dependency_source"), nullable=False
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
