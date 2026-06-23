# Account Risk Scoring

This repo is where I am building out a monthly account-risk workflow in small steps.

Current flow right now:
- generate synthetic account snapshots
- build first-pass features in SQL
- generate synthetic risk events
- build a feature + label training slice CSV
- run a quick score pass on the same data

All data is synthetic at this stage.

Where files are at:
- `scripts/generate_account_snapshots_v1.py`
- `scripts/generate_risk_events_v1.py`
- `scripts/export_training_slice_v1.py`
- `sql/account_month_features_v1.sql`
- `sql/labels_from_events_v1.sql`
- `docs/account_snapshot_schema_v1.md`
- `docs/target_definition.md`

Generate snapshots:

```bash
python3 scripts/generate_account_snapshots_v1.py --rows 200 --seed 7
```

Output: `data/synthetic/account_snapshot_v1.csv` (gitignored).

Generate events and training slice:

```bash
python3 scripts/generate_risk_events_v1.py
python3 scripts/export_training_slice_v1.py
```

JAX step (optional):

JAX here is just for a quick vectorized score check. It is not model training yet.

Install and run:

```bash
pip install "jax[cpu]"
python3 scripts/jax_score_smoke.py --input data/synthetic/account_snapshot_v1.csv --top-n 10
```

What this script does:
- reads the snapshot CSV
- builds a feature matrix from existing columns
- applies fixed weights and prints highest-score rows

Next steps:

- add first baseline model script using `training_slice_v1.csv`
- keep refining label quality and event generation assumptions
