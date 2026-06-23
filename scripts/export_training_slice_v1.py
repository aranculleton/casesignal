#!/usr/bin/env python3
"""Build a training-slice CSV from snapshot and event synthetic tables."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export feature + label training slice")
    parser.add_argument("--snapshots", type=Path, default=Path("data/synthetic/account_snapshot_v1.csv"))
    parser.add_argument("--events", type=Path, default=Path("data/synthetic/risk_events_v1.csv"))
    parser.add_argument("--out", type=Path, default=Path("data/synthetic/training_slice_v1.csv"))
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def build_event_index(event_rows: list[dict[str, str]]) -> dict[str, list[date]]:
    by_account: dict[str, list[date]] = defaultdict(list)
    skipped = 0

    for row in event_rows:
        account_id = row.get("account_id", "")
        event_date_text = row.get("event_date", "")
        if not account_id or not event_date_text:
            skipped += 1
            continue

        try:
            by_account[account_id].append(date.fromisoformat(event_date_text))
        except ValueError:
            skipped += 1

    for account_id in by_account:
        by_account[account_id].sort()

    if skipped:
        print(f"Skipped {skipped} event rows due to missing/invalid values")

    return by_account


def main() -> int:
    args = parse_args()
    if not args.snapshots.exists():
        print(f"Snapshot file not found: {args.snapshots}")
        return 1
    if not args.events.exists():
        print(f"Event file not found: {args.events}")
        return 1

    snapshot_rows = read_csv(args.snapshots)
    event_rows = read_csv(args.events)
    events_by_account = build_event_index(event_rows)

    out_rows: list[dict[str, str]] = []
    skipped_snapshots = 0
    positives = 0

    for row in snapshot_rows:
        try:
            snapshot_date = date.fromisoformat(row["snapshot_date"])
            util = float(row["utilization_ratio"])
            payments_due_30d = int(row["payments_due_30d"])
            missed = int(row["missed_payment_90d"])
            hardship = int(row["hardship_flag_90d"])
            collections = int(row["collections_contact_90d"])
        except (KeyError, ValueError):
            skipped_snapshots += 1
            continue

        window_end = snapshot_date + timedelta(days=90)
        event_dates = events_by_account.get(row["account_id"], [])
        matched = [d for d in event_dates if d > snapshot_date and d <= window_end]

        label = 1 if matched else 0
        positives += label

        out_rows.append(
            {
                "snapshot_id": row["snapshot_id"],
                "account_id": row["account_id"],
                "snapshot_date": snapshot_date.isoformat(),
                "months_on_book": row["months_on_book"],
                "credit_limit": row["credit_limit"],
                "balance": row["balance"],
                "utilization_ratio": row["utilization_ratio"],
                "payments_due_30d": str(payments_due_30d),
                "missed_payment_90d": str(missed),
                "hardship_flag_90d": str(hardship),
                "collections_contact_90d": str(collections),
                "high_utilization_flag": "1" if util >= 0.90 else "0",
                "any_recent_distress_flag": "1" if (missed + hardship + collections) > 0 else "0",
                "event_count_next_90d": str(len(matched)),
                "first_event_date_next_90d": matched[0].isoformat() if matched else "",
                "risk_event_next_window": str(label),
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
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
        "high_utilization_flag",
        "any_recent_distress_flag",
        "event_count_next_90d",
        "first_event_date_next_90d",
        "risk_event_next_window",
    ]

    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(out_rows)} training rows to {args.out}")
    if out_rows:
        positive_rate = positives / len(out_rows)
        print(f"Positive label rows: {positives} ({positive_rate:.2%})")
    if skipped_snapshots:
        print(f"Skipped {skipped_snapshots} snapshot rows due to missing/invalid values")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())