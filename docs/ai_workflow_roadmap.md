# AI Product Integration Roadmap

This plan is about integrating AI into the scoring product itself.
Not "AI writing code".

## Direction

Working project name: **RiskSignal Copilot**

Core idea:
- keep a normal risk score from structured account data
- add AI-derived signal from free-text case notes
- combine both into a triage-ready output:
  - priority score
  - short risk reason summary
  - next-best-action suggestion

## Why this makes sense

For real usage:
- structured models miss signal in notes/case updates
- AI helps convert unstructured notes into usable risk features
- teams get faster triage context, not just a number

For CV value:
- shows AI integrated into product behavior
- keeps measurable outputs (precision/recall, triage lift, time-to-review)
- keeps risk modeling + data engineering narrative intact

## End-to-end target architecture

1. Structured pipeline
- snapshots -> features -> labels -> baseline model score

2. Note signal pipeline
- synthetic case notes -> AI extraction -> risk indicators

3. Hybrid scoring layer
- combine structured score + note signal score

4. Triage output layer
- score band + reasons + suggested action

## Phase plan

## Phase 1: Baseline model control

Goal:
- train first non-AI baseline on `training_slice_v1.csv`

Deliverables:
- `scripts/train_baseline_v1.py`
- metrics output (ROC-AUC, PR-AUC, calibration note)
- saved predictions file for downstream comparison

## Phase 2: Synthetic case-note dataset

Goal:
- add realistic free-text notes linked to accounts/snapshots

Deliverables:
- `scripts/generate_case_notes_v1.py`
- `docs/case_note_schema_v1.md`
- sample note classes (payment stress, income shock, vulnerability mention, admin-only)

## Phase 3: AI note-signal extraction

Goal:
- convert note text into structured risk indicators

Deliverables:
- `scripts/extract_note_signals_v1.py`
- extraction schema (JSON fields + confidence)
- fallback deterministic parser for offline test mode

## Phase 4: Hybrid score assembly

Goal:
- merge baseline score and note-signal score into one triage score

Deliverables:
- `scripts/build_hybrid_score_v1.py`
- weighted blend + simple calibration rule
- comparison report vs baseline-only

## Phase 5: Action summary output

Goal:
- output short human-readable case summaries and next action

Deliverables:
- `scripts/generate_case_summary_v1.py`
- action taxonomy (`monitor`, `call`, `hardship review`, `collections review`)
- one-line reason pack from structured + note signals

## Phase 6: Evaluation and evidence pack

Goal:
- show AI layer adds value instead of noise

Deliverables:
- evaluation notebook/script comparing baseline vs hybrid
- metrics: lift, precision@top-k, reviewer-time proxy
- `docs/case_study_risksignal_copilot.md`

## Guardrails

- do not claim autonomous decisioning
- always preserve deterministic fallback path
- keep feature leakage checks in place
- keep extraction confidence thresholds explicit

## Next immediate step

Build Phase 1 (`train_baseline_v1.py`) and lock the baseline metrics before adding note-signal AI.
