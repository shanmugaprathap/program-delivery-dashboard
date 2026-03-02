"""Date utilities, RAG calculations, and helper functions."""

from dataclasses import dataclass
from datetime import date, timedelta

from src.utils.constants import (
    DORA_BENCHMARKS,
    MilestoneStatus,
    ProgramStatus,
    RiskLikelihood,
    RiskSeverity,
)


def current_quarter() -> str:
    """Return the current quarter string, e.g. 'Q1 2026'."""
    today = date.today()
    q = (today.month - 1) // 3 + 1
    return f"Q{q} {today.year}"


def quarter_date_range(quarter: str) -> tuple[date, date]:
    """Return (start, end) dates for a quarter string like 'Q1 2026'."""
    q, year = quarter.split()
    q_num = int(q[1])
    year = int(year)
    start_month = (q_num - 1) * 3 + 1
    start = date(year, start_month, 1)
    if q_num == 4:
        end = date(year, 12, 31)
    else:
        end = date(year, start_month + 3, 1) - timedelta(days=1)
    return start, end


def rag_status(percent_complete: float, target_percent: float) -> ProgramStatus:
    """Determine RAG status based on completion vs target.

    - On Track: within 10% of target
    - At Risk: 10-25% behind target
    - Off Track: >25% behind target
    - Completed: 100%
    """
    if percent_complete >= 100:
        return ProgramStatus.COMPLETED
    gap = target_percent - percent_complete
    if gap <= 10:
        return ProgramStatus.ON_TRACK
    elif gap <= 25:
        return ProgramStatus.AT_RISK
    else:
        return ProgramStatus.OFF_TRACK


def risk_score(severity: RiskSeverity, likelihood: RiskLikelihood) -> int:
    """Calculate numeric risk score (1-16) from severity and likelihood."""
    severity_map = {
        RiskSeverity.LOW: 1,
        RiskSeverity.MEDIUM: 2,
        RiskSeverity.HIGH: 3,
        RiskSeverity.CRITICAL: 4,
    }
    likelihood_map = {
        RiskLikelihood.LOW: 1,
        RiskLikelihood.MEDIUM: 2,
        RiskLikelihood.HIGH: 3,
    }
    return severity_map[severity] * likelihood_map[likelihood]


def days_until(target: date) -> int:
    """Return days from today until target date (negative if past)."""
    return (target - date.today()).days


def format_delta(days: int) -> str:
    """Format a day delta as a human-readable string."""
    if days == 0:
        return "Today"
    elif days > 0:
        return f"In {days} days"
    else:
        return f"{abs(days)} days ago"


def percent_change(current: float, previous: float) -> float | None:
    """Calculate percent change. Returns None if previous is zero."""
    if previous == 0:
        return None
    return ((current - previous) / previous) * 100


def format_percent_delta(current: float, previous: float) -> str | None:
    """Format percent change as a signed string like '+5.2%' or '-3.1%'.

    Returns None if previous is zero.
    """
    change = percent_change(current, previous)
    if change is None:
        return None
    if abs(change) < 1e-9:
        return "0.0%"
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}%"


# ---------------------------------------------------------------------------
# DORA Maturity Classification
# ---------------------------------------------------------------------------


def classify_dora_maturity(
    deploy_freq: float,
    lead_time: float,
    cfr: float,
    mttr: float,
) -> str:
    """Classify DORA maturity level using weakest-link approach.

    Returns one of: 'Elite', 'High', 'Medium', 'Low'.
    """
    benchmarks = DORA_BENCHMARKS

    def _classify_metric(value: float, metric: str, higher_is_better: bool) -> str:
        thresholds = benchmarks[metric]
        if higher_is_better:
            if value >= thresholds["elite"]:
                return "Elite"
            elif value >= thresholds["high"]:
                return "High"
            elif value >= thresholds["medium"]:
                return "Medium"
            else:
                return "Low"
        else:
            if value <= thresholds["elite"]:
                return "Elite"
            elif value <= thresholds["high"]:
                return "High"
            elif value <= thresholds["medium"]:
                return "Medium"
            else:
                return "Low"

    levels = [
        _classify_metric(deploy_freq, "deployment_frequency", higher_is_better=True),
        _classify_metric(lead_time, "lead_time_days", higher_is_better=False),
        _classify_metric(cfr, "change_failure_rate", higher_is_better=False),
        _classify_metric(mttr, "mttr_hours", higher_is_better=False),
    ]

    rank = {"Elite": 3, "High": 2, "Medium": 1, "Low": 0}
    weakest = min(levels, key=lambda lvl: rank[lvl])
    return weakest


# ---------------------------------------------------------------------------
# Decisions Engine
# ---------------------------------------------------------------------------


@dataclass
class DecisionItem:
    """An actionable decision for leadership."""

    severity: str  # "critical", "high", "medium"
    program: str
    title: str
    recommendation: str


def generate_decisions(
    programs_df,
    risks_df,
    milestones_df,
    escalations_df,
) -> list[DecisionItem]:
    """Generate actionable decisions from current data.

    Rules:
    - OFF_TRACK programs -> "Re-scope or add resources"
    - Open escalations >30 days -> "Escalate to next level"
    - CRITICAL+HIGH likelihood risks -> "Accept, mitigate, or transfer"
    - BLOCKED milestones -> "Unblock milestone"
    """
    decisions = []
    today = date.today()

    # OFF_TRACK programs
    off_track = programs_df[programs_df["status"] == ProgramStatus.OFF_TRACK.value]
    for _, row in off_track.iterrows():
        decisions.append(
            DecisionItem(
                severity="critical",
                program=row["name"],
                title=f"{row['name']} is off track at {row['percent_complete']:.0f}%",
                recommendation="Re-scope deliverables or add resources",
            )
        )

    # CRITICAL severity + HIGH likelihood open risks
    if not risks_df.empty:
        critical_risks = risks_df[
            (risks_df["is_open"] == True)
            & (risks_df["severity"] == RiskSeverity.CRITICAL.value)
            & (risks_df["likelihood"] == RiskLikelihood.HIGH.value)
        ]
        for _, row in critical_risks.iterrows():
            prog_name = row.get("program_id", "Unknown")
            decisions.append(
                DecisionItem(
                    severity="critical",
                    program=prog_name,
                    title=f"Critical risk: {row['title']}",
                    recommendation="Accept, mitigate, or transfer risk",
                )
            )

    # Open escalations > 30 days
    if not escalations_df.empty:
        open_esc = escalations_df[escalations_df["resolved_date"].isna()].copy()
        for _, row in open_esc.iterrows():
            raised = row["raised_date"]
            if hasattr(raised, "date"):
                raised = raised.date()
            age = (today - raised).days
            if age > 30:
                decisions.append(
                    DecisionItem(
                        severity="high",
                        program=row.get("program_id", "Unknown"),
                        title=f"Escalation open {age} days: {row['title']}",
                        recommendation="Escalate to next level",
                    )
                )

    # BLOCKED milestones
    if not milestones_df.empty:
        blocked = milestones_df[milestones_df["status"] == MilestoneStatus.BLOCKED.value]
        for _, row in blocked.iterrows():
            decisions.append(
                DecisionItem(
                    severity="high",
                    program=row.get("program_id", "Unknown"),
                    title=f"Blocked milestone: {row['name']}",
                    recommendation=f"Unblock milestone for {row.get('program_id', 'program')}",
                )
            )

    # Sort by severity
    severity_rank = {"critical": 0, "high": 1, "medium": 2}
    decisions.sort(key=lambda d: severity_rank.get(d.severity, 3))

    return decisions
