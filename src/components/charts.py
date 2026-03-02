"""Plotly chart factory functions for the dashboard."""

from datetime import date as _date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils.constants import (
    CHART_PALETTE,
    DORA_BAND_COLORS,
    DORA_BENCHMARKS,
    MILESTONE_COLORS,
    SEVERITY_COLORS,
    STATUS_COLORS,
    MilestoneStatus,
    ProgramStatus,
    RiskLikelihood,
    RiskSeverity,
)

_LAYOUT_DEFAULTS = dict(
    font=dict(family="Inter, sans-serif", size=12, color="#1A1A2E"),
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=40, r=20, t=40, b=40),
    hoverlabel=dict(bgcolor="white", font_size=12),
)


def _apply_layout(fig: go.Figure, **kwargs) -> go.Figure:
    merged = {**_LAYOUT_DEFAULTS, **kwargs}
    fig.update_layout(**merged)
    return fig


def _hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert a hex color like '#C0392B' to 'rgba(192, 57, 43, 0.5)'."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _empty_chart(message: str, height: int = 300) -> go.Figure:
    """Return a blank chart with a centered message."""
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
    )
    return _apply_layout(fig, height=height)


# ---------------------------------------------------------------------------
# Program Health
# ---------------------------------------------------------------------------


def program_status_donut(programs_df: pd.DataFrame) -> go.Figure:
    """Donut chart of program status distribution."""
    counts = programs_df["status"].value_counts()
    colors = [STATUS_COLORS.get(ProgramStatus(s), "#95A5A6") for s in counts.index]
    fig = go.Figure(
        go.Pie(
            labels=counts.index,
            values=counts.values,
            hole=0.55,
            marker=dict(colors=colors),
            textinfo="label+value",
            textfont_size=13,
        )
    )
    return _apply_layout(fig, title="Portfolio Status", showlegend=False, height=320)


