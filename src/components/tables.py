"""Styled DataFrame displays."""

import pandas as pd
import streamlit as st

from src.utils.constants import SEVERITY_COLORS, STATUS_COLORS, ProgramStatus, RiskSeverity


def styled_program_table(df: pd.DataFrame):
    """Display programs table with status color coding."""
    display_df = df[
        ["name", "department", "status", "percent_complete", "owner", "target_end_date"]
    ].copy()
    display_df.columns = ["Program", "Department", "Status", "% Complete", "Owner", "Target Date"]

    st.dataframe(
        display_df.style.applymap(
            lambda v: (
                f"color: {STATUS_COLORS.get(ProgramStatus(v), '#1A1A2E')}; font-weight: 600"
                if v in [s.value for s in ProgramStatus]
                else ""
            ),
            subset=["Status"],
        ).format({"% Complete": "{:.0f}%"}),
        use_container_width=True,
        hide_index=True,
    )


def styled_risk_table(df: pd.DataFrame):
    """Display risks table with severity color coding."""
    display_df = df[["title", "program_id", "severity", "likelihood", "owner", "is_open"]].copy()
    display_df.columns = ["Risk", "Program", "Severity", "Likelihood", "Owner", "Open"]
    display_df["Open"] = display_df["Open"].map({True: "Yes", False: "No"})

    st.dataframe(
        display_df.style.applymap(
            lambda v: (
                f"color: {SEVERITY_COLORS.get(RiskSeverity(v), '#1A1A2E')}; font-weight: 600"
                if v in [s.value for s in RiskSeverity]
                else ""
            ),
            subset=["Severity"],
        ),
        use_container_width=True,
        hide_index=True,
    )


def styled_escalation_table(df: pd.DataFrame):
    """Display escalations table."""
    display_df = df[["title", "program_id", "level", "raised_date", "resolved_date"]].copy()
    display_df.columns = ["Escalation", "Program", "Level", "Raised", "Resolved"]
    display_df["Resolved"] = display_df["Resolved"].fillna("Open")

    st.dataframe(display_df, use_container_width=True, hide_index=True)


def styled_milestone_table(df: pd.DataFrame):
    """Display milestones table."""
    display_df = df[
        ["name", "program_id", "status", "due_date", "quarter", "is_key_milestone"]
    ].copy()
    display_df.columns = ["Milestone", "Program", "Status", "Due Date", "Quarter", "Key"]
    display_df["Key"] = display_df["Key"].map({True: "Yes", False: ""})

    st.dataframe(display_df, use_container_width=True, hide_index=True)
