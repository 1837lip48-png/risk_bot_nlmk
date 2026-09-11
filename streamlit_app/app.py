"""
RiskAssess Bot — НЛМК. Streamlit-версия интерфейса (по решению чек-листа:
«прототип HTML/JS → реализация на Streamlit», см. RiskAssess_Bot_checklist.xlsx).

Запуск:  streamlit run app.py
"""
import re
from datetime import date, timedelta

import streamlit as st
import plotly.graph_objects as go

from data import (
    RISKS, LESSONS, RISK_CATS, RSTATUS, STRATEGIES, ACTION_STATUSES, ACTION_TYPES,
    ROLES_FULL, ROLE_LABEL, LOGIN_ROLES, EXPERT_STATUSES,
    PROJECT_TYPES, INDUSTRIES, CONTRACT_MODELS, CAPEX_RANGES, STAGES,
    PROGRAM_TOTAL_RISKS, RISK_TO_LESSON_CAT,
    severity_of, SEV_LABEL, SEV_COLOR, SEV_TINT,
    cat_badge_html, status_pill_html, score_pill_html, action_status_pill,
)
from styles import global_css
from logo import logo_svg

st.set_page_config(page_title="RiskAssess Bot · НЛМК", layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------ session
ss = st.session_state
ss.setdefault("stage", "login")          # login -> profile -> app
ss.setdefault("dark", False)
ss.setdefault("view", "dashboard")
ss.setdefault("user", {"name": "", "role": "riskmanager", "spp": ""})
ss.setdefault("project", {
    "name": "Программа ЦГП-2 (Стан 1700)", "new": False,
    "type": PROJECT_TYPES[1], "industry": INDUSTRIES[0], "region": "Липецкая область",
    "contract_model": CONTRACT_MODELS[0], "capex_range": CAPEX_RANGES[2],
    "duration": "48 мес.", "stage": STAGES[0],
    "long_lead": "Да", "unique_suppliers": "Да", "logistics_notes": "",
})
ss.setdefault("candidates", None)   # см. seed_candidates()
ss.setdefault("chat_log", [])

st.markdown(global_css(dark=ss["dark"]), unsafe_allow_html=True)


def seed_candidates():
    """Пул новых рисков-кандидатов (F-13/F-30) — иллюстративные примеры для
    демонстрации экспертного воркфлоу; реальных данных по кандидатам, ожидающим
    решения экспертов, в исходных материалах программы нет."""
    return [
        {"id": "C-01", "text": "Возможное удорожание металлоконструкций ЦГП-2 из-за роста цен на прокат во 2 п/г 2026",
         "category": "economic", "source": "Предложено вручную · Гущин И.В.", "status": "Предложено", "quality_ok": False},
        {"id": "C-02", "text": "Риск срыва поставки редукторов рольганг-тележки из-за санкционных ограничений на комплектующие",
         "category": "supply", "source": "RAG-подсказка · похожий урок LL-014", "status": "Требует уточнения", "quality_ok": True},
        {"id": "C-03", "text": "Недостаточная пропускная способность подъездных ж/д путей на пике поставок ОТО в 2027 г.",
         "category": "smr", "source": "Предложено вручную · Мордовкин Д.С.", "status": "Недостаточно данных", "quality_ok": False},
    ]


if ss["candidates"] is None:
    ss["candidates"] = seed_candidates()


def initials(name: str) -> str:
    parts = [p for p in name.strip().split() if p]
    return ((parts[0][0] if parts else "") + (parts[1][0] if len(parts) > 1 else "")).upper() or "—"


def quality_check(text: str, cause: str = "", consequence: str = "", owner: str = "") -> list[str]:
    """F-12: отсутствующие элементы и уточняющие вопросы по формулировке риска."""
    missing = []
    if not text or len(text.strip()) < 15:
        missing.append("Слишком короткое или отсутствующее описание риск-события — уточните, что именно может произойти.")
    if not cause:
        missing.append("Не указана причина — какое условие/фактор делает риск возможным?")
    if not consequence:
        missing.append("Не указано прямое следствие — на какой КПЭ (сроки/CAPEX/качество/объём) повлияет риск?")
    if not owner:
        missing.append("Не назначен владелец риска — кто будет отвечать за уточнение и меры?")
    if text and "%" not in text and "млн" not in text and "млрд" not in text and not missing:
        missing.append("Уточните материальность: есть ли оценка отклонения от КПЭ в % или деньгах?")
    return missing


# ============================================================ ЭКРАН: ЛОГИН
def render_login():
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        st.markdown("<div class='st-key-login_box'>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                f'<div class="login-brand"><div class="logo">{logo_svg(30,16,"#1492ff")}</div>'
                f'<div class="name">RiskAssess Bot</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown("**Укажите себя, роль и проект**")

            name = st.text_input("ФИО", value=ss["user"]["name"], placeholder="Введите имя")
            role_labels = [r["label"] for r in LOGIN_ROLES]
            role = st.selectbox("Роль", role_labels, index=0)

            spp_raw = st.text_input("СПП проекта", value=ss["user"]["spp"], placeholder="Только цифры, например 20240317")
            spp_digits = "".join(ch for ch in spp_raw if ch.isdigit())
            if spp_raw and spp_raw != spp_digits:
                st.caption("⚠ СПП указывается только цифрами — нецифровые символы будут отброшены.")

            project_choice = st.selectbox(
                "Проект", ["Программа ЦГП-2 (Стан 1700)", "+ Новый проект…"],
                help="Риск-регистр ведётся отдельно по каждому проекту.",
            )

            dark_toggle = st.toggle("Тёмная тема", value=ss["dark"])
            if dark_toggle != ss["dark"]:
                ss["dark"] = dark_toggle
                st.rerun()

            with st.expander("Роли и права доступа (ТЗ, разд. 4)"):
                st.caption("Для входа доступны 2 ключевые роли — Инициатор риска и Риск-менеджер. "
                           "Остальные роли назначаются как владельцы/участники по конкретным рискам.")
                for rr in ROLES_FULL:
                    st.markdown(f"**{rr['label']}** — {rr['rights']}")
                    st.caption(rr["limits"])

            if st.button("Войти", type="primary", use_container_width=True):
                if not name.strip():
                    st.error("Укажите ФИО.")
                else:
                    ss["user"] = {"name": name.strip(),
                                  "role": "initiator" if role == LOGIN_ROLES[0]["label"] else "riskmanager",
                                  "spp": spp_digits}
                    if project_choice.startswith("+"):
                        ss["project"]["new"] = True
                        ss["stage"] = "profile"
                    else:
                        ss["project"]["new"] = False
                        ss["stage"] = "app"
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================ ЭКРАН: ПРОФИЛЬ НОВОГО ПРОЕКТА (F-04, разд. 9.1)
def render_profile_form():
    _, mid, _ = st.columns([0.6, 2, 0.6])
    with mid:
        st.markdown("<div class='st-key-profile_box'>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### Профиль нового проекта")
            st.caption("Формируется по параметрам ТЗ (разд. 9.1) — используется для поиска похожих исторических "
                       "проектов и калибровки исторической вероятности/влияния.")

            p = dict(ss["project"])
            p["name"] = st.text_input("Название проекта", value="")
            c1, c2 = st.columns(2)
            with c1:
                p["type"] = st.selectbox("Тип проекта (brownfield/greenfield)", PROJECT_TYPES)
                p["industry"] = st.selectbox("Отрасль", INDUSTRIES)
                p["region"] = st.text_input("Регион и внешние условия", value=p["region"])
                p["contract_model"] = st.selectbox("Контрактная модель", CONTRACT_MODELS)
            with c2:
                p["capex_range"] = st.selectbox("CAPEX-диапазон", CAPEX_RANGES)
                p["duration"] = st.text_input("Длительность", value=p["duration"])
                p["stage"] = st.selectbox("Стадия", STAGES)
                p["long_lead"] = st.selectbox("Long-lead оборудование", ["Да", "Нет"])
            p["unique_suppliers"] = st.selectbox("Зависимость от уникальных поставщиков", ["Да", "Нет", "Частичная"])
            p["logistics_notes"] = st.text_area("Логистические и регуляторные особенности", value=p["logistics_notes"])

            cols = st.columns(2)
            if cols[0].button("Назад", use_container_width=True):
                ss["stage"] = "login"
                st.rerun()
            if cols[1].button("Создать проект и продолжить", type="primary", use_container_width=True):
                if not p["name"].strip():
                    st.error("Укажите название проекта.")
                else:
                    ss["project"] = p
                    ss["stage"] = "app"
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================ SIDEBAR
NAV_ITEMS = [
    ("dashboard", "📊", "Дэшборд"),
    ("register", "📋", "Риск-регистр"),
    ("matrix", "🔲", "Риск-матрица"),
    ("candidates", "➕", "Пул новых рисков"),
    ("lessons", "📘", "Извлечённые уроки"),
    ("chat", "💬", "Чат с ботом"),
]


def render_sidebar():
    with st.sidebar:
        st.markdown(
            f'<div class="nlmk-brand"><div class="logo">{logo_svg(26,14,"#1492ff")}</div>'
            f'<div class="name">RiskAssess Bot</div></div>',
            unsafe_allow_html=True,
        )
        for key, icon, label in NAV_ITEMS:
            active = ss["view"] == key
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         type="primary" if active else "secondary", use_container_width=True):
                ss["view"] = key
                st.rerun()

        st.markdown(
            f'<div class="nav-user"><div class="av">{initials(ss["user"]["name"])}</div>'
            f'<div class="txt"><div class="n">{ss["user"]["name"] or "—"}</div>'
            f'<div class="r">{"Риск-менеджер" if ss["user"]["role"]=="riskmanager" else "Инициатор риска"}</div></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        dark_toggle = st.toggle("🌙 Тёмная тема", value=ss["dark"], key="dark_toggle_app")
        if dark_toggle != ss["dark"]:
            ss["dark"] = dark_toggle
            st.rerun()
        if st.button("Сменить проект / выйти", use_container_width=True):
            ss["stage"] = "login"
            st.rerun()


# ============================================================ ЭКРАН: ДЭШБОРД
#
# Ниже — вспомогательные функции только для дэшборда (_dash_*). Они не трогают
# data.py и не меняют модель полей RISKS (см. README: «модель полей risks —
# по чек-листу будет отдельный шаблон, произвольные новые поля не добавляем»).
# Всё, что дэшборду нужно сверх готовых полей (статус жизненного цикла,
# просрочка на произвольную дату, таксономия из 7 групп, ₽-оценка ущерба),
# вычисляется на лету из уже существующих реальных полей риска.

# 7 таксономических групп по задаче дэшборда — «Технологические» и
# «Технические» (ключи tech/techn в RISK_CATS) объединены в одну группу.
# Цвета — те же токены ds-2.0, что и в styles.py:CAT_COLORS, но в HEX,
# т.к. Plotly не умеет резолвить CSS-переменные var(--...).
_DASH_CAT_TO_BUCKET = {
    "tech": "tech_techn", "techn": "tech_techn",
    "pir": "pir", "supply": "supply", "smr": "smr",
    "process": "process", "regulatory": "regulatory", "economic": "economic",
}
DASH_CAT_HEX = {
    "tech_techn": ("Технологические/Технические", "#167ffb"),  # accent-600
    "pir": ("ПИР", "#037963"),                                  # mint-700
    "supply": ("Снабжение", "#0096e2"),                         # cyan-700
    "smr": ("СМР/ПНР", "#ee1505"),                              # red-700
    "process": ("Процессные", "#803be0"),                       # violet-700
    "regulatory": ("Регуляторные", "#8a6d00"),                  # gold-700
    "economic": ("Экономические", "#0b3461"),                   # navycat-700
}

_DASH_LIFECYCLE_ORDER = ["Новый", "В работе", "Митигирован", "Закрыт", "Реализовался"]
_DASH_LIFECYCLE_HEX = {
    "Новый": "#0096e2", "В работе": "#167ffb", "Митигирован": "#0d932b",
    "Закрыт": "#66747e", "Реализовался": "#ee1505",
}

_DASH_RU_MONTHS = {"янв": 1, "фев": 2, "мар": 3, "апр": 4, "май": 5, "июн": 6,
                    "июл": 7, "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12}


def _dash_parse_due(due: str):
    """Разбор плановой даты мероприятия («мон.гг»). Локальная копия парсера
    (в data.py есть приватный аналог) — по условиям задачи страницы дэшборда
    трогать data.py нельзя, а формат даты дэшборду нужен для периодных KPI."""
    if not due or "." not in due:
        return None
    mon, yy = due.split(".")
    mon = mon.strip().lower()[:3]
    if mon not in _DASH_RU_MONTHS or not yy.strip().isdigit():
        return None
    return date(2000 + int(yy.strip()), _DASH_RU_MONTHS[mon], 1)


def _dash_overdue_actions_asof(risks, asof: date):
    """Мероприятия, просроченные по состоянию на дату asof. Даты реальные
    (actions[].dueDate), поэтому расчёт на любую дату — не фабрикация:
    просто тот же критерий просрочки, что и в data.py, применённый к другой
    точке отсчёта вместо «сегодня» (нужно для дельты KPI за период)."""
    out = []
    for r in risks:
        for a in r["actions"]:
            if a.get("status") in ("В работе", "Планируется"):
                d = _dash_parse_due(a.get("dueDate", ""))
                if d and d < asof:
                    out.append({"risk": r, "action": a})
    return out


def _dash_lifecycle_status(r) -> str:
    """Статус риска для донат-чарта (новый/в работе/митигирован/закрыт/
    реализовался). Такого поля в реестре нет (см. README), поэтому статус
    выводится из уже посчитанных реальных полей — статусов мероприятий и
    остаточной оценки (score/scoreRes) — без добавления новых полей в данные."""
    statuses = [a.get("status") for a in r["actions"]]
    if not statuses:
        return "Новый"
    if all(s == "Выполнено" for s in statuses):
        return "Закрыт"
    if severity_of(r["scoreRes"]) != severity_of(r["score"]):
        return "Митигирован"
    if all(s == "Планируется" for s in statuses):
        return "Новый"
    return "В работе"


def _dash_fin_impact_mln(text):
    """Парсинг реальной ₽-оценки из finImpact, если она указана текстом
    в реестре (сейчас — только у одного риска из 15); для остальных
    возвращает None, без подстановки выдуманных сумм."""
    if not text or text == "—":
        return None
    m = re.search(r"([\d,.]+)\s*млрд", text)
    if m:
        return float(m.group(1).replace(",", ".")) * 1000
    m = re.search(r"([\d,.]+)\s*млн", text)
    if m:
        return float(m.group(1).replace(",", "."))
    return None


def _dash_trend_html(delta, note: str) -> str:
    if delta is None:
        return f'<div class="kpi-note">{note}</div>'
    if delta > 0:
        return f'<div class="kpi-note" style="color:var(--red-700); font-weight:700;">▲ +{delta} {note}</div>'
    if delta < 0:
        return f'<div class="kpi-note" style="color:var(--green-700); font-weight:700;">▼ {delta} {note}</div>'
    return f'<div class="kpi-note">без изменений · {note}</div>'


def _dash_chart_layout(fig, dark: bool, height: int, **extra):
    text_color = "#ccd1d4" if dark else "#4d5d69"
    fig.update_layout(
        margin=dict(l=8, r=8, t=8, b=8), height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="PT Root UI, Segoe UI, Arial, sans-serif", size=12, color=text_color),
        **extra,
    )
    return fig


def _dash_render_taxonomy_bar(risks, dark: bool):
    counts = {k: 0 for k in DASH_CAT_HEX}
    for r in risks:
        counts[_DASH_CAT_TO_BUCKET[r["category"]]] += 1
    keys = list(DASH_CAT_HEX)
    labels = [DASH_CAT_HEX[k][0] for k in keys]
    values = [counts[k] for k in keys]
    colors = [DASH_CAT_HEX[k][1] for k in keys]
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h", marker_color=colors,
        text=values, textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x} риск(ов)<extra></extra>",
    ))
    _dash_chart_layout(
        fig, dark, 300,
        xaxis=dict(showgrid=False, visible=False, range=[0, max(values + [1]) * 1.25]),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _dash_render_status_donut(risks, dark: bool):
    counts = {k: 0 for k in _DASH_LIFECYCLE_ORDER}
    for r in risks:
        counts[_dash_lifecycle_status(r)] += 1
    labels = _DASH_LIFECYCLE_ORDER
    values = [counts[k] for k in labels]
    colors = [_DASH_LIFECYCLE_HEX[k] for k in labels]
    text_color = "#ccd1d4" if dark else "#4d5d69"
    ring_line = "#33404b" if dark else "#ffffff"
    total = sum(values) or 1
    # для нулевых долей подпись процента не рисуем — иначе несколько «0%»
    # накладываются друг на друга в точке, где нет дуги
    slice_text = [f"{round(100 * v / total)}%" if v else "" for v in values]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62, sort=False,
        marker=dict(colors=colors, line=dict(color=ring_line, width=2)),
        text=slice_text, textinfo="text", textfont=dict(color="#ffffff", size=11),
        hovertemplate="%{label}: %{value} риск(ов) (%{percent})<extra></extra>",
    ))
    _dash_chart_layout(
        fig, dark, 300,
        legend=dict(orientation="h", yanchor="top", y=-0.05, font=dict(size=11)),
        annotations=[dict(text=f"{sum(values)}<br>рисков", x=0.5, y=0.5, showarrow=False,
                           font=dict(size=15, color=text_color))],
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Статус выводится по ходу мероприятий и изменению остаточной оценки риска — "
               "отдельного поля «статус риска» с такими значениями в реестре пока нет.")


