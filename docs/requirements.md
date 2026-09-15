# Project Charter: Business Process Mining & Bottleneck Discovery Studio

## Vision and business problem

Operational teams often make improvement decisions from averages, surveys, and manually maintained process maps. Those views conceal rework loops, exception paths, hand-off delays, and where customers wait. The studio will use timestamped event data to show how work actually flows, identify material bottlenecks, and give owners a shared evidence base for prioritizing improvement work.

## Stakeholder personas

| Persona | Primary need | Typical decisions |
| --- | --- | --- |
| Business Analyst | Self-service, traceable process evidence | Which variants, cohorts, and causes merit deeper analysis? |
| Operations Excellence | Portfolio-level improvement opportunity sizing | Which initiative should be prioritized and how will benefits be measured? |
| Process Owner | Trusted view of a process they own | Where should capacity, policy, automation, or controls change? |

## Decisions the product must support

- Prioritize the stages, queues, and variants with the greatest avoidable delay or rework.
- Compare actual process conformance with an approved target process.
- Identify segment-specific problems by product, channel, region, customer class, or workload cohort.
- Size an improvement hypothesis through case volume, elapsed time, touch time, SLA breach rate, and rework rate.
- Track whether a completed intervention produced a sustained, measurable improvement.

## Scope

### In scope

- Ingest approved event-log extracts containing case ID, activity, event timestamp, source system, and permitted attributes.
- Data-quality profiling; process maps; variant analysis; throughput, waiting, rework, conformance, and SLA metrics.
- Scheduled Power BI and Excel-ready outputs with drill-through to authorized case-level evidence.
- Documented KPI definitions, lineage, access controls, and reproducible SQL/Python logic.

### Out of scope

- Direct operational workflow execution, ticket routing, or automated decisioning.
- Replacing source-system records, enterprise data governance, or the corporate data lake.
- Unapproved surveillance of individuals or use of process metrics for performance management.
- Predictive optimization, real-time streaming, and cross-company data sharing in the initial release.

## Data ownership and refresh cadence

| Data domain | Business data owner | Technical custodian | Planned cadence |
| --- | --- | --- | --- |
| Core process events | Named Process Owner | Source-system product team | Daily, by 06:00 local time |
| Workforce/queue reference data | Operations Excellence lead | HR/workforce data team | Weekly |
| Customer/product reference data | Domain data steward | Enterprise data platform | Daily |

The named owner approves intended use, completeness, retention, and material changes. Custodians deliver governed extracts and notify the team before schema or logic changes.

## Security and privacy

- Use least-privilege, role-based access; segregate raw data from published metrics.
- Pseudonymize person and customer identifiers before analytical use; exclude free text and sensitive special-category fields unless explicitly approved.
- Encrypt data in transit and at rest; retain audit logs for access and published refreshes.
- Do not commit source extracts, credentials, or personal data. Follow enterprise retention schedules and conduct a privacy/security review before production access.

## Assumptions and risks

Assumptions and open decisions are maintained in [assumptions.md](assumptions.md). Principal risks include incomplete event capture, inconsistent timestamps, changing source semantics, stakeholder misinterpretation of correlation as causation, and use of employee-level data outside the approved purpose.

## Measurable acceptance criteria

1. A pilot event log can be reconstructed into cases with at least 98% of valid events assigned to a case and a documented exception list.
2. At least 95% of included events have a valid activity and timestamp; duplicate and ordering rules are tested and reported.
3. Published process-map, variant, throughput, waiting-time, rework, and SLA metrics reconcile to agreed sample calculations within 1%.
4. Authorized users can filter by agreed cohort dimensions and drill to permitted supporting evidence; unauthorized users cannot access raw or identifiable data.
5. The daily refresh completes by 08:00 local time on at least 95% of scheduled business days, with freshness and failure status visible.
6. Each pilot Process Owner signs off on definitions and identifies at least one prioritized improvement hypothesis supported by the studio.
