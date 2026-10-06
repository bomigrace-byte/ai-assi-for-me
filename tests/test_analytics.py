import unittest
from datetime import date, datetime, timedelta, timezone

from backend.analytics import analyze_technology, rank_technologies
from backend.models import TechnologyData


class AnalyticsRulesTest(unittest.TestCase):
    def make_rows(self, value: int, count: int, repository: str, offset: int = 0) -> list[TechnologyData]:
        base = 1767484800
        collected = datetime(2026, 1, 1, tzinfo=timezone.utc)
        return [
            TechnologyData(
                technology=repository.split("/")[0],
                repository=repository,
                date=date(2026, 1, 1) + timedelta(days=7 * (index + offset)),
                week_start_epoch=base + 604800 * (index + offset),
                value=value,
                metric="weekly_new_stars",
                source="github",
                source_type="github_star_history",
                analysis_eligible=True,
                collected_at=collected,
            )
            for index in range(count)
        ]

    def test_exact_ten_percent_is_stable(self) -> None:
        rows = self.make_rows(100, 13, "stable/repo") + self.make_rows(110, 13, "stable/repo", 13)
        result = analyze_technology(rows, "13w")
        self.assertEqual(result.status, "stable")
        self.assertEqual(result.momentum_change_percent, 10.0)

    def test_zero_baseline_and_missing_data(self) -> None:
        zero_rows = self.make_rows(0, 13, "zero/repo") + self.make_rows(10, 13, "zero/repo", 13)
        self.assertEqual(analyze_technology(zero_rows, "13w").status, "insufficient_baseline")
        self.assertEqual(analyze_technology(self.make_rows(1, 25, "short/repo"), "13w").status, "insufficient_data")

    def test_ranking_excludes_manual_rows_by_model_policy(self) -> None:
        rows = self.make_rows(100, 13, "slow/repo") + self.make_rows(130, 13, "slow/repo", 13)
        self.assertEqual(rank_technologies(rows, "13w", 5)[0].repository, "slow/repo")


if __name__ == "__main__":
    unittest.main()