def _dash_render_damage_bubble(risks, dark: bool):
    text_color = "#ccd1d4" if dark else "#4d5d69"
    cat_order = [DASH_CAT_HEX[k][0] for k in DASH_CAT_HEX]
    xs, ys, sizes, colors, hovers = [], [], [], [], []
    annotated = None
    for r in risks:
        bucket = _DASH_CAT_TO_BUCKET[r["category"]]
        cat_label, cat_hex = DASH_CAT_HEX[bucket]
        fin_mln = _dash_fin_impact_mln(r.get("finImpact"))
        xs.append(cat_label)
        ys.append(r["score"])
        sizes.append(20 + r["score"] * 5)
        colors.append(cat_hex)
        fin_txt = f"≈{fin_mln:,.0f} млн ₽ (указано в реестре)".replace(",", " ") if fin_mln \
            else "финансовая оценка не указана в реестре"
        hovers.append(f'{r["id"]} · {r["description"][:70]}…<br>RRA={r["score"]} · {fin_txt}')
        if fin_mln and annotated is None:
            annotated = (cat_label, r["score"], fin_txt)
    fig = go.Figure(go.Scatter(
        x=xs, y=ys, mode="markers",
        marker=dict(size=sizes, color=colors, opacity=.85,
                    line=dict(width=1, color=("#1c222a" if dark else "#ffffff"))),
        hovertext=hovers, hoverinfo="text",
    ))
    if annotated:
        cat_label, score_y, fin_txt = annotated
        fig.add_annotation(x=cat_label, y=score_y, text=fin_txt.replace("указано в реестре", "факт"),
                            showarrow=True, arrowhead=2, ax=40, ay=-30,
                            font=dict(size=10, color=text_color))
    grid_color = "#3c4854" if dark else "#e5e8ea"
    _dash_chart_layout(
        fig, dark, 320,
        xaxis=dict(categoryorder="array", categoryarray=cat_order, tickfont=dict(size=10),
                    showgrid=False),
        yaxis=dict(title="RRA = P×I", range=[0, 10], gridcolor=grid_color, zeroline=False),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Размер пузырька — оценка RRA (P×I) по методике v2.2. Денежная оценка ущерба указана "
               "в реестре только для одного риска из 15 — она вынесена подписью; для остальных сумма "
               "в реестре не приведена (показывать вымышленные ₽ было бы недостоверно).")


