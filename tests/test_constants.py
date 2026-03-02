"""Tests for constants module."""

from datetime import date

from src.utils.constants import QUARTERS, compute_quarters


class TestComputeQuarters:
    def test_empty_returns_default(self):
        result = compute_quarters([])
        assert result == list(QUARTERS)

    def test_single_date(self):
        result = compute_quarters([date(2025, 3, 15)])
        assert result == ["Q1 2025"]

    def test_multiple_dates_sorted(self):
        dates = [date(2025, 10, 1), date(2025, 3, 15), date(2026, 1, 5)]
        result = compute_quarters(dates)
        assert result == ["Q1 2025", "Q4 2025", "Q1 2026"]
