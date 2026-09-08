# PlaceMux Phase 3 - Task 22
## Data-Subject Rights & Resilience

### AI/ML Focus

Stand up drift monitoring and retraining.

This task provides a deterministic and explainable baseline pipeline that:

1. Loads reference and current recommendation data.
2. Measures recommendation quality.
3. Compares score distributions.
4. Calculates Population Stability Index (PSI).
5. Measures mean score shift.
6. Detects significant drift.
7. Detects precision/recall regression.
8. Determines whether retraining is required.
9. Executes a deterministic model refresh/recalibration stage.
10. Assigns a new model version.
11. Persists the monitoring report.
12. Reloads the persisted report.
13. Validates the complete workflow end-to-end.

---

## Monitoring Metrics

### Precision

Measures how many recommended items are relevant.

### Recall

Measures how many relevant items are successfully recommended.

### FPR

Measures the proportion of irrelevant recommendations among non-relevant cases.

### PSI

Population Stability Index compares the reference score distribution with
the current score distribution.

Interpretation used by this baseline:

- PSI < 0.10: little or no drift
- PSI 0.10-0.20: moderate drift
- PSI >= 0.20: significant drift

The PSI threshold used by the demo is:

`0.20`

---

## Retraining Trigger

Retraining is required when either:

- Significant distribution drift is detected.
- Precision decreases by at least 5 percentage points.
- Recall decreases by at least 5 percentage points.

The pipeline records the trigger reason.

---

## Retraining Implementation

The current implementation intentionally uses a deterministic model
refresh/recalibration stage.

It does not pretend that a production training cluster, model registry,
feature store, scheduler, or deployment platform already exists.

The refresh creates:

`v2-drift-retrained`

Production MLOps can later replace this stage with:

- scheduled training
- feature pipelines
- model registry
- validation gates
- canary deployment
- rollback
- monitoring alerts

---

## Data

`data/drift_test_data.json`

Contains reference and current real-shaped recommendation records.

The current distribution intentionally differs from the reference
distribution so that the monitoring and retraining trigger can be
demonstrated end-to-end.

---

## Persistence

The generated report is saved to:

`logs/drift_retraining_report.json`

The demo also reloads the persisted report and validates the stored
model version, drift result, and retraining state.

---

## Limitations

This is an MLOps foundation/demo rather than a production monitoring system.

Production deployment should additionally provide:

- continuous monitoring
- alerting
- scheduled retraining
- model registry
- approval gates
- rollback
- real production traffic
- larger held-out datasets
- data-quality monitoring
- feature-level drift monitoring
- model performance monitoring
- access controls
- disaster recovery

The data in this demo is synthetic/real-shaped and should not be treated
as production monitoring evidence.