def render_dashboard():
    st.title("Дэшборд")
    st.caption(f'{ss["project"]["name"]} · СПП-{ss["user"]["spp"] or "—"} · {ss["project"]["region"]}')

    period_options = {"7 дней": 7, "30 дней": 30, "90 дней": 90, "180 дней": 180}
    hc, pc = st.columns([3, 1])
    with pc:
        period_label = st.selectbox("Период", list(period_options), index=1, key="dash_period",
                                     help="Применяется к показателю просроченных мероприятий и "
                                          "к необязательному фильтру таблицы ниже — другие даты "
                                          "(обнаружения/закрытия риска) в данных программы не ведутся.")
    period_days = period_options[period_label]
    today = date.today()
    overdue_now_list = _dash_overdue_actions_asof(RISKS, today)
    overdue_prev_list = _dash_overdue_actions_asof(RISKS, today - timedelta(days=period_days))
    overdue_now = len(overdue_now_list)
    overdue_delta = overdue_now - len(overdue_prev_list)

    if overdue_now_list:
        st.error(f"⏰ Просрочено мероприятий: {overdue_now} — плановый срок реализации уже прошёл.")
        with st.expander("Показать просроченные мероприятия"):
            for item in overdue_now_list:
                r, a = item["risk"], item["action"]
                st.markdown(
                    f'<span style="color:var(--accent-600); font-weight:700; font-size:12px;">{r["id"]}</span> '
                    f'{a["text"]} <span style="color:var(--ink-400); font-size:11px;"> — '
                    f'{a["responsible"]} · срок {a["dueDate"]}</span>',
                    unsafe_allow_html=True,
                )

    high = sum(1 for r in RISKS if severity_of(r["score"]) == "high")
    closed = sum(1 for r in RISKS if _dash_lifecycle_status(r) == "Закрыт")
    no_history_note = "истории по датам обнаружения/закрытия риска в данных нет"
    k1, k2, k3, k4 = st.columns(4)
    for col, label, value, note_html, color in [
        (k1, "Всего активных рисков", len(RISKS),
         f'<div class="kpi-note">из {PROGRAM_TOTAL_RISKS} рисков программы</div>', "var(--ink-900)"),
        (k2, "Критических (высокий приоритет)", high,
         f'<div class="kpi-note">RRA 6–9, {no_history_note}</div>', "var(--amber-600)"),
        (k3, "Закрыто (все меры выполнены)", closed,
         f'<div class="kpi-note">{no_history_note}</div>', "var(--green-700)"),
        (k4, "Просрочено мероприятий", overdue_now,
         _dash_trend_html(overdue_delta, f"за {period_label}"), "var(--red-700)"),
    ]:
        col.markdown(
            f'<div class="kpi-tile"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="color:{color}">{value}</div>'
            f'{note_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 1.1])
    with left:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Риск-матрица (RRA = P×I)</div>', unsafe_allow_html=True)
            render_matrix_grid(RISKS, mode="inherent")
    with right:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Распределение по таксономии</div>', unsafe_allow_html=True)
            _dash_render_taxonomy_bar(RISKS, ss["dark"])

    st.markdown("<br>", unsafe_allow_html=True)
    left2, right2 = st.columns([1, 1.1])
    with left2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Статус риска</div>', unsafe_allow_html=True)
            _dash_render_status_donut(RISKS, ss["dark"])
    with right2:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Топ-5 самых критичных рисков</div>', unsafe_allow_html=True)
            top5 = sorted(RISKS, key=lambda r: (-r["score"], r["id"]))[:5]
            for r in top5:
                fin = r["finImpact"] if r["finImpact"] and r["finImpact"] != "—" else "не указано"
                st.markdown(
                    f'<div style="padding:10px 0; border-bottom:1px solid var(--line);">'
                    f'<div style="display:flex; justify-content:space-between; gap:8px;">'
                    f'<span style="color:var(--accent-600); font-weight:700; font-size:12px;">{r["id"]}</span>'
                    f'{score_pill_html(r["score"])}</div>'
                    f'<div style="font-size:12.5px; color:var(--ink-900); margin:4px 0 6px;">{r["description"]}</div>'
                    f'{cat_badge_html(r["category"])} '
                    f'<span class="badge" style="background:var(--canvas-alt); color:var(--ink-700);">{r["strategy"]}</span>'
                    f'<div style="font-size:11.5px; color:var(--ink-600); margin-top:6px;">'
                    f'👤 {r["owner"]} &nbsp;·&nbsp; 💰 {fin}</div>'
                    f'</div>', unsafe_allow_html=True)
                if st.button("Подробнее", key=f"dash_top5_{r['id']}"):
                    ss["open_risk"] = r["id"]
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="panel-title">Оценка ущерба от рисков</div>', unsafe_allow_html=True)
        _dash_render_damage_bubble(RISKS, ss["dark"])

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="panel-title">Реестр рисков — фильтры</div>', unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns(4)
        cat_filter = fc1.selectbox("Категория", ["Все"] + [RISK_CATS[k]["label"] for k in RISK_CATS],
                                    key="dash_f_cat")
        status_filter = fc2.selectbox("Статус", ["Все"] + [RSTATUS[k]["label"] for k in RSTATUS],
                                       key="dash_f_status")
        owners = sorted({r["owner"] for r in RISKS})
        owner_filter = fc3.selectbox("Ответственный", ["Все"] + owners, key="dash_f_owner")
        q = fc4.text_input("Поиск по ID или описанию", key="dash_f_q")
        period_only = st.checkbox(
            f"Показывать только риски с мероприятиями за «{period_label}»",
            key="dash_f_period",
            help="Фильтр по плановым срокам мероприятий (actions[].dueDate) — "
                 "иной привязки риска к периоду в данных нет.",
        )

        rows = RISKS
        if cat_filter != "Все":
            key = [k for k in RISK_CATS if RISK_CATS[k]["label"] == cat_filter][0]
            rows = [r for r in rows if r["category"] == key]
        if status_filter != "Все":
            key = [k for k in RSTATUS if RSTATUS[k]["label"] == status_filter][0]
            rows = [r for r in rows if r["status"] == key]
        if owner_filter != "Все":
            rows = [r for r in rows if r["owner"] == owner_filter]
        if q:
            ql = q.lower()
            rows = [r for r in rows if ql in r["id"].lower() or ql in r["description"].lower()]
        if period_only:
            cutoff = today - timedelta(days=period_days)
            rows = [r for r in rows if any(
                (_dash_parse_due(a.get("dueDate", "")) or date.min) >= cutoff for a in r["actions"])]

        header = st.columns([0.7, 1.3, 3, 0.6, 1.2, 1.4, 0.6])
        for c, t in zip(header, ["ID", "Категория", "Описание", "Score", "Владелец", "Статус", ""]):
            c.markdown(f"**{t}**")
        for r in rows:
            cols = st.columns([0.7, 1.3, 3, 0.6, 1.2, 1.4, 0.6])
            cols[0].markdown(f'<span class="mono" style="color:var(--accent-600); font-weight:700;">{r["id"]}</span>',
                              unsafe_allow_html=True)
            cols[1].markdown(cat_badge_html(r["category"]), unsafe_allow_html=True)
            cols[2].markdown(r["description"][:100] + ("…" if len(r["description"]) > 100 else ""))
            cols[3].markdown(score_pill_html(r["score"]), unsafe_allow_html=True)
            cols[4].markdown(r["owner"])
            cols[5].markdown(status_pill_html(r["status"]), unsafe_allow_html=True)
            if cols[6].button("Открыть", key=f"dash_open_{r['id']}"):
                ss["open_risk"] = r["id"]
                st.rerun()
        st.markdown(f'<div style="color:var(--ink-400); font-size:12px; margin-top:6px;">{len(rows)} рисков</div>',
                    unsafe_allow_html=True)

    if ss.get("open_risk"):
        render_risk_dialog(ss["open_risk"])

def render_matrix_grid(risks, mode="inherent"):
    html = '<div class="matrix-wrap">'
    for row in (3, 2, 1):
        html += '<div class="matrix-row">'
        rowlabel = {3: "Высокая", 2: "Средняя", 1: "Низкая"}[row]
        html += (f'<div class="matrix-yhead"><b style="font-family:var(--font-mono); '
                 f'font-size:14px; color:var(--ink-900);">{row}</b><br>{rowlabel}</div>')
        for col in (1, 2, 3):
            sev = severity_of(row * col)
            bubbles = ""
            for r in risks:
                p, i = (r["p"], r["i"]) if mode == "inherent" else (r["pRes"], r["iRes"])
                if p == row and i == col:
                    bs = r["score"] if mode == "inherent" else r["scoreRes"]
                    bsev = severity_of(bs)
                    bubbles += (f'<div class="matrix-bubble" style="background:{SEV_COLOR[bsev]}" '
                                f'title="{r["id"]} — {r["description"]}">{r["id"].replace("R-","")}</div>')
            html += f'<div class="matrix-cell" style="background:{SEV_TINT[sev]}">{bubbles}</div>'
        html += "</div>"
    html += '<div class="matrix-row"><div class="matrix-yhead"></div>'
    for col, lbl in [(1, "Низкое"), (2, "Среднее"), (3, "Высокое")]:
        html += f'<div class="matrix-xfoot"><b style="font-family:var(--font-mono);">{col}</b><br>{lbl}</div>'
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)
    st.markdown(
        f'<div style="display:flex; gap:14px; font-size:11.5px; color:var(--ink-600); margin-top:8px;">'
        f'<span>🟢 L — низкий (RRA 1–2)</span><span>🟡 M — средний (RRA 3–4)</span>'
        f'<span>🟠 H — высокий (RRA 6–9)</span></div>', unsafe_allow_html=True)


