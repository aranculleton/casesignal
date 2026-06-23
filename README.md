# CaseSignal

CaseSignal is a synthetic credit-risk decisioning pipeline.

It combines structured credit-account behavior with AI-extracted servicing-note signals
to rank accounts by near-term delinquency or escalation risk, explain risk movement,
and support human review.

The project is intentionally scoped as a prototype: the data is synthetic,
the scoring logic is transparent, and the AI component is limited to extracting
auditable note signals rather than making final risk decisions.

## Use case

In lending and servicing workflows, teams need to prioritize which accounts to review first.
CaseSignal models that workflow with:
- a transparent baseline risk score
- note-derived risk indicators from servicing notes
- hybrid score bands and review-ready context

## Why AI is used (and bounded)

AI is used for one narrow task: converting unstructured servicing notes into
structured, auditable indicators (for example hardship mention, income shock language,
or vulnerability context).

AI is not used for final risk decisions.
Final ranking remains deterministic and reviewable:
- baseline structured model score
- note-signal feature block
- explicit hybrid scoring rule

If extraction fails, the pipeline falls back to structured-only scoring.

## Primary project question

Do AI-extracted servicing-note signals improve top-k risk prioritization
over structured features alone?

Core evaluation metrics:
- ROC-AUC
- precision@top-k
- lift@top-k
- reviewer-time proxy

## Current status

Already in place:
- synthetic snapshots and events generation
- SQL feature and label drafts
- training slice export

Core files:
- `scripts/generate_account_snapshots_v1.py`
- `scripts/generate_risk_events_v1.py`
- `scripts/export_training_slice_v1.py`
- `sql/account_month_features_v1.sql`
- `sql/labels_from_events_v1.sql`

## Two-week MVP scope

Week 1:
1. train a baseline model on `training_slice_v1.csv`
2. generate synthetic servicing notes linked to account-month rows
3. define note-signal schema + deterministic fallback parser

Week 2:
1. add note-signal extraction step
2. build hybrid score + action banding
3. compare baseline vs hybrid (`precision@top-k`, lift, reviewer-time proxy)
4. write a short model-card style limitations note

This scope is intentionally sized for one developer over two focused weeks.

## Quick run (current data flow)

```bash
python3 scripts/generate_account_snapshots_v1.py --rows 200 --seed 7
python3 scripts/generate_risk_events_v1.py
python3 scripts/export_training_slice_v1.py
```

Expected outputs:
- `data/synthetic/account_snapshot_v1.csv`
- `data/synthetic/risk_events_v1.csv`
- `data/synthetic/training_slice_v1.csv`

## Roadmap

Detailed build plan: `docs/ai_workflow_roadmap.md`.
