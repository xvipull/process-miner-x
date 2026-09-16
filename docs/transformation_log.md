# Transformation Log

The selected pilot dataset is a **customer order-fulfilment event log**. Its required contract is in [data_dictionary.md](data_dictionary.md). Raw input remains immutable in `data/raw/`; the pipeline only reads it and writes derived records to `data/staging/`.

| Step | Rule | Output / evidence |
| --- | --- | --- |
| Contract check | Require `event_id`, `case_id`, `activity_name`, `event_timestamp`, and `source_system` | Required-column quality result |
| Key standardization | Trim and uppercase `event_id` and `case_id`; enforce unique accepted `event_id` | Business keys suitable for reconciliation |
| Date standardization | Parse ISO 8601 timestamps and convert to UTC (`Z`) | Comparable sequencing and date dimension keys |
| Category standardization | Map known activity aliases; uppercase source, currency, and region/channel; title-case queue | Governed categories |
| Currency/value standardization | Remove display symbols/separators; parse decimal amount; accept range 0–10,000,000 | Numeric amount and ISO currency code |
| Quarantine | Rows with missing required values, unknown source, invalid timestamp, or invalid amount are excluded from fact load and recorded | `data/staging/quarantined_events.csv` |
| Reconciliation | Account for raw = accepted + quarantined; reconcile fact row count and amount total | Generated DQ report |

Run locally:

```bash
python -m unittest discover -s tests -v
python src/pipeline.py --input data/raw/order_events.csv --as-of 2025-02-16T00:00:00Z
```