# ============================================================ ЭКРАН: РИСК-МАТРИЦА (полная)
def render_matrix():
    st.title("Риск-матрица 3×3")
    st.caption("RRA = P × I по «Методике оценки рисков для мегапроектов» v2.2 — вероятность × материальность")
    mode = st.radio("Режим", ["Свойственный риск", "Остаточный риск"], horizontal=True, label_visibility="collapsed")
    with st.container(border=True):
        render_matrix_grid(RISKS, mode="inherent" if mode.startswith("Свой") else "residual")


# ============================================================ ЭКРАН: РИСК-РЕГИСТР
def render_register():
    head_l, head_r = st.columns([3, 1.4])
    with head_l:
        st.title("Риск-регистр")
        st.caption(f'Топ-{len(RISKS)} из {PROGRAM_TOTAL_RISKS} рисков программы {ss["project"]["name"]} '
                   f'с оценкой P/I по методике и статусом мероприятий')
    with head_r:
        st.markdown("<div style='height:34px'></div>", unsafe_allow_html=True)
        ec1, ec2 = st.columns(2)
        if ec1.button("📄 Экспорт в PDF", use_container_width=True, help="F-46: экспорт отчётов — .xlsx и PDF"):
            st.toast("Отчёт сформирован (PDF) — мок для демонстрации F-46.")
        if ec2.button("📊 Экспорт .xlsx", use_container_width=True, help="F-46: экспорт отчётов — .xlsx и PDF"):
            st.toast("Реестр выгружен (.xlsx) — мок для демонстрации F-46.")

    c1, c2, c3 = st.columns(3)
    cat_filter = c1.selectbox("Категория", ["Все"] + [RISK_CATS[k]["label"] for k in RISK_CATS])
    status_filter = c2.selectbox("Статус", ["Все"] + [RSTATUS[k]["label"] for k in RSTATUS])
    q = c3.text_input("Поиск по ID или описанию", "")

    rows = RISKS
    if cat_filter != "Все":
        key = [k for k in RISK_CATS if RISK_CATS[k]["label"] == cat_filter][0]
        rows = [r for r in rows if r["category"] == key]
    if status_filter != "Все":
        key = [k for k in RSTATUS if RSTATUS[k]["label"] == status_filter][0]
        rows = [r for r in rows if r["status"] == key]
    if q:
        ql = q.lower()
        rows = [r for r in rows if ql in r["id"].lower() or ql in r["description"].lower()]

    with st.container(border=True):
        header = st.columns([0.7, 1.1, 3, 0.4, 0.4, 0.6, 1.2, 1.4, 0.6])
        for c, t in zip(header, ["ID", "Категория", "Описание", "P", "I", "Score", "Владелец", "Статус", ""]):
            c.markdown(f"**{t}**")
        for r in rows:
            cols = st.columns([0.7, 1.1, 3, 0.4, 0.4, 0.6, 1.2, 1.4, 0.6])
            cols[0].markdown(f'<span class="mono" style="color:var(--accent-600); font-weight:700;">{r["id"]}</span>',
                              unsafe_allow_html=True)
            cols[1].markdown(cat_badge_html(r["category"]), unsafe_allow_html=True)
            cols[2].markdown(r["description"][:120] + ("…" if len(r["description"]) > 120 else ""))
            cols[3].markdown(str(r["p"]))
            cols[4].markdown(str(r["i"]))
            cols[5].markdown(score_pill_html(r["score"]), unsafe_allow_html=True)
            cols[6].markdown(r["owner"])
            cols[7].markdown(status_pill_html(r["status"]), unsafe_allow_html=True)
            if cols[8].button("Открыть", key=f"open_{r['id']}"):
                ss["open_risk"] = r["id"]
                st.rerun()
        st.markdown(f'<div style="color:var(--ink-400); font-size:12px; margin-top:6px;">{len(rows)} рисков</div>',
                    unsafe_allow_html=True)

    if ss.get("open_risk"):
        render_risk_dialog(ss["open_risk"])


