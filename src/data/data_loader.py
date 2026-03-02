"""Data loader abstraction — returns DataFrames from mock or JIRA source."""

from datetime import date

import pandas as pd
import streamlit as st

from src.data import mock_data
from src.utils.config import get


@st.cache_data(ttl=1800)
def load_programs() -> pd.DataFrame:
    """Load programs as a DataFrame."""
    source = get("data_source", "mock")
    if source == "jira":
        from src.data.jira_client import fetch_programs

        return fetch_programs()
    if source == "asana":
        from src.data.asana_client import fetch_programs

        return fetch_programs()
    return pd.DataFrame([p.model_dump() for p in mock_data.get_programs()])


@st.cache_data(ttl=1800)
def load_milestones() -> pd.DataFrame:
    source = get("data_source", "mock")
    if source == "jira":
        from src.data.jira_client import fetch_milestones

        return fetch_milestones()
    if source == "asana":
        from src.data.asana_client import fetch_milestones

        return fetch_milestones()
    return pd.DataFrame([m.model_dump() for m in mock_data.get_milestones()])


@st.cache_data(ttl=1800)
def load_risks() -> pd.DataFrame:
    """Load risks with computed risk_age_days column."""
    source = get("data_source", "mock")
    if source == "jira":
        from src.data.jira_client import fetch_risks

        return fetch_risks()
    if source == "asana":
        from src.data.asana_client import fetch_risks

        return fetch_risks()
    df = pd.DataFrame([r.model_dump() for r in mock_data.get_risks()])
    today = date.today()
    df["risk_age_days"] = df["raised_date"].apply(lambda d: (today - d).days)
    return df


@st.cache_data(ttl=1800)
def load_escalations() -> pd.DataFrame:
    source = get("data_source", "mock")
    if source == "jira":
        from src.data.jira_client import fetch_escalations

        return fetch_escalations()
    if source == "asana":
        from src.data.asana_client import fetch_escalations

        return fetch_escalations()
    return pd.DataFrame([e.model_dump() for e in mock_data.get_escalations()])


@st.cache_data(ttl=1800)
def load_metrics() -> pd.DataFrame:
    source = get("data_source", "mock")
    if source == "jira":
        from src.data.jira_client import fetch_metrics

        return fetch_metrics()
    if source == "asana":
        from src.data.asana_client import fetch_metrics

        return fetch_metrics()
    return pd.DataFrame([m.model_dump() for m in mock_data.get_metrics()])


@st.cache_data(ttl=1800)
def load_weekly_snapshots() -> pd.DataFrame:
    source = get("data_source", "mock")
    if source == "jira":
        from src.data.jira_client import fetch_weekly_snapshots

        return fetch_weekly_snapshots()
    if source == "asana":
        from src.data.asana_client import fetch_weekly_snapshots

        return fetch_weekly_snapshots()
    return pd.DataFrame([s.model_dump() for s in mock_data.get_weekly_snapshots()])
