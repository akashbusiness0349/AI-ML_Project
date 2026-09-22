# Phase 3 — Task 10
# Model Experiment, A/B Replay, Guardrails & Safe Decision

## Objective

Run the first model experiment end-to-end with:

- preregistered hypothesis
- fixed primary metric
- chronological held-out evaluation
- baseline comparison
- effect size
- statistical significance
- guardrails
- explainability
- safe fallback
- executable A/B replay demo
- final ship/do-not-ship decision

## Data Provenance

The verified dataset used by this implementation originates from
Phase 3 Task 08.

Task 08 explicitly documents that no production dataset was available.
Therefore the dataset is marked `synthetic_demo`.

This implementation does NOT present synthetic results as production
performance.

Production/live causal A/B validation remains NOT ESTABLISHED.

## Experimental Design

Data split:

- 60% chronological training
- 20% chronological validation
- 20% chronological holdout

Model:

- Logistic Regression
- standardized behavioral features

Baseline:

- non-ML recency score

Features:

- event_count_14d
- active_days_14d
- days_since_last_activity
- event_type_diversity_14d
- recent_3d_events
- recent_7d_events
- activity_rate_14d

Target:

- churn_label

Future-horizon information is excluded from prediction features.

## Preregistration

The experiment uses a locked preregistration.

Primary offline metric:

- held-out model average precision

Secondary replay metric:

- 14-day churn rate

Alpha:

- 0.05

Minimum relative effect:

- 5%

## A/B Replay

The implementation deterministically assigns entities to:

- control
- treatment

using SHA-256 hashing.

The replay calculates:

- control outcome rate
- treatment outcome rate
- absolute effect
- relative effect
- z-score
- p-value
- 95% confidence interval

Important:

This is an offline historical replay, not a causal production A/B test.

## Explainability

The model exposes:

- feature coefficients
- direction of effect
- worked prediction example

## Safe Fallback

When the ML model is unavailable, the system falls back to
the non-ML recency baseline.

## Final Decision

Production shipment requires:

1. preregistered statistical guardrails
2. verified production data
3. genuine online/live causal evidence

Because verified production/live data is unavailable in this repository,
the final decision is expected to be:

DO_NOT_SHIP