@st.dialog("Карточка риска", width="large")
def render_risk_dialog(risk_id):
    r = next(x for x in RISKS if x["id"] == risk_id)
    st.markdown(f"##### {r['id']} · {r['description']}")
    st.markdown(
        f'{cat_badge_html(r["category"])} &nbsp; <span class="badge" style="background:var(--canvas-alt); '
        f'color:var(--ink-700);">{r["stage"]}</span> &nbsp; {status_pill_html(r["status"])} &nbsp; '
        f'<span class="badge" style="background:var(--canvas-alt); color:var(--ink-700);">{r["strategy"]}</span>'
        + (' &nbsp; <span class="badge" style="background:var(--red-50); color:var(--red-700);">⏰ Просрочено</span>'
           if r["overdue_computed"] else ""),
        unsafe_allow_html=True,
    )
    st.markdown(
        f'👤 **{r["owner"]}** &nbsp;·&nbsp; Свойственный: P{r["p"]}×I{r["i"]} = {score_pill_html(r["score"])} '
        f'&nbsp;·&nbsp; Остаточный: P{r["pRes"]}×I{r["iRes"]} = {score_pill_html(r["scoreRes"])}',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    c1.markdown(f"**Причина**\n\n{r['cause']}")
    c2.markdown(f"**Прямое следствие**\n\n{r['consequence']}")
    if r["finImpact"] and r["finImpact"] != "—":
        st.markdown(f"**Финансовое влияние:** {r['finImpact']}")

    st.markdown("**Мероприятия реагирования**")
    for a in r["actions"]:
        st.markdown(
            f'{action_status_pill(a["status"])} {a["text"]} '
            f'<span style="color:var(--ink-400); font-size:11px;"> — {a["type"]} · {a["responsible"]} · '
            f'срок {a["dueDate"]}{" · " + a["cost"] if a.get("cost") and a["cost"] != "—" else ""}</span>'
            + (f'<div style="color:var(--ink-400); font-size:11px;">Триггер: {a["trigger"]}</div>' if a.get("trigger") else ""),
            unsafe_allow_html=True,
        )

    with st.expander("🔍 Проверка качества формулировки (F-12)"):
        issues = quality_check(r["description"], r["cause"], r["consequence"], r["owner"])
        if issues:
            for it in issues:
                st.warning(it)
        else:
            st.success("Формулировка риска содержит причину, следствие, владельца и материальность.")

    lesson_cat = RISK_TO_LESSON_CAT.get(r["category"])
    related = [l for l in LESSONS if lesson_cat and l["cc"] == lesson_cat][:3]
    if related:
        st.markdown(f'**Похожие уроки в базе** ({SEV_LABEL[severity_of(r["score"])]}, '
                    f'категория «{RISK_CATS[r["category"]]["label"]}»)')
        for l in related:
            st.markdown(f'<span class="badge" style="background:var(--canvas-alt); color:var(--ink-700);">'
                        f'{l["id"]}</span> {l["title"]}', unsafe_allow_html=True)

    if st.button("Закрыть", type="primary"):
        ss["open_risk"] = None
        st.rerun()


# ============================================================ ЭКРАН: ПУЛ НОВЫХ РИСКОВ (F-13/F-30)
def render_candidates():
    st.title("Пул новых рисков")
    st.caption("Риск не включается в основной реестр до экспертного решения (F-13). "
               "Статусы предложений (F-30): предложено / принято / изменено / отклонено / требует уточнения / недостаточно данных.")

    with st.expander("➕ Предложить новый риск", expanded=False):
        text = st.text_area("Формулировка риска")
        cat = st.selectbox("Категория", [RISK_CATS[k]["label"] for k in RISK_CATS], key="cand_cat")
        cause = st.text_input("Причина (если известна)", key="cand_cause")
        cons = st.text_input("Прямое следствие (если известно)", key="cand_cons")
        if st.button("Проверить формулировку (F-12)"):
            issues = quality_check(text, cause, cons, owner="")
            if issues:
                for it in issues:
                    st.warning(it)
            else:
                st.success("Формулировка полная — можно отправлять на экспертное решение.")
        if st.button("Отправить в пул", type="primary"):
            if text.strip():
                cat_key = [k for k in RISK_CATS if RISK_CATS[k]["label"] == cat][0]
                new_id = f"C-{len(ss['candidates'])+1:02d}"
                ss["candidates"].append({
                    "id": new_id, "text": text.strip(), "category": cat_key,
                    "source": f"Предложено вручную · {ss['user']['name'] or 'аноним'}",
                    "status": "Предложено", "quality_ok": not quality_check(text, cause, cons, ""),
                })
                st.rerun()
            else:
                st.error("Введите формулировку риска.")

    with st.container(border=True):
        for c in ss["candidates"]:
            cols = st.columns([2.2, 1, 0.9, 1.4])
            with cols[0]:
                st.markdown(f'{cat_badge_html(c["category"])}  {c["text"]}', unsafe_allow_html=True)
                st.caption(c["source"])
            cols[1].markdown("✅ формулировка полная" if c["quality_ok"] else "⚠ требует уточнения")
            cols[2].markdown(f'<span class="badge" style="background:var(--accent-50); color:var(--accent-600);">'
                              f'{c["status"]}</span>', unsafe_allow_html=True)
            new_status = cols[3].selectbox("Статус", EXPERT_STATUSES,
                                            index=EXPERT_STATUSES.index(c["status"]),
                                            key=f"status_{c['id']}", label_visibility="collapsed")
            if new_status != c["status"]:
                c["status"] = new_status
                st.rerun()
            st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)


