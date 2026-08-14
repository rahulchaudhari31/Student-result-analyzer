"""Ports of the React components: AnalysisView.jsx + StudentProfile.jsx.

Uses native Streamlit tabs/mini-tabs and plotly (via charts.py) while keeping
the exact visual language (glass cards, metric boxes, badges, tables).
"""

import streamlit as st

import charts
import ui
from config import GRADES, GRADE_POINTS

SUBJECT_GRADE_PRIORITY = {
    'O': 0, 'A+': 1, 'A': 2, 'B+': 3, 'B': 4, 'C': 5, 'P': 6,
    'F': 7, 'FF': 8, 'AB': 9, 'ABS': 10,
}


def chart_card(title, fig):
    if fig is None:
        return
    with st.container(border=True):
        st.markdown(
            f'<h5 style="margin-bottom:12px;color:#f8fafc">{ui.esc(title)}</h5>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})


# ------------------------------------------------------------------ analysis
ANALYSIS_TABS = [
    ("📊", "Overview"),
    ("🏆", "Top Performers"),
    ("❌", "Failures"),
    ("📚", "Subject Analysis"),
    ("📋", "Detailed List"),
    ("📈", "Advanced Insights"),
]


def analysis_tabs(analysis):
    labels = [f"{emoji} {title}" for emoji, title in ANALYSIS_TABS]
    tabs = st.tabs(labels)
    with tabs[0]:
        overview_tab(analysis)
    with tabs[1]:
        top_performers_tab(analysis)
    with tabs[2]:
        failures_tab(analysis)
    with tabs[3]:
        subject_analysis_tab(analysis)
    with tabs[4]:
        detailed_list_tab(analysis)
    with tabs[5]:
        advanced_insights_tab(analysis)


def overview_tab(analysis):
    ui.section_title("fas fa-tachometer-alt", "Performance Overview")
    ui.metric_cards(analysis.get("summary") or {})
    valid = [s for s in analysis.get("students", []) if s.get("HasValidSGPA")]
    sgpas = [s.get("SGPA") for s in valid]
    summary = analysis.get("summary") or {}
    c1, c2 = st.columns(2)
    with c1:
        chart_card("SGPA Distribution", charts.sgpa_histogram(sgpas))
    with c2:
        chart_card(
            "Pass / Fail Ratio",
            charts.pass_fail_donut(summary.get("passed_students", 0), summary.get("failed_students", 0)),
        )


def top_performers_tab(analysis):
    ui.section_title("fas fa-trophy", "Top Performers")
    rows = []
    for i, s in enumerate(analysis.get("top_students") or []):
        rows.append({
            "Rank": i + 1,
            "Seat No": s.get("Seat No"),
            "Name": s.get("Name"),
            "SGPA": s.get("SGPA"),
            "Credits": s.get("Credits"),
        })
    ui.data_table(
        [
            {"key": "Rank", "header": "Rank"},
            {"key": "Seat No", "header": "Seat No"},
            {"key": "Name", "header": "Name"},
            {"key": "SGPA", "header": "SGPA"},
            {"key": "Credits", "header": "Credits"},
        ],
        rows[:10],
        uid="top",
    )


def failures_tab(analysis):
    failed = analysis.get("failed_students") or []
    rows = []
    for s in failed:
        failed_subs = ", ".join(
            sub.get("Course Name")
            for sub in (s.get("Subjects") or [])
            if sub.get("Grade") in ["F", "FF", "AB", "IC", "ABS"]
        )
        rows.append({
            "Seat No": s.get("Seat No"),
            "Name": s.get("Name"),
            "SGPA Raw": s.get("SGPA_Raw"),
            "Failed Subjects": failed_subs or "N/A",
        })
    if not rows:
        ui.alert("🎉 All students passed!", "success")
        return
    ui.section_title("fas fa-user-times", "Failure Analysis")
    ui.data_table(
        [
            {"key": "Seat No", "header": "Seat No"},
            {"key": "Name", "header": "Name"},
            {"key": "SGPA Raw", "header": "SGPA"},
            {"key": "Failed Subjects", "header": "Failed Subjects"},
        ],
        rows,
        uid="fail",
    )


def subject_analysis_tab(analysis):
    ui.section_title("fas fa-book", "Subject-wise Grade Distribution")

    subject_rows = sorted(
        analysis.get("subject_grade_summary") or [],
        key=lambda r: r.get("Failure Rate (%)", 0),
        reverse=True,
    )
    student_names = ["All Students"] + sorted({s.get("Name") for s in analysis.get("students", [])})

    c1, c2 = st.columns(2)
    with c1:
        student_filter = st.selectbox("Filter by Student", student_names, key="sa_student")

    filtered_rows = subject_rows
    if student_filter != "All Students":
        student = next(
            (s for s in analysis.get("students", []) if s.get("Name") == student_filter), None
        )
        subj_names = [sub.get("Course Name") for sub in (student.get("Subjects") or [])]
        filtered_rows = [r for r in filtered_rows if r.get("Course Name") in subj_names]

    subject_names = sorted({r.get("Course Name") for r in filtered_rows})
    with c2:
        active_subject = None
        if subject_names:
            active_subject = st.selectbox("Select Subject", subject_names, key="sa_subject")

    st.markdown(
        '<h5 style="margin-bottom:12px">'
        '<i class="fas fa-sort-amount-down" style="margin-right:8px;color:#818cf8"></i>'
        "Critical Subjects (Highest Failure Rates)</h5>",
        unsafe_allow_html=True,
    )
    ui.data_table(
        (
            [{"key": "Course Name", "header": "Course Name"}, {"key": "Total Students", "header": "Total"}]
            + [{"key": g, "header": g, "sortable": False} for g in GRADES]
            + [{"key": "Failure Rate (%)", "header": "Failure %"}]
        ),
        filtered_rows[:10],
        uid="crit",
    )

    chart_card("Grade Count by Subject", charts.stacked_grade_bar(filtered_rows[:15], GRADES))

    if not active_subject:
        return
    ui.section_title("fas fa-microscope", "Individual Subject Analysis")
    subject_stats = next((r for r in filtered_rows if r.get("Course Name") == active_subject), None)
    if not subject_stats:
        return

    total = subject_stats.get("Total Students", 0)
    failures = subject_stats.get("F", 0)
    pass_rate = ((1 - failures / total) * 100) if total > 0 else 0
    top_grade = next((g for g in GRADES if subject_stats.get(g, 0) > 0), "N/A")

    ui.metric_grid([
        ui.metric_box("fas fa-users", "Total Students", total),
        ui.metric_box("fas fa-percentage", "Pass Rate", f"{pass_rate:.1f}%",
                      color="#4ade80", bg="rgba(74, 222, 128, 0.15)"),
        ui.metric_box("fas fa-times-circle", "Failures", failures,
                      color="#f87171", bg="rgba(248, 113, 113, 0.15)"),
        ui.metric_box("fas fa-crown", "Top Grade", top_grade,
                      color="#fbbf24", bg="rgba(251, 191, 36, 0.15)"),
    ], 4)

    subject_students = []
    for s in analysis.get("students", []):
        for sub in (s.get("Subjects") or []):
            if sub.get("Course Name") == active_subject:
                subject_students.append({
                    "Seat No": s.get("Seat No"),
                    "Name": s.get("Name"),
                    "Grade": sub.get("Grade"),
                    "PRN": s.get("PRN"),
                    "SGPA": s.get("SGPA") or 0,
                    "_isFail": sub.get("Grade") in ["F", "FF", "AB", "IC", "ABS"],
                })

    subject_students.sort(key=lambda x: (
        SUBJECT_GRADE_PRIORITY.get(x["Grade"], 100), -x.get("SGPA", 0)
    ))
    top_subject = subject_students[:10]
    failed_subject = [s for s in subject_students if s["_isFail"]]

    c1, c2 = st.columns(2)
    with c1:
        chart_card(
            f"Grade Distribution - {active_subject}",
            charts.grade_pie(
                [{"name": g, "value": subject_stats.get(g, 0)} for g in GRADES],
                hole=0,
            ),
        )
    with c2:
        st.markdown(
            '<h5 style="margin-bottom:12px">'
            '<i class="fas fa-trophy" style="margin-right:8px;color:#818cf8"></i>'
            f"Top Performers in {ui.esc(active_subject)}</h5>",
            unsafe_allow_html=True,
        )
        ui.data_table(
            [
                {"key": "Seat No", "header": "Seat No"},
                {"key": "Name", "header": "Name"},
                {"key": "Grade", "header": "Grade", "render": lambda v, r: ui.grade_badge(v)},
                {"key": "SGPA", "header": "SGPA"},
            ],
            top_subject,
            uid="sub_top",
        )

    st.markdown(
        f'<h5 style="margin-bottom:12px">❌ Students who failed in {ui.esc(active_subject)}</h5>',
        unsafe_allow_html=True,
    )
    if failed_subject:
        ui.data_table(
            [
                {"key": "Seat No", "header": "Seat No"},
                {"key": "Name", "header": "Name"},
                {"key": "Grade", "header": "Grade", "render": lambda v, r: ui.grade_badge(v)},
                {"key": "PRN", "header": "PRN"},
            ],
            failed_subject,
            uid="sub_fail",
        )
    else:
        ui.alert(f"No students failed in {active_subject}! 🎉", "success")


def detailed_list_tab(analysis):
    ui.section_title("fas fa-list", "Complete Student Registry")

    rows = [{k: v for k, v in s.items() if k != "Subjects"} for s in analysis.get("students", [])]

    c1, c2, c3 = st.columns(3)
    with c1:
        min_sgpa = st.slider("Min SGPA", 0.0, 10.0, 0.0, 0.1, key="dl_min")
    with c2:
        status = st.selectbox("Status", ["All", "Pass", "Fail"], key="dl_status")
    with c3:
        sort = st.selectbox("Sort", ["High to Low", "Low to High"], key="dl_sort")

    rows = [r for r in rows if (r.get("SGPA") or 0) >= min_sgpa]
    if status != "All":
        rows = [r for r in rows if r.get("Result Status") == status]
    rows = sorted(rows, key=lambda r: r.get("SGPA") or 0, reverse=(sort == "High to Low"))

    ui.data_table(
        [
            {"key": "Seat No", "header": "Seat No"},
            {"key": "PRN", "header": "PRN"},
            {"key": "Name", "header": "Name"},
            {"key": "SGPA", "header": "SGPA"},
            {"key": "Result Status", "header": "Result", "render": lambda v, r: ui.result_badge(v)},
            {"key": "Passed Subjects", "header": "Passed"},
            {"key": "Total Subjects", "header": "Total"},
            {"key": "Credits", "header": "Credits"},
        ],
        rows,
        uid="detail",
    )


def advanced_insights_tab(analysis):
    ui.section_title("fas fa-chart-line", "Advanced Statistical Analysis")

    valid = [s for s in analysis.get("students", []) if s.get("HasValidSGPA")]
    sgpas = [s.get("SGPA") for s in valid]
    stats = (analysis.get("batch_statistics") or {}).get("sgpa_stats")

    if stats and sgpas:
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown(
                    '<h5 style="margin-bottom:16px">SGPA Distribution Statistics</h5>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    ui.stat_row("Mean SGPA", f"{stats['mean']:.2f}")
                    + ui.stat_row("Median SGPA", f"{stats['median']:.2f}")
                    + ui.stat_row("Standard Deviation", f"{stats['std']:.2f}")
                    + ui.stat_row("Range", f"{stats['min']} – {stats['max']}")
                    + ui.stat_row("Top 10% Cutoff", f"> {stats['p90']:.2f}")
                    + ui.stat_row("Bottom 10% Cutoff", f"< {stats['p10']:.2f}"),
                    unsafe_allow_html=True,
                )
        with c2:
            chart_card("SGPA Distribution", charts.sgpa_histogram(sgpas))

    st.markdown(charts.grade_heatmap(analysis.get("subject_grade_summary")), unsafe_allow_html=True)

    grade_data = [
        {"name": name, "value": value}
        for name, value in (analysis.get("grade_distribution") or {}).items()
    ]
    chart_card("Overall Grade Distribution", charts.grade_pie(grade_data, hole=0))


# ------------------------------------------------------------------ student profile
def prediction_card_html(prediction):
    return (
        '<div class="glass-card" style="border-left:4px solid #818cf8;margin-bottom:0">'
        '<div style="display:flex;align-items:center;gap:15px">'
        '<div class="metric-icon" style="background:rgba(129,140,248,.2);color:#818cf8;margin-bottom:0">'
        '<i class="fas fa-crystal-ball"></i></div>'
        "<div>"
        '<div class="metric-label">SGPA Projection</div>'
        f'<div class="metric-value">{prediction}</div>'
        '<div style="font-size:.8rem;color:#94a3b8;margin-top:5px">Based on performance trend</div>'
        "</div></div></div>"
    )


def failure_card_html(failed_subjects):
    items = "".join(
        (
            '<div style="display:flex;justify-content:space-between;padding:8px;'
            'background:rgba(255,255,255,.05);border-radius:6px;margin-bottom:6px">'
            f'<span style="color:#e2e8f0;font-size:.85rem">{ui.esc(item.get("Subject", ""))}</span>'
            f'<span style="color:#f87171;font-weight:700;font-size:.85rem">{ui.esc(item.get("Grade"))} '
            f'<span style="color:#64748b;font-weight:400;font-size:.7rem">'
            f'({ui.esc(str(item.get("Exam") or "").split(" ")[0])})</span></span></div>'
        )
        for item in failed_subjects
    )
    return (
        '<div class="glass-card" style="border-left:4px solid #f87171;'
        'background:rgba(248,113,113,.05);margin-bottom:0">'
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">'
        '<i class="fas fa-exclamation-triangle" style="color:#f87171"></i>'
        '<h5 style="color:#f87171;margin:0;font-size:1rem">Subject Failure Alerts</h5></div>'
        f"{items}</div>"
    )


def semester_card_html(r):
    is_pass = r.get("Result") == "Pass"
    color = "#4ade80" if is_pass else "#f87171"
    bg = "rgba(74,222,128,0.1)" if is_pass else "rgba(248,113,113,0.1)"
    return (
        '<div class="glass-card" style="padding:20px;'
        f'border-left:4px solid {color};margin-bottom:0">'
        f'<div style="font-weight:700;font-size:.9rem;color:#e2e8f0;margin-bottom:10px;'
        f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="{ui.esc(r.get("Exam"))}">'
        f"{ui.esc(r.get('Exam'))}</div>"
        '<div style="display:flex;justify-content:space-between;align-items:flex-end">'
        "<div>"
        '<div style="font-size:.7rem;color:#94a3b8;text-transform:uppercase">SGPA</div>'
        f'<div style="font-size:1.6rem;font-weight:800;color:{color};line-height:1">{ui.esc(r.get("SGPA"))}</div>'
        "</div>"
        '<div style="text-align:right">'
        '<div style="font-size:.7rem;color:#94a3b8;text-transform:uppercase">Result</div>'
        f'<div style="font-size:.9rem;font-weight:600;color:#f8fafc;background:{bg};'
        f'padding:2px 8px;border-radius:4px">{ui.esc(r.get("Result"))}</div>'
        "</div></div></div>"
    )


def student_profile(student, with_back=False, reset_key=None):
    if with_back:
        if st.button("← Back", key="sp_back"):
            st.session_state["sp_active"] = None
            if reset_key:
                st.session_state.pop(reset_key, None)
            st.rerun()

    ui.profile_hero(student.get("name"), student.get("prn"), student.get("mother"))

    prediction = student.get("predicted_next_sgpa")
    failed_subjects = student.get("failed_subjects") or []

    if prediction is not None or failed_subjects:
        c1, c2 = st.columns(2)
        if prediction is not None:
            with c1:
                st.markdown(prediction_card_html(prediction), unsafe_allow_html=True)
        if failed_subjects:
            with c2:
                st.markdown(failure_card_html(failed_subjects[:6]), unsafe_allow_html=True)

    results = student.get("results") or []
    if not results:
        ui.alert("No detailed result history available.", "info")
        return

    ui.section_title("fas fa-chart-line", "Academic Progression")
    chart_card(
        "SGPA Growth",
        charts.sgpa_line_chart([{"Exam": r.get("Exam"), "SGPA": r.get("SGPA")} for r in results]),
    )

    subject_data = []
    for r in results:
        for sub in (r.get("Subjects") or []):
            subject_data.append({
                "Course Name": sub.get("Course Name") or sub.get("Course Code") or "Unknown",
                "Grade": (sub.get("Grade") or "").strip(),
                "Grade Point": GRADE_POINTS.get(sub.get("Grade"), 0),
                "Exam": r.get("Exam"),
            })

    if subject_data:
        st.markdown(
            '<h4 class="mb-16"><i class="fas fa-chart-bar" style="margin-right:8px;color:#818cf8"></i>'
            "Subject Performance Analysis</h4>",
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            ui.data_table(
                [
                    {"key": "Course Name", "header": "Course"},
                    {"key": "Grade", "header": "Grade", "render": lambda v, r: ui.grade_badge(v)},
                    {"key": "Grade Point", "header": "Grade Point"},
                    {"key": "Exam", "header": "Exam"},
                ],
                subject_data,
                uid="sp_subjects",
                searchable=False,
                sortable=False,
            )

    st.markdown(
        '<h3 class="section-title"><i class="fas fa-layer-group" style="margin-right:8px;color:#818cf8"></i>'
        "Semester Snapshots</h3>",
        unsafe_allow_html=True,
    )
    for i in range(0, len(results), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < len(results):
                with cols[j]:
                    st.markdown(semester_card_html(results[idx]), unsafe_allow_html=True)

    st.markdown(
        '<h3 class="section-title"><i class="fas fa-file-contract" style="margin-right:8px;color:#818cf8"></i>'
        "Detailed Transcripts</h3>",
        unsafe_allow_html=True,
    )
    for i, r in enumerate(results):
        with st.expander(f"{r.get('Exam')} (SGPA: {r.get('SGPA')})"):
            st.markdown(
                f'<p class="muted mb-16" style="font-size:0.9rem">'
                f'<strong>Seat No:</strong> <code>{ui.esc(r.get("Seat"))}</code>'
                f'<span style="margin:0 16px">|</span>'
                f'<strong>Credits:</strong> <code>{ui.esc(r.get("Credits"))}</code></p>',
                unsafe_allow_html=True,
            )
            ui.data_table(
                [
                    {"key": "Course Code", "header": "Code"},
                    {"key": "Course Name", "header": "Name"},
                    {"key": "Grade", "header": "Grade", "render": lambda v, r: ui.grade_badge(v)},
                ],
                r.get("Subjects") or [],
                uid=f"tr_{i}",
                searchable=False,
                sortable=False,
            )
