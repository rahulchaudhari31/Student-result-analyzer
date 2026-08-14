"""Smart Result Analysis System - Streamlit frontend.

1:1 port of the React SPA (LoginPage / TeacherDashboard / StudentDashboard)
with the exact same styles and layouts. Talks to the FastAPI backend the same
way the React app did (see frontend/src/api/client.js).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

import charts
import components
import ui
from api_client import ApiError, client as api
from config import DEPARTMENTS, YEARS

st.set_page_config(
    page_title="Smart Result Analysis System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ui.inject_css()

for key in ["user", "analysis", "saved_active", "sp_active", "sp_prn", "auth_error"]:
    if key not in st.session_state:
        st.session_state[key] = None


def do_logout():
    st.session_state.user = None
    st.session_state.analysis = None
    st.session_state.saved_active = None
    st.session_state.sp_active = None
    st.session_state.sp_prn = None
    api.set_token(None)
    st.rerun()


# ================================================================ login / register
def login_page():
    st.markdown(
        '<div class="app-header"><h1>Smart Result Analysis System</h1>'
        "<p>Advanced Analytics &amp; Academic Tracking System</p></div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        with st.container(border=True):
            mode = st.radio(
                "Mode", ["Login", "Register"],
                key="auth_mode", horizontal=True, label_visibility="collapsed",
            )
            if mode == "Login":
                render_login()
            else:
                render_register()


def render_login():
    role = st.selectbox("Role", ["Teacher", "Student"], key="login_role")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Sign In", type="primary", key="login_submit"):
        if not email or not password:
            st.session_state.auth_error = "Please fill all fields."
        else:
            try:
                data = api.login(email, password)
                if data["role"] != role.lower():
                    st.session_state.auth_error = (
                        f"Role mismatch. This account is registered as '{data['role']}'."
                    )
                else:
                    st.session_state.user = data
                    st.session_state.auth_error = None
                    api.set_token(data["token"])
                    st.rerun()
            except ApiError as e:
                st.session_state.auth_error = e.message

    if st.session_state.auth_error:
        ui.alert(st.session_state.auth_error, "error")


def render_register():
    name = st.text_input("Full Name", key="reg_name")
    email = st.text_input("Email Address", key="reg_email")
    password = st.text_input("Create Password", type="password", key="reg_password")
    role = st.selectbox("I am a...", ["Student", "Teacher"], key="reg_role")

    if st.button("Create Account", type="primary", key="reg_submit"):
        if not name or not email:
            st.session_state.auth_error = "Please fill all fields."
        elif len(password) < 6:
            st.session_state.auth_error = "Password must be at least 6 characters."
        else:
            try:
                data = api.register(email, password, name, role.lower())
                st.session_state.user = data
                st.session_state.auth_error = None
                api.set_token(data["token"])
                st.rerun()
            except ApiError as e:
                st.session_state.auth_error = e.message

    if st.session_state.auth_error:
        ui.alert(st.session_state.auth_error, "error")


# ================================================================ teacher
def teacher_dashboard():
    nav_opts = ["Upload", "Saved", "Search", "Overview", "Logout"]
    icons = {"Upload": "⬆", "Saved": "📁", "Search": "🔍", "Overview": "🏢", "Logout": "🚪"}
    nav = st.radio(
        "Nav", nav_opts, key="teacher_nav", horizontal=True,
        label_visibility="collapsed", format_func=lambda l: f"{icons[l]} {l}",
    )
    if nav == "Logout":
        do_logout()
    elif nav == "Upload":
        upload_tab()
    elif nav == "Saved":
        saved_tab()
    elif nav == "Search":
        search_tab()
    else:
        overview_tab()
    ui.footer()


def upload_tab():
    ui.section_title("fas fa-upload", "Upload Result PDF")

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            uploaded = st.file_uploader("PDF File", type=["pdf"], key="up_pdf")
        with c2:
            exam_tag = st.text_input("Exam Name", placeholder="e.g., SE Computer May 2024", key="up_tag")
        with c3:
            department = st.selectbox("Department", DEPARTMENTS, key="up_dept")
        c4, c5 = st.columns(2)
        with c4:
            year = st.selectbox("Year", YEARS, key="up_year")
        with c5:
            analyze_clicked = st.button("Analyze PDF", type="primary", key="up_analyze")

    if analyze_clicked:
        if uploaded is None:
            st.session_state.analysis = None
            st.session_state.upload_error = "Please select a PDF file first."
        elif not exam_tag or not exam_tag.strip():
            st.session_state.upload_error = "Please provide an Exam Name to proceed."
        else:
            try:
                with st.spinner("Processing…"):
                    data = api.analyze(uploaded.getvalue(), uploaded.name)
                st.session_state.analysis = data
                st.session_state.upload_error = None
                st.session_state.upload_msg = None
            except ApiError as e:
                st.session_state.upload_error = e.message

    if st.session_state.get("upload_error"):
        ui.alert(st.session_state["upload_error"], "error")
    if st.session_state.get("upload_msg"):
        ui.alert(st.session_state["upload_msg"], "success")

    analysis = st.session_state.get("analysis")
    if analysis:
        ui.alert(
            f"Successfully processed {len(analysis['students'])} student records "
            f"(detected {analysis['pdf_type'].upper()} format)",
            "success",
        )
        ui.metric_cards(analysis.get("summary") or {})
        components.analysis_tabs(analysis)

        with st.container(border=True):
            st.markdown('<div style="text-align:center">', unsafe_allow_html=True)
            if st.button("Save Data to Cloud", type="primary", key="up_save"):
                payload = {
                    "file_name": uploaded.name if uploaded else "uploaded_result.pdf",
                    "exam_tag": exam_tag,
                    "department": department,
                    "year": year,
                    "students_data": analysis["students"],
                    "uploaded_by": (st.session_state.user or {}).get("name") or "Unknown",
                    "summary": analysis.get("summary") or {},
                }
                try:
                    res = api.save_result(payload)
                    st.session_state.upload_msg = (
                        f"Success! Data archived securely. (ID: {res['message']})"
                    )
                    st.session_state.upload_error = None
                except ApiError as e:
                    st.session_state.upload_error = e.message
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def saved_tab():
    active = st.session_state.get("saved_active")
    if active:
        if st.button("← Back to List", key="sv_back"):
            st.session_state.saved_active = None
            st.rerun()
        ui.section_title(
            "fas fa-chart-bar", f"Analysis: {active.get('exam_tag') or 'Unknown'}"
        )
        ui.metric_cards(active.get("summary") or {})
        components.analysis_tabs(
            {
                "students": active.get("students_data") or [],
                "summary": active.get("summary") or {},
                "top_students": [],
                "failed_students": [],
                "subject_grade_summary": [],
                "grade_distribution": {},
                "batch_statistics": {},
                "pdf_type": "saved",
            }
        )
        return

    ui.section_title("fas fa-folder-open", "Archived Results")

    try:
        with st.spinner("Loading archived results…"):
            files = api.list_results()
    except ApiError as e:
        ui.alert(e.message, "error")
        return

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            search = st.text_input("Search Results", key="sv_search", placeholder="Search by Exam Name…")
        with c2:
            dept_filter = st.selectbox("Department", ["All"] + DEPARTMENTS, key="sv_dept")
        with c3:
            year_filter = st.selectbox("Year", ["All"] + YEARS, key="sv_year")

    q = (search or "").strip().lower()
    filtered = []
    for f in files:
        tag = str(f.get("exam_tag") or "").lower()
        fname = str(f.get("file_name") or "").lower()
        if q and q not in tag and q not in fname:
            continue
        if dept_filter != "All" and f.get("department") != dept_filter:
            continue
        if year_filter != "All" and f.get("year") != year_filter:
            continue
        filtered.append(f)

    if not filtered:
        ui.alert("No results match your filters.", "info")
        return

    for i in range(0, len(filtered), 2):
        c1, c2 = st.columns(2)
        with c1:
            if i < len(filtered):
                render_saved_card(filtered[i], "a")
        with c2:
            if i + 1 < len(filtered):
                render_saved_card(filtered[i + 1], "b")


def render_saved_card(f, suffix):
    summary = f.get("summary") or {}
    st.markdown(
        '<div class="saved-card">'
        '<div class="saved-card-header">'
        f'<h4 title="{ui.esc(f.get("exam_tag"))}">{ui.esc(f.get("exam_tag") or "N/A")}</h4>'
        f'<span style="font-size:.75rem;color:#94a3b8;background:rgba(255,255,255,.1);'
        f'padding:4px 8px;border-radius:12px;white-space:nowrap">'
        f'{ui.format_date(f.get("uploaded_at"))}</span>'
        "</div>"
        '<div class="saved-meta">'
        f'<i class="fas fa-building" style="color:#818cf8;margin-right:6px"></i>'
        f"{ui.esc(f.get('department') or 'N/A')} &nbsp;|&nbsp; "
        f'<i class="fas fa-calendar" style="color:#818cf8;margin-right:6px"></i>'
        f"{ui.esc(f.get('year') or 'N/A')}"
        "</div>"
        '<div class="saved-stats">'
        f'<div class="saved-stat"><div class="label">Students</div>'
        f'<div class="value">{f.get("total_students", 0)}</div></div>'
        f'<div class="saved-stat"><div class="label">Pass Rate</div>'
        f'<div class="value" style="color:#4ade80">{(summary.get("pass_percentage") or 0)}%</div></div>'
        f'<div class="saved-stat"><div class="label">Avg SGPA</div>'
        f'<div class="value" style="color:#fbbf24">{summary.get("average_sgpa", 0)}</div></div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    if st.button("View Dashboard", type="primary", key=f"sv_view_{suffix}"):
        st.session_state.saved_active = f
        st.rerun()


def search_tab():
    ui.section_title("fas fa-search", "Global Student Search")

    if st.session_state.get("sp_active"):
        components.student_profile(
            st.session_state["sp_active"], with_back=True, reset_key="srch_select"
        )
        return

    try:
        identifiers = api.identifiers()
    except ApiError as e:
        ui.alert(e.message, "error")
        return

    opts = ["Search…"] + [
        f"{name} | {prn}"
        for prn, name in sorted(identifiers.items(), key=lambda kv: str(kv[1]).lower())
    ]
    with st.container(border=True):
        selected = st.selectbox("Search Student by Name or PRN", opts, key="srch_select")

    if selected and selected != "Search…":
        prn = selected.split(" | ")[-1]
        try:
            with st.spinner("Loading profile…"):
                profile = api.history(prn)
            st.session_state.sp_active = profile
        except ApiError as e:
            ui.alert(e.message, "error")

    if st.session_state.get("sp_active"):
        components.student_profile(
            st.session_state["sp_active"], with_back=True, reset_key="srch_select"
        )


def overview_tab():
    ui.section_title("fas fa-building", "Institutional Performance Overview")

    try:
        with st.spinner("Aggregating institutional data…"):
            data = api.overview()
    except ApiError as e:
        ui.alert(e.message, "error")
        return

    ui.metric_grid(
        [
            ui.metric_box("fas fa-university", "Total Students", data.get("total_students", 0)),
            ui.metric_box(
                "fas fa-graduation-cap", "Overall Pass Rate",
                f"{data.get('overall_pass_rate', 0)}%",
                color="#4ade80", bg="rgba(74, 222, 128, 0.15)",
            ),
            ui.metric_box(
                "fas fa-star", "Institutional Avg SGPA",
                data.get("overall_avg_sgpa", 0),
                color="#fbbf24", bg="rgba(251, 191, 36, 0.15)",
            ),
            ui.metric_box(
                "fas fa-file-alt", "Exams Analyzed", data.get("exams_analyzed", 0),
                color="#818cf8",
            ),
        ],
        4,
    )

    dept_stats = data.get("department_stats") or []
    st.markdown(
        '<h4 class="mb-16"><i class="fas fa-building" style="margin-right:8px;color:#818cf8"></i>'
        "Department-wise Performance</h4>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        components.chart_card(
            "Pass Percentage by Dept",
            charts.simple_line_chart(dept_stats, "department", "pass_rate", "Pass Percentage by Dept", color="#818cf8"),
        )
    with c2:
        components.chart_card(
            "Average SGPA by Dept",
            charts.simple_line_chart(dept_stats, "department", "avg_sgpa", "Average SGPA by Dept", color="#fbbf24"),
        )

    year_stats = data.get("year_stats") or []
    st.markdown(
        '<h4 class="mb-16"><i class="fas fa-calendar" style="margin-right:8px;color:#818cf8"></i>'
        "Year-wise Progression</h4>",
        unsafe_allow_html=True,
    )
    components.chart_card(
        "Pass Rate Trend across Years",
        charts.simple_line_chart(year_stats, "year", "pass_rate", "Pass Rate Trend across Years", color="#a855f7"),
    )


# ================================================================ student
def student_dashboard():
    nav_opts = ["My Dashboard", "Logout"]
    icons = {"My Dashboard": "🎓", "Logout": "🚪"}
    nav = st.radio(
        "Nav", nav_opts, key="student_nav", horizontal=True,
        label_visibility="collapsed", format_func=lambda l: f"{icons[l]} {l}",
    )
    if nav == "Logout":
        do_logout()

    user = st.session_state.user or {}
    st.markdown(
        '<div style="text-align:center;margin-bottom:20px"><span class="muted">'
        f'Signed in as <strong style="color:#f8fafc">{ui.esc(user.get("name"))}</strong>'
        "</span></div>",
        unsafe_allow_html=True,
    )

    ui.section_title("fas fa-search", "Find Your Records")

    try:
        identifiers = api.identifiers()
    except ApiError as e:
        ui.alert(e.message, "error")
        return

    opts = ["Select Your Profile…"] + [
        f"{name} | {prn}"
        for prn, name in sorted(identifiers.items(), key=lambda kv: str(kv[1]).lower())
    ]
    with st.container(border=True):
        selected = st.selectbox("Confirm Identity", opts, key="stu_select")

    if selected and selected != "Select Your Profile…":
        prn = selected.split(" | ")[-1]
        if st.session_state.get("sp_prn") != prn:
            try:
                with st.spinner("Retrieving academic records…"):
                    profile = api.history(prn)
                st.session_state.sp_active = profile
                st.session_state.sp_prn = prn
            except ApiError as e:
                ui.alert(e.message, "error")

    if st.session_state.get("sp_active"):
        components.student_profile(st.session_state["sp_active"])

    ui.footer()


# ================================================================ router
user = st.session_state.get("user")
api.set_token(user.get("token") if user else None)

if not user:
    login_page()
elif user.get("role") == "teacher":
    teacher_dashboard()
else:
    student_dashboard()