# ============================================================ ЭКРАН: ИЗВЛЕЧЁННЫЕ УРОКИ
def render_lessons():
    st.title("Извлечённые уроки")
    st.caption("База проблем и извлечённых уроков по проектам НЛМК — источник данных для оценки новых рисков.")
    ccs = sorted({l["cc"] for l in LESSONS if l["cc"]})
    c1, c2 = st.columns([1, 2])
    cc_filter = c1.selectbox("Центр компетенций", ["Все"] + ccs)
    q = c2.text_input("Поиск", "")

    rows = LESSONS
    if cc_filter != "Все":
        rows = [l for l in rows if l["cc"] == cc_filter]
    if q:
        ql = q.lower()
        rows = [l for l in rows if ql in l["title"].lower() or ql in (l.get("lesson") or "").lower()]

    st.markdown(f'<div style="color:var(--ink-400); font-size:12px; margin-bottom:6px;">'
                f'Найдено {len(rows)} из {len(LESSONS)} уроков &nbsp;·&nbsp; '
                f'<span title="RAG-контур (chunking/embeddings/reranking) — бэкенд, вне интерфейса MVP">'
                f'🔎 поиск по ключевым словам, векторный поиск — F-23/F-25 (бэкенд)</span></div>',
                unsafe_allow_html=True)

    with st.container(border=True):
        for l in rows[:30]:
            with st.expander(f'{l["id"]} · {l["title"]}'):
                st.markdown(f'<span class="badge" style="background:var(--canvas-alt); color:var(--ink-700);">'
                            f'{l["cc"] or "Не указан"}</span> &nbsp; '
                            f'<span class="pill pill-verified">✔ источник проверен</span>', unsafe_allow_html=True)
                st.markdown(f"**Проблема:** {l.get('problem','—')}")
                st.markdown(f"**Корневая причина:** {l.get('rootCause','—')}")
                st.markdown(f"**Урок:** {l.get('lesson','—')}")
                if l.get("improvement"):
                    st.markdown(f"**Улучшение:** {l['improvement']}")
        if len(rows) > 30:
            st.caption(f"Показаны первые 30 из {len(rows)} — уточните поиск.")


