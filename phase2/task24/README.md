# PlaceMux Phase 3 - Task 24

## Launch Rehearsal

Task 24 closes the initial fairness audit and records a model sign-off for launch rehearsal.

## Objective

- Close the Task 21 fairness audit.
- Recalculate fairness metrics.
- Verify all audit groups.
- Persist fairness evidence.
- Record model version and sign-off status.
- Produce a demoable launch-rehearsal handoff.

## Model

Model version:

`v1-fairness-audit`

Sign-off version:

`v1-launch-signoff`

## Metrics

The audit reports:

- Selection-rate disparity
- True-positive-rate disparity
- False-positive-rate disparity
- Precision disparity
- Disparate-impact ratio

## Sign-off

The model is marked:

`APPROVED_WITH_LIMITATIONS`

Launch recommendation:

`CONTROLLED_LAUNCH`

This is intentional because the audit sample is small and the measured disparate-impact ratio remains a governance review finding.

## Evidence

The demo persists:

`logs/fairness_signoff_report.json`

and:

`logs/launch_rehearsal_result.json`

## Important limitation

The dataset is synthetic/real-shaped and small.

The results are suitable for launch rehearsal and engineering evidence, but they are not a production fairness certification.

A production launch would require larger representative data, continued monitoring, governance review, and periodic fairness reassessment.

## Definition of Done

- Fairness close complete.
- Audit evidence persisted.
- Metrics recalculated.
- Limitations documented.
- Model version recorded.
- Sign-off persisted.
- End-to-end demo completed.
- ML go-ahead handoff produced.