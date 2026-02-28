"""Realistic mock data generator for 6 programs with correlated milestones, risks, and metrics."""

import random
from datetime import date, timedelta

from src.data.models import (
    DeliveryMetric,
    Escalation,
    Milestone,
    Program,
    RiskItem,
    WeeklySnapshot,
)
from src.utils.constants import (
    EscalationLevel,
    MilestoneStatus,
    ProgramStatus,
    RiskLikelihood,
    RiskSeverity,
)

SEED = 42


def _seed():
    random.seed(SEED)


# ---------------------------------------------------------------------------
# Programs
# ---------------------------------------------------------------------------

PROGRAMS = [
    Program(
        id="PRG-001",
        name="Cloud Platform Migration",
        department="Cloud Engineering",
        status=ProgramStatus.ON_TRACK,
        percent_complete=72,
        start_date=date(2025, 4, 1),
        target_end_date=date(2026, 6, 30),
        owner="Priya Sharma",
        description="Migrate legacy on-prem services to AWS/GCP hybrid cloud.",
        budget_millions=4.2,
    ),
    Program(
        id="PRG-002",
        name="SRE Observability Rollout",
        department="SRE",
        status=ProgramStatus.ON_TRACK,
        percent_complete=85,
        start_date=date(2025, 1, 15),
        target_end_date=date(2026, 3, 31),
        owner="James Chen",
        description=(
            "Deploy unified observability stack (metrics, logs, traces) across all services."
        ),
        budget_millions=2.1,
    ),
    Program(
        id="PRG-003",
        name="Zero Trust Security",
        department="Security",
        status=ProgramStatus.AT_RISK,
        percent_complete=45,
        start_date=date(2025, 3, 1),
        target_end_date=date(2026, 5, 31),
        owner="Maria Lopez",
        description=(
            "Implement zero-trust architecture with mTLS, IAM overhaul, and microsegmentation."
        ),
        budget_millions=3.5,
    ),
    Program(
        id="PRG-004",
        name="API Gateway Modernization",
        department="Platform",
        status=ProgramStatus.ON_TRACK,
        percent_complete=60,
        start_date=date(2025, 6, 1),
        target_end_date=date(2026, 8, 31),
        owner="Alex Kim",
        description="Replace legacy API gateway with Kong/Envoy-based solution.",
        budget_millions=1.8,
    ),
    Program(
        id="PRG-005",
        name="Disaster Recovery Automation",
        department="SRE",
        status=ProgramStatus.OFF_TRACK,
        percent_complete=30,
        start_date=date(2025, 5, 1),
        target_end_date=date(2026, 4, 30),
        owner="David Okonkwo",
        description="Automate DR runbooks and achieve <4hr RTO for Tier-1 services.",
        budget_millions=2.8,
    ),
    Program(
        id="PRG-006",
        name="Data Platform Consolidation",
        department="Data Engineering",
        status=ProgramStatus.COMPLETED,
        percent_complete=100,
        start_date=date(2025, 1, 1),
        target_end_date=date(2025, 12, 31),
        owner="Sarah Tanaka",
        description="Consolidate Redshift, BigQuery, and Snowflake into unified lakehouse.",
        budget_millions=3.0,
    ),
]


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------


