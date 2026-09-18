# Phase 3 — Task 06: Growth Instrumentation & North-Star Metrics

## Objective

Instrument the intelligence layer for growth by capturing impression, click, apply, and shortlist events for ranked results.

The system records enough information to reconstruct exactly what was shown, in what order, by which model version, and what happened afterward.

## Core Requirements

- Impression/click/apply/shortlist event schema
- Position logging for every ranked result
- Model-version logging for every ranked result
- Joinable outcome attribution
- Real upstream logged data
- Held-out validation
- End-to-end event flow
- Real-volume event generation
- Explainable ranking example
- Model-unavailable fallback
- Reproducible experiment evidence

## North-Star Metrics

The instrumentation supports:

- Impression volume
- Click-through rate
- Apply-through rate
- Shortlist-through rate
- Click-to-apply rate
- Apply-to-shortlist rate
- Position-level click rate
- Position-level apply rate
- Position-level shortlist rate

## Event Identity

Every event contains:

- event_id
- impression_id
- request_id
- ranked_list_id
- user_id
- item_id
- event_type
- position
- model_version
- timestamp

Outcome events reuse the original impression_id and ranked_list_id so the complete user journey can be reconstructed.

## Model Version

The ranking implementation uses:

`skill-ranker-v1.0.0`

Every ranked item stores the model version that produced its position.

## Failure Behavior

If the ranking model is unavailable, the system returns a safe degraded response:

- status: degraded
- error_code: MODEL_UNAVAILABLE
- model_available: false
- recommendation: NO_RANKING

No fabricated ranking or outcome is emitted.

## Evidence

The demo produces:

- event_log.json
- ranked_lists.json
- journey_trace.json
- schema_validation.json
- volume_results.json
- heldout_results.json
- failure_test.json
- explainability_example.json
- north_star_metrics.json
- experiment_log.csv
- final_signoff.json

## Reproducibility

The complete Task 06 workflow is executable through:

`python phase3/task06/run_task06_demo.py`

The integration validation is executable through:

`python phase3/task06/run_task06_integration.py`