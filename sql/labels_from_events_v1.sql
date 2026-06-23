-- First pass label query from snapshot + event tables.
-- Uses a 90-day forward window from each snapshot_date.

WITH snapshots AS (
    SELECT
        snapshot_id,
        account_id,
        CAST(snapshot_date AS DATE) AS snapshot_date
    FROM account_snapshot_v1
),
events AS (
    SELECT
        event_id,
        account_id,
        CAST(event_date AS DATE) AS event_date,
        event_type
    FROM risk_events_v1
),
labels AS (
    SELECT
        s.snapshot_id,
        s.account_id,
        s.snapshot_date,
        COUNT(e.event_id) AS event_count_next_90d,
        MIN(e.event_date) AS first_event_date_next_90d,
        CASE WHEN COUNT(e.event_id) > 0 THEN 1 ELSE 0 END AS risk_event_next_window
    FROM snapshots s
    LEFT JOIN events e
      ON e.account_id = s.account_id
     AND e.event_date > s.snapshot_date
     AND e.event_date <= s.snapshot_date + INTERVAL 90 DAY
    GROUP BY
        s.snapshot_id,
        s.account_id,
        s.snapshot_date
)
SELECT
    snapshot_id,
    account_id,
    snapshot_date,
    event_count_next_90d,
    first_event_date_next_90d,
    risk_event_next_window
FROM labels;