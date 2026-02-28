"""Program Delivery Dashboard — Streamlit entry point."""

import streamlit as st

st.set_page_config(
    page_title="Program Delivery Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.pages import (  # noqa: E402
    executive_summary,
    kpi_metrics,
    milestone_tracker,
    program_health,
    risk_management,
)

PAGES = {
    "Executive Summary": executive_summary,
    "Program Health": program_health,
    "Milestone Tracker": milestone_tracker,
    "Risk Management": risk_management,
    "KPI Metrics": kpi_metrics,
}

# Sidebar
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:1rem 0;">
            <div style="font-size:1.4rem;font-weight:700;color:#1B6AC9;">
                Program Delivery
            </div>
            <div style="font-size:0.85rem;color:#6B7280;">Dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    page = st.radio("Navigation", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    st.caption("Data source: Mock (seed=42)")
    st.caption("Last refresh: Live")

# Render selected page
PAGES[page].render()
