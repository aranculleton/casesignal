#!/usr/bin/env python3
"""Generate review-ready case summaries from hybrid scores and note signals."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


SIGNAL_REASON_MAP = {
    "hardship_signal": "hardship_mentioned",
    "income_shock_signal": "income_shock_mentioned",
    "missed_payment_signal": "missed_payment_mentioned",
    "arrangement_break_signal": "arrangement_break_mentioned",
    "collections_signal": "collections_escalation_mentioned",
    "vulnerability_signal": "vulnerability_mentioned",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate case summary output")
    parser.add_argument(
        "--hybrid-predictions",
        type=Path,
        default=Path("data/synthetic/hybrid_predictions_v1.csv"),
        help="Hybrid predictions CSV",
    )
    parser.add_argument(
        "--note-signals",
        type=Path,
        default=Path("data/synthetic/note_signals_v1.csv"),
        help="Note signal CSV",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/synthetic/case_summary_v1.csv"),
        help="Case summary output CSV",
    )
    parser.add_argument(
        "--split",
        choices=("all", "test", "train"),
        default="test",
        help="Which split to include in output",
    )
    parser.add_argument("--high-threshold", type=float, default=0.25, help="High-risk threshold")
    parser.add_argument("--elevated-threshold", type=float, default=0.10, help="Elevated-risk threshold")
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def parse_float(value: str | None, default: float = 0.0) -> float:
    try:
        return float(value or "")
    except ValueError:
        return default


def parse_int(value: str | None, default: int = 0) -> int:
    try:
        return int(value or "")
    except ValueError:
        return default


def risk_band_from_score(score: float, high_threshold: float, elevated_threshold: float) -> str:
    if score >= high_threshold:
        return "high"
    if score >= elevated_threshold:
        return "elevated"
    return "low"


def recommended_action_for_band(risk_band: str) -> str:
    if risk_band == "high":
        return "priority_manual_review_24h"
    if risk_band == "elevated":
        return "manual_review_3_business_days"
    return "routine_monitoring_queue"


def build_reason_codes(
    baseline_score: float,
    note_signal_score: float,
    note_row: dict[str, str],
) -> list[str]:
    reason_codes: list[str] = []

    if baseline_score >= 0.70:
        reason_codes.append("high_structured_risk")
    if note_signal_score >= 0.40:
        reason_codes.append("elevated_note_risk")

    for signal_name, reason_label in SIGNAL_REASON_MAP.items():
        if parse_int(note_row.get(signal_name), default=0) == 1:
            reason_codes.append(reason_label)

    if not reason_codes:
        reason_codes.append("low_observed_risk")

    return reason_codes


def build_case_summary(risk_band: str, reason_codes: list[str], score: float) -> str:
    lead = {
        "high": "High-priority review recommended",
        "elevated": "Elevated-risk review recommended",
        "low": "Routine monitoring recommended",
    }[risk_band]
    return f"{lead} (hybrid_score={score:.3f}). Key reasons: {', '.join(reason_codes)}."


def main() -> int:
    args = parse_args()
    if args.elevated_threshold > args.high_threshold:
        print("Invalid thresholds: elevated-threshold must be <= high-threshold")
        return 1
    if not args.hybrid_predictions.exists():
        print(f"Hybrid predictions not found: {args.hybrid_predictions}")
        return 1
    if not args.note_signals.exists():
        print(f"Note signals not found: {args.note_signals}")
        return 1

    hybrid_rows = read_rows(args.hybrid_predictions)
    note_rows = read_rows(args.note_signals)
    if not hybrid_rows:
        print("Hybrid predictions input is empty")
        return 1

    note_by_snapshot = {row.get("snapshot_id", ""): row for row in note_rows if row.get("snapshot_id")}

    out_rows: list[dict[str, str]] = []
    band_counts = {"high": 0, "elevated": 0, "low": 0}

    for row in hybrid_rows:
        split = row.get("split", "")
        if args.split != "all" and split != args.split:
            continue

        hybrid_score = parse_float(row.get("hybrid_score"), default=0.0)
        baseline_score = parse_float(row.get("baseline_score"), default=0.0)
        snapshot_id = row.get("snapshot_id", "")

        note_row = note_by_snapshot.get(snapshot_id, {})
        note_signal_score = parse_float(note_row.get("note_signal_score"), default=0.0)

        risk_band = risk_band_from_score(
            score=hybrid_score,
            high_threshold=args.high_threshold,
            elevated_threshold=args.elevated_threshold,
        )
        action = recommended_action_for_band(risk_band)
        reason_codes = build_reason_codes(
            baseline_score=baseline_score,
            note_signal_score=note_signal_score,
            note_row=note_row,
        )
        case_summary = build_case_summary(risk_band=risk_band, reason_codes=reason_codes, score=hybrid_score)

        band_counts[risk_band] += 1
        out_rows.append(
            {
                "snapshot_id": snapshot_id,
                "account_id": row.get("account_id", ""),
                "snapshot_date": row.get("snapshot_date", ""),
                "split": split,
                "hybrid_score": f"{hybrid_score:.6f}",
                "risk_band": risk_band,
                "recommended_action": action,
                "reason_codes": ";".join(reason_codes),
                "case_summary": case_summary,
            }
        )

    if not out_rows:
        print("No rows matched the requested split")
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "snapshot_id",
                "account_id",
                "snapshot_date",
                "split",
                "hybrid_score",
                "risk_band",
                "recommended_action",
                "reason_codes",
                "case_summary",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(out_rows)} case summary rows to {args.out}")
    print("Risk-band distribution:")
    for risk_band in ("high", "elevated", "low"):
        print(f"- {risk_band}: {band_counts[risk_band]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
