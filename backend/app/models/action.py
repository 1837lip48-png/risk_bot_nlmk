from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ActionKind, ActionStatus, ActionStrategy


class Action(Base):
    """Action { ... } — process_full_v4.md, раздел 5 + этапы 4-5.

    strategy и kind — поля мероприятия, а не риска (раздел «Модель данных», явное требование).
    planned_date / forecast_actual_date — ДВЕ ОТДЕЛЬНЫЕ ОТСТУПЛЕНИЯ от буквального раздела 5:
    там оба поля типизированы как даты (соответствует компоненту DatePicker в
    nlmk_ds2_components.md). Реальные seed-данные из workspace.html (15 рисков ЦГП-2)
    хранят план/срок как произвольный текст программы — «июн.26», «Фазы 3, 4», «2028»,
    «2030», «Не требуется» — а не календарную дату. Принуждение к типу Date потребовало бы
    придумывать точные даты, которых нет в источнике (прямо запрещено CLAUDE.md: «seed-данные
    — использовать реальные, не выдумывать новые»). Поэтому оба поля — String; фронтенд может
    класть туда как ISO-дату (из DatePicker для новых мероприятий), так и текст фазы/года для
    существующих. Требует подтверждения на экране 3.1 (форма мероприятия), см. отчёт по схеме.
    cost — тоже String по той же причине: реальные значения — «tbd», «Не требуется», «7 млн
    руб.», «2,7 млн руб.», не чистое число.
    assignee_id — nullable и **не** array: раздел 5 даёт его как одиночное значение, хотя
    некоторые реальные мероприятия перечисляют несколько исполнителей одной строкой
    («Сараев Д.В., Мощенко М.Г., Долгов А.В.») — при импорте seed это потребует решения
    (первый исполнитель как assignee + остальные в текст задачи, либо расширение модели до
    массива по аналогии с Risk.owner_ids). Не решаю это самовольно на этапе схемы.
    """

    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    risk_id: Mapped[str] = mapped_column(ForeignKey("risks.id"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)

    kind: Mapped[ActionKind] = mapped_column(Enum(ActionKind, name="action_kind"), nullable=False)
    strategy: Mapped[ActionStrategy] = mapped_column(Enum(ActionStrategy, name="action_strategy"), nullable=False)
    trigger_condition: Mapped[str | None] = mapped_column(Text, nullable=True)  # только для kind=contingency

    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    cost: Mapped[str | None] = mapped_column(String(100), nullable=True)

    planned_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    forecast_actual_date: Mapped[str | None] = mapped_column(String(50), nullable=True)

    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus, name="action_status"), nullable=False, default=ActionStatus.PLANNED
    )
