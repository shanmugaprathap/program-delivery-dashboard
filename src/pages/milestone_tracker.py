"""Gantt chart, delivery predictability, milestone details."""

import streamlit as st

from src.components.charts import delivery_predictability, gantt_chart, milestone_status_bar
from src.components.filters import program_filter, quarter_filter
from src.components.status_cards import metric_card
from src.components.tables import styled_milestone_table
from src.data.data_loader import load_milestones, load_programs
from src.utils.constants import MilestoneStatus


def render():
    st.title("Milestone Tracker")

    programs = load_programs()
    milestones = load_milestones()

    # Filters
    with st.expander("Filters", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            selected_ids = program_filter(programs, key="mt_prog")
        with col2:
            selected_quarters = quarter_filter(key="mt_qtr")

    filtered = milestones[
        (milestones["program_id"].isin(selected_ids))
        & (milestones["quarter"].isin(selected_quarters))
    ]

    # Summary metrics
    total = len(filtered)
    completed = len(filtered[filtered["status"] == MilestoneStatus.COMPLETED.value])
    in_progress = len(filtered[filtered["status"] == MilestoneStatus.IN_PROGRESS.value])
    delayed = len(filtered[filtered["status"] == MilestoneStatus.DELAYED.value])
    blocked = len(filtered[filtered["status"] == MilestoneStatus.BLOCKED.value])
    key_milestones = len(filtered[filtered["is_key_milestone"]])

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        metric_card("Total", str(total))
    with c2:
        metric_card("Completed", str(completed), color="#2E8B57")
    with c3:
        metric_card("In Progress", str(in_progress), color="#1B6AC9")
    with c4:
        metric_card("Delayed", str(delayed), color="#D4A017")
    with c5:
        metric_card("Blocked", str(blocked), color="#C0392B")
    with c6:
        metric_card("Key Milestones", str(key_milestones), color="#8E44AD")

    st.markdown("---")

    # Gantt chart
    st.plotly_chart(gantt_chart(filtered, programs), use_container_width=True)

    # Charts row
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(milestone_status_bar(filtered), use_container_width=True)
    with col2:
        st.plotly_chart(delivery_predictability(filtered), use_container_width=True)

    # Table
    with st.expander("Milestone Details"):
        key_only = st.checkbox("Key milestones only", key="mt_key_only")
        display_df = filtered[filtered["is_key_milestone"]] if key_only else filtered
        styled_milestone_table(display_df)
