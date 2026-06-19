# Account Risk Scoring

Early WIP for an account-risk scoring project.

Goal:
Build a small, reproducible pipeline that ranks accounts by 90-day risk.

Data:
Synthetic only. Real customer/account data is not included.

Status:
Still early, now with a first synthetic snapshot generator.

First working notes:
- target draft: docs/target_definition.md
- snapshot schema v1: docs/account_snapshot_schema_v1.md

Quick local run:

```bash
python3 scripts/generate_account_snapshots_v1.py --rows 200 --seed 7
```

Output:
- data/synthetic/account_snapshot_v1.csv (gitignored)
