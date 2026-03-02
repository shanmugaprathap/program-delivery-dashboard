"""Asana REST API integration for portfolio-based program delivery data.

To enable Asana integration:
1. Set data_source: asana in config/settings.yaml
2. Provide your Asana Personal Access Token in the asana section
3. Set the portfolio_gid from your Asana portfolio URL

Portfolio URL format: https://app.asana.com/0/portfolio/{portfolio_gid}/{project_gid}

This module fetches portfolio projects and their tasks, mapping them to the
dashboard's data models (Program, Milestone, RiskItem, etc.).
"""

from datetime import date, timedelta

import pandas as pd
import requests

from src.utils.config import get_nested
from src.utils.constants import (
    EscalationLevel,
    MilestoneStatus,
    ProgramStatus,
    RiskLikelihood,
    RiskSeverity,
)

_BASE_URL = "https://app.asana.com/api/1.0"


def _get_session() -> tuple[requests.Session, str]:
    """Create an authenticated Asana session and return (session, portfolio_gid)."""
    token = get_nested("asana", "personal_access_token")
    portfolio_gid = get_nested("asana", "portfolio_gid")
    if not token or not portfolio_gid:
        raise ValueError(
            "Asana not configured. Set asana.personal_access_token and "
            "asana.portfolio_gid in config/settings.yaml."
        )
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
    )
    return session, portfolio_gid


def _get(session: requests.Session, path: str, params: dict | None = None) -> dict:
    """Make a GET request to the Asana API."""
    resp = session.get(f"{_BASE_URL}{path}", params=params or {})
    resp.raise_for_status()
    return resp.json()


def _paginate(session: requests.Session, path: str, params: dict | None = None) -> list[dict]:
    """Fetch all pages of a paginated Asana endpoint."""
    params = dict(params or {})
    params.setdefault("limit", 100)
    results = []
    while True:
        data = _get(session, path, params)
        results.extend(data.get("data", []))
        next_page = data.get("next_page")
        if not next_page or not next_page.get("offset"):
            break
        params["offset"] = next_page["offset"]
    return results


def _parse_date(value: str | None) -> date | None:
    """Parse an Asana date string (YYYY-MM-DD) to a Python date."""
    if not value:
        return None
    return date.fromisoformat(value)


def _map_status(status_text: str | None, percent: float) -> ProgramStatus:
    """Map Asana project status to ProgramStatus enum."""
    if percent >= 100:
        return ProgramStatus.COMPLETED
    if not status_text:
        return ProgramStatus.ON_TRACK
    lower = status_text.lower()
    if "off track" in lower:
        return ProgramStatus.OFF_TRACK
    if "at risk" in lower:
        return ProgramStatus.AT_RISK
    return ProgramStatus.ON_TRACK


def _map_milestone_status(task: dict) -> MilestoneStatus:
    """Map an Asana task to a MilestoneStatus."""
    if task.get("completed"):
        return MilestoneStatus.COMPLETED
    assignee_status = task.get("assignee_status", "")
    if assignee_status == "upcoming":
        return MilestoneStatus.NOT_STARTED
    # Check for blocked via dependencies or tags
    for tag in task.get("tags", []):
        tag_name = tag.get("name", "").lower()
        if "blocked" in tag_name:
            return MilestoneStatus.BLOCKED
        if "delayed" in tag_name:
            return MilestoneStatus.DELAYED
    # If due date is past and not completed, mark as delayed
    due = _parse_date(task.get("due_on"))
    if due and due < date.today() and not task.get("completed"):
        return MilestoneStatus.DELAYED
    return MilestoneStatus.IN_PROGRESS


def _task_quarter(task: dict) -> str:
    """Determine the quarter string from a task's due date."""
    due = _parse_date(task.get("due_on"))
    if not due:
        today = date.today()
        q = (today.month - 1) // 3 + 1
        return f"Q{q} {today.year}"
    q = (due.month - 1) // 3 + 1
    return f"Q{q} {due.year}"