# ============================================================ ЭКРАН: ЧАТ С БОТОМ (F-28)
def render_chat():
    st.title("Чат с ботом")
    st.caption("Вопросы о рисках, исторических аналогах, мерах и статистике (F-28). "
               "При недостатке источников бот сообщает об отсутствии данных, а не додумывает (F-29).")

    for msg in ss["chat_log"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

    prompt = st.chat_input("Спросите про риски программы ЦГП-2…")
    if prompt:
        ss["chat_log"].append({"role": "user", "text": prompt})
        answer = mock_llm_answer(prompt)
        ss["chat_log"].append({"role": "assistant", "text": answer})
        st.rerun()


def mock_llm_answer(prompt: str) -> str:
    """Мок-ответ без реального LLM-вызова — только по уже загруженным реальным
    данным реестра/уроков; иначе — явное сообщение о недостатке данных (F-29)."""
    pl = prompt.lower()
    hits = [r for r in RISKS if any(w in r["description"].lower() for w in pl.split() if len(w) > 4)]
    if "топ" in pl or "критичн" in pl or "самые" in pl:
        top = sorted(RISKS, key=lambda r: -r["score"])[:3]
        lines = [f"- **{r['id']}** ({r['score']}, {SEV_LABEL[severity_of(r['score'])]}) — {r['description']}" for r in top]
        return "Топ-3 риска программы по критичности (RRA):\n\n" + "\n".join(lines)
    if hits:
        r = hits[0]
        return (f"По запросу нашёл риск **{r['id']}**: {r['description']}\n\n"
                f"Владелец: {r['owner']} · Статус: {RSTATUS[r['status']]['label']} · "
                f"RRA {r['score']} ({SEV_LABEL[severity_of(r['score'])]}).")
    return ("Недостаточно данных в загруженном реестре и базе уроков, чтобы ответить точно "
            "(F-29 — контроль галлюцинаций). Попробуйте уточнить запрос или укажите ID риска.")


# ============================================================ ROUTER
if ss["stage"] == "login":
    render_login()
elif ss["stage"] == "profile":
    render_profile_form()
else:
    render_sidebar()
    view = ss["view"]
    if view == "dashboard":
        render_dashboard()
    elif view == "register":
        render_register()
    elif view == "matrix":
        render_matrix()
    elif view == "candidates":
        render_candidates()
    elif view == "lessons":
        render_lessons()
    elif view == "chat":
        render_chat()
