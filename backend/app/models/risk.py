from datetime import date, datetime

from sqlalchemy import ARRAY, Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.enums import RiskCategory, RiskStatus


class Risk(Base):
    """Risk { ... } — process_full_v4.md, раздел 5.

    Risk.id — составной код (`12-1111-1-1Ri`), первичный ключ, глобально уникален.
    Risk.display_number — простой номер для печатных паспортов, НЕ уникален глобально
    (уникален только в рамках конкретного отчёта) — намеренно без unique-констрейнта.
    Risk.owner_ids — ARRAY, реальные риски показывают до 3 совладельцев (раздел 3, этап 4).
    Postgres ARRAY не поддерживает FK на элементы — ссылочная целостность на User
    обеспечивается только на уровне сервисного слоя, не БД (осознанный компромисс ради
    буквального выполнения требования «ownerIds — массив, не одно значение»).
    """

    __tablename__ = "risks"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    display_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[RiskCategory] = mapped_column(Enum(RiskCategory, name="risk_category"), nullable=False)
    status: Mapped[RiskStatus] = mapped_column(
        Enum(RiskStatus, name="risk_status"), nullable=False, default=RiskStatus.IDENTIFICATION
    )

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False, default=list)

    identification_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    identification_phase: Mapped[str | None] = mapped_column(String(255), nullable=True)
    realization_phase: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Полное описание риска — 3 из 5 частей (раздел 4.3 «Паспорт риска»)
    cause: Mapped[str] = mapped_column(Text, nullable=False)
    risk_event: Mapped[str] = mapped_column(Text, nullable=False)
    direct_consequence: Mapped[str] = mapped_column(Text, nullable=False)

    # Качественная оценка P — чек-лист из 3 вопросов, детерминированно даёт 1-3 (этап 2)
    p_checklist: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # {"q1": bool, "q2": bool, "q3": bool}
    p: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Качественная оценка I — описательная шкала 1-3, I=3 обязательно с обоснованием
    i_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    i_justification: Mapped[str | None] = mapped_column(Text, nullable=True)

    # RRA = P x I, зона (L/M/H) считается на лету сервисным слоем, не хранится отдельным полем
    rra: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Количественная оценка — отдельный блок, без формул методики (этап 2)
    quant_probability_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    quant_schedule_impact_months: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    quant_budget_impact_mln: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    scenarios: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # {optimistic, mostLikely, pessimistic}
    expected_loss: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    # Эскалация комитету — триггер I=3, отдельный флаг, не 4-я зона severity (этап 3)
    committee_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    committee_decision: Mapped[str | None] = mapped_column(Text, nullable=True)
    committee_decision_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Остаточная оценка — этап 7, тоже два независимых слоя
    residual_rra: Mapped[int | None] = mapped_column(Integer, nullable=True)
    residual_expected_loss: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)

    source_lesson_id: Mapped[str | None] = mapped_column(ForeignKey("lessons.id"), nullable=True)

    review_frequency_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    next_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ДОБАВЛЕНО сверх буквального раздела 5: без этого поля невозможно реализовать
    # ветку «Архивирован (объединён с [ID])» из раздела 3 (объединение дублей на Карте связей,
    # этап 6) — раздел 5 описывает поля риска, но не даёт отдельного поля для этой связи.
    merged_into_risk_id: Mapped[str | None] = mapped_column(ForeignKey("risks.id"), nullable=True)
