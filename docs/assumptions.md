# Assumptions, Risks, and Open Decisions

## Working assumptions

1. `case_id` reliably represents one process instance across included source systems.
2. Event timestamps are recorded consistently enough to order events after documented timezone conversion.
3. Source owners will supply a data contract and provide at least 12 months of pilot history.
4. Process Owners will approve the event inclusion/exclusion rules and target-process conformance rules.
5. Daily batch refresh is sufficient for the initial decision cadence.

## Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Missing or duplicate events | Misleading paths and cycle times | Profile completeness; quarantine exceptions; reconcile to source counts |
| Timestamp ambiguity | Incorrect order and waiting times | Normalize to UTC; use deterministic tie-breakers; publish limitations |
| Schema/semantic change | Broken refresh or drifting KPIs | Version data contract; automated validation; owner change notice |
| Privacy misuse | Harm and policy breach | Pseudonymize, restrict access, aggregate outputs, approve use cases |
| False causal inference | Poor investment decision | Label findings as hypotheses; combine with operational validation |

## Open decisions

- Confirm pilot process, SLA thresholds, and eligible start/end events.
- Name individual data owners and approve access roles.
- Set retention period, refresh service-level objective, and dashboard publication workspace.
- Agree whether elapsed time excludes non-business hours for each KPI.
