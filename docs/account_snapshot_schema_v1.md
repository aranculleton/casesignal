# Account Snapshot Schema v1

First base table for feature work.

Table name: `account_snapshot_v1`

Intended grain: one row per `account_id` + `snapshot_date`

Columns:

| column | type | note |
| --- | --- | --- |
| snapshot_id | text | id built from `account_id` + `snapshot_date`; should be unique for each snapshot row |
| account_id | text | synthetic account identifier |
| snapshot_date | date | monthly snapshot date |
| months_on_book | int | account age in months |
| credit_limit | int | synthetic credit limit |
| balance | numeric(10,2) | synthetic end-of-snapshot balance |
| utilization_ratio | numeric(6,4) | `balance / credit_limit` |
| payments_due_30d | int | count of payments due in trailing 30 days (current generator range: 0-3) |
| missed_payment_90d | int (0/1) | flag for any missed payment in trailing 90 days |
| hardship_flag_90d | int (0/1) | flag for hardship-style support in trailing 90 days |
| collections_contact_90d | int (0/1) | flag for collections contact in trailing 90 days |

Current limits:
- synthetic values only
- no event/label table joined yet