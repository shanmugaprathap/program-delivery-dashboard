"""Color palette, status enums, and shared constants."""

from enum import Enum


class ProgramStatus(str, Enum):
    ON_TRACK = "On Track"
    AT_RISK = "At Risk"
    OFF_TRACK = "Off Track"
    COMPLETED = "Completed"


class RiskSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RiskLikelihood(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class MilestoneStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    DELAYED = "Delayed"
    BLOCKED = "Blocked"


class EscalationLevel(str, Enum):
    TEAM_LEAD = "Team Lead"
    DIRECTOR = "Director"
    VP = "VP"
    C_SUITE = "C-Suite"


# Professional muted color palette
STATUS_COLORS = {
    ProgramStatus.ON_TRACK: "#2E8B57",
    ProgramStatus.AT_RISK: "#D4A017",
    ProgramStatus.OFF_TRACK: "#C0392B",
    ProgramStatus.COMPLETED: "#5B7DB1",
}

SEVERITY_COLORS = {
    RiskSeverity.LOW: "#5B7DB1",
    RiskSeverity.MEDIUM: "#D4A017",
    RiskSeverity.HIGH: "#E67E22",
    RiskSeverity.CRITICAL: "#C0392B",
}

MILESTONE_COLORS = {
    MilestoneStatus.NOT_STARTED: "#95A5A6",
    MilestoneStatus.IN_PROGRESS: "#1B6AC9",
    MilestoneStatus.COMPLETED: "#2E8B57",
    MilestoneStatus.DELAYED: "#D4A017",
    MilestoneStatus.BLOCKED: "#C0392B",
}

# Chart palette
CHART_PALETTE = [
    "#1B6AC9",  # Primary blue
    "#2E8B57",  # Green
    "#D4A017",  # Amber
    "#C0392B",  # Red
    "#8E44AD",  # Purple
    "#E67E22",  # Orange
    "#16A085",  # Teal
    "#5B7DB1",  # Steel blue
]

QUARTERS = ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025", "Q1 2026"]

DEPARTMENTS = [
    "Cloud Engineering",
    "SRE",
    "Security",
    "Platform",
    "Data Engineering",
]
