#!/usr/bin/env python3
"""Generate a small synthetic account snapshot table (v1)."""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic account snapshots.")
    parser.add_argument("--rows", type=int, default=500, help="Number of rows to generate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/synthetic/account_snapshot_v1.csv"),
        help="Output CSV path.",
    )
    return parser.parse_args()


def month_end(dt: date) -> date:
    """Return a month-end date for any given date."""
    if dt.month == 12:
        next_month = date(dt.year + 1, 1, 1)
    else:
        next_month = date(dt.year, dt.month + 1, 1)
    return next_month - timedelta(days=1)


def generate_rows(row_count: int, seed: int) -> list[dict[str, str]]:
    rng = random.Random(seed)

    start = date(2025, 1, 1)
    snapshots: list[dict[str, str]] = []

    for _ in range(row_count):
        account_num = rng.randint(100000, 102499)
        account_id = f"A{account_num}"

        day_offset = rng.randint(0, 540)
        snapshot_date = month_end(start + timedelta(days=day_offset))

        months_on_book = rng.randint(1, 120)
        credit_limit = rng.choice([500, 1000, 1500, 2500, 5000, 8000])

        base_util = min(max(rng.gauss(0.55, 0.25), 0.0), 1.35)
        balance = round(credit_limit * base_util, 2)
        utilization_ratio = round(balance / credit_limit, 4)

        payments_due_30d = rng.randint(0, 3)

        miss_score = 0.05 + (0.22 if utilization_ratio > 0.85 else 0.0) + (0.08 if payments_due_30d >= 2 else 0.0)
        missed_payment_90d = int(rng.random() < min(miss_score, 0.9))

        hardship_score = 0.03 + (0.12 if missed_payment_90d else 0.0)
        hardship_flag_90d = int(rng.random() < hardship_score)

        collections_score = 0.02 + (0.18 if missed_payment_90d else 0.0) + (0.10 if hardship_flag_90d else 0.0)
        collections_contact_90d = int(rng.random() < min(collections_score, 0.9))

        snapshots.append(
            {
                "snapshot_id": f"{account_id}_{snapshot_date.isoformat()}",
                "account_id": account_id,
                "snapshot_date": snapshot_date.isoformat(),
                "months_on_book": str(months_on_book),
                "credit_limit": str(credit_limit),
                "balance": f"{balance:.2f}",
                "utilization_ratio": f"{utilization_ratio:.4f}",
                "payments_due_30d": str(payments_due_30d),
                "missed_payment_90d": str(missed_payment_90d),
                "hardship_flag_90d": str(hardship_flag_90d),
                "collections_contact_90d": str(collections_contact_90d),
            }
        )

    return snapshots


def write_csv(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "snapshot_id",
        "account_id",
        "snapshot_date",
        "months_on_book",
        "credit_limit",
        "balance",
        "utilization_ratio",
        "payments_due_30d",
        "missed_payment_90d",
        "hardship_flag_90d",
        "collections_contact_90d",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    rows = generate_rows(row_count=args.rows, seed=args.seed)
    write_csv(rows, args.out)
    print(f"Wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()