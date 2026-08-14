"""Theme injection + HTML render helpers.

Ported 1:1 from `frontend/src/styles/global.css` (the React app) with the
addition of Streamlit-specific overrides so the native widgets adopt the same
dark glassmorphism look. No layout / style changes vs the React version.
"""

import html as _html

import streamlit as st

from config import FAIL_GRADES

ACCENT = "#818cf8"

_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg-color: #020617;
  --sidebar-bg: #0f172a;
  --card-bg: rgba(30, 41, 59, 0.4);
  --border-color: rgba(255, 255, 255, 0.08);
  --primary-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --accent-color: #818cf8;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, #root { min-height: 100vh; background-color: var(--bg-color); font-family: 'Inter', sans-serif; color: var(--text-primary); }

/* ---------- Streamlit shell ---------- */
#MainMenu { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stFooter"] { display: none; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stStatusWidget"] { display: none; }
.stApp { background-color: var(--bg-color); font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] {
  background: radial-gradient(circle at 50% 0%, rgba(99, 102, 241, 0.12) 0%, transparent 60%);
}
.block-container { max-width: 1200px; padding-top: 1.2rem; padding-bottom: 5rem; }

h1, h2, h3, h4, h5, h6 { color: var(--text-primary); font-weight: 800; letter-spacing: -0.025em; }
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] { color: var(--text-secondary); }
a { color: var(--accent-color); text-decoration: none; }

/* ---------- Widgets ---------- */
[data-testid="stWidgetLabel"] p {
  font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;
  color: var(--text-secondary); margin-bottom: 6px;
}
[data-testid="stTextInput"] div[data-baseweb="input"],
[data-testid="stTextArea"] div[data-baseweb="textarea"] {
  background-color: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}
