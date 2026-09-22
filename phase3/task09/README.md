# Phase 3 — Task 09
# Experimentation Platform, Feature Flags & Guardrails

## Objective

Make the intelligence layer safe to experiment on by providing:

1. Model variant serving
2. Stable traffic assignment
3. Permanent holdout
4. Offline baseline comparison
5. Guardrail metrics
6. Safe challenger shutdown
7. Model-unavailable fallback
8. Reproducible experiment logs
9. Explainable predictions
10. End-to-end validation

The operational target is:

> Ship a new model to 10% of traffic and know within days whether it is better or worse.

---

## Experiment design

The entity-level traffic allocation is:

| Group | Allocation | Policy |
|---|---:|---|
| Control | 80% | model-v1 |
| Challenger | 10% | model-v2 |
| Permanent holdout | 10% | non-ML baseline |

Assignment uses SHA-256 hashing of:

`experiment_id + salt + entity_id`

Therefore the same entity receives the same assignment across requests and process restarts.

---

## Permanent holdout

The permanent holdout is not routed to model-v1 or model-v2.

It receives a deterministic non-ML baseline.

This allows cumulative model value to be measured against a stable reference population.

The holdout is assigned at entity level rather than event level.

---

## Model variants

### model-v1

Control model.

Features:

- engagement_score
- events_1d
- events_7d
- events_14d
- days_since_last_event
- hiring_relevance

### model-v2

Challenger model.

Features:

- all model-v1 features
- engagement_velocity
- activity_intensity_7d

Both models are logistic-regression pipelines with standardized inputs.

---

## Leakage protection

The experiment uses chronological train/evaluation separation.

Future outcome labels are not included in model features.

The feature definitions are explicitly maintained in `src/model.py`.

Production implementations must construct features only from information available before the prediction timestamp.

---

## Offline evaluation

The challenger is evaluated against the control model on held-out chronological data.

The primary offline metric is Average Precision.

The experiment log reports:

- control Average Precision
- challenger Average Precision
- offline metric gap
- expected online effect

Offline improvement is not presented as proof of online causal uplift.

---

## Online effect

The declared online target is:

- primary outcome metric: outcome_rate
- expected minimum relative uplift: 5%
- measurement window: 7 days

The actual online causal effect must be measured from production randomized traffic.

A synthetic demo cannot establish a production online effect.

---

## Guardrails

The challenger is stopped when a guardrail fails.

Current guardrails:

### Hiring relevance

Minimum:

`0.70`

### Average Precision

Minimum:

`0.05`

### Error rate

Maximum:

`0.35`

If any guardrail fails:

`HALT_CHALLENGER`

The safe behavior is:

`CONTROL_MODEL_CONTINUES`

---

## Model unavailable behavior

If model-v1 or model-v2 cannot be loaded or inference fails, the serving layer uses:

`NON_ML_FALLBACK`

The fallback is deterministic and explainable.

---

## Synthetic demo data

`generate_logged_data.py` creates:

`phase3/task09/data/demo_logged_data.json`

The file is labeled:

`source_type = synthetic_demo`

This fixture exists only to verify the engineering workflow.

It must not be represented as production evidence.

For a production submission, replace the fixture with approved production logged data while preserving the validated schema.

---

## Required data contract

Each logged record contains:

- event_id
- entity_id
- entity_type
- event_timestamp
- event_type
- engagement_score
- hiring_relevance
- outcome_label

Allowed entity types:

- candidate
- company

---

## Installation

From repository root:

```bash
source /home/akash/Projects/Altrodav/venv/bin/activate

pip install -r phase3/task09/requirements.txt