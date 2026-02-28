"""Clean executive summary for leadership with export capability."""

import io
from datetime import date

import streamlit as st

from src.components.charts import completion_bar_chart, program_status_donut
from src.components.status_cards import metric_card, status_badge
from src.data.data_loader import (
    load_escalations,
    load_metrics,
    load_milestones,
    load_programs,
    load_risks,
)
from src.utils.constants import MilestoneStatus, ProgramStatus, RiskSeverity


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
    open_risks = len(risks[risks["is_open"]])
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
            (risks["is_open"])
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

    # DORA highlights
    st.subheader("Delivery Health (Latest Week)")
    latest_week = metrics["week_start"].max()
    latest = metrics[metrics["week_start"] == latest_week]
    dc1, dc2, dc3, dc4 = st.columns(4)
    with dc1:
        metric_card(
            "Avg Deploy Freq", f"{latest['deployment_frequency'].mean():.1f}/wk", color="#1B6AC9"
        )
    with dc2:
        metric_card("Avg Lead Time", f"{latest['lead_time_days'].mean():.1f} days", color="#2E8B57")
    with dc3:
        metric_card("Total Velocity", f"{latest['velocity'].sum():.0f} pts", color="#8E44AD")
    with dc4:
        metric_card("Incidents", str(latest["incident_count"].sum()), color="#C0392B")

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
    open_r = risks[risks["is_open"]][["title", "program_id", "severity", "likelihood"]]
    open_r.to_csv(buf, index=False)
    buf.write("\n=== Open Escalations ===\n")
    open_e = escalations[escalations["resolved_date"].isna()][
        ["title", "program_id", "level", "raised_date"]
    ]
    open_e.to_csv(buf, index=False)
    return buf.getvalue()
