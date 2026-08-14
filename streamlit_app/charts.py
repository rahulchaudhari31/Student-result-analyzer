"""Dark-themed plotly replicas of the recharts components in Charts.jsx."""

import plotly.graph_objects as go

from config import GRADE_COLORS
from ui import esc as _esc

PAPER = "rgba(0,0,0,0)"
GRID = "rgba(255,255,255,0.06)"
AXIS = "#94a3b8"


def _base_layout(height=280):
    return dict(
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        hoverlabel=dict(
            bgcolor="#0f172a", bordercolor="rgba(255,255,255,0.1)", font=dict(color="#f8fafc")
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color="#94a3b8", size=11),
        ),
    )


def _axes():
    return dict(
        xaxis=dict(
            gridcolor=GRID, linecolor="rgba(255,255,255,0.1)", zerolinecolor=GRID,
            tickfont=dict(color=AXIS, size=11),
        ),
        yaxis=dict(
            gridcolor=GRID, linecolor="rgba(255,255,255,0.1)", zerolinecolor=GRID,
            tickfont=dict(color=AXIS, size=11),
        ),
    )


def sgpa_histogram(values, title="SGPA Distribution"):
    values = [v for v in values if v is not None]
    if not values:
        return None
    lo = min(values)
    hi = max(values)
    bin_width = max(0.5, (hi - lo) / 12)
    bins = {}
    for v in values:
        key = (int(v // bin_width) * bin_width)
        bins[key] = bins.get(key, 0) + 1
    data = [{"bin": key, "count": count} for key, count in bins.items()]
    data.sort(key=lambda d: d["bin"])

    fig = go.Figure(
        go.Bar(
            x=[f"{d['bin']:.1f}" for d in data],
            y=[d["count"] for d in data],
            marker_color="#00d4ff",
            marker_line_width=0,
            hovertemplate="%{x}: %{y}<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout(), **_axes())
    fig.update_traces(marker=dict(line=dict(color="#00d4ff", width=0)))
    return fig


def pass_fail_donut(passed, failed):
    labels, values, colors = [], [], []
    if passed > 0:
        labels.append("Pass"); values.append(passed); colors.append("#00ff9d")
    if failed > 0:
        labels.append("Fail"); values.append(failed); colors.append("#ff4b4b")
    if not labels:
        return None
    fig = go.Figure(
        go.Pie(
            labels=labels, values=values, hole=0.45,
            marker=dict(colors=colors, line=dict(color="#020617", width=2)),
            textinfo="label+percent", textfont=dict(color="#f8fafc", size=12),
        )
    )
    fig.update_layout(**_base_layout(), showlegend=True)
    return fig


def grade_pie(data, title="Grade Distribution", hole=0):
    safe = [d for d in (data or []) if d.get("value", 0) > 0]
    if not safe:
        return None
    colors = [GRADE_COLORS.get(d["name"], "#94a3b8") for d in safe]
    fig = go.Figure(
        go.Pie(
            labels=[d["name"] for d in safe],
            values=[d["value"] for d in safe],
            hole=0.45 if hole else 0,
            marker=dict(colors=colors, line=dict(color="#020617", width=2)),
            textinfo="label+percent", textfont=dict(color="#f8fafc", size=12),
        )
    )
    fig.update_layout(**_base_layout(), showlegend=True)
    return fig


def stacked_grade_bar(data, grades):
    grades = [g for g in (grades or []) if any(d.get(g, 0) > 0 for d in (data or []))]
    fig = go.Figure()
    for g in grades:
        fig.add_trace(
            go.Bar(
                name=g,
                x=[d.get("Course Name", d.get("Course Code", "")) for d in data],
                y=[d.get(g, 0) for d in data],
                marker_color=GRADE_COLORS.get(g, "#94a3b8"),
                hovertemplate="%{x}<br>%{y}<extra></extra>",
            )
        )
    axes = _axes()
    axes["xaxis"].update(tickangle=-25, tickfont=dict(color=AXIS, size=10))
    fig.update_layout(
        **_base_layout(height=340),
        **axes,
        barmode="stack",
        showlegend=True,
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=70),
    )
    return fig


def sgpa_line_chart(data, title="SGPA Growth"):
    xs = [d.get("Exam", "") for d in data]
    ys = [d.get("SGPA", 0) for d in data]
    fig = go.Figure(
        go.Scatter(
            x=xs, y=ys, mode="lines+markers",
            line=dict(color="#00d4ff", width=3),
            marker=dict(size=9, color="#00d4ff"),
            hovertemplate="%{x}<br>SGPA: %{y}<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout(height=300), **_axes())
    fig.update_yaxes(range=[0, 10])
    return fig


def simple_line_chart(data, x_key, y_key, title, color="#a855f7"):
    fig = go.Figure(
        go.Scatter(
            x=[d.get(x_key, "") for d in data],
            y=[d.get(y_key, 0) for d in data],
            mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=9, color=color),
            hovertemplate="%{x}<br>%{y}<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout(height=280), **_axes())
    return fig


def grade_heatmap(data):
    """HTML table replica of the GradeHeatmap component."""
    grades = ["O", "A+", "A", "B+", "B", "C", "P", "F"]
    subjects = (data or [])[:20]
    max_count = max(
        [1] + [int(s.get(g, 0) or 0) for s in subjects for g in grades],
    )

    head = "<tr><th>Subject</th>" + "".join(f"<th>{g}</th>" for g in grades) + "</tr>"
    body = ""
    for s in subjects:
        tds = ""
        for g in grades:
            v = int(s.get(g, 0) or 0)
            alpha = 0.05 if v == 0 else 0.25 + (v / max_count) * 0.75
            tds += (
                f'<td style="text-align:center;background:rgba(16, 185, 129, {alpha:.2f});'
                f'color:{("#64748b" if v == 0 else "#fff")}">{v if v else ""}</td>'
            )
        body += (
            f'<tr><td style="max-width:180px;overflow:hidden;text-overflow:ellipsis" '
            f'title="{_esc(s.get("Course Name", ""))}">{_esc(s.get("Course Name", ""))}</td>{tds}</tr>'
        )

    return (
        '<div class="chart-card" style="overflow-x:auto;margin-bottom:16px">'
        "<h5 style=\"margin-bottom:12px\">Grade Concentration Heatmap</h5>"
        f'<table class="data-table" style="min-width:500px"><thead>{head}</thead><tbody>{body}</tbody></table>'
        "</div>"
    )
