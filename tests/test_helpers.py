"""Tests for utility helper functions."""

from datetime import date

import pandas as pd

from src.utils.constants import (
    MilestoneStatus,
    ProgramStatus,
    RiskLikelihood,
    RiskSeverity,
)
from src.utils.helpers import (
    classify_dora_maturity,
    current_quarter,
    days_until,
    format_delta,
    format_percent_delta,
    generate_decisions,
    percent_change,
    quarter_date_range,
    rag_status,
    risk_score,
)


class TestCurrentQuarter:
    def test_returns_string_format(self):
        q = current_quarter()
        assert q.startswith("Q")
        parts = q.split()
        assert len(parts) == 2
        assert int(parts[0][1]) in range(1, 5)
        assert int(parts[1]) >= 2025


class TestQuarterDateRange:
    def test_q1(self):
        start, end = quarter_date_range("Q1 2026")
        assert start == date(2026, 1, 1)
        assert end == date(2026, 3, 31)

    def test_q4(self):
        start, end = quarter_date_range("Q4 2025")
        assert start == date(2025, 10, 1)
        assert end == date(2025, 12, 31)


class TestRagStatus:
    def test_completed(self):
        assert rag_status(100, 100) == ProgramStatus.COMPLETED

    def test_on_track(self):
        assert rag_status(70, 75) == ProgramStatus.ON_TRACK

    def test_at_risk(self):
        assert rag_status(55, 75) == ProgramStatus.AT_RISK

    def test_off_track(self):
        assert rag_status(40, 75) == ProgramStatus.OFF_TRACK


class TestRiskScore:
    def test_low_low(self):
        assert risk_score(RiskSeverity.LOW, RiskLikelihood.LOW) == 1

    def test_critical_high(self):
        assert risk_score(RiskSeverity.CRITICAL, RiskLikelihood.HIGH) == 12

    def test_medium_medium(self):
        assert risk_score(RiskSeverity.MEDIUM, RiskLikelihood.MEDIUM) == 4


class TestDaysUntil:
    def test_future_date(self):
        future = date(2099, 12, 31)
        assert days_until(future) > 0

    def test_past_date(self):
        past = date(2020, 1, 1)
        assert days_until(past) < 0


class TestFormatDelta:
    def test_today(self):
        assert format_delta(0) == "Today"

    def test_future(self):
        assert format_delta(5) == "In 5 days"

    def test_past(self):
        assert format_delta(-3) == "3 days ago"


class TestPercentChange:
    def test_increase(self):
        assert percent_change(110, 100) == 10.0

    def test_decrease(self):
        assert percent_change(90, 100) == -10.0

    def test_zero_previous(self):
        assert percent_change(100, 0) is None


class TestFormatPercentDelta:
    def test_increase(self):
        result = format_percent_delta(110, 100)
        assert result == "+10.0%"

    def test_decrease(self):
        result = format_percent_delta(90, 100)
        assert result == "-10.0%"

    def test_zero_change(self):
        result = format_percent_delta(100, 100)
        assert result == "0.0%"

    def test_zero_previous(self):
        result = format_percent_delta(100, 0)
        assert result is None


class TestClassifyDoraMaturity:
    def test_elite(self):
        level = classify_dora_maturity(
            deploy_freq=10.0, lead_time=0.5, cfr=3.0, mttr=0.5
        )
        assert level == "Elite"

    def test_low(self):
        level = classify_dora_maturity(
            deploy_freq=0.1, lead_time=60.0, cfr=30.0, mttr=500.0
        )
        assert level == "Low"

    def test_weakest_link(self):
        # Elite on 3 metrics, Low on mttr -> Low overall
        level = classify_dora_maturity(
            deploy_freq=10.0, lead_time=0.5, cfr=3.0, mttr=500.0
        )
        assert level == "Low"

    def test_medium(self):
        level = classify_dora_maturity(
            deploy_freq=0.5, lead_time=15.0, cfr=12.0, mttr=100.0
        )
        assert level == "Medium"


class TestGenerateDecisions:
    def _make_programs_df(self, statuses):
        rows = []
        for i, status in enumerate(statuses):
            rows.append({
                "id": f"PRG-{i:03d}",
                "name": f"Program {i}",
                "status": status.value,
                "percent_complete": 30.0 if status == ProgramStatus.OFF_TRACK else 80.0,
                "department": "Eng",
                "owner": "Owner",
                "start_date": date(2025, 1, 1),
                "target_end_date": date(2026, 1, 1),
                "budget_millions": 1.0,
                "budget_spent_millions": 0.5,
            })
        return pd.DataFrame(rows)

    def _empty_df(self, columns):
        return pd.DataFrame(columns=columns)

    def test_off_track_generates_decision(self):
        programs = self._make_programs_df([ProgramStatus.OFF_TRACK])
        decisions = generate_decisions(
            programs,
            self._empty_df(["severity", "likelihood", "is_open", "title", "program_id"]),
            self._empty_df(["status", "name", "program_id"]),
            self._empty_df(["resolved_date", "raised_date", "title", "program_id"]),
        )
        assert len(decisions) >= 1
        assert decisions[0].severity == "critical"
        assert "off track" in decisions[0].title.lower()

    def test_blocked_milestone_generates_decision(self):
        programs = self._make_programs_df([ProgramStatus.ON_TRACK])
        milestones = pd.DataFrame([{
            "status": MilestoneStatus.BLOCKED.value,
            "name": "Blocked Task",
            "program_id": "PRG-000",
        }])
        decisions = generate_decisions(
            programs,
            self._empty_df(["severity", "likelihood", "is_open", "title", "program_id"]),
            milestones,
            self._empty_df(["resolved_date", "raised_date", "title", "program_id"]),
        )
        assert any("Blocked" in d.title for d in decisions)

    def test_clean_state_empty(self):
        programs = self._make_programs_df([ProgramStatus.ON_TRACK])
        decisions = generate_decisions(
            programs,
            self._empty_df(["severity", "likelihood", "is_open", "title", "program_id"]),
            self._empty_df(["status", "name", "program_id"]),
            self._empty_df(["resolved_date", "raised_date", "title", "program_id"]),
        )
        assert len(decisions) == 0
