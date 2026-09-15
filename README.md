# process-miner-x

Business Process Mining & Bottleneck Discovery Studio turns event-log data into evidence for improving customer, operational, and compliance outcomes.

## Purpose

The studio gives analysts and process owners a governed way to reconstruct actual process paths, locate bottlenecks, quantify their impact, and prioritize improvements.

## Architecture

```text
Source systems → raw event extracts → staging/quality checks → process metrics & models
                                                        ├→ SQL analyses
                                                        ├→ Python transformations
                                                        └→ Power BI / Excel / reports
```

| Layer | Location | Responsibility |
| --- | --- | --- |
| Source landing | `data/raw/` | Immutable, access-controlled extracts |
| Preparation | `data/staging/`, `sql/`, `src/` | Validation, standardization, feature creation |
| Analysis | `notebooks/`, `sql/` | Discovery and reproducible metric calculations |
| Consumption | `powerbi/`, `excel/`, `reports/` | Governed stakeholder outputs |

## Documentation

- [Project charter and requirements](docs/requirements.md)
- [KPI catalog](docs/kpi_catalog.md)
- [Data dictionary](docs/data_dictionary.md)
- [Assumptions and decisions](docs/assumptions.md)

## Screenshot placeholders

| Process map | Bottleneck dashboard | Variant analysis |
| --- | --- | --- |
| _Add approved process-flow screenshot here_ | _Add approved KPI dashboard screenshot here_ | _Add approved path-comparison screenshot here_ |

## Repository layout

`data/` holds controlled data zones; `sql/` and `src/` contain reusable transformations; `notebooks/` supports exploration; `tests/` verifies logic; and presentation artifacts belong in `powerbi/`, `excel/`, and `reports/`.

No production or personal data may be committed to this repository.
