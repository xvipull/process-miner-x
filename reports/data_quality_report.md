# Data Quality Report

- Input: `data/raw/order_events.csv`
- Run as of: `2025-02-16T00:00:00+00:00`
- Rows: 4 raw / 4 accepted / 0 quarantined

| Check | Status | Observed | Threshold |
| --- | --- | --- | --- |
| required_columns | PASS | all present | all required |
| null_rate_case_id | PASS | 0.0 | 0.0 |
| null_rate_activity_name | PASS | 0.0 | 0.01 |
| null_rate_event_timestamp | PASS | 0.0 | 0.01 |
| null_rate_source_system | PASS | 0.0 | 0.0 |
| duplicate_event_id | PASS | 0 | 0 |
| invalid_amount_range | PASS | 0 | 0 |
| future_event_timestamp | PASS | 0 | 0 |
| freshness | PASS | 14.0 | <= 48 hours |
| source_system_reference | PASS | 0 | 0 |
| row_reconciliation | PASS | 4 = 4 + 0 | raw = accepted + rejected |

## Model reconciliation

Fact events: 4; fact amount total: 3699.5.
