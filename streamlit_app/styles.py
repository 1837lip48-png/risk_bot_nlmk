"""Глобальный CSS: токены НЛМК ds-2.0 (те же значения, что в HTML-прототипе)."""

TOKENS_LIGHT = """
:root{
  --navy-900:#112542; --navy-800:#0b3461; --navy-700:#243e64;
  --accent-600:#167ffb; --accent-500:#008fff; --accent-100:#cbe1ff; --accent-50:#e8f5ff;
  --ink-900:#001729; --ink-700:#4d5d69; --ink-600:#66747e; --ink-400:#99a2a9;
  --paper-0:#ffffff; --canvas:#edeeef; --canvas-alt:#f2f3f4; --line:#e5e8ea;
  --green-700:#0d932b; --green-600:#00b22c; --green-50:#e5f8e8;
  --amber-700:#f97b0f; --amber-600:#ff8b0f; --amber-50:#fff3e0;
  --red-700:#ee1505; --red-600:#fc200c; --red-50:#ffedf0;
  --gold-700:#8a6d00; --gold-600:#ffb700; --gold-50:#ffffe6;
  --violet-700:#803be0; --violet-50:#f4ebfe;
  --mint-700:#037963; --mint-50:#e0fbf5;
  --navycat-700:#0b3461; --navycat-50:#e6e9ed;
  --cyan-700:#0096e2; --cyan-50:#dff7fe;
  --slate-700:#334554; --slate-50:#f2f3f4;
  --logo-blue:#1492ff;
  --font-display:'Golos Text','PT Root UI','Segoe UI',Arial,sans-serif;
  --font-body:'Golos Text','PT Root UI','Segoe UI',Arial,sans-serif;
  --font-mono:'IBM Plex Mono','SFMono-Regular',monospace;
  --radius-card:8px; --radius-chip:4px;
}
"""

CAT_COLORS = {
    "tech": ("var(--accent-50)", "var(--accent-600)"),
    "pir": ("var(--mint-50)", "var(--mint-700)"),
    "techn": ("var(--slate-50)", "var(--slate-700)"),
    "supply": ("var(--cyan-50)", "var(--cyan-700)"),
    "smr": ("var(--red-50)", "var(--red-700)"),
    "process": ("var(--violet-50)", "var(--violet-700)"),
    "regulatory": ("var(--gold-50)", "var(--gold-700)"),
    "economic": ("var(--navycat-50)", "var(--navycat-700)"),
}
STATUS_COLORS = {
    "identification": ("var(--canvas-alt)", "var(--ink-700)"),
    "analysis": ("var(--violet-50)", "var(--violet-700)"),
    "response": ("var(--amber-50)", "var(--amber-700)"),
    "monitoring": ("var(--accent-50)", "var(--accent-600)"),
    "unset": ("var(--canvas-alt)", "var(--ink-400)"),
    "verified": ("var(--green-50)", "var(--green-700)"),
    "rejected": ("var(--red-50)", "var(--red-700)"),
}


def _badge_rules():
    rules = []
    for k, (bg, fg) in CAT_COLORS.items():
        rules.append(f".badge-{k}{{background:{bg};color:{fg};}}")
    for k, (bg, fg) in STATUS_COLORS.items():
        rules.append(f".pill-{k}{{background:{bg};color:{fg};}}")
    return "\n".join(rules)


TOKENS_DARK = """
:root{
  --navy-900:#0b1626; --navy-800:#0b3461; --navy-700:#243e64;
  --ink-900:#f2f3f4; --ink-700:#ccd1d4; --ink-600:#99a2a9; --ink-400:#7c8993;
  --paper-0:#475363; --canvas:#3c4854; --canvas-alt:#33404b; --line:#56636e;
  --accent-50:#16233f; --accent-100:#1b3563;
  --green-50:#0f2b1c; --amber-50:#2e2413; --red-50:#301c1d; --gold-50:#2c2408;
  --violet-50:#241c3d; --mint-50:#102a26; --navycat-50:#1c2838; --cyan-50:#0e2a35; --slate-50:#33404b;
}
"""


