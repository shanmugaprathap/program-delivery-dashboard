"""SRE-aligned DORA metrics, velocity, defect/incident trends."""

import streamlit as st

from src.components.charts import (
    defect_incident_trend,
    dora_metrics_chart,
    velocity_trend,
)
from src.components.filters import program_filter
from src.components.status_cards import metric_card
from src.data.data_loader import load_metrics, load_programs


def render():
    st.title("KPI Metrics")

    programs = load_programs()
    metrics = load_metrics()

    # Filter
    with st.expander("Filters", expanded=False):
        selected_ids = program_filter(programs, key="kpi_prog")

    filtered = metrics[metrics["program_id"].isin(selected_ids)]

    if filtered.empty:
        st.warning("No metrics available for the selected programs.")
        return

    # Latest week summary
    latest_week = filtered["week_start"].max()
    latest = filtered[filtered["week_start"] == latest_week]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "Avg Deploy Freq",
            f"{latest['deployment_frequency'].mean():.1f}/wk",
            color="#1B6AC9",
        )
    with c2:
        metric_card(
            "Avg Lead Time",
            f"{latest['lead_time_days'].mean():.1f} days",
            color="#2E8B57",
        )
    with c3:
        metric_card(
            "Avg CFR",
            f"{latest['change_failure_rate'].mean():.1f}%",
            color="#D4A017",
        )
    with c4:
        metric_card(
            "Avg MTTR",
            f"{latest['mttr_hours'].mean():.1f} hrs",
            color="#C0392B",
        )

    st.markdown("---")

    # DORA metrics
    st.plotly_chart(dora_metrics_chart(filtered), use_container_width=True)

    # Velocity and defects side by side
    col1, col2 = st.columns(2)
    with col1:
        program_select = st.selectbox(
            "Program for velocity detail",
            options=["All Programs"] + programs[programs["id"].isin(selected_ids)]["name"].tolist(),
            key="kpi_vel_prog",
        )
        pid = None
        if program_select != "All Programs":
            pid = programs[programs["name"] == program_select]["id"].values[0]
        st.plotly_chart(velocity_trend(filtered, program_id=pid), use_container_width=True)

    with col2:
        st.plotly_chart(defect_incident_trend(filtered), use_container_width=True)
