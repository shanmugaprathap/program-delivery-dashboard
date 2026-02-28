"""Pydantic models for program delivery data."""

from datetime import date

from pydantic import BaseModel, Field

from src.utils.constants import (
    EscalationLevel,
    MilestoneStatus,
    ProgramStatus,
    RiskLikelihood,
    RiskSeverity,
)


class Program(BaseModel):
    id: str
    name: str
    department: str
    status: ProgramStatus
    percent_complete: float = Field(ge=0, le=100)
    start_date: date
    target_end_date: date
    owner: str
    description: str = ""
    budget_millions: float = 0.0


class Milestone(BaseModel):
    id: str
    program_id: str
    name: str
    status: MilestoneStatus
    due_date: date
    completed_date: date | None = None
    quarter: str
    owner: str = ""
    is_key_milestone: bool = False


class RiskItem(BaseModel):
    id: str
    program_id: str
    title: str
    description: str = ""
    severity: RiskSeverity
    likelihood: RiskLikelihood
    mitigation: str = ""
    owner: str = ""
    raised_date: date
    is_open: bool = True


class Escalation(BaseModel):
    id: str
    program_id: str
    risk_id: str | None = None
    title: str
    level: EscalationLevel
    raised_date: date
    resolved_date: date | None = None
    resolution: str = ""


class DeliveryMetric(BaseModel):
    """Weekly snapshot of delivery metrics for a program."""

    program_id: str
    week_start: date
    velocity: float = 0.0
    planned_points: float = 0.0
    delivered_points: float = 0.0
    defect_count: int = 0
    incident_count: int = 0
    mttr_hours: float = 0.0  # Mean Time To Recover
    deployment_frequency: float = 0.0  # Deploys per week
    lead_time_days: float = 0.0  # Commit to deploy
    change_failure_rate: float = 0.0  # Percentage


class WeeklySnapshot(BaseModel):
    """Aggregated weekly snapshot across all programs."""

    week_start: date
    total_velocity: float = 0.0
    total_defects: int = 0
    total_incidents: int = 0
    avg_mttr_hours: float = 0.0
    avg_deployment_frequency: float = 0.0
    avg_lead_time_days: float = 0.0
    avg_change_failure_rate: float = 0.0
    programs_on_track: int = 0
    programs_at_risk: int = 0
    programs_off_track: int = 0
