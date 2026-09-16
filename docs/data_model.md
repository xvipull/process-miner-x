# Analytics Data Model

The project database is SQLite at `data/analytics.db`; it is rebuilt on every pipeline run for reproducibility. Surrogate keys are integer technical keys; business keys are retained and uniquely constrained.

| Table | Grain | Surrogate key | Business key / relationships |
| --- | --- | --- | --- |
| `fact_process_event` | One accepted source event | `event_key` | `event_id`; foreign keys to case, activity, source system, and event date |
| `dim_case` | One process instance | `case_key` | `case_id` (unique), plus product, region/channel, customer reference |
| `dim_activity` | One normalized activity | `activity_key` | `activity_name` (unique) |
| `dim_source_system` | One approved source system | `source_system_key` | `source_system` (unique) |
| `dim_date` | One calendar date | `date_key` (`YYYYMMDD`) | `calendar_date` (unique) |

SQLite foreign keys are enabled during loading. The pipeline checks source-system reference validity before load and the database enforces all dimensional foreign-key relationships.
