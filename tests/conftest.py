"""Shared test fixtures."""

import pytest

from src.data.mock_data import (
    get_escalations,
    get_metrics,
    get_milestones,
    get_programs,
    get_risks,
    get_weekly_snapshots,
)


@pytest.fixture
def programs():
    return get_programs()


@pytest.fixture
def milestones():
    return get_milestones()


@pytest.fixture
def risks():
    return get_risks()


@pytest.fixture
def escalations():
    return get_escalations()


@pytest.fixture
def metrics():
    return get_metrics()


@pytest.fixture
def weekly_snapshots():
    return get_weekly_snapshots()
