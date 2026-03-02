"""SRE-aligned DORA metrics, velocity, defect/incident trends."""

import pandas as pd
import streamlit as st

from src.components.charts import defect_incident_trend, dora_metrics_chart, velocity_trend
from src.components.filters import program_filter
from src.components.status_cards import metric_card
from src.data.data_loader import load_metrics, load_programs
from src.utils.helpers import classify_dora_maturity, format_percent_delta


def render():
    st.title("KPI Metrics")

    programs = load_programs()
    metrics = load_metrics()

    # Filter
    with st.expander("Filters", expanded=False):
        selected_ids = program_filter(programs, key="kpi_prog")

    if metrics.empty:
        st.warning("No delivery metrics available. Metrics are not provided by the Asana data source.")
        return

    filtered = metrics[metrics["program_id"].isin(selected_ids)]

    if filtered.empty:
        st.warning("No metrics available for the selected programs.")
        return

    # Latest and previous week
    sorted_weeks = sorted(filtered["week_start"].unique())
    if not sorted_weeks:
        st.warning("No weekly data available.")
        return
    latest_week = sorted_weeks[-1]
    prev_week = sorted_weeks[-2] if len(sorted_weeks) >= 2 else None

    latest = filtered[filtered["week_start"] == latest_week]
    prev = filtered[filtered["week_start"] == prev_week] if prev_week else None

    deploy_cur = latest["deployment_frequency"].mean()
    lead_cur = latest["lead_time_days"].mean()
    cfr_cur = latest["change_failure_rate"].mean()
    mttr_cur = latest["mttr_hours"].mean()

    deploy_delta = None
    lead_delta = None
    cfr_delta = None
    mttr_delta = None
    if prev is not None:
        deploy_delta = format_percent_delta(deploy_cur, prev["deployment_frequency"].mean())
        lead_delta = format_percent_delta(lead_cur, prev["lead_time_days"].mean())
        cfr_delta = format_percent_delta(cfr_cur, prev["change_failure_rate"].mean())
        mttr_delta = format_percent_delta(mttr_cur, prev["mttr_hours"].mean())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "Avg Deploy Freq", f"{deploy_cur:.1f}/wk",
            delta=deploy_delta, color="#1B6AC9",
        )
    with c2:
        metric_card(
            "Avg Lead Time", f"{lead_cur:.1f} days",
            delta=lead_delta, color="#2E8B57", inverse_delta=True,
        )
    with c3:
        metric_card(
            "Avg CFR", f"{cfr_cur:.1f}%",
            delta=cfr_delta, color="#D4A017", inverse_delta=True,
        )
    with c4:
        metric_card(
            "Avg MTTR", f"{mttr_cur:.1f} hrs",
            delta=mttr_delta, color="#C0392B", inverse_delta=True,
        )

    st.markdown("---")

    # DORA metrics chart with benchmark bands
    st.plotly_chart(dora_metrics_chart(filtered), use_container_width=True)

    # DORA Maturity by Program
    st.subheader("DORA Maturity by Program")
    maturity_rows = []
    for pid in selected_ids:
        prog_latest = latest[latest["program_id"] == pid]
        if prog_latest.empty:
            continue
        prog_name = programs[programs["id"] == pid]["name"].values
        name = prog_name[0] if len(prog_name) > 0 else pid
        df_val = prog_latest["deployment_frequency"].mean()
        lt_val = prog_latest["lead_time_days"].mean()
        cfr_val = prog_latest["change_failure_rate"].mean()
        mttr_val = prog_latest["mttr_hours"].mean()
        level = classify_dora_maturity(df_val, lt_val, cfr_val, mttr_val)
        maturity_rows.append({
            "Program": name,
            "Deploy Freq": f"{df_val:.1f}/wk",
            "Lead Time": f"{lt_val:.1f}d",
            "CFR": f"{cfr_val:.1f}%",
            "MTTR": f"{mttr_val:.1f}h",
            "Maturity": level,
        })

    if maturity_rows:
        maturity_df = pd.DataFrame(maturity_rows)
        maturity_colors = {
            "Elite": "color: #2E8B57; font-weight: 600",
            "High": "color: #1B6AC9; font-weight: 600",
            "Medium": "color: #D4A017; font-weight: 600",
            "Low": "color: #C0392B; font-weight: 600",
        }
        st.dataframe(
            maturity_df.style.applymap(
                lambda v: maturity_colors.get(v, ""),
                subset=["Maturity"],
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")

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
