# RiskSignal Copilot

`account-risk-scoring` is now focused on one thing:
build a useful AI-powered risk triage layer on top of account risk scoring.

## What this project is

The product direction is a hybrid system:
- normal risk score from structured data
- AI-extracted risk signals from free-text case notes
- combined priority score + short action summary for case workers

This keeps model math where it should be, and uses AI where it adds value
(unstructured signals and decision support).

## What already exists

Structured data pipeline:
- synthetic snapshots
- synthetic risk events
- SQL feature draft
- SQL label draft
- training slice export

Main files right now:
- `scripts/generate_account_snapshots_v1.py`
- `scripts/generate_risk_events_v1.py`
- `scripts/export_training_slice_v1.py`
- `sql/account_month_features_v1.sql`
- `sql/labels_from_events_v1.sql`

## Where AI is integrated (project direction)

AI is part of the scoring product itself, not just development workflow.

Planned integration:
1. parse synthetic case notes into structured risk signals
2. combine structured score + note-derived score
3. output a short risk reason summary and next-best-action suggestion

## Current roadmap

See `docs/ai_workflow_roadmap.md` for the full start-to-finish plan.

## Quick run (current baseline data flow)

```bash
python3 scripts/generate_account_snapshots_v1.py --rows 200 --seed 7
python3 scripts/generate_risk_events_v1.py
python3 scripts/export_training_slice_v1.py
```

## Next build step

Add the first baseline model script using `training_slice_v1.csv`, then layer in the first AI note-signal module.