def _extract_custom_field(task: dict, field_name: str) -> str | None:
    """Extract a custom field value by name from a task."""
    for field in task.get("custom_fields", []):
        if field.get("name", "").lower() == field_name.lower():
            if field.get("enum_value"):
                return field["enum_value"].get("name")
            if field.get("text_value"):
                return field["text_value"]
            if field.get("number_value") is not None:
                return str(field["number_value"])
            if field.get("display_value"):
                return field["display_value"]
    return None


def _compute_percent_complete(session: requests.Session, project_gid: str) -> float:
    """Compute percent complete from task completion ratio."""
    tasks = _paginate(
        session,
        f"/projects/{project_gid}/tasks",
        params={"opt_fields": "completed"},
    )
    if not tasks:
        return 0.0
    completed = sum(1 for t in tasks if t.get("completed"))
    return round((completed / len(tasks)) * 100, 1)


def fetch_programs() -> pd.DataFrame:
    """Fetch portfolio items (projects) and map to Program model."""
    session, portfolio_gid = _get_session()

    items = _paginate(
        session,
        f"/portfolios/{portfolio_gid}/items",
        params={
            "opt_fields": (
                "name,owner,owner.name,due_on,start_on,"
                "current_status_update,current_status_update.status_type,"
                "current_status_update.text,"
                "custom_fields,custom_fields.name,"
                "custom_fields.enum_value,custom_fields.enum_value.name,"
                "custom_fields.number_value,custom_fields.text_value,"
                "custom_fields.display_value"
            ),
        },
    )

    department_field = get_nested("asana", "department_field", "Department")
    budget_field = get_nested("asana", "budget_field", "Budget")
    budget_spent_field = get_nested("asana", "budget_spent_field", "Budget Spent")

    programs = []
    for idx, item in enumerate(items, 1):
        gid = item["gid"]

        # Get project status from current_status_update
        status_update = item.get("current_status_update") or {}
        status_type = status_update.get("status_type", "")

        # Compute completion percentage from tasks
        percent = _compute_percent_complete(session, gid)

        owner = item.get("owner") or {}
        start = _parse_date(item.get("start_on")) or date.today()
        end = _parse_date(item.get("due_on")) or (date.today() + timedelta(days=180))

        # Extract custom fields for department, budget
        department = _extract_custom_field(item, department_field) or "General"
        budget_str = _extract_custom_field(item, budget_field)
        budget_spent_str = _extract_custom_field(item, budget_spent_field)
        budget = float(budget_str) if budget_str else 0.0
        budget_spent = float(budget_spent_str) if budget_spent_str else 0.0

        description = status_update.get("text", "") or ""

        programs.append(
            {
                "id": f"PRG-{idx:03d}",
                "name": item.get("name", f"Project {idx}"),
                "department": department,
                "status": _map_status(status_type, percent).value,
                "percent_complete": percent,
                "start_date": start,
                "target_end_date": end,
                "owner": owner.get("name", "Unassigned"),
                "description": description,
                "budget_millions": budget,
                "budget_spent_millions": budget_spent,
            }
        )

    if not programs:
        return pd.DataFrame(
            columns=[
                "id", "name", "department", "status", "percent_complete",
                "start_date", "target_end_date", "owner", "description",
                "budget_millions", "budget_spent_millions",
            ]
        )
    return pd.DataFrame(programs)


def _fetch_project_tasks(
    session: requests.Session,
    project_gid: str,
) -> list[dict]:
    """Fetch tasks for a project with relevant fields."""
    return _paginate(
        session,
        f"/projects/{project_gid}/tasks",
        params={
            "opt_fields": (
                "name,completed,completed_at,due_on,assignee,assignee.name,"
                "tags,tags.name,assignee_status,"
                "custom_fields,custom_fields.name,"
                "custom_fields.enum_value,custom_fields.enum_value.name,"
                "custom_fields.number_value,custom_fields.text_value,"
                "custom_fields.display_value,"
                "is_rendered_as_separator"
            ),
        },
    )


