# PlaceMux Phase 3 - Task 02
## Observability Deep-Dive, SLOs & Error Budgets

## Objective

Define and demonstrate service-level objectives for the PlaceMux intelligence layer.

The implementation covers:

1. Inference SLOs
2. Monitoring and alerting
3. Model-service error budget
4. Synthetic breach testing
5. Safe model-unavailable behavior
6. Reproducible evidence artifacts

The goal is to detect slow inference or degraded recommendation quality before users are silently affected.

---

## Scope

This task uses the existing Task 25 production-style go-live rehearsal traffic as the primary traffic source.

Primary source:

`phase2/task25/data/production_traffic.json`

The source is explicitly a production-style rehearsal and is not claimed to represent external marketplace production traffic.

Offline comparison reference:

`phase3/task01/data/offline_evaluation.json`

The offline evaluation is retained as a baseline reference and is not presented as a fresh production evaluation.

---

## SLO Definitions

| SLO | Target | Measurement |
|---|---:|---|
| P95 inference latency | <= 100 ms | Successful inference events |
| Availability | >= 99% | Successful events / total events |
| Minimum precision | >= 80% | TP / (TP + FP) |
| Score distribution | Non-degenerate | More than one unique score |
| Prediction drift | PSI <= 0.20 | Reference vs current score distribution |

These are engineering objectives for the PlaceMux intelligence-layer rehearsal and are not external contractual SLAs.

---

## Data Provenance

Task 02 directly reads:

`phase2/task25/data/production_traffic.json`

The implementation records:

- absolute source path
- SHA-256 hash
- model version
- event count
- traffic scope

This prevents the Task 02 evidence from silently using a separately curated copy of the traffic dataset.

---

## Current Baseline

The existing Task 25 traffic contains 20 events.

Observed baseline from the Task 02 calculation should be treated as the authoritative Task 02 calculation.

Expected monitoring dimensions include:

- precision
- recall
- false-positive rate
- average latency
- P95 latency
- maximum latency
- availability
- score mean
- score minimum
- score maximum
- unique score count
- PSI
- model version consistency

---

## Monitoring

The monitoring layer evaluates:

### Latency

An alert is generated when:

`P95 latency > 100 ms`

Alert:

`LATENCY_SLO_BREACH`

Owner:

`DevOps`

### Availability

An alert is generated when:

`Availability < 99%`

Alert:

`AVAILABILITY_SLO_BREACH`

Owner:

`DevOps`

### Prediction quality

An alert is generated when:

`Precision < 80%`

Alert:

`PRECISION_SLO_BREACH`

Owner:

`ML Engineer`

### Score distribution

An alert is generated when all successful events have the same score.

Alert:

`DEGENERATE_SCORE_DISTRIBUTION`

Owner:

`ML Engineer`

This protects against a model silently returning a constant prediction score.

### Prediction drift

An alert is generated when:

`PSI > 0.20`

Alert:

`PREDICTION_DRIFT`

Owner:

`ML Engineer`

---

## Error Budget

Availability SLO:

99%

Allowed failure rate:

1%

For a measurement window containing N inference events:

`allowed failures = N × 0.01`

The implementation reports:

- total events
- failed events
- allowed failures
- consumed failures
- remaining budget
- consumed fraction
- remaining fraction
- budget status

For very small rehearsal windows, the fractional error budget is retained instead of rounding it to an integer. This makes the calculation explicit rather than hiding the limitation of a small sample.

---

## Synthetic Breach Tests

The end-to-end runner performs controlled failure simulations.

### 1. Normal traffic

Uses the actual Task 25 rehearsal events without modification.

Purpose:

Establish the observed baseline.

### 2. Synthetic latency breach

All simulated latency values are increased above the 100 ms SLO.

Expected alert:

`LATENCY_SLO_BREACH`

### 3. Synthetic quality breach

The recommendation outcomes are modified so that recommendation quality becomes clearly unacceptable.

Expected alert:

`PRECISION_SLO_BREACH`

The synthetic data is used only to test the alerting mechanism and is clearly separated from the real baseline traffic.

### 4. Model unavailable

The model failure path returns:

```text
status = MODEL_UNAVAILABLE
fallback_action = return_no_recommendation
safe = True