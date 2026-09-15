# KPI Catalog

| KPI | Definition | Formula / grain | Owner | Target use |
| --- | --- | --- | --- | --- |
| Case throughput time | Calendar time from first to final included event | `end_ts - start_ts` per case | Process Owner | Find long-running cases |
| Stage waiting time | Time between one completed event and next started event | `next_event_ts - event_ts` per case transition | Operations Excellence | Locate queue delays |
| SLA breach rate | Cases exceeding agreed cycle-time threshold | `breached cases / eligible cases` | Process Owner | Manage service commitment |
| Rework rate | Cases repeating an activity or returning to an earlier stage | `rework cases / completed cases` | Business Analyst | Identify avoidable loops |
| Variant concentration | Share of cases accounted for by most frequent variants | `top N variant cases / all cases` | Business Analyst | Simplify process complexity |
| Conformance rate | Cases following approved path rules | `conformant cases / eligible cases` | Process Owner | Assess control adherence |
| Touch-time proxy | Sum of events or measured active-duration fields where available | Per case; clearly label source method | Process Owner | Separate active effort from waiting |

All KPIs must show period, cohort filters, eligible-case count, freshness timestamp, and definition version.