def fetch_milestones() -> pd.DataFrame:
    """Fetch tasks from portfolio projects and map to Milestone model.

    By default maps all tasks. If asana.milestone_tag is set in config,
    only tasks with that tag are treated as milestones.
    """
    session, portfolio_gid = _get_session()
    milestone_tag = get_nested("asana", "milestone_tag")

    items = _paginate(
        session,
        f"/portfolios/{portfolio_gid}/items",
        params={"opt_fields": "name"},
    )

    milestones = []
    mid = 0
    for prg_idx, item in enumerate(items, 1):
        project_gid = item["gid"]
        program_id = f"PRG-{prg_idx:03d}"
        tasks = _fetch_project_tasks(session, project_gid)

        for task in tasks:
            # Skip section separators
            if task.get("is_rendered_as_separator"):
                continue

            # If milestone_tag configured, filter by tag
            if milestone_tag:
                tag_names = [t.get("name", "").lower() for t in task.get("tags", [])]
                if milestone_tag.lower() not in tag_names:
                    continue

            mid += 1
            assignee = task.get("assignee") or {}
            due = _parse_date(task.get("due_on"))
            completed_at = task.get("completed_at")
            completed_date = None
            if completed_at:
                completed_date = date.fromisoformat(completed_at[:10])

            # Determine if key milestone from custom field or tag
            is_key = False
            for tag in task.get("tags", []):
                if "key" in tag.get("name", "").lower():
                    is_key = True
                    break

            milestones.append(
                {
                    "id": f"MS-{mid:03d}",
                    "program_id": program_id,
                    "name": task.get("name", ""),
                    "status": _map_milestone_status(task).value,
                    "due_date": due or date.today(),
                    "completed_date": completed_date,
                    "quarter": _task_quarter(task),
                    "owner": assignee.get("name", ""),
                    "is_key_milestone": is_key,
                }
            )

    if not milestones:
        return pd.DataFrame(
            columns=[
                "id", "program_id", "name", "status", "due_date",
                "completed_date", "quarter", "owner", "is_key_milestone",
            ]
        )
    return pd.DataFrame(milestones)


def fetch_risks() -> pd.DataFrame:
    """Fetch tasks tagged as risks from portfolio projects.

    Looks for tasks with a tag matching asana.risk_tag (default: 'risk').
    Risk severity and likelihood are read from custom fields named
    'Severity' and 'Likelihood' (configurable via config).
    """
    session, portfolio_gid = _get_session()
    risk_tag = get_nested("asana", "risk_tag", "risk")
    severity_field = get_nested("asana", "severity_field", "Severity")
    likelihood_field = get_nested("asana", "likelihood_field", "Likelihood")

    items = _paginate(
        session,
        f"/portfolios/{portfolio_gid}/items",
        params={"opt_fields": "name"},
    )

    severity_map = {
        "low": RiskSeverity.LOW,
        "medium": RiskSeverity.MEDIUM,
        "high": RiskSeverity.HIGH,
        "critical": RiskSeverity.CRITICAL,
    }
    likelihood_map = {
        "low": RiskLikelihood.LOW,
        "medium": RiskLikelihood.MEDIUM,
        "high": RiskLikelihood.HIGH,
    }

    risks = []
    rid = 0
    today = date.today()
    for prg_idx, item in enumerate(items, 1):
        project_gid = item["gid"]
        program_id = f"PRG-{prg_idx:03d}"
        tasks = _fetch_project_tasks(session, project_gid)

        for task in tasks:
            tag_names = [t.get("name", "").lower() for t in task.get("tags", [])]
            if risk_tag.lower() not in tag_names:
                continue

            rid += 1
            assignee = task.get("assignee") or {}
            sev_val = (_extract_custom_field(task, severity_field) or "medium").lower()
            lik_val = (_extract_custom_field(task, likelihood_field) or "medium").lower()

            created = _parse_date(task.get("due_on")) or today

            risks.append(
                {
                    "id": f"RSK-{rid:03d}",
                    "program_id": program_id,
                    "title": task.get("name", ""),
                    "description": "",
                    "severity": severity_map.get(sev_val, RiskSeverity.MEDIUM).value,
                    "likelihood": likelihood_map.get(lik_val, RiskLikelihood.MEDIUM).value,
                    "mitigation": "",
                    "owner": assignee.get("name", ""),
                    "raised_date": created,
                    "is_open": not task.get("completed", False),
                    "risk_age_days": (today - created).days,
                }
            )

    if not risks:
        return pd.DataFrame(
            columns=[
                "id", "program_id", "title", "description", "severity",
                "likelihood", "mitigation", "owner", "raised_date",
                "is_open", "risk_age_days",
            ]
        )
    return pd.DataFrame(risks)


