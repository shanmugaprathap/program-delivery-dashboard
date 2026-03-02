"""Tests for mock data consistency and completeness."""


class TestPrograms:
    def test_six_programs(self, programs):
        assert len(programs) == 6

    def test_unique_ids(self, programs):
        ids = [p.id for p in programs]
        assert len(ids) == len(set(ids))

    def test_completed_program_at_100(self, programs):
        for p in programs:
            if p.status.value == "Completed":
                assert p.percent_complete == 100

    def test_all_have_owners(self, programs):
        for p in programs:
            assert p.owner

    def test_budget_spent_set(self, programs):
        """All programs should have budget_spent_millions > 0."""
        for p in programs:
            assert p.budget_spent_millions > 0
            assert p.budget_millions > 0

    def test_budget_correlation(self, programs):
        """OFF_TRACK programs should have higher budget utilization ratio."""
        for p in programs:
            utilization = p.budget_spent_millions / p.budget_millions
            if p.status.value == "Off Track":
                # Off-track should be significantly overspending relative to completion
                completion_ratio = p.percent_complete / 100
                assert utilization > completion_ratio * 1.2


class TestMilestones:
    def test_milestones_generated(self, milestones):
        assert len(milestones) > 30

    def test_all_linked_to_programs(self, milestones, programs):
        program_ids = {p.id for p in programs}
        for m in milestones:
            assert m.program_id in program_ids

    def test_completed_have_date(self, milestones):
        for m in milestones:
            if m.status.value == "Completed":
                assert m.completed_date is not None

    def test_reproducible(self, milestones):
        """Running generator again produces the same data (seed=42)."""
        from src.data.mock_data import get_milestones

        second_run = get_milestones()
        assert len(milestones) == len(second_run)
        for a, b in zip(milestones, second_run):
            assert a.id == b.id
            assert a.name == b.name


class TestRisks:
    def test_risks_generated(self, risks):
        assert len(risks) > 10

    def test_all_linked_to_programs(self, risks, programs):
        program_ids = {p.id for p in programs}
        for r in risks:
            assert r.program_id in program_ids


class TestMetrics:
    def test_metrics_generated(self, metrics):
        assert len(metrics) > 100

    def test_all_linked_to_programs(self, metrics, programs):
        program_ids = {p.id for p in programs}
        for m in metrics:
            assert m.program_id in program_ids

    def test_no_negative_velocity(self, metrics):
        for m in metrics:
            assert m.velocity >= 0

    def test_cfr_correlation(self, metrics):
        """OFF_TRACK programs should have higher average CFR than ON_TRACK."""
        from src.utils.constants import ProgramStatus
        from src.data.mock_data import PROGRAMS

        on_track_ids = {p.id for p in PROGRAMS if p.status == ProgramStatus.ON_TRACK}
        off_track_ids = {p.id for p in PROGRAMS if p.status == ProgramStatus.OFF_TRACK}

        on_track_cfr = [m.change_failure_rate for m in metrics if m.program_id in on_track_ids]
        off_track_cfr = [m.change_failure_rate for m in metrics if m.program_id in off_track_ids]

        if on_track_cfr and off_track_cfr:
            avg_on = sum(on_track_cfr) / len(on_track_cfr)
            avg_off = sum(off_track_cfr) / len(off_track_cfr)
            assert avg_off > avg_on

    def test_off_track_degrading_velocity(self, metrics):
        """OFF_TRACK programs should show declining velocity trend."""
        off_track_metrics = [m for m in metrics if m.program_id == "PRG-005"]
        if len(off_track_metrics) >= 10:
            first_half = off_track_metrics[: len(off_track_metrics) // 2]
            second_half = off_track_metrics[len(off_track_metrics) // 2 :]
            avg_first = sum(m.velocity for m in first_half) / len(first_half)
            avg_second = sum(m.velocity for m in second_half) / len(second_half)
            assert avg_second < avg_first


class TestWeeklySnapshots:
    def test_snapshots_generated(self, weekly_snapshots):
        assert len(weekly_snapshots) > 20

    def test_sorted_by_week(self, weekly_snapshots):
        weeks = [s.week_start for s in weekly_snapshots]
        assert weeks == sorted(weeks)

    def test_varying_status_counts(self, weekly_snapshots):
        """Status counts should vary across weeks (dynamic, not static)."""
        if len(weekly_snapshots) >= 10:
            first = weekly_snapshots[0]
            last = weekly_snapshots[-1]
            # At least one status count should differ between first and last week
            changed = (
                first.programs_on_track != last.programs_on_track
                or first.programs_at_risk != last.programs_at_risk
                or first.programs_off_track != last.programs_off_track
            )
            assert changed