def _generate_milestones() -> list[Milestone]:
    _seed()
    milestones = []
    mid = 0

    program_milestones = {
        "PRG-001": [
            ("Network architecture design", "Q2 2025", True, MilestoneStatus.COMPLETED),
            ("VPC peering setup", "Q2 2025", False, MilestoneStatus.COMPLETED),
            ("Dev environment migration", "Q3 2025", True, MilestoneStatus.COMPLETED),
            ("Staging environment migration", "Q4 2025", True, MilestoneStatus.COMPLETED),
            ("Database replication cutover", "Q4 2025", False, MilestoneStatus.COMPLETED),
            ("Production Tier-2 migration", "Q1 2026", True, MilestoneStatus.IN_PROGRESS),
            ("Production Tier-1 migration", "Q2 2026", True, MilestoneStatus.NOT_STARTED),
            ("Decommission legacy infra", "Q2 2026", False, MilestoneStatus.NOT_STARTED),
        ],
        "PRG-002": [
            ("Metrics pipeline MVP", "Q1 2025", True, MilestoneStatus.COMPLETED),
            ("Log aggregation rollout", "Q2 2025", True, MilestoneStatus.COMPLETED),
            ("Distributed tracing integration", "Q3 2025", True, MilestoneStatus.COMPLETED),
            ("Alerting rules migration", "Q3 2025", False, MilestoneStatus.COMPLETED),
            ("SLO dashboards for Tier-1", "Q4 2025", True, MilestoneStatus.COMPLETED),
            ("On-call runbook automation", "Q1 2026", False, MilestoneStatus.COMPLETED),
            ("Full observability coverage", "Q1 2026", True, MilestoneStatus.IN_PROGRESS),
        ],
        "PRG-003": [
            ("IAM audit & gap analysis", "Q1 2025", True, MilestoneStatus.COMPLETED),
            ("mTLS for internal services", "Q2 2025", True, MilestoneStatus.COMPLETED),
            ("Identity provider migration", "Q3 2025", True, MilestoneStatus.DELAYED),
            ("Microsegmentation Phase 1", "Q4 2025", True, MilestoneStatus.IN_PROGRESS),
            ("Endpoint detection rollout", "Q1 2026", False, MilestoneStatus.NOT_STARTED),
            ("Microsegmentation Phase 2", "Q1 2026", True, MilestoneStatus.NOT_STARTED),
            ("Compliance certification", "Q2 2026", True, MilestoneStatus.NOT_STARTED),
        ],
        "PRG-004": [
            ("API inventory & mapping", "Q3 2025", True, MilestoneStatus.COMPLETED),
            ("Kong gateway POC", "Q3 2025", False, MilestoneStatus.COMPLETED),
            ("Internal API migration", "Q4 2025", True, MilestoneStatus.COMPLETED),
            ("Partner API migration", "Q1 2026", True, MilestoneStatus.IN_PROGRESS),
            ("Rate limiting & throttling", "Q1 2026", False, MilestoneStatus.IN_PROGRESS),
            ("Public API migration", "Q2 2026", True, MilestoneStatus.NOT_STARTED),
            ("Legacy gateway decommission", "Q3 2026", False, MilestoneStatus.NOT_STARTED),
        ],
        "PRG-005": [
            ("DR runbook audit", "Q2 2025", True, MilestoneStatus.COMPLETED),
            ("Automated failover POC", "Q3 2025", True, MilestoneStatus.DELAYED),
            ("Tier-1 DR automation", "Q4 2025", True, MilestoneStatus.BLOCKED),
            ("DR testing framework", "Q1 2026", False, MilestoneStatus.NOT_STARTED),
            ("Cross-region replication", "Q1 2026", True, MilestoneStatus.NOT_STARTED),
            ("Full DR drill execution", "Q2 2026", True, MilestoneStatus.NOT_STARTED),
        ],
        "PRG-006": [
            ("Data source inventory", "Q1 2025", True, MilestoneStatus.COMPLETED),
            ("Lakehouse architecture", "Q1 2025", True, MilestoneStatus.COMPLETED),
            ("ETL pipeline migration", "Q2 2025", True, MilestoneStatus.COMPLETED),
            ("Data quality framework", "Q3 2025", True, MilestoneStatus.COMPLETED),
            ("Self-service analytics", "Q3 2025", False, MilestoneStatus.COMPLETED),
            ("Legacy warehouse decommission", "Q4 2025", True, MilestoneStatus.COMPLETED),
            ("Cost optimization review", "Q4 2025", False, MilestoneStatus.COMPLETED),
        ],
    }

    for pid, ms_list in program_milestones.items():
        for name, quarter, is_key, status in ms_list:
            mid += 1
            q_num = int(quarter[1])
            year = int(quarter.split()[1])
            base_month = (q_num - 1) * 3 + 1
            due = date(year, base_month, 1) + timedelta(days=random.randint(15, 75))
            completed = None
            if status == MilestoneStatus.COMPLETED:
                completed = due - timedelta(days=random.randint(-5, 10))
            elif status == MilestoneStatus.DELAYED:
                completed = None

            milestones.append(
                Milestone(
                    id=f"MS-{mid:03d}",
                    program_id=pid,
                    name=name,
                    status=status,
                    due_date=due,
                    completed_date=completed,
                    quarter=quarter,
                    owner=random.choice(
                        ["Priya", "James", "Maria", "Alex", "David", "Sarah", "Li", "Kumar"]
                    ),
                    is_key_milestone=is_key,
                )
            )
    return milestones


# ---------------------------------------------------------------------------
# Risks
# ---------------------------------------------------------------------------


