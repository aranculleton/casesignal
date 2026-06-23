#!/usr/bin/env python3
"""Quick JAX score check using the snapshot CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DRAFT_WEIGHTS = (1.35, 0.45, 1.6, 1.1, 1.3)
DRAFT_BIAS = -2.1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a JAX score check.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/synthetic/account_snapshot_v1.csv"),
        help="Input snapshot CSV",
    )
    parser.add_argument("--top-n", type=int, default=10, help="Rows to print")
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def main() -> int:
    args = parse_args()

    try:
        import jax.numpy as jnp
    except ImportError:
        print("JAX is not installed yet.")
        print("Install it with: pip install \"jax[cpu]\"")
        return 1

    if not args.input.exists():
        print(f"Input file not found: {args.input}")
        print("Generate it first with scripts/generate_account_snapshots_v1.py")
        return 1

    rows = load_rows(args.input)
    if not rows:
        print("Input CSV is empty.")
        return 1

    required_cols = {
        "account_id",
        "snapshot_date",
        "utilization_ratio",
        "payments_due_30d",
        "missed_payment_90d",
        "hardship_flag_90d",
        "collections_contact_90d",
    }
    missing = [name for name in sorted(required_cols) if name not in rows[0]]
    if missing:
        print(f"Missing required columns: {', '.join(missing)}")
        return 1

    account_keys = [f"{row['account_id']} @ {row['snapshot_date']}" for row in rows]

    try:
        x = jnp.array(
            [
                [
                    float(row["utilization_ratio"]),
                    float(row["payments_due_30d"]) / 3.0,
                    float(row["missed_payment_90d"]),
                    float(row["hardship_flag_90d"]),
                    float(row["collections_contact_90d"]),
                ]
                for row in rows
            ],
            dtype=jnp.float32,
        )
    except ValueError:
        print("Could not parse one or more numeric input columns")
        return 1

    # Rough weights for now; replace after baseline model work.
    weights = jnp.array(DRAFT_WEIGHTS, dtype=jnp.float32)
    bias = jnp.array(DRAFT_BIAS, dtype=jnp.float32)

    logits = x @ weights + bias
    probs = 1.0 / (1.0 + jnp.exp(-logits))

    top_n = max(1, min(args.top_n, len(rows)))
    top_idx = jnp.argsort(probs)[::-1][:top_n].tolist()

    print(f"Top {top_n} risk rows from {args.input}:")
    for rank, idx in enumerate(top_idx, start=1):
        print(f"{rank:>2}. {account_keys[idx]}  score={float(probs[idx]):.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())