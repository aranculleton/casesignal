from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "scoring_metrics_v1.py"
SPEC = importlib.util.spec_from_file_location("scoring_metrics_v1", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ScoringMetricsTests(unittest.TestCase):
    def test_roc_auc_perfect_ranking(self) -> None:
        labels = [0, 0, 1, 1]
        scores = [0.10, 0.20, 0.80, 0.90]
        self.assertAlmostEqual(MODULE.roc_auc_score(labels, scores), 1.0)

    def test_roc_auc_tied_scores_returns_half(self) -> None:
        labels = [0, 1, 0, 1]
        scores = [0.50, 0.50, 0.50, 0.50]
        self.assertAlmostEqual(MODULE.roc_auc_score(labels, scores), 0.5)

    def test_precision_and_lift_top_k(self) -> None:
        labels = [1, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        scores = [0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10, 0.05]

        precision, top_k = MODULE.precision_at_top_k(labels, scores, top_fraction=0.20)
        lift, base_rate, _ = MODULE.lift_at_top_k(labels, scores, top_fraction=0.20)

        self.assertEqual(top_k, 2)
        self.assertAlmostEqual(precision, 0.5)
        self.assertAlmostEqual(base_rate, 0.2)
        self.assertAlmostEqual(lift, 2.5)

    def test_reviewer_time_proxy_hits_target(self) -> None:
        labels = [1, 0, 1, 0, 0]
        scores = [0.90, 0.80, 0.70, 0.60, 0.10]

        share, count = MODULE.reviewer_time_proxy(labels, scores, target_positive_share=0.50)

        self.assertEqual(count, 1)
        self.assertAlmostEqual(share, 0.2)

    def test_model_metrics_has_expected_counts(self) -> None:
        labels = [1, 0, 1, 0, 0]
        scores = [0.90, 0.80, 0.70, 0.60, 0.10]

        metrics = MODULE.model_metrics(
            labels=labels,
            scores=scores,
            top_fraction=0.40,
            target_positive_share=0.50,
        )

        self.assertEqual(metrics["total_rows"], 5)
        self.assertEqual(metrics["positive_rows"], 2)
        self.assertEqual(metrics["top_k_count"], 2)


if __name__ == "__main__":
    unittest.main()
