# Account Snapshot Schema v1

Purpose:
- first synthetic base table for feature prototyping
- one row per account snapshot

Table name:
- account_snapshot_v1

Grain:
- one row per account_id and snapshot_date

Columns:

| column | type | note |
| --- | --- | --- |
| snapshot_id | text | synthetic unique id (`account_id` + `snapshot_date`) |
| account_id | text | synthetic account identifier |
| snapshot_date | date | monthly snapshot date |
| months_on_book | int | account age in months |
| credit_limit | int | synthetic credit limit |
| balance | numeric(10,2) | synthetic end-of-snapshot balance |
| utilization_ratio | numeric(6,4) | `balance / credit_limit` |
| payments_due_30d | int | payments due in trailing 30 days |
| missed_payment_90d | int (0/1) | any missed payment in trailing 90 days |
| hardship_flag_90d | int (0/1) | hardship-style support in trailing 90 days |
| collections_contact_90d | int (0/1) | collections contact in trailing 90 days |

Why this first:
- simple enough to generate and inspect quickly
- contains a few plausible risk signals for later label experiments
- keeps leakage boundaries clear because all fields are as-of snapshot_date