def global_css(dark: bool = False) -> str:
    return f"""
<style>
{TOKENS_LIGHT}
{TOKENS_DARK if dark else ""}

html, body, [class*="css"] {{ font-family: var(--font-body); }}
.stApp {{ background: var(--canvas); }}
#MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1280px; }}

h1,h2,h3,h4 {{ font-family: var(--font-display); color: var(--ink-900); }}

/* ---------- Карточки/панели (нативные bordered-контейнеры Streamlit) ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--paper-0); border:1px solid var(--line) !important; border-radius: var(--radius-card) !important;
}}
.panel-title {{ font-size:12px; font-weight:800; letter-spacing:.5px; text-transform:uppercase; color:var(--ink-700); margin-bottom:6px;}}

/* Логин/профиль — центрированная карточка */
div[data-testid="stVerticalBlockBorderWrapper"].login-card,
.st-key-login_box div[data-testid="stVerticalBlockBorderWrapper"],
.st-key-profile_box div[data-testid="stVerticalBlockBorderWrapper"] {{
  box-shadow: 0 20px 50px -20px rgba(0,23,41,.25);
}}

/* ---------- Значки / статусы ---------- */
.badge {{ display:inline-flex; align-items:center; padding:3px 9px; border-radius:var(--radius-chip); font-size:11.5px; font-weight:700; }}
.pill {{ display:inline-flex; align-items:center; gap:5px; padding:3px 9px; border-radius:var(--radius-chip); font-size:11px; font-weight:700; }}
{_badge_rules()}
.score-pill {{ display:inline-flex; align-items:center; justify-content:center; min-width:30px; padding:2px 7px;
  border-radius:8px; font-family:var(--font-mono); font-weight:800; font-size:13px; color:#fff; }}

/* ---------- KPI-тайлы ---------- */
.kpi-tile {{ background: var(--paper-0); border:1px solid var(--line); border-radius: var(--radius-card); padding:14px 16px; }}
.kpi-label {{ font-size:11px; font-weight:800; letter-spacing:.4px; text-transform:uppercase; color:var(--ink-600); }}
.kpi-value {{ font-family:var(--font-display); font-size:28px; font-weight:800; color:var(--ink-900); margin-top:2px;}}
.kpi-note {{ font-size:11px; color:var(--ink-400); margin-top:2px;}}

/* ---------- Матрица 3x3 ---------- */
.matrix-wrap {{ display:inline-block; }}
.matrix-row {{ display:flex; align-items:stretch; }}
.matrix-yhead {{ width:74px; display:flex; flex-direction:column; align-items:center; justify-content:center;
  font-size:11px; color:var(--ink-600); font-weight:700; text-align:center; }}
.matrix-cell {{ width:150px; height:110px; margin:3px; border-radius:8px; padding:6px; display:flex; flex-wrap:wrap;
  align-content:flex-start; gap:4px; }}
.matrix-bubble {{ width:30px;height:30px;border-radius:50%; display:flex;align-items:center;justify-content:center;
  color:#fff; font-family:var(--font-mono); font-weight:800; font-size:9.5px; border:2px solid rgba(255,255,255,.85);
  box-shadow:0 2px 6px rgba(0,23,41,.25); }}
.matrix-xfoot {{ width:150px; margin:3px; text-align:center; font-size:11px; color:var(--ink-600); font-weight:700;}}

/* ---------- Sidebar (иконки, раскрытие по наведению) ---------- */
section[data-testid="stSidebar"] {{
  background: var(--navy-900) !important; width: 74px !important; min-width:74px !important;
  transition: width .18s ease; overflow: visible !important; z-index: 999;
}}
section[data-testid="stSidebar"]:hover {{ width: 250px !important; min-width:250px !important; }}
section[data-testid="stSidebar"] .block-container {{ padding: 18px 10px; }}
section[data-testid="stSidebar"] * {{ color:#c9d3de; }}
.nlmk-brand {{ display:flex; align-items:center; gap:10px; margin-bottom:22px; white-space:nowrap; overflow:hidden;}}
.nlmk-brand .logo {{ width:34px; height:34px; border-radius:8px; background:#fff; display:flex; align-items:center;
  justify-content:center; flex-shrink:0; }}
.nlmk-brand .name {{ font-family:var(--font-display); font-weight:800; font-size:14px; color:#fff; opacity:0;
  transition: opacity .15s; }}
section[data-testid="stSidebar"]:hover .nlmk-brand .name {{ opacity:1; }}

section[data-testid="stSidebar"] div[data-testid="stButton"] button {{
  background: transparent; border:none; color:#c9d3de; text-align:left; justify-content:flex-start;
  white-space:nowrap; overflow:hidden; font-weight:600; font-size:13.5px; padding:9px 10px; width:100%;
  border-radius:8px; margin-bottom:2px; box-shadow:none;
}}
section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {{ background: rgba(255,255,255,.08); color:#fff; }}
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {{
  background: var(--accent-600) !important; color:#fff !important; border-color:var(--accent-600) !important;
}}
section[data-testid="stSidebar"] div[data-testid="stButton"] button p {{ white-space:nowrap; }}

.nav-user {{ display:flex; align-items:center; gap:10px; margin-top:16px; padding-top:14px;
  border-top:1px solid rgba(255,255,255,.12); white-space:nowrap; overflow:hidden; max-width:220px;}}
.nav-user .av {{ width:30px;height:30px;border-radius:50%; background:var(--accent-500); color:#fff; display:flex;
  align-items:center; justify-content:center; font-size:11.5px; font-weight:800; flex-shrink:0;}}
.nav-user .txt {{ opacity:0; transition:opacity .12s; line-height:1.25; white-space:nowrap; overflow:hidden; }}
section[data-testid="stSidebar"]:hover .nav-user .txt {{ opacity:1; }}
.nav-user .txt .n {{ font-size:12.5px; font-weight:700; color:#fff; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:170px;}}
.nav-user .txt .r {{ font-size:11px; color:#8fa0b3; white-space:nowrap; }}

/* Все текстовые элементы сайдбара не переносятся при ширине 74px */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p {{
  white-space: nowrap; overflow: hidden; text-overflow: clip;
}}

/* ---------- Логин ---------- */
.login-wrap {{ max-width:420px; margin: 40px auto; background:var(--paper-0); border:1px solid var(--line);
  border-radius:16px; padding:32px 30px; box-shadow: 0 20px 50px -20px rgba(0,23,41,.25);}}
.login-brand {{ display:flex; align-items:center; gap:12px; margin-bottom:22px;}}
.login-brand .logo {{ width:44px;height:44px;border-radius:10px; background:var(--navy-900); display:flex;
  align-items:center; justify-content:center;}}
.login-brand .name {{ font-family:var(--font-display); font-weight:800; font-size:19px; color:var(--ink-900);}}

/* ---------- Streamlit widget tuning ---------- */
div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] > div, div[data-testid="stTextArea"] textarea {{
  border-radius:8px !important;
}}
.stButton>button {{ border-radius:8px; font-weight:700; }}
.stButton>button[kind="primary"] {{ background: var(--accent-500); border-color: var(--accent-500); }}

hr {{ border-color: var(--line); }}
</style>
"""
