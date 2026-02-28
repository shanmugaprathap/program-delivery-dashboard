"""Risk heatmap, escalation timeline, risk trends."""

import streamlit as st

from src.components.charts import risk_heatmap, risk_trend
from src.components.filters import program_filter, severity_filter
from src.components.status_cards import metric_card
from src.components.tables import styled_escalation_table, styled_risk_table
from src.data.data_loader import load_escalations, load_programs, load_risks
from src.utils.constants import RiskSeverity


def render():
    st.title("Risk Management")

    programs = load_programs()
    risks = load_risks()
    escalations = load_escalations()

    # Filters
    with st.expander("Filters", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            selected_ids = program_filter(programs, key="rm_prog")
        with col2:
            selected_severities = severity_filter(key="rm_sev")

    filtered_risks = risks[
        (risks["program_id"].isin(selected_ids)) & (risks["severity"].isin(selected_severities))
    ]
    filtered_esc = escalations[escalations["program_id"].isin(selected_ids)]

    # Summary
    open_risks = filtered_risks[filtered_risks["is_open"]]
    total_open = len(open_risks)
    critical = len(open_risks[open_risks["severity"] == RiskSeverity.CRITICAL.value])
    high = len(open_risks[open_risks["severity"] == RiskSeverity.HIGH.value])
    open_escalations = len(filtered_esc[filtered_esc["resolved_date"].isna()])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Open Risks", str(total_open), color="#D4A017")
    with c2:
        metric_card("Critical", str(critical), color="#C0392B")
    with c3:
        metric_card("High", str(high), color="#E67E22")
    with c4:
        metric_card("Open Escalations", str(open_escalations), color="#8E44AD")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(risk_heatmap(filtered_risks), use_container_width=True)
    with col2:
        st.plotly_chart(risk_trend(filtered_risks), use_container_width=True)

    # Risk table
    st.subheader("Risk Register")
    open_only = st.checkbox("Open risks only", value=True, key="rm_open_only")
    display_risks = filtered_risks[filtered_risks["is_open"]] if open_only else filtered_risks
    styled_risk_table(display_risks)

    # Escalations
    st.subheader("Escalations")
    styled_escalation_table(filtered_esc)
