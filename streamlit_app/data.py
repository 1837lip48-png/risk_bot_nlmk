"""
Данные и бизнес-логика RiskAssess Bot.

Риски и уроки — реальные данные Программы ЦГП-2 (НЛМК), перенесённые из
предыдущей HTML-версии прототипа (data/risk_data.json). Методология расчёта
критичности (RRA = P×I, 3×3, L/M/H) и остаточной оценки риска соответствует
«Методике оценки рисков для мегапроектов» v2.2.
"""
import json
import os
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

with open(os.path.join(DATA_DIR, "risk_data.json"), encoding="utf-8") as f:
    _RAW = json.load(f)

RISK_CATS = _RAW["RISK_CATS"]
RSTATUS = _RAW["RSTATUS"]
STRATEGIES = _RAW["STRATEGIES"]
ACTION_STATUSES = _RAW["ACTION_STATUSES"]
ACTION_TYPES = _RAW["ACTION_TYPES"]
_RISKS_RAW = _RAW["RISKS"]
LESSONS = _RAW["LESSONS"]

# 7 ролей по ТЗ (разд. 4) — права и ограничения
ROLES_FULL = [
    {"id": "admin", "label": "Администратор",
     "rights": "Управляет пользователями, ролями, справочниками, настройками и аудитом",
     "limits": "Не подменяет содержательные решения владельца риска без делегирования"},
    {"id": "riskmanager", "label": "Риск-менеджер/модератор",
     "rights": "Запускает сессии, загружает материалы, ведёт реестр, верифицирует предложения и методологию",
     "limits": "Значимые изменения должны иметь основание и фиксироваться в журнале"},
    {"id": "owner", "label": "Владелец риска",
     "rights": "Уточняет риск, подтверждает оценки, выбирает меры, обновляет статусы",
     "limits": "Работает в пределах назначенного контура рисков"},
    {"id": "expert", "label": "Эксперт предметной области",
     "rights": "Комментирует и предлагает причины, события, последствия, меры и триггеры",
     "limits": "Не утверждает итоговые оценки без отдельного права"},
    {"id": "pm", "label": "Руководитель проекта/портфеля",
     "rights": "Просматривает dashboard, топ-риски, статусы, отчёты; участвует в согласовании",
     "limits": "Не редактирует данные без роли владельца/модератора"},
    {"id": "viewer", "label": "Viewer",
     "rights": "Просматривает утверждённые данные и отчёты",
     "limits": "Не редактирует, не комментирует и не запускает LLM-действия"},
    {"id": "service", "label": "Интеграционный сервис",
     "rights": "Выполняет технический обмен через API в будущем",
     "limits": "Сервисная учётная запись, ограниченные права и полный аудит"},
]
ROLE_LABEL = {r["id"]: r["label"] for r in ROLES_FULL}

# Ключевые роли для входа в систему (чек-лист: «Ключевые роли 2 — инициатор и
# риск-менеджер, другие роли нужны как владельцы рисков»)
LOGIN_ROLES = [
    {"id": "initiator", "label": "Инициатор риска"},
    {"id": "riskmanager", "label": "Риск-менеджер"},
]

EXPERT_STATUSES = ["Предложено", "Принято", "Изменено", "Отклонено", "Требует уточнения", "Недостаточно данных"]

PROJECT_TYPES = ["Гринфилд (новое строительство)", "Браунфилд (реконструкция действующего актива)"]
INDUSTRIES = ["Чёрная металлургия", "Энергетика", "Горнодобыча", "Логистика/инфраструктура", "Другое"]
CONTRACT_MODELS = ["EPC", "EPCM", "Хозспособ + отдельные подряды", "Смешанная модель"]
CAPEX_RANGES = ["до 10 млрд ₽", "10–50 млрд ₽", "50–150 млрд ₽", "свыше 150 млрд ₽"]
STAGES = ["Фаза 1 — Инициация", "Фаза 2 — Проектирование", "Фаза 3 — Закупки",
          "Фаза 4 — Строительство", "Фаза 5 — Ввод в эксплуатацию"]