def completion_bar_chart(programs_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of program completion percentages."""
    df = programs_df.sort_values("percent_complete", ascending=True)
    colors = [STATUS_COLORS.get(ProgramStatus(s), "#95A5A6") for s in df["status"]]
    fig = go.Figure(
        go.Bar(
            y=df["name"],
            x=df["percent_complete"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.0f}%" for v in df["percent_complete"]],
            textposition="auto",
        )
    )
    return _apply_layout(
        fig,
        title="Program Completion",
        xaxis=dict(range=[0, 105], title="% Complete"),
        yaxis=dict(title=""),
        height=350,
    )


# ---------------------------------------------------------------------------
# Budget Charts
# ---------------------------------------------------------------------------


def budget_by_program_bar(programs_df: pd.DataFrame) -> go.Figure:
    """Grouped horizontal bar: budgeted vs spent per program."""
    if programs_df.empty:
        return _empty_chart("No budget data")
    df = programs_df.sort_values("budget_millions", ascending=True)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=df["name"],
            x=df["budget_millions"],
            orientation="h",
            name="Budgeted",
            marker_color=CHART_PALETTE[0],
            text=[f"${v:.1f}M" for v in df["budget_millions"]],
            textposition="auto",
        )
    )
    fig.add_trace(
        go.Bar(
            y=df["name"],
            x=df["budget_spent_millions"],
            orientation="h",
            name="Spent",
            marker_color=CHART_PALETTE[3],
            text=[f"${v:.1f}M" for v in df["budget_spent_millions"]],
            textposition="auto",
        )
    )
    return _apply_layout(
        fig,
        title="Budget vs Spend by Program",
        barmode="group",
        yaxis=dict(title=""),
        xaxis=dict(title="$ Millions"),
        height=380,
    )


def budget_by_status_pie(programs_df: pd.DataFrame) -> go.Figure:
    """Donut chart of budget allocation by program status."""
    if programs_df.empty:
        return _empty_chart("No budget data")
    budget_by_status = programs_df.groupby("status")["budget_millions"].sum()
    colors = [STATUS_COLORS.get(ProgramStatus(s), "#95A5A6") for s in budget_by_status.index]
    fig = go.Figure(
        go.Pie(
            labels=budget_by_status.index,
            values=budget_by_status.values,
            hole=0.55,
            marker=dict(colors=colors),
            textinfo="label+value",
            texttemplate="%{label}<br>$%{value:.1f}M",
            textfont_size=12,
        )
    )
    return _apply_layout(fig, title="Budget by Status", showlegend=False, height=320)


def budget_utilization_bar(programs_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of budget utilization % with 100% threshold line."""
    if programs_df.empty:
        return _empty_chart("No budget data")
    df = programs_df.copy()
    df["utilization"] = df.apply(
        lambda r: (r["budget_spent_millions"] / r["budget_millions"] * 100)
        if r["budget_millions"] > 0
        else 0,
        axis=1,
    )
    df = df.sort_values("utilization", ascending=True)
    colors = [
        "#C0392B" if u > 100 else ("#D4A017" if u > 85 else "#2E8B57") for u in df["utilization"]
    ]
    fig = go.Figure(
        go.Bar(
            y=df["name"],
            x=df["utilization"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:.0f}%" for v in df["utilization"]],
            textposition="auto",
        )
    )
    fig.add_shape(
        type="line",
        x0=100,
        x1=100,
        y0=-0.5,
        y1=len(df) - 0.5,
        line=dict(color="#C0392B", width=2, dash="dash"),
    )
    fig.add_annotation(
        x=100,
        y=len(df) - 0.5,
        text="100%",
        showarrow=False,
        font=dict(size=10, color="#C0392B"),
        yshift=12,
    )
    return _apply_layout(
        fig,
        title="Budget Utilization",
        xaxis=dict(title="% Utilized", range=[0, max(df["utilization"].max() * 1.1, 110)]),
        yaxis=dict(title=""),
        height=350,
    )


# ---------------------------------------------------------------------------
# Milestone Tracker
# ---------------------------------------------------------------------------


def gantt_chart(milestones_df: pd.DataFrame, programs_df: pd.DataFrame) -> go.Figure:
    """Swim-lane milestone timeline — each milestone on its own row, grouped by program."""
    df = milestones_df.merge(
        programs_df[["id", "name"]], left_on="program_id", right_on="id", suffixes=("", "_prog")
    )
    df = df.sort_values(["name_prog", "due_date"], ascending=[True, True])

    color_map = {s.value: MILESTONE_COLORS[s] for s in MilestoneStatus}
    symbol_map = {
        MilestoneStatus.COMPLETED.value: "circle",
        MilestoneStatus.IN_PROGRESS.value: "diamond",
        MilestoneStatus.NOT_STARTED.value: "circle-open",
        MilestoneStatus.DELAYED.value: "x",
        MilestoneStatus.BLOCKED.value: "square",
    }

    # Build row labels: "  Milestone Name" indented under program headers
    labels = []
    seen_programs = set()
    for _, row in df.iterrows():
        prog = row["name_prog"]
        if prog not in seen_programs:
            seen_programs.add(prog)
        labels.append(f"  {row['name']}")
    df = df.copy()
    df["label"] = labels

    fig = go.Figure()

    # Horizontal connector lines per program (swim lane background)
    for prog in df["name_prog"].unique():
        prog_rows = df[df["name_prog"] == prog]
        if len(prog_rows) > 1:
            fig.add_trace(
                go.Scatter(
                    x=prog_rows["due_date"],
                    y=prog_rows["label"],
                    mode="lines",
                    line=dict(color="#E0E0E0", width=1.5),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

    # Milestone markers by status
    for status_val, color in color_map.items():
        subset = df[df["status"] == status_val]
        if subset.empty:
            continue
        is_key = subset["is_key_milestone"]
        sizes = [14 if k else 10 for k in is_key]
        borders = [2.5 if k else 0 for k in is_key]
        fig.add_trace(
            go.Scatter(
                x=subset["due_date"],
                y=subset["label"],
                mode="markers",
                name=status_val,
                marker=dict(
                    size=sizes,
                    symbol=symbol_map.get(status_val, "circle"),
                    color=color,
                    line=dict(
                        width=borders,
                        color="#1A1A2E",
                    ),
                ),
                customdata=subset[["name_prog", "quarter"]].values,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Program: %{customdata[0]}<br>"
                    "Due: %{x|%b %d, %Y}<br>"
                    "Quarter: %{customdata[1]}<br>"
                    "Status: " + status_val + "<extra></extra>"
                ),
            )
        )

    # Add today line
    today = _date.today().isoformat()
    fig.add_shape(
        type="line",
        x0=today,
        x1=today,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#C0392B", width=1.5, dash="dash"),
    )
    fig.add_annotation(
        x=today,
        y=1,
        yref="paper",
        text="Today",
        showarrow=False,
        font=dict(size=10, color="#C0392B"),
        yshift=10,
    )

    n_rows = len(df)
    return _apply_layout(
        fig,
        title="Milestone Timeline",
        yaxis=dict(
            title="",
            autorange="reversed",
            showgrid=False,
            tickfont=dict(size=10),
        ),
        xaxis=dict(
            title="",
            gridcolor="#F0F0F0",
            tickformat="%b %Y",
        ),
        height=max(400, n_rows * 32 + 80),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
    )


def milestone_status_bar(milestones_df: pd.DataFrame) -> go.Figure:
    """Stacked bar chart: milestone status by quarter."""
    counts = milestones_df.groupby(["quarter", "status"]).size().reset_index(name="count")
    color_map = {s.value: MILESTONE_COLORS[s] for s in MilestoneStatus}
    fig = px.bar(
        counts,
        x="quarter",
        y="count",
        color="status",
        color_discrete_map=color_map,
        barmode="stack",
    )
    return _apply_layout(fig, title="Milestones by Quarter", height=350)


def delivery_predictability(milestones_df: pd.DataFrame) -> go.Figure:
    """Bar chart showing on-time vs late delivery per quarter."""
    completed = milestones_df[milestones_df["status"] == MilestoneStatus.COMPLETED.value].copy()
    if completed.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No completed milestones",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return _apply_layout(fig, height=300)

    completed["on_time"] = completed["completed_date"] <= completed["due_date"]
    summary = completed.groupby("quarter")["on_time"].agg(["sum", "count"]).reset_index()
    summary.columns = ["quarter", "on_time", "total"]
    summary["late"] = summary["total"] - summary["on_time"]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=summary["quarter"], y=summary["on_time"], name="On Time", marker_color="#2E8B57")
    )
    fig.add_trace(
        go.Bar(x=summary["quarter"], y=summary["late"], name="Late", marker_color="#D4A017")
    )
    return _apply_layout(fig, title="Delivery Predictability", barmode="stack", height=320)