[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
[data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within { border-color: var(--accent-color); }
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea { background: transparent; color: #fff; caret-color: #fff; }
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: #64748b; }

[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  background-color: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  color: #fff;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover { border-color: rgba(168, 85, 247, 0.4); }
[data-testid="stSelectbox"] div[data-baseweb="select"] > div span { color: #fff; }
div[data-baseweb="popover"] ul {
  background-color: var(--sidebar-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}
div[data-baseweb="popover"] li[role="option"] { color: var(--text-secondary); }
div[data-baseweb="popover"] li[role="option"][aria-selected="true"] { background: var(--primary-gradient); color: #fff; }
div[data-baseweb="popover"] li[role="option"]:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }

[data-testid="stFileUploader"] section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed var(--border-color);
  border-radius: 12px;
}
[data-testid="stFileUploader"] button[kind="secondary"] { width: auto; }
[data-testid="stFileUploaderDropzoneInstructions"] div, [data-testid="stFileUploaderFileMetadata"] { color: var(--text-secondary); }

[data-baseweb="slider"] div[role="slider"] { background-color: #818cf8 !important; border-color: #818cf8 !important; }
[data-testid="stSlider"] [data-testid="stSliderTrackFilled"], [data-baseweb="slider"] [data-testid="stSliderTrackFilled"] { background-color: #6366f1 !important; }

/* ---------- Buttons ---------- */
div[data-testid="stButton"] > button {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.7rem 1.5rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: none;
}
div[data-testid="stButton"] > button:hover {
  border-color: rgba(168, 85, 247, 0.4);
  color: #fff;
  transform: translateY(-1px);
}
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"] {
  background: var(--primary-gradient);
  color: #fff;
  border: none;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}
div[data-testid="stButton"] > button[kind="primary"]:hover,
div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"]:hover {
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5);
  transform: translateY(-2px);
  border: none;
}
div[data-testid="stButton"] > button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

/* ---------- Nav pills (st.radio) ---------- */
div[data-testid="stRadio"] > div {
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 36px;
  padding: 8px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);
  width: fit-content;
  margin: 0 auto;
}
div[data-testid="stRadio"] > div > label {
  background: transparent;
  border: none;
  border-radius: 28px;
  padding: 10px 22px;
  color: var(--text-secondary);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin: 0;
}
div[data-testid="stRadio"] > div > label:hover { background: rgba(255, 255, 255, 0.05); color: #fff; }
div[data-testid="stRadio"] > div > label > div:first-child { display: none !important; }
div[data-testid="stRadio"] > div > label > div:nth-child(2) { margin: 0; }
div[data-testid="stRadio"] > div > label:has(input:checked) {
  background: var(--primary-gradient);
  color: #fff;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
}
div[data-testid="stRadio"] > div > label:has(input:checked) > div:nth-child(2) { color: #fff !important; }

/* ---------- Mini tabs (st.tabs) ---------- */
[data-testid="stTabs"] { gap: 8px; margin: 16px 0; }
[data-testid="stTabs"] [role="tablist"] { gap: 8px; }
[data-testid="stTabs"] button[data-baseweb="tab"],
[data-testid="stTabs"] button[role="tab"] {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 8px 16px;
  color: var(--text-secondary);
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
[data-testid="stTabs"] button[data-baseweb="tab"]:hover,
[data-testid="stTabs"] button[role="tab"]:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"],
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  background: var(--primary-gradient);
  color: #fff;
  border-color: transparent;
}
[data-testid="stTabs"] div[role="tabpanel"] { padding-top: 8px; }

/* ---------- Containers (glass cards) ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: rgba(168, 85, 247, 0.3);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4);
}
[data-testid="stExpander"] {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  margin-bottom: 16px;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
}
[data-testid="stExpander"] summary { color: var(--text-primary); font-weight: 600; }

/* ============================================================
   Below: 1:1 port of global.css (cards, tables, alerts, etc.)
   ============================================================ */

.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  background: #ffffff; color: #000000; border: none; padding: 0.75rem 1.5rem;
  border-radius: 12px; font-weight: 600; font-family: 'Inter', sans-serif; font-size: 0.9rem;
  cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}
.btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.btn-primary { background: var(--primary-gradient); color: #fff; }
.btn-ghost { background: rgba(255, 255, 255, 0.05); color: var(--text-primary); border: 1px solid var(--border-color); box-shadow: none; }
.btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); color: #fff; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3); }
.btn-block { width: 100%; }
.btn-sm { padding: 0.45rem 0.9rem; font-size: 0.8rem; border-radius: 10px; }

.input, .select {
  width: 100%; background-color: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color); border-radius: 12px; color: #fff;
  padding: 0.65rem 0.9rem; font-family: 'Inter', sans-serif; font-size: 0.9rem; outline: none;
  transition: border-color 0.2s;
}
.input:focus, .select:focus { border-color: var(--accent-color); }
.select option { background-color: var(--sidebar-bg); color: #fff; }
label.field-label {
  display: block; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 1px; margin-bottom: 6px; color: var(--text-secondary);
}

.glass-card {
  background: var(--card-bg); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-color); border-radius: 20px; padding: 24px; margin-bottom: 24px;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3); transition: all 0.3s ease;
}
.glass-card:hover {
  transform: translateY(-3px); box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4);
  border-color: rgba(168, 85, 247, 0.3);
}

.metric-box {
  background: rgba(255, 255, 255, 0.03); border-radius: 16px; padding: 24px;
  border: 1px solid var(--border-color); display: flex; flex-direction: column;
  align-items: center; text-align: center; transition: all 0.3s ease; height: 100%;
}
.metric-box:hover { border-color: var(--accent-color); background: rgba(255, 255, 255, 0.05); transform: translateY(-2px); }
.metric-icon {
  font-size: 1.4rem; margin-bottom: 14px; color: var(--accent-color);
  background: rgba(129, 140, 248, 0.15); width: 46px; height: 46px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
}
.metric-value { font-size: 2rem; font-weight: 800; color: var(--text-primary); line-height: 1.1; margin-bottom: 4px; }
.metric-label { font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }

.app-shell { min-height: 100vh; display: flex; flex-direction: column; padding-bottom: 70px; }
.navbar { position: sticky; top: 16px; z-index: 1000; display: flex; justify-content: center; margin: 16px auto 24px; width: fit-content; max-width: 95vw; }
.navbar-inner {
  background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px); padding: 8px;
  border-radius: 36px; border: 1px solid rgba(255, 255, 255, 0.1); display: flex; gap: 8px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5); flex-wrap: wrap; justify-content: center;
}
.nav-item {
  background: transparent; border: none; border-radius: 28px; padding: 10px 22px;
  color: var(--text-secondary); font-family: 'Inter', sans-serif; font-size: 0.95rem;
  font-weight: 600; cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex; align-items: center; gap: 8px;
}
.nav-item:hover { background: rgba(255, 255, 255, 0.05); color: #fff; }
.nav-item.active { background: var(--primary-gradient); color: #fff; box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3); }

.content { width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 24px; flex: 1; }

.footer {
  position: fixed; bottom: 0; left: 0; width: 100%; padding: 8px; font-size: 0.75rem;
  background: rgba(15, 23, 42, 0.95); backdrop-filter: blur(10px); text-align: center;
  z-index: 9999; border-top: 1px solid var(--border-color);
}
.footer p { color: var(--text-secondary); margin: 0; }

.auth-shell { min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
.app-header { text-align: center; padding: 30px 0 40px; }
.app-header h1 {
  font-size: 2.6rem; background: var(--primary-gradient);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  margin-bottom: 8px;
}
.auth-card { width: 100%; max-width: 480px; margin: 0 auto; }

.tabs {
  display: flex; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-color);
  border-radius: 12px; padding: 4px; margin-bottom: 24px;
}
.tab-btn { flex: 1; background: transparent; border: none; padding: 10px; border-radius: 8px; color: var(--text-secondary); font-family: 'Inter', sans-serif; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.tab-btn.active { background: var(--primary-gradient); color: #fff; }
.form-group { margin-bottom: 16px; }

.table-wrap { overflow-x: auto; background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border-color); border-radius: 14px; }
table.data-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.data-table th {
  text-align: left; padding: 12px 14px; color: var(--text-secondary); font-size: 0.75rem;
  text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid var(--border-color);
  background: rgba(255, 255, 255, 0.02); white-space: nowrap;
}
.data-table td { padding: 10px 14px; color: var(--text-primary); border-bottom: 1px solid rgba(255, 255, 255, 0.04); white-space: nowrap; }
.data-table tr:hover td { background: rgba(255, 255, 255, 0.03); }

.badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.badge-pass { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
.badge-fail { background: rgba(248, 113, 113, 0.15); color: #f87171; }
.badge-neutral { background: rgba(148, 163, 184, 0.15); color: #94a3b8; }

.alert { padding: 12px 16px; border-radius: 12px; margin-bottom: 16px; font-size: 0.9rem; border: 1px solid var(--border-color); }
.alert-error { background: rgba(248, 113, 113, 0.1); border-color: rgba(248, 113, 113, 0.3); color: #f87171; }
.alert-success { background: rgba(74, 222, 128, 0.1); border-color: rgba(74, 222, 128, 0.3); color: #4ade80; }
.alert-info { background: rgba(129, 140, 248, 0.1); border-color: rgba(129, 140, 248, 0.3); color: #818cf8; }

.grid { display: grid; gap: 16px; }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

.section-title { margin: 8px 0 18px; }

.profile-hero {
  background: var(--primary-gradient); border-radius: 20px; padding: 28px;
  display: flex; align-items: center; gap: 22px; color: white;
  box-shadow: 0 20px 40px -10px rgba(99, 102, 241, 0.4); margin-bottom: 28px;
}
.profile-avatar {
  width: 70px; height: 70px; background: rgba(255, 255, 255, 0.2); border-radius: 18px;
  display: flex; align-items: center; justify-content: center; font-size: 1.8rem; color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}
.profile-info h2 { color: #fff; margin: 0 0 4px; font-size: 1.5rem; }
.profile-info p { color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; margin: 0; }

.podium-container { display: flex; align-items: flex-end; justify-content: center; gap: 15px; padding: 20px 0; margin-top: 15px; }
.podium-step { display: flex; flex-direction: column; align-items: center; flex: 1; border-radius: 12px 12px 0 0; padding: 15px 10px; text-align: center; }
.podium-1 { background: linear-gradient(180deg, rgba(251, 191, 36, 0.2) 0%, rgba(251, 191, 36, 0.05) 100%); border: 1.5px solid #fbbf24; height: 160px; order: 2; }
.podium-2 { background: linear-gradient(180deg, rgba(226, 232, 240, 0.2) 0%, rgba(226, 232, 240, 0.05) 100%); border: 1.5px solid #e2e8f0; height: 130px; order: 1; }
.podium-3 { background: linear-gradient(180deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.05) 100%); border: 1.5px solid #f59e0b; height: 105px; order: 3; }
.podium-badge { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; margin-bottom: 8px; font-size: 0.9rem; }
.badge-1 { background: #fbbf24; color: #000; box-shadow: 0 0 15px rgba(251, 191, 36, 0.4); }
.badge-2 { background: #cbd5e1; color: #000; }
.badge-3 { background: #d97706; color: #fff; }
.podium-name { font-weight: 700; color: #f8fafc; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 100%; }
.podium-val { font-weight: 800; color: #818cf8; font-size: 1.2rem; margin-top: 4px; }

.progress-bar-container { margin-bottom: 12px; }
.progress-bar-label { display: flex; justify-content: space-between; font-size: 0.8rem; color: #cbd5e1; margin-bottom: 4px; }
.progress-bar-bg { background-color: rgba(255, 255, 255, 0.05); border-radius: 6px; height: 8px; width: 100%; overflow: hidden; }
.progress-bar-fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, #6366f1, #a855f7); }

.insight-highlight { padding: 10px 14px; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 10px; margin-bottom: 10px; font-size: 0.85rem; color: #cbd5e1; }

.mini-tabs { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }
.mini-tab { background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-color); border-radius: 10px; padding: 8px 16px; color: var(--text-secondary); font-family: 'Inter', sans-serif; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
.mini-tab:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
.mini-tab.active { background: var(--primary-gradient); color: #fff; border-color: transparent; }

.chart-card { background: rgba(15, 23, 42, 0.5); border: 1px solid var(--border-color); border-radius: 14px; padding: 16px; }
.saved-card { background: var(--card-bg); backdrop-filter: blur(20px); border: 1px solid var(--border-color); border-radius: 20px; padding: 20px; transition: all 0.3s; }
.saved-card:hover { transform: translateY(-3px); border-color: rgba(168, 85, 247, 0.3); }
.saved-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
.saved-card-header h4 { color: #f8fafc; font-size: 1.05rem; margin: 0; }
.saved-meta { font-size: 0.85rem; color: #cbd5e1; margin-bottom: 14px; }
.saved-stats { display: flex; justify-content: space-between; background: rgba(0, 0, 0, 0.2); padding: 12px; border-radius: 10px; }
.saved-stat { text-align: center; }
.saved-stat .label { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; }
.saved-stat .value { font-weight: 700; color: #f8fafc; font-size: 1rem; }

.empty-state { text-align: center; padding: 40px; color: var(--text-secondary); font-size: 0.95rem; }

.mt-8 { margin-top: 8px; }
.mt-16 { margin-top: 16px; }
.mb-16 { margin-bottom: 16px; }
.mb-24 { margin-bottom: 24px; }
.text-center { text-align: center; }
.muted { color: var(--text-secondary); }

@media (max-width: 900px) {
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
  .grid-3 { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  .app-header h1 { font-size: 1.9rem; }
  .content { padding: 0 14px; }
}
"""


def inject_css():
    st.markdown(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">'
        + f"<style>{_CSS}</style>",
        unsafe_allow_html=True,
    )


def esc(value):
    if value is None:
        return ""
    return _html.escape(str(value))


# ---------------------------------------------------------------- simple blocks
def section_title(icon, title, style=None):
    style_attr = f' style="{style}"' if style else ""
    icon_html = f'<i class="{icon}" style="margin-right:8px;color:#818cf8"></i>' if icon else ""
    st.markdown(
        f'<h3 class="section-title"{style_attr}>{icon_html}{esc(title)}</h3>',
        unsafe_allow_html=True,
    )


def alert(msg, kind="info"):
    st.markdown(
        f'<div class="alert alert-{kind}">{esc(msg)}</div>',
        unsafe_allow_html=True,
    )


def metric_box(icon, label, value, color="#818cf8", bg="rgba(129, 140, 248, 0.15)"):
    return (
        f'<div class="metric-box">'
        f'<div class="metric-icon" style="color:{color};background:{bg}"><i class="{icon}"></i></div>'
        f'<div class="metric-label">{esc(label)}</div>'
        f'<div class="metric-value">{esc(value)}</div>'
        f"</div>"
    )


def metric_grid(boxes, cols=4):
    st.markdown(f'<div class="grid grid-{cols} mb-24">{"".join(boxes)}</div>', unsafe_allow_html=True)


def metric_cards(summary):
    summary = summary or {}
    boxes = [
        metric_box("fas fa-users", "Total Students", summary.get("total_students", 0)),
        metric_box(
            "fas fa-check-circle", "Passed", summary.get("passed_students", 0),
            color="#4ade80", bg="rgba(74, 222, 128, 0.15)",
        ),
        metric_box(
            "fas fa-times-circle", "Failed", summary.get("failed_students", 0),
            color="#f87171", bg="rgba(248, 113, 113, 0.15)",
        ),
        metric_box(
            "fas fa-chart-bar", "Avg SGPA", summary.get("average_sgpa", 0),
            color="#fbbf24", bg="rgba(251, 191, 36, 0.15)",
        ),
    ]
    metric_grid(boxes, 4)


def result_badge(value):
    is_pass = value == "Pass"
    cls = "badge badge-pass" if is_pass else "badge badge-fail"
    return f'<span class="{cls}">{esc(value)}</span>'


def grade_badge(grade):
    is_fail = grade in FAIL_GRADES
    cls = "badge badge-fail" if is_fail else "badge badge-pass"
    return f'<span class="{cls}">{esc(grade)}</span>'


def stat_row(label, value):
    return (
        f'<div style="display:flex;justify-content:space-between;padding:8px 0;'
        f'border-bottom:1px solid rgba(255,255,255,0.05)">'
        f"<span>{esc(label)}</span><strong style=\"color:#f8fafc\">{esc(value)}</strong></div>"
    )


def footer():
    st.markdown(
        '<div class="footer"><p>Developed by '
        '<span style="color:#818cf8;font-weight:600">Sakshi, Rahul, Sakshi</span>'
        "&nbsp;|&nbsp; Smart Result Analysis System</p></div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------- data tables
def data_table(columns, rows, uid, empty="No data available", searchable=True, sortable=True):
    """Render a searchable / sortable HTML table styled like the React DataTable."""
    rows = [r for r in (rows or []) if r]
    if not rows:
        st.markdown(f'<div class="empty-state">{esc(empty)}</div>', unsafe_allow_html=True)
        return

    visible = rows

    if searchable:
        c1, c2 = st.columns([3, 1])
        with c1:
            search_q = st.text_input(
                "Search", key=f"dt_search_{uid}", placeholder="Search…",
                label_visibility="collapsed",
            )
        search_q = (search_q or "").strip().lower()
        if search_q:
            visible = [
                r for r in visible
                if any(str(r.get(c["key"], "") or "").lower().find(search_q) >= 0 for c in columns)
            ]
        with c2:
            st.markdown(
                f'<div class="muted" style="font-size:0.85rem;padding-top:12px;text-align:right">'
                f"{len(visible)} of {len(rows)}</div>",
                unsafe_allow_html=True,
            )

    sort_col = None
    sort_dir = "asc"
    if sortable:
        sortable_cols = [c for c in columns if c.get("sortable", True)]
        keys = [c["key"] for c in sortable_cols]
        names = {c["key"]: c["header"] for c in sortable_cols}
        c1, c2 = st.columns(2)
        with c1:
            sort_col = st.selectbox(
                "Sort by", keys, key=f"dt_sort_{uid}",
                format_func=lambda k: names[k], label_visibility="collapsed",
            )
        with c2:
            order = st.radio(
                "Order", ["Ascending", "Descending"], key=f"dt_dir_{uid}",
                horizontal=True, label_visibility="collapsed",
            )
            sort_dir = "asc" if order == "Ascending" else "desc"
        if sort_col:

            def _key(r):
                v = r.get(sort_col)
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    return (0, v)
                return (1, str(v or ""))

            visible = sorted(visible, key=_key, reverse=(sort_dir == "desc"))

    thead = "".join(f"<th>{esc(c['header'])}</th>" for c in columns)
    body = ""
    for row in visible:
        tds = ""
        for col in columns:
            value = row.get(col["key"])
            render = col.get("render")
            if render:
                tds += f"<td>{render(value, row)}</td>"
            else:
                tds += f"<td>{esc(value if value is not None else '—')}</td>"
        body += f"<tr>{tds}</tr>"

    st.markdown(
        f'<div class="table-wrap"><table class="data-table">'
        f"<thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table></div>",
        unsafe_allow_html=True,
    )


def profile_hero(name, prn, mother=None):
    mother_html = ""
    if mother:
        mother_html = (
            f'<span style="margin:0 10px">|</span>'
            f'<i class="fas fa-user" style="margin-right:8px"></i>{esc(mother)}'
        )
    st.markdown(
        '<div class="profile-hero">'
        '<div class="profile-avatar"><i class="fas fa-user-graduate"></i></div>'
        '<div class="profile-info">'
        f"<h2>{esc(name)}</h2>"
        f'<p><i class="fas fa-id-card" style="margin-right:8px"></i> {esc(prn)}{mother_html}</p>'
        "</div></div>",
        unsafe_allow_html=True,
    )


def format_date(value):
    if not value:
        return "—"
    s = str(value)
    return s[:10]
