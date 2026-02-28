"""Date utilities, RAG calculations, and helper functions."""

from datetime import date, timedelta

from src.utils.constants import ProgramStatus, RiskLikelihood, RiskSeverity


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