# ---------------------------------------------------------------------------
# Risk Management
# ---------------------------------------------------------------------------


def risk_heatmap(risks_df: pd.DataFrame) -> go.Figure:
    """Heatmap of risk severity vs likelihood."""
    sev_order = [s.value for s in RiskSeverity]
    lik_order = [lik.value for lik in RiskLikelihood]

    matrix = []
    for sev in sev_order:
        row = []
        for lik in lik_order:
            count = len(
                risks_df[
                    (risks_df["severity"] == sev)
                    & (risks_df["likelihood"] == lik)
                    & (risks_df["is_open"])
                ]
            )
            row.append(count)
        matrix.append(row)

    fig = go.Figure(
        go.Heatmap(
            z=matrix,
            x=lik_order,
            y=sev_order,
            colorscale=[[0, "#F0F4F8"], [0.5, "#D4A017"], [1, "#C0392B"]],
            text=matrix,
            texttemplate="%{text}",
            showscale=False,
        )
    )
    return _apply_layout(
        fig,
        title="Risk Heatmap (Open Risks)",
        xaxis_title="Likelihood",
        yaxis_title="Severity",
        height=350,
    )


def risk_trend(risks_df: pd.DataFrame) -> go.Figure:
    """Cumulative stacked area chart of open risks over time by severity."""
    open_risks = risks_df[risks_df["is_open"]].copy()
    if open_risks.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No open risks", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        return _apply_layout(fig, height=300)

    # Build cumulative open risk counts over time
    if "raised_date" not in open_risks.columns:
        # Fallback: simple bar chart if no date data
        counts = open_risks.groupby("severity").size().reset_index(name="count")
        colors = [SEVERITY_COLORS.get(RiskSeverity(s), "#95A5A6") for s in counts["severity"]]
        fig = go.Figure(
            go.Bar(
                x=counts["severity"],
                y=counts["count"],
                marker_color=colors,
                text=counts["count"],
                textposition="auto",
            )
        )
        return _apply_layout(fig, title="Open Risks by Severity", height=320)

    # Generate time series: for each day from earliest raised_date to today,
    # count cumulative open risks by severity
    min_date = open_risks["raised_date"].min()
    today = _date.today()
    if hasattr(min_date, "date"):
        min_date = min_date.date()

    sev_order = [s.value for s in RiskSeverity]
    fig = go.Figure()

    for sev in reversed(sev_order):
        sev_risks = open_risks[open_risks["severity"] == sev]
        if sev_risks.empty:
            continue

        # Build cumulative count at month boundaries for efficiency
        dates = []
        counts = []
        d = min_date
        while d <= today:
            count = len(sev_risks[sev_risks["raised_date"] <= d])
            dates.append(d)
            counts.append(count)
            # Move to next month
            if d.month == 12:
                d = d.replace(year=d.year + 1, month=1, day=1)
            else:
                d = d.replace(month=d.month + 1, day=1)
        # Always include today
        if dates[-1] != today:
            count = len(sev_risks[sev_risks["raised_date"] <= today])
            dates.append(today)
            counts.append(count)

        color = SEVERITY_COLORS.get(RiskSeverity(sev), "#95A5A6")
        fill = _hex_to_rgba(color, 0.5) if color.startswith("#") else color
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=counts,
                name=sev,
                stackgroup="one",
                line=dict(color=color),
                fillcolor=fill,
            )
        )

    return _apply_layout(
        fig,
        title="Cumulative Open Risks Over Time",
        xaxis_title="Date",
        yaxis_title="Open Risks",
        height=350,
    )


