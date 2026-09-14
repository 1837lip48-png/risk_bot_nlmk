import enum


class ProjectRoleName(str, enum.Enum):
    """Роли, выбираемые на входе (process_full_v4.md, раздел 1), плюс системная роль admin."""

    RISK_MANAGER = "risk_manager"
    RISK_OWNER = "risk_owner"
    INITIATOR = "initiator"
    ADMIN = "admin"


class RiskCategory(str, enum.Enum):
    """8 фиксированных категорий — дословно из раздела 4.1, не редактируемый справочник."""

    TECHNOLOGICAL = "Технологические"
    TECHNICAL = "Технические"
    PROCESS = "Процессные"
    REGULATORY = "Регуляторные"
    DESIGN = "ПИР"
    CONSTRUCTION = "СМР/ПНР"
    PROCUREMENT = "Снабжение"
    ECONOMIC = "Экономические"


class RiskStatus(str, enum.Enum):
    """Статус-конвейер риска, раздел 3. archived_merged — отдельная ветка, только для дублей."""

    IDENTIFICATION = "identification"
    ANALYSIS_ASSESSMENT = "analysis_assessment"
    MANAGEMENT = "management"
    MONITORING_CONTROL = "monitoring_control"
    CLOSED = "closed"
    ARCHIVED_MERGED = "archived_merged"


class ActionKind(str, enum.Enum):
    """«Вид мероприятия», раздел 4/этап 4 — литералы как в схеме раздела 5."""

    CAUSE = "cause"
    CONSEQUENCE = "consequence"
    CONTINGENCY = "contingency"
    EXISTING_PROCEDURE = "existing_procedure"


class ActionStrategy(str, enum.Enum):
    """Стратегия управления риском — поле Action, не Risk (этап 4). Литералы из раздела 5."""

    REDUCE = "reduce"
    TRANSFER = "transfer"
    AVOID = "avoid"
    ACCEPT = "accept"


class ActionStatus(str, enum.Enum):
    """Статус мероприятия — собственный цикл, отдельный от статуса риска (этап 5)."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    REJECTED = "rejected"


class RiskDependencyType(str, enum.Enum):
    """Тип связи — фиксированный список, раздел 5 даёт литералы дословно на русском."""

    REINFORCES = "усиливает"
    LEADS_TO = "ведёт_к"
    DEPENDS_ON = "зависит_от"
    DUPLICATES = "дублирует"


class RiskDependencySource(str, enum.Enum):
    """Разделяет ручную Карту связей и AI Knowledge Graph (обязательное поле, раздел «Модель данных»)."""

    MANUAL = "manual"
    AI_SUGGESTED = "ai_suggested"
