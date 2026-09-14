from datetime import datetime

from sqlalchemy import ARRAY, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.enums import ActionStrategy


class Lesson(Base):
    """Lesson { ... } — process_full_v4.md, раздел 5 + раздел 4.6 (14 полей реального шаблона).

    id — строковый код вида `L-01` (раздел 4.6), не автоинкремент.
    category — здесь НЕ RiskCategory: раздел 4.6 явно требует более гранулярную категорию
    («категория + подкатегория через слэш», например «Проектирование / компоновка») —
    свободная строка, а не тот же 8-значный справочник, что у Risk.
    impact — свободный текст («547 млн ₽ / 10 мес.»), не структурированные числа — дословное
    требование раздела 4.6.
    source_risk_id — структурированное поле добавлено по прямой рекомендации раздела 4.6
    («для трассируемости Lesson↔Risk в новой системе стоит добавить отдельное структурированное
    поле sourceRiskId»), в реальном Excel-шаблоне такого поля нет физически.
    """

    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    project: Mapped[str] = mapped_column(String(255), nullable=False)
    phase: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    problem_or_risk_event: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trigger_indicator: Mapped[str | None] = mapped_column(Text, nullable=True)
    strategy: Mapped[ActionStrategy | None] = mapped_column(
        Enum(ActionStrategy, name="action_strategy"), nullable=True
    )
    lesson_learned: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)

    # use_alter: Risk.source_lesson_id -> Lesson и Lesson.source_risk_id -> Risk образуют
    # цикл FK между двумя таблицами; use_alter откладывает этот constraint в ALTER TABLE,
    # чтобы SQLAlchemy/Alembic могли создать обе таблицы без ошибки порядка создания.
    source_risk_id: Mapped[str | None] = mapped_column(
        ForeignKey("risks.id", use_alter=True, name="fk_lessons_source_risk_id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
