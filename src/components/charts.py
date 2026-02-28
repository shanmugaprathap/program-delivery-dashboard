"""Plotly chart factory functions for the dashboard."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils.constants import (
    CHART_PALETTE,
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
# Milestone Tracker
# ---------------------------------------------------------------------------


def gantt_chart(milestones_df: pd.DataFrame, programs_df: pd.DataFrame) -> go.Figure:
    """Scatter-based milestone timeline grouped by program."""
    df = milestones_df.merge(
        programs_df[["id", "name"]], left_on="program_id", right_on="id", suffixes=("", "_prog")
    )
    df = df.sort_values(["name_prog", "due_date"])

    color_map = {s.value: MILESTONE_COLORS[s] for s in MilestoneStatus}

    fig = go.Figure()
    for status_val, color in color_map.items():
        subset = df[df["status"] == status_val]
        if subset.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=subset["due_date"],
                y=subset["name_prog"],
                mode="markers",
                name=status_val,
                marker=dict(size=12, symbol="diamond", color=color),
                text=subset["name"],
                hovertemplate=(
                    "<b>%{text}</b><br>Due: %{x}<br>Status: "
                    + status_val
                    + "<extra></extra>"
                ),
            )
        )
    return _apply_layout(
        fig,
        title="Milestone Timeline",
        yaxis_title="",
        height=max(350, len(df) * 12),
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
    """Line chart of open risks over time by severity."""
    open_risks = risks_df[risks_df["is_open"]].copy()
    if open_risks.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No open risks", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
        )
        return _apply_layout(fig, height=300)

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
    """Multi-panel DORA metrics: deployment freq, lead time, CFR, MTTR."""
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

    return _apply_layout(fig, title="DORA Metrics", height=500, showlegend=False)


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
