#!/usr/bin/env python3
"""Inspect hybrid score distribution and suggest band thresholds."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check hybrid-score distribution")
    parser.add_argument(
        "--hybrid-predictions",
        type=Path,
        default=Path("data/synthetic/hybrid_predictions_v1.csv"),
        help="Hybrid predictions CSV",
    )
    parser.add_argument(
        "--split",
        choices=("all", "train", "test"),
        default="test",
        help="Which split to evaluate",
    )
    parser.add_argument("--high-quantile", type=float, default=0.95, help="Quantile for high-risk threshold")
    parser.add_argument(
        "--elevated-quantile",
        type=float,
        default=0.85,
        help="Quantile for elevated-risk threshold",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional output path for threshold summary JSON",
    )
    return parser.parse_args()


def quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    q = max(0.0, min(1.0, q))
    idx = int(round((len(sorted_values) - 1) * q))
    return sorted_values[idx]


def collect_scores(predictions_path: Path, split: str) -> list[float]:
    scores: list[float] = []
    with predictions_path.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if split != "all" and row.get("split") != split:
                continue
            try:
                scores.append(float(row["hybrid_score"]))
            except (KeyError, ValueError):
                continue
    scores.sort()
    return scores


def threshold_payload(
    scores: list[float],
    split: str,
    elevated_quantile: float,
    high_quantile: float,
) -> dict[str, float | int | str]:
    return {
        "split": split,
        "rows_evaluated": len(scores),
        "elevated_quantile": elevated_quantile,
        "high_quantile": high_quantile,
        "elevated_threshold": quantile(scores, elevated_quantile),
        "high_threshold": quantile(scores, high_quantile),
    }


def main() -> int:
    args = parse_args()
    if not args.hybrid_predictions.exists():
        print(f"Missing input: {args.hybrid_predictions}")
        return 1
    if args.elevated_quantile > args.high_quantile:
        print("elevated-quantile must be <= high-quantile")
        return 1

    scores = collect_scores(args.hybrid_predictions, args.split)

    if not scores:
        print("No scores found for requested split")
        return 1

    payload = threshold_payload(
        scores=scores,
        split=args.split,
        elevated_quantile=args.elevated_quantile,
        high_quantile=args.high_quantile,
    )

    print(f"Rows evaluated: {payload['rows_evaluated']} (split={payload['split']})")
    for q in (0.50, 0.75, 0.90, 0.95, 0.99):
        print(f"p{int(q * 100):02d}: {quantile(scores, q):.4f}")

    print("Suggested thresholds:")
    print(f"- elevated ({args.elevated_quantile:.0%}): {payload['elevated_threshold']:.4f}")
    print(f"- high ({args.high_quantile:.0%}): {payload['high_threshold']:.4f}")

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        with args.json_out.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        print(f"Wrote threshold summary to {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
