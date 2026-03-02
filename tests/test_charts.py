"""Tests for chart rendering — ensures all charts build without errors."""

import pandas as pd

from src.components.charts import (
    budget_by_program_bar,
    budget_by_status_pie,
    budget_utilization_bar,
    completion_bar_chart,
    defect_incident_trend,
    delivery_predictability,
    dora_metrics_chart,
    gantt_chart,
    milestone_status_bar,
    program_status_donut,
    risk_heatmap,
    risk_trend,
    velocity_trend,
)
from src.data.mock_data import get_metrics, get_milestones, get_programs, get_risks


def _programs_df():
    return pd.DataFrame([p.model_dump() for p in get_programs()])


def _milestones_df():
    return pd.DataFrame([m.model_dump() for m in get_milestones()])


def _risks_df():
    return pd.DataFrame([r.model_dump() for r in get_risks()])


def _metrics_df():
    return pd.DataFrame([m.model_dump() for m in get_metrics()])


class TestChartRendering:
    def test_program_status_donut(self):
        fig = program_status_donut(_programs_df())
        assert fig is not None

    def test_completion_bar_chart(self):
        fig = completion_bar_chart(_programs_df())
        assert fig is not None

    def test_gantt_chart(self):
        fig = gantt_chart(_milestones_df(), _programs_df())
        assert fig is not None

    def test_milestone_status_bar(self):
        fig = milestone_status_bar(_milestones_df())
        assert fig is not None

    def test_delivery_predictability(self):
        fig = delivery_predictability(_milestones_df())
        assert fig is not None

    def test_risk_heatmap(self):
        fig = risk_heatmap(_risks_df())
        assert fig is not None

    def test_risk_trend(self):
        fig = risk_trend(_risks_df())
        assert fig is not None
        # Should have traces for the stacked area chart
        assert len(fig.data) > 0

    def test_velocity_trend(self):
        fig = velocity_trend(_metrics_df())
        assert fig is not None

    def test_velocity_trend_single_program(self):
        fig = velocity_trend(_metrics_df(), program_id="PRG-001")
        assert fig is not None

    def test_dora_metrics_chart(self):
        fig = dora_metrics_chart(_metrics_df())
        assert fig is not None

    def test_defect_incident_trend(self):
        fig = defect_incident_trend(_metrics_df())
        assert fig is not None

    def test_budget_by_program_bar(self):
        fig = budget_by_program_bar(_programs_df())
        assert fig is not None
        assert len(fig.data) == 2  # Budgeted + Spent traces

    def test_budget_by_status_pie(self):
        fig = budget_by_status_pie(_programs_df())
        assert fig is not None

    def test_budget_utilization_bar(self):
        fig = budget_utilization_bar(_programs_df())
        assert fig is not None