def fetch_escalations() -> pd.DataFrame:
    """Fetch tasks tagged as escalations from portfolio projects.

    Looks for tasks with a tag matching asana.escalation_tag (default: 'escalation').
    Escalation level is read from a custom field named 'Escalation Level'.
    """
    session, portfolio_gid = _get_session()
    esc_tag = get_nested("asana", "escalation_tag", "escalation")
    level_field = get_nested("asana", "escalation_level_field", "Escalation Level")

    items = _paginate(
        session,
        f"/portfolios/{portfolio_gid}/items",
        params={"opt_fields": "name"},
    )

    level_map = {
        "team lead": EscalationLevel.TEAM_LEAD,
        "director": EscalationLevel.DIRECTOR,
        "vp": EscalationLevel.VP,
        "c-suite": EscalationLevel.C_SUITE,
    }

    escalations = []
    eid = 0
    for prg_idx, item in enumerate(items, 1):
        project_gid = item["gid"]
        program_id = f"PRG-{prg_idx:03d}"
        tasks = _fetch_project_tasks(session, project_gid)

        for task in tasks:
            tag_names = [t.get("name", "").lower() for t in task.get("tags", [])]
            if esc_tag.lower() not in tag_names:
                continue

            eid += 1
            level_val = (_extract_custom_field(task, level_field) or "director").lower()
            due = _parse_date(task.get("due_on"))
            resolved = None
            if task.get("completed"):
                completed_at = task.get("completed_at")
                if completed_at:
                    resolved = date.fromisoformat(completed_at[:10])

            escalations.append(
                {
                    "id": f"ESC-{eid:03d}",
                    "program_id": program_id,
                    "risk_id": None,
                    "title": task.get("name", ""),
                    "level": level_map.get(level_val, EscalationLevel.DIRECTOR).value,
                    "raised_date": due or date.today(),
                    "resolved_date": resolved,
                    "resolution": "",
                }
            )

    if not escalations:
        return pd.DataFrame(
            columns=[
                "id", "program_id", "risk_id", "title", "level",
                "raised_date", "resolved_date", "resolution",
            ]
        )
    return pd.DataFrame(escalations)


def fetch_metrics() -> pd.DataFrame:
    """Return empty metrics DataFrame — Asana has no native delivery metrics.

    Delivery metrics (velocity, DORA, etc.) are not available in Asana.
    The dashboard will show empty metric charts when using the Asana source.
    Consider supplementing with a CI/CD data source for these metrics.
    """
    return pd.DataFrame(
        columns=[
            "program_id",
            "week_start",
            "velocity",
            "planned_points",
            "delivered_points",
            "defect_count",
            "incident_count",
            "mttr_hours",
            "deployment_frequency",
            "lead_time_days",
            "change_failure_rate",
        ]
    )


def fetch_weekly_snapshots() -> pd.DataFrame:
    """Return empty weekly snapshots — not available from Asana."""
    return pd.DataFrame(
        columns=[
            "week_start",
            "total_velocity",
            "total_defects",
            "total_incidents",
            "avg_mttr_hours",
            "avg_deployment_frequency",
            "avg_lead_time_days",
            "avg_change_failure_rate",
            "programs_on_track",
            "programs_at_risk",
            "programs_off_track",
        ]
    )
