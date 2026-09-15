# Data Dictionary

## Required event-log fields

| Field | Type | Required | Description | Example / rule |
| --- | --- | --- | --- | --- |
| `case_id` | string | Yes | Stable identifier for a process instance | `ORD-10492`; non-null |
| `activity_name` | string | Yes | Normalized business activity | `Validate order` |
| `event_timestamp` | timestamp UTC | Yes | Time the activity occurred | ISO 8601, timezone retained at ingestion |
| `event_id` | string | Recommended | Unique source event identifier | Used for deduplication |
| `event_lifecycle` | string | No | Start/complete/status lifecycle | Controlled vocabulary |
| `source_system` | string | Yes | System creating the event | Approved source name |
| `actor_pseudonym` | string | No | Tokenized role/user reference | Never store direct user ID in published layer |
| `queue_or_team` | string | No | Work queue or organizational unit | Governed reference value |
| `product_or_service` | string | No | Process segment attribute | Approved domain value |
| `region_or_channel` | string | No | Segmentation attribute | No precise address data |
| `sla_due_timestamp` | timestamp UTC | No | Contractual/internal due time | Required for SLA measures |

## Derived fields

| Field | Description |
| --- | --- |
| `event_sequence` | Deterministic ordering within a case using timestamp, lifecycle priority, then event ID |
| `case_start_timestamp` / `case_end_timestamp` | First and last included event timestamps |
| `previous_activity_name` / `next_activity_name` | Neighboring activity in the ordered event sequence |
| `is_rework_event` | Flag indicating a repeated activity or approved backward transition rule |
| `data_quality_status` | Valid, quarantined, or excluded with reason |