def _generate_risks() -> list[RiskItem]:
    _seed()
    risks_data = [
        ("PRG-001", "Cloud vendor lock-in", RiskSeverity.HIGH, RiskLikelihood.MEDIUM, True),
        (
            "PRG-001",
            "Data transfer costs exceed budget",
            RiskSeverity.MEDIUM,
            RiskLikelihood.HIGH,
            True,
        ),
        (
            "PRG-001",
            "Skill gap in cloud-native tooling",
            RiskSeverity.MEDIUM,
            RiskLikelihood.LOW,
            False,
        ),
        (
            "PRG-002",
            "Alert fatigue from noisy rules",
            RiskSeverity.MEDIUM,
            RiskLikelihood.HIGH,
            True,
        ),
        (
            "PRG-002",
            "Tracing overhead on latency-sensitive services",
            RiskSeverity.LOW,
            RiskLikelihood.MEDIUM,
            False,
        ),
        (
            "PRG-003",
            "mTLS certificate rotation failures",
            RiskSeverity.CRITICAL,
            RiskLikelihood.MEDIUM,
            True,
        ),
        (
            "PRG-003",
            "Legacy apps incompatible with zero-trust",
            RiskSeverity.HIGH,
            RiskLikelihood.HIGH,
            True,
        ),
        (
            "PRG-003",
            "Vendor delay on IdP integration",
            RiskSeverity.HIGH,
            RiskLikelihood.MEDIUM,
            True,
        ),
        (
            "PRG-004",
            "Breaking changes to partner APIs",
            RiskSeverity.HIGH,
            RiskLikelihood.MEDIUM,
            True,
        ),
        (
            "PRG-004",
            "Rate limiting misconfiguration",
            RiskSeverity.MEDIUM,
            RiskLikelihood.LOW,
            False,
        ),
        (
            "PRG-005",
            "Cross-region latency exceeds RTO",
            RiskSeverity.CRITICAL,
            RiskLikelihood.HIGH,
            True,
        ),
        (
            "PRG-005",
            "DR testing impacts production",
            RiskSeverity.HIGH,
            RiskLikelihood.MEDIUM,
            True,
        ),
        (
            "PRG-005",
            "Incomplete runbook documentation",
            RiskSeverity.MEDIUM,
            RiskLikelihood.HIGH,
            True,
        ),
        ("PRG-006", "Data loss during migration", RiskSeverity.CRITICAL, RiskLikelihood.LOW, False),
    ]
    risks = []
    for i, (pid, title, sev, lik, is_open) in enumerate(risks_data, 1):
        risks.append(
            RiskItem(
                id=f"RSK-{i:03d}",
                program_id=pid,
                title=title,
                severity=sev,
                likelihood=lik,
                mitigation=f"Mitigation plan documented in confluence for {title.lower()}.",
                owner=random.choice(["Priya", "James", "Maria", "Alex", "David", "Sarah"]),
                raised_date=date(2025, 1, 1) + timedelta(days=random.randint(0, 300)),
                is_open=is_open,
            )
        )
    return risks


# ---------------------------------------------------------------------------
# Escalations
# ---------------------------------------------------------------------------


def _generate_escalations() -> list[Escalation]:
    return [
        Escalation(
            id="ESC-001",
            program_id="PRG-003",
            risk_id="RSK-007",
            title="Legacy app compatibility blocking zero-trust rollout",
            level=EscalationLevel.VP,
            raised_date=date(2025, 9, 15),
            resolved_date=None,
        ),
        Escalation(
            id="ESC-002",
            program_id="PRG-005",
            risk_id="RSK-011",
            title="DR automation blocked by cross-region infra gaps",
            level=EscalationLevel.DIRECTOR,
            raised_date=date(2025, 10, 1),
            resolved_date=None,
        ),
        Escalation(
            id="ESC-003",
            program_id="PRG-003",
            risk_id="RSK-008",
            title="IdP vendor missing contractual delivery date",
            level=EscalationLevel.DIRECTOR,
            raised_date=date(2025, 11, 10),
            resolved_date=date(2025, 12, 20),
            resolution="Vendor allocated dedicated engineering team; revised timeline accepted.",
        ),
        Escalation(
            id="ESC-004",
            program_id="PRG-001",
            risk_id="RSK-002",
            title="Cloud data transfer costs 40% over budget",
            level=EscalationLevel.DIRECTOR,
            raised_date=date(2026, 1, 5),
            resolved_date=date(2026, 1, 25),
            resolution="Negotiated committed use discounts; revised budget approved.",
        ),
        Escalation(
            id="ESC-005",
            program_id="PRG-005",
            risk_id="RSK-011",
            title="RTO target unachievable with current architecture",
            level=EscalationLevel.VP,
            raised_date=date(2026, 2, 1),
            resolved_date=None,
        ),
    ]