# ---------------------------------------------------------------------------
# KPI / DORA Metrics
# ---------------------------------------------------------------------------


def velocity_trend(metrics_df: pd.DataFrame, program_id: str | None = None) -> go.Figure:
    """Line chart of velocity over time."""
    df = metrics_df.copy()
    if program_id:
        df = df[df["program_id"] == program_id]

    agg = (
        df.groupby("week_start")
        .agg({"velocity": "sum", "planned_points": "sum", "delivered_points": "sum"})
        .reset_index()
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=agg["week_start"],
            y=agg["velocity"],
            name="Velocity",
            line=dict(color=CHART_PALETTE[0], width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=agg["week_start"],
            y=agg["planned_points"],
            name="Planned",
            line=dict(color="#95A5A6", dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=agg["week_start"],
            y=agg["delivered_points"],
            name="Delivered",
            line=dict(color=CHART_PALETTE[1], width=2),
        )
    )
    return _apply_layout(
        fig, title="Velocity Trend", xaxis_title="Week", yaxis_title="Story Points", height=380
    )


def dora_metrics_chart(metrics_df: pd.DataFrame) -> go.Figure:
    """Multi-panel DORA metrics with benchmark bands."""
    agg = (
        metrics_df.groupby("week_start")
        .agg(
            {
                "deployment_frequency": "mean",
                "lead_time_days": "mean",
                "change_failure_rate": "mean",
                "mttr_hours": "mean",
            }
        )
        .reset_index()
    )

    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Deployment Frequency",
            "Lead Time (days)",
            "Change Failure Rate (%)",
            "MTTR (hours)",
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=agg["week_start"], y=agg["deployment_frequency"], line=dict(color=CHART_PALETTE[0])
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=agg["week_start"], y=agg["lead_time_days"], line=dict(color=CHART_PALETTE[1])),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(
            x=agg["week_start"], y=agg["change_failure_rate"], line=dict(color=CHART_PALETTE[2])
        ),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=agg["week_start"], y=agg["mttr_hours"], line=dict(color=CHART_PALETTE[3])),
        row=2,
        col=2,
    )

    # Add DORA benchmark bands
    benchmarks = DORA_BENCHMARKS
    band_colors = DORA_BAND_COLORS

    # Deployment Frequency (higher is better) — row=1, col=1
    _add_dora_bands_higher(fig, benchmarks["deployment_frequency"], band_colors, row=1, col=1)

    # Lead Time (lower is better) — row=1, col=2
    _add_dora_bands_lower(fig, benchmarks["lead_time_days"], band_colors, row=1, col=2)

    # CFR (lower is better) — row=2, col=1
    _add_dora_bands_lower(fig, benchmarks["change_failure_rate"], band_colors, row=2, col=1)

    # MTTR (lower is better) — row=2, col=2
    _add_dora_bands_lower(fig, benchmarks["mttr_hours"], band_colors, row=2, col=2)

    return _apply_layout(fig, title="DORA Metrics", height=500, showlegend=False)


