# Target Definition Draft

Current first-pass target:

- Label name: `risk_event_next_window`
- Unit: one account snapshot row
- Window: next 90 days after `snapshot_date`
- Positive label: `1` if at least one risk event lands in that window
- Negative label: `0` if no event lands in that window

Risk event types planned:

- missed payment
- hardship-style support flag
- collections referral

Current scope note:
- this is a target spec only for now
- synthetic event-table generation is the next build step

Leakage rule:

- features must be built using data available on or before `snapshot_date` only.