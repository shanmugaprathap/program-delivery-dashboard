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
        display_df.style.map(
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


def _age_color(age_days: int) -> str:
    """Return CSS color string based on risk age."""
    if age_days > 90:
        return "color: #C0392B; font-weight: 600"
    elif age_days > 60:
        return "color: #E67E22; font-weight: 600"
    return ""


def styled_risk_table(df: pd.DataFrame):
    """Display risks table with severity color coding, age, and risk score."""
    from src.utils.constants import RiskLikelihood
    from src.utils.helpers import risk_score

    cols = ["title", "program_id", "severity", "likelihood", "owner", "is_open"]
    has_age = "risk_age_days" in df.columns

    display_df = df[cols].copy()

    # Compute risk score
    display_df["Risk Score"] = df.apply(
        lambda r: risk_score(
            RiskSeverity(r["severity"]), RiskLikelihood(r["likelihood"])
        ),
        axis=1,
    )

    if has_age:
        display_df["Age (days)"] = df["risk_age_days"].values

    display_df.columns = (
        ["Risk", "Program", "Severity", "Likelihood", "Owner", "Open", "Risk Score"]
        + (["Age (days)"] if has_age else [])
    )
    display_df["Open"] = display_df["Open"].map({True: "Yes", False: "No"})

    styler = display_df.style.map(
        lambda v: (
            f"color: {SEVERITY_COLORS.get(RiskSeverity(v), '#1A1A2E')}; font-weight: 600"
            if v in [s.value for s in RiskSeverity]
            else ""
        ),
        subset=["Severity"],
    )

    if has_age:
        styler = styler.map(_age_color, subset=["Age (days)"])

    st.dataframe(styler, use_container_width=True, hide_index=True)


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
