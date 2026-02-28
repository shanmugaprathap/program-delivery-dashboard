"""Tests for Pydantic models."""

from datetime import date

import pytest
from pydantic import ValidationError

from src.data.models import DeliveryMetric, Milestone, Program, RiskItem
from src.utils.constants import (
    MilestoneStatus,
    ProgramStatus,
    RiskLikelihood,
    RiskSeverity,
)


class TestProgram:
    def test_valid_program(self):
        p = Program(
            id="PRG-999",
            name="Test Program",
            department="Engineering",
            status=ProgramStatus.ON_TRACK,
            percent_complete=50.0,
            start_date=date(2025, 1, 1),
            target_end_date=date(2025, 12, 31),
            owner="Test Owner",
        )
        assert p.name == "Test Program"
        assert p.percent_complete == 50.0

    def test_percent_complete_bounds(self):
        with pytest.raises(ValidationError):
            Program(
                id="PRG-999",
                name="Test",
                department="Eng",
                status=ProgramStatus.ON_TRACK,
                percent_complete=101,
                start_date=date(2025, 1, 1),
                target_end_date=date(2025, 12, 31),
                owner="Test",
            )

    def test_percent_complete_negative(self):
        with pytest.raises(ValidationError):
            Program(
                id="PRG-999",
                name="Test",
                department="Eng",
                status=ProgramStatus.ON_TRACK,
                percent_complete=-1,
                start_date=date(2025, 1, 1),
                target_end_date=date(2025, 12, 31),
                owner="Test",
            )


class TestMilestone:
    def test_valid_milestone(self):
        m = Milestone(
            id="MS-999",
            program_id="PRG-001",
            name="Test Milestone",
            status=MilestoneStatus.IN_PROGRESS,
            due_date=date(2025, 6, 30),
            quarter="Q2 2025",
        )
        assert m.completed_date is None
        assert m.is_key_milestone is False


class TestRiskItem:
    def test_valid_risk(self):
        r = RiskItem(
            id="RSK-999",
            program_id="PRG-001",
            title="Test Risk",
            severity=RiskSeverity.HIGH,
            likelihood=RiskLikelihood.MEDIUM,
            raised_date=date(2025, 3, 15),
        )
        assert r.is_open is True


class TestDeliveryMetric:
    def test_valid_metric(self):
        m = DeliveryMetric(
            program_id="PRG-001",
            week_start=date(2025, 7, 7),
            velocity=45.0,
            deployment_frequency=4.0,
        )
        assert m.defect_count == 0
        assert m.change_failure_rate == 0.0
