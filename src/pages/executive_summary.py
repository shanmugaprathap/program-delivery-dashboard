"""Clean executive summary for leadership with export capability."""

from datetime import date
import io

import streamlit as st

from src.components.charts import (
    budget_by_program_bar,
    budget_by_status_pie,
    completion_bar_chart,
    program_status_donut,
)
from src.components.status_cards import metric_card, status_badge
from src.data.data_loader import (
    load_escalations,
    load_metrics,
    load_milestones,
    load_programs,
    load_risks,
)
from src.utils.constants import MilestoneStatus, ProgramStatus, RiskSeverity
from src.utils.helpers import format_percent_delta, generate_decisions


def render():
    st.title("Executive Summary")
    st.caption(f"Report Date: {date.today().strftime('%B %d, %Y')}")

    programs = load_programs()
    milestones = load_milestones()
    risks = load_risks()
    escalations = load_escalations()
    metrics = load_metrics()

    # Top-line metrics
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    total_programs = len(programs)
    on_track = len(programs[programs["status"] == ProgramStatus.ON_TRACK.value])
    at_risk = len(programs[programs["status"] == ProgramStatus.AT_RISK.value])
    off_track = len(programs[programs["status"] == ProgramStatus.OFF_TRACK.value])
    open_risks = len(risks[risks["is_open"] == True])
    open_esc = len(escalations[escalations["resolved_date"].isna()])

    with c1:
        metric_card("Programs", str(total_programs))
    with c2:
        metric_card("On Track", str(on_track), color="#2E8B57")
    with c3:
        metric_card("At Risk", str(at_risk), color="#D4A017")
    with c4:
        metric_card("Off Track", str(off_track), color="#C0392B")
    with c5:
        metric_card("Open Risks", str(open_risks), color="#E67E22")
    with c6:
        metric_card("Escalations", str(open_esc), color="#8E44AD")

    st.markdown("---")

    # Portfolio chart
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(program_status_donut(programs), use_container_width=True)
    with col2:
        st.plotly_chart(completion_bar_chart(programs), use_container_width=True)

    st.markdown("---")

    # Budget Overview
    st.subheader("Budget Overview")
    total_budget = programs["budget_millions"].sum()
    total_spent = programs["budget_spent_millions"].sum()
    utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0

    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        metric_card("Total Budget", f"${total_budget:.1f}M", color="#1B6AC9")
    with bc2:
        metric_card("Total Spent", f"${total_spent:.1f}M", color="#8E44AD")
    with bc3:
        util_color = "#C0392B" if utilization > 100 else ("#D4A017" if utilization > 85 else "#2E8B57")
        metric_card("Utilization", f"{utilization:.0f}%", color=util_color)

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.plotly_chart(budget_by_program_bar(programs), use_container_width=True)
    with col_b2:
        st.plotly_chart(budget_by_status_pie(programs), use_container_width=True)

    st.markdown("---")

    # Key highlights
    st.subheader("Key Highlights")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Programs Requiring Attention**")
        attention = programs[
            programs["status"].isin([ProgramStatus.AT_RISK.value, ProgramStatus.OFF_TRACK.value])
        ]
        for _, row in attention.iterrows():
            badge = status_badge(ProgramStatus(row["status"]))
            st.markdown(
                f"{badge} **{row['name']}** — {row['percent_complete']:.0f}% complete, "
                f"owned by {row['owner']}",
                unsafe_allow_html=True,
            )

        # Critical risks
        st.markdown("**Critical & High Open Risks**")
        critical_risks = risks[
            (risks["is_open"] == True)
            & (risks["severity"].isin([RiskSeverity.CRITICAL.value, RiskSeverity.HIGH.value]))
        ]
        for _, row in critical_risks.iterrows():
            st.markdown(f"- **{row['severity']}**: {row['title']} ({row['program_id']})")

    with col_b:
        st.markdown("**Upcoming Key Milestones**")
        upcoming = (
            milestones[
                (milestones["is_key_milestone"])
                & (
                    milestones["status"].isin(
                        [MilestoneStatus.IN_PROGRESS.value, MilestoneStatus.NOT_STARTED.value]
                    )
                )
            ]
            .sort_values("due_date")
            .head(5)
        )
        for _, row in upcoming.iterrows():
            st.markdown(f"- {row['name']} — due {row['due_date']} ({row['program_id']})")

        # Open escalations
        st.markdown("**Open Escalations**")
        open_escs = escalations[escalations["resolved_date"].isna()]
        for _, row in open_escs.iterrows():
            st.markdown(f"- **{row['level']}**: {row['title']}")

    st.markdown("---")

    # DORA highlights with WoW deltas
    st.subheader("Delivery Health (Latest Week)")
    if metrics.empty:
        st.info("No delivery metrics available for the current data source.")
        sorted_weeks = []
    else:
        sorted_weeks = sorted(metrics["week_start"].unique())
    latest_week = sorted_weeks[-1] if sorted_weeks else None
    prev_week = sorted_weeks[-2] if len(sorted_weeks) >= 2 else None

    if latest_week is not None:
        latest = metrics[metrics["week_start"] == latest_week]
        prev = metrics[metrics["week_start"] == prev_week] if prev_week is not None else None

        deploy_cur = latest["deployment_frequency"].mean()
        lead_cur = latest["lead_time_days"].mean()
        vel_cur = latest["velocity"].sum()
        inc_cur = latest["incident_count"].sum()

        deploy_delta = None
        lead_delta = None
        vel_delta = None
        inc_delta = None

        if prev is not None:
            deploy_delta = format_percent_delta(deploy_cur, prev["deployment_frequency"].mean())
            lead_delta = format_percent_delta(lead_cur, prev["lead_time_days"].mean())
            vel_delta = format_percent_delta(vel_cur, prev["velocity"].sum())
            inc_delta = format_percent_delta(float(inc_cur), float(prev["incident_count"].sum()))

        dc1, dc2, dc3, dc4 = st.columns(4)
        with dc1:
            metric_card("Avg Deploy Freq", f"{deploy_cur:.1f}/wk", delta=deploy_delta, color="#1B6AC9")
        with dc2:
            metric_card(
                "Avg Lead Time", f"{lead_cur:.1f} days",
                delta=lead_delta, color="#2E8B57", inverse_delta=True,
            )
        with dc3:
            metric_card("Total Velocity", f"{vel_cur:.0f} pts", delta=vel_delta, color="#8E44AD")
        with dc4:
            metric_card(
                "Incidents", str(int(inc_cur)),
                delta=inc_delta, color="#C0392B", inverse_delta=True,
            )

    st.markdown("---")

    # Decisions Needed
    decisions = generate_decisions(programs, risks, milestones, escalations)
    if decisions:
        st.subheader("Decisions Needed")
        severity_icons = {
            "critical": ":red_circle:",
            "high": ":orange_circle:",
            "medium": ":large_yellow_circle:",
        }
        for d in decisions:
            icon = severity_icons.get(d.severity, ":white_circle:")
            st.markdown(
                f"{icon} **{d.title}**  \n"
                f"&nbsp;&nbsp;&nbsp;&nbsp;Recommendation: {d.recommendation}"
            )
        st.markdown("---")

    # Export
    st.subheader("Export")
    export_data = _build_export(programs, milestones, risks, escalations)
    st.download_button(
        label="Download Summary (CSV)",
        data=export_data,
        file_name=f"executive_summary_{date.today().isoformat()}.csv",
        mime="text/csv",
    )


def _build_export(programs, milestones, risks, escalations) -> str:
    """Build a CSV export of the executive summary."""
    buf = io.StringIO()
    buf.write("=== Programs ===\n")
    programs[["name", "status", "percent_complete", "department", "owner"]].to_csv(buf, index=False)
    buf.write("\n=== Open Risks ===\n")
    open_r = risks[risks["is_open"] == True][["title", "program_id", "severity", "likelihood"]]
    open_r.to_csv(buf, index=False)
    buf.write("\n=== Open Escalations ===\n")
    open_e = escalations[escalations["resolved_date"].isna()][
        ["title", "program_id", "level", "raised_date"]
    ]
    open_e.to_csv(buf, index=False)
    return buf.getvalue()
