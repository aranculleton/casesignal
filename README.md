# Account Risk Scoring

This project is for testing a simple monthly account-risk workflow.

Right now the flow is:
- generate synthetic account snapshots
- build first-pass features in SQL
- run a basic score pass on the same data

All data is synthetic at this stage.

Main files:
- `scripts/generate_account_snapshots_v1.py`
- `sql/account_month_features_v1.sql`
- `docs/account_snapshot_schema_v1.md`
- `docs/target_definition.md`

Run locally:

```bash
python3 scripts/generate_account_snapshots_v1.py --rows 200 --seed 7
```

Output: `data/synthetic/account_snapshot_v1.csv` (gitignored).

JAX step (optional):

JAX is only used here for a quick vectorized score pass. It does not train a model yet.

Install and run:

```bash
pip install "jax[cpu]"
python3 scripts/jax_score_smoke.py --input data/synthetic/account_snapshot_v1.csv --top-n 10
```

What this script does:
- reads the snapshot CSV
- builds a feature matrix from existing columns
- applies fixed weights and prints highest-score rows

Next:

- add a synthetic event table for labels
- make the SQL feature query runnable in a repeatable local flow
- replace fixed weights with a fitted baseline
