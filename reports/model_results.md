# Model Results (v1)

Generated: 2026-06-23T18:17:22+00:00

| Model | ROC-AUC | Precision@Top 10% | Lift@Top 10% | Reviewer-time proxy |
| --- | --- | --- | --- | --- |
| Structured baseline | 0.847 | 0.292 | 3.68 | 13.3% (32/240) for 50% escalation capture |
| Structured + servicing-note signals | 0.790 | 0.333 | 4.21 | 14.2% (34/240) for 50% escalation capture |

Reviewer-time proxy definition:

The reviewer-time proxy estimates how many accounts a team would need to review
to capture a fixed share of future escalations.
