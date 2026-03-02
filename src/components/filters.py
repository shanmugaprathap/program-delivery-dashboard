"""Shared filter widgets for the dashboard."""

import pandas as pd
import streamlit as st

from src.utils.constants import QUARTERS, ProgramStatus, RiskSeverity, compute_quarters


def program_filter(programs_df, key: str = "program_filter") -> list[str]:
    """Multi-select filter for programs. Returns selected program IDs."""
    options = programs_df[["id", "name"]].drop_duplicates()
    selected_names = st.multiselect(
        "Programs",
        options=options["name"].tolist(),
        default=options["name"].tolist(),
        key=key,
    )
    return options[options["name"].isin(selected_names)]["id"].tolist()


def quarter_filter(
    key: str = "quarter_filter",
    milestones_df: pd.DataFrame | None = None,
) -> list[str]:
    """Multi-select filter for quarters. Derives quarters from data when provided."""
    if milestones_df is not None and not milestones_df.empty:
        quarters = compute_quarters(milestones_df["due_date"].tolist())
    else:
        quarters = list(QUARTERS)
    return st.multiselect("Quarters", options=quarters, default=quarters, key=key)


def status_filter(key: str = "status_filter") -> list[str]:
    """Multi-select filter for program status."""
    options = [s.value for s in ProgramStatus]
    return st.multiselect("Status", options=options, default=options, key=key)


def severity_filter(key: str = "severity_filter") -> list[str]:
    """Multi-select filter for risk severity."""
    options = [s.value for s in RiskSeverity]
    return st.multiselect("Severity", options=options, default=options, key=key)