def _add_dora_bands_higher(fig, thresholds, colors, row, col):
    """Add benchmark bands for metrics where higher is better."""
    fig.add_hrect(
        y0=thresholds["elite"], y1=1000,
        fillcolor=colors["elite"], line_width=0,
        row=row, col=col,
    )
    fig.add_hrect(
        y0=thresholds["high"], y1=thresholds["elite"],
        fillcolor=colors["high"], line_width=0,
        row=row, col=col,
    )
    fig.add_hrect(
        y0=thresholds["medium"], y1=thresholds["high"],
        fillcolor=colors["medium"], line_width=0,
        row=row, col=col,
    )
    fig.add_hrect(
        y0=0, y1=thresholds["medium"],
        fillcolor=colors["low"], line_width=0,
        row=row, col=col,
    )


def _add_dora_bands_lower(fig, thresholds, colors, row, col):
    """Add benchmark bands for metrics where lower is better."""
    fig.add_hrect(
        y0=0, y1=thresholds["elite"],
        fillcolor=colors["elite"], line_width=0,
        row=row, col=col,
    )
    fig.add_hrect(
        y0=thresholds["elite"], y1=thresholds["high"],
        fillcolor=colors["high"], line_width=0,
        row=row, col=col,
    )
    fig.add_hrect(
        y0=thresholds["high"], y1=thresholds["medium"],
        fillcolor=colors["medium"], line_width=0,
        row=row, col=col,
    )
    fig.add_hrect(
        y0=thresholds["medium"], y1=1000,
        fillcolor=colors["low"], line_width=0,
        row=row, col=col,
    )


def defect_incident_trend(metrics_df: pd.DataFrame) -> go.Figure:
    """Stacked area chart of defects and incidents over time."""
    agg = (
        metrics_df.groupby("week_start")
        .agg({"defect_count": "sum", "incident_count": "sum"})
        .reset_index()
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=agg["week_start"],
            y=agg["defect_count"],
            fill="tozeroy",
            name="Defects",
            line=dict(color=CHART_PALETTE[2]),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=agg["week_start"],
            y=agg["incident_count"],
            fill="tozeroy",
            name="Incidents",
            line=dict(color=CHART_PALETTE[3]),
        )
    )
    return _apply_layout(fig, title="Defect & Incident Trend", height=350)
