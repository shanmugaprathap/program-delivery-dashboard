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


class TestWeeklySnapshots:
    def test_snapshots_generated(self, weekly_snapshots):
        assert len(weekly_snapshots) > 20

    def test_sorted_by_week(self, weekly_snapshots):
        weeks = [s.week_start for s in weekly_snapshots]
        assert weeks == sorted(weeks)
