"""
RiskAssess Bot — НЛМК. Streamlit-версия интерфейса (по решению чек-листа:
«прототип HTML/JS → реализация на Streamlit», см. RiskAssess_Bot_checklist.xlsx).

Запуск:  streamlit run app.py
"""
import streamlit as st

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
def render_dashboard():
    st.title("Дэшборд")
    st.caption(f'{ss["project"]["name"]} · СПП-{ss["user"]["spp"] or "—"} · {ss["project"]["region"]}')

    high = sum(1 for r in RISKS if severity_of(r["score"]) == "high")
    overdue = sum(1 for r in RISKS if r["overdue_computed"])
    k1, k2, k3, k4 = st.columns(4)
    for col, label, value, note, color in [
        (k1, "Рисков в программе", PROGRAM_TOTAL_RISKS, f"в реестре — топ-{len(RISKS)} с паспортами", "var(--ink-900)"),
        (k2, "Высокий уровень критичности (H)", high, "RRA 6–9 по свойственной оценке", "var(--amber-600)"),
        (k3, "ТОП-риски (эскалация на УК)", len(RISKS), "требуют внимания/решения УК", "var(--accent-500)"),
        (k4, "Просрочено мероприятий", overdue, "плановый срок реализации прошёл", "var(--amber-600)"),
    ]:
        col.markdown(
            f'<div class="kpi-tile"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value" style="color:{color}">{value}</div>'
            f'<div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 1.1])
    with left:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Риск-матрица (RRA = P×I)</div>', unsafe_allow_html=True)
            render_matrix_grid(RISKS, mode="inherent")
    with right:
        with st.container(border=True):
            st.markdown('<div class="panel-title">Топ рисков по критичности</div>', unsafe_allow_html=True)
            top = sorted(RISKS, key=lambda r: (-r["score"], r["id"]))[:5]
            for i, r in enumerate(top, 1):
                st.markdown(
                    f'<div style="display:flex; gap:10px; align-items:center; padding:8px 0; '
                    f'border-bottom:1px solid var(--line);">'
                    f'<div style="font-weight:800; color:var(--ink-400); width:18px;">{i}</div>'
                    f'<div style="flex:1;"><span style="color:var(--accent-600); font-weight:700; '
                    f'font-size:12px;">{r["id"]}</span>'
                    f'<div style="font-size:12.5px; color:var(--ink-900);">{r["description"]}</div></div>'
                    f'{score_pill_html(r["score"])}</div>', unsafe_allow_html=True)


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
