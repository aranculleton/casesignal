from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_case_summary_v1.py"
SPEC = importlib.util.spec_from_file_location("generate_case_summary_v1", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class CaseSummaryScriptTests(unittest.TestCase):
    def test_high_risk_band_and_actions(self) -> None:
        band = MODULE.risk_band_from_score(score=0.81, high_threshold=0.65, elevated_threshold=0.40)
        action = MODULE.recommended_action_for_band(band)

        self.assertEqual(band, "high")
        self.assertEqual(action, "priority_manual_review_24h")

    def test_reason_codes_include_note_signals(self) -> None:
        reason_codes = MODULE.build_reason_codes(
            baseline_score=0.74,
            note_signal_score=0.45,
            note_row={
                "hardship_signal": "1",
                "income_shock_signal": "0",
                "missed_payment_signal": "1",
                "arrangement_break_signal": "0",
                "collections_signal": "0",
                "vulnerability_signal": "0",
            },
        )

        self.assertIn("high_structured_risk", reason_codes)
        self.assertIn("elevated_note_risk", reason_codes)
        self.assertIn("hardship_mentioned", reason_codes)
        self.assertIn("missed_payment_mentioned", reason_codes)


if __name__ == "__main__":
    unittest.main()
