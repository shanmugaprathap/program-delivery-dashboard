"""Tests for utility helper functions."""

from datetime import date

from src.utils.constants import ProgramStatus, RiskLikelihood, RiskSeverity
from src.utils.helpers import (
    current_quarter,
    days_until,
    format_delta,
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
