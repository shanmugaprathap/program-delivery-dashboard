"""Portfolio overview — status cards, completion bars, program details."""

import streamlit as st

from src.components.charts import completion_bar_chart, program_status_donut
from src.components.filters import program_filter, status_filter
from src.components.status_cards import metric_card, program_card
from src.components.tables import styled_program_table
from src.data.data_loader import load_programs
from src.utils.constants import ProgramStatus


def render():
    st.title("Program Health Overview")

    programs = load_programs()

    # Filters
    with st.expander("Filters", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            selected_ids = program_filter(programs, key="ph_prog")
        with col2:
            selected_statuses = status_filter(key="ph_status")

    filtered = programs[
        (programs["id"].isin(selected_ids)) & (programs["status"].isin(selected_statuses))
    ]

    # Top-level metrics
    total = len(filtered)
    on_track = len(filtered[filtered["status"] == ProgramStatus.ON_TRACK.value])
    at_risk = len(filtered[filtered["status"] == ProgramStatus.AT_RISK.value])
    off_track = len(filtered[filtered["status"] == ProgramStatus.OFF_TRACK.value])
    completed = len(filtered[filtered["status"] == ProgramStatus.COMPLETED.value])
    avg_completion = filtered["percent_complete"].mean() if total > 0 else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        metric_card("Total Programs", str(total))
    with c2:
        metric_card("On Track", str(on_track), color="#2E8B57")
    with c3:
        metric_card("At Risk", str(at_risk), color="#D4A017")
    with c4:
        metric_card("Off Track", str(off_track), color="#C0392B")
    with c5:
        metric_card("Completed", str(completed), color="#5B7DB1")
    with c6:
        metric_card("Avg Completion", f"{avg_completion:.0f}%", color="#8E44AD")

    st.markdown("---")

    # Charts row
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(program_status_donut(filtered), use_container_width=True)
    with col_right:
        st.plotly_chart(completion_bar_chart(filtered), use_container_width=True)

    # Program cards
    st.subheader("Program Details")
    cols = st.columns(2)
    for i, (_, row) in enumerate(filtered.iterrows()):
        with cols[i % 2]:
            program_card(
                row["name"],
                ProgramStatus(row["status"]),
                row["percent_complete"],
                row["department"],
                row["owner"],
            )

    # Table view
    with st.expander("Detailed Table View"):
        styled_program_table(filtered)