def severity_of(score: int) -> str:
    """RRA 3×3: L=1-2, M=3-4, H=6-9 (методика v2.2, стр.8)."""
    if score >= 6:
        return "high"
    if score >= 3:
        return "medium"
    return "low"


SEV_LABEL = {"high": "Высокий (H)", "medium": "Средний (M)", "low": "Низкий (L)"}
SEV_COLOR = {"high": "#ff8b0f", "medium": "#ffb700", "low": "#00b22c"}
SEV_TINT = {"high": "#fff3e0", "medium": "#ffffe6", "low": "#e5f8e8"}

# Сегодняшняя дата — для расчёта просроченности мероприятий относительно
# реальных плановых сроков (как и в HTML-версии).
TODAY = date.today()
_RU_MONTHS = {"янв": 1, "фев": 2, "мар": 3, "апр": 4, "май": 5, "июн": 6,
              "июл": 7, "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12}


def _parse_due(due: str):
    if not due or "." not in due:
        return None
    mon, yy = due.split(".")
    mon = mon.strip().lower()[:3]
    if mon not in _RU_MONTHS or not yy.strip().isdigit():
        return None
    return date(2000 + int(yy.strip()), _RU_MONTHS[mon], 1)


def compute_overdue(actions) -> bool:
    for a in actions:
        if a.get("status") in ("В работе", "Планируется"):
            d = _parse_due(a.get("dueDate", ""))
            if d and d < TODAY:
                return True
    return False


def residual_answers(actions):
    if not actions:
        return False, False, False
    q1 = all(a.get("status") in ("В работе", "Выполнено") for a in actions)
    q2 = all(a.get("status") == "Выполнено" for a in actions)
    q3 = q2
    return q1, q2, q3


def residual_level_of(score, actions):
    orig = severity_of(score)
    da = sum(residual_answers(actions))
    if da >= 3:
        return "low"
    if da == 2:
        return "medium" if orig == "high" else "low"
    return orig


def pick_pi(level, p, i):
    targets = {"low": (1, 2), "medium": (3, 4), "high": (6, 9)}
    lo, hi = targets[level]
    if lo <= p * i <= hi:
        return p, i
    for np_ in range(p, 0, -1):
        for ni in range(i, 0, -1):
            if lo <= np_ * ni <= hi:
                return np_, ni
    return 1, 1


def _build_risks():
    risks = []
    for idx, r in enumerate(_RISKS_RAW):
        r = dict(r)
        r["seq"] = idx
        r["score"] = r["p"] * r["i"]
        level = residual_level_of(r["score"], r["actions"])
        r["pRes"], r["iRes"] = pick_pi(level, r["p"], r["i"])
        r["scoreRes"] = r["pRes"] * r["iRes"]
        r["overdue_computed"] = compute_overdue(r["actions"])
        risks.append(r)
    return risks


RISKS = _build_risks()
PROGRAM_TOTAL_RISKS = 92  # тепловая карта Программы ЦГП-2, УК№8, стр.1

RISK_TO_LESSON_CAT = {"tech": None, "pir": "ПИР", "techn": None, "supply": "Закупка оборудования",
                       "smr": "СМР", "process": None, "regulatory": None, "economic": None}


def cat_badge_html(cat_key: str) -> str:
    cat = RISK_CATS[cat_key]
    return f'<span class="badge badge-{cat_key}">{cat["label"]}</span>'


def status_pill_html(status_key: str) -> str:
    st_ = RSTATUS[status_key]
    return f'<span class="pill pill-{status_key}">{st_["label"]}</span>'


def score_pill_html(score: int) -> str:
    sev = severity_of(score)
    return f'<span class="score-pill" style="background:{SEV_COLOR[sev]}">{score}</span>'


def action_status_pill(status: str) -> str:
    cls = {"Планируется": "pill-identification", "В работе": "pill-monitoring",
           "Выполнено": "pill-verified", "Отклонено": "pill-rejected"}.get(status, "pill-unset")
    return f'<span class="pill {cls}">{status}</span>'
