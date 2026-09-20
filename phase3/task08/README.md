# Phase 3 — Task 08
# Churn & Disengagement Prediction

## Objective

Build and evaluate a churn/disengagement prediction pipeline with:

- strict churn label
- fixed prediction horizon
- temporal feature construction
- target leakage prevention
- chronological held-out evaluation
- Precision-Recall evaluation
- non-ML baseline
- lift measurement
- prioritized at-risk list
- explainable risk reasons
- safe model-unavailable fallback
- reproducible experiment evidence

---

## Important Data Availability Note

The Task 08 assignment did not provide a production dataset.

Therefore this implementation includes a deterministic synthetic demo dataset
for demonstrating the complete end-to-end engineering workflow.

The synthetic dataset is explicitly marked:

    synthetic_demo

Synthetic metrics must NOT be presented as production performance.

When real production event data becomes available, the same pipeline can be
run against it using the `--data` argument and:

    --source-type production

---

# Data Contract

The pipeline expects JSON events with:

- entity_id
- entity_type
- timestamp
- event_type

Example:

```json
[
  {
    "entity_id": "candidate_001",
    "entity_type": "candidate",
    "timestamp": "2026-01-10T10:30:00Z",
    "event_type": "login"
  }
]