# ---------------------------------------------------------------------------
# Delivery Metrics (weekly, per program)
# ---------------------------------------------------------------------------


def _generate_metrics() -> list[DeliveryMetric]:
    _seed()
    metrics = []
    start = date(2025, 7, 7)  # Start tracking from Q3 2025
    num_weeks = 34  # ~8 months of data

    program_profiles = {
        "PRG-001": {"velocity_base": 45, "defect_base": 3, "deploy_freq": 4.0, "lead_time": 2.5},
        "PRG-002": {"velocity_base": 38, "defect_base": 2, "deploy_freq": 8.0, "lead_time": 1.0},
        "PRG-003": {"velocity_base": 25, "defect_base": 5, "deploy_freq": 2.0, "lead_time": 5.0},
        "PRG-004": {"velocity_base": 32, "defect_base": 3, "deploy_freq": 5.0, "lead_time": 2.0},
        "PRG-005": {"velocity_base": 18, "defect_base": 4, "deploy_freq": 1.5, "lead_time": 7.0},
        "PRG-006": {"velocity_base": 40, "defect_base": 1, "deploy_freq": 6.0, "lead_time": 1.5},
    }

    for pid, prof in program_profiles.items():
        for w in range(num_weeks):
            week = start + timedelta(weeks=w)
            noise = random.uniform(0.8, 1.2)
            trend = 1 + (w * 0.005)  # Slight upward trend

            velocity = round(prof["velocity_base"] * noise * trend, 1)
            planned = round(velocity * random.uniform(0.9, 1.15), 1)
            delivered = round(velocity * random.uniform(0.85, 1.05), 1)
            defects = max(0, int(prof["defect_base"] * noise + random.randint(-2, 2)))
            incidents = max(0, random.randint(0, max(1, defects // 2)))
            mttr = round(random.uniform(0.5, 4.0), 1)
            deploy_freq = round(prof["deploy_freq"] * noise, 1)
            lead_time = round(prof["lead_time"] * random.uniform(0.7, 1.3), 1)
            cfr = round(random.uniform(2, 18), 1)

            metrics.append(
                DeliveryMetric(
                    program_id=pid,
                    week_start=week,
                    velocity=velocity,
                    planned_points=planned,
                    delivered_points=delivered,
                    defect_count=defects,
                    incident_count=incidents,
                    mttr_hours=mttr,
                    deployment_frequency=deploy_freq,
                    lead_time_days=lead_time,
                    change_failure_rate=cfr,
                )
            )
    return metrics


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_programs() -> list[Program]:
    return PROGRAMS


def get_milestones() -> list[Milestone]:
    return _generate_milestones()


def get_risks() -> list[RiskItem]:
    return _generate_risks()


def get_escalations() -> list[Escalation]:
    return _generate_escalations()


def get_metrics() -> list[DeliveryMetric]:
    return _generate_metrics()


def get_weekly_snapshots() -> list[WeeklySnapshot]:
    """Aggregate per-program metrics into weekly snapshots."""
    metrics = get_metrics()
    programs = get_programs()
    weeks: dict[date, list[DeliveryMetric]] = {}
    for m in metrics:
        weeks.setdefault(m.week_start, []).append(m)

    status_counts = {}
    for p in programs:
        status_counts[p.status] = status_counts.get(p.status, 0) + 1

    snapshots = []
    for week, week_metrics in sorted(weeks.items()):
        n = len(week_metrics)
        snapshots.append(
            WeeklySnapshot(
                week_start=week,
                total_velocity=round(sum(m.velocity for m in week_metrics), 1),
                total_defects=sum(m.defect_count for m in week_metrics),
                total_incidents=sum(m.incident_count for m in week_metrics),
                avg_mttr_hours=round(sum(m.mttr_hours for m in week_metrics) / n, 1),
                avg_deployment_frequency=round(
                    sum(m.deployment_frequency for m in week_metrics) / n, 1
                ),
                avg_lead_time_days=round(sum(m.lead_time_days for m in week_metrics) / n, 1),
                avg_change_failure_rate=round(
                    sum(m.change_failure_rate for m in week_metrics) / n, 1
                ),
                programs_on_track=status_counts.get(ProgramStatus.ON_TRACK, 0),
                programs_at_risk=status_counts.get(ProgramStatus.AT_RISK, 0),
                programs_off_track=status_counts.get(ProgramStatus.OFF_TRACK, 0),
            )
        )
    return snapshots
