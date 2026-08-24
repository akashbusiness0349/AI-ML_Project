# PlaceMux Phase 2 — Task 6
## Payments Design & Gateway Setup

### Focus

Establish a reliable match-quality baseline before monetization or payment-related changes affect marketplace matching behavior.

### Objective

The current marketplace matching system is evaluated using representative job and candidate ranking data.

The baseline provides a reference point for measuring whether future monetization changes improve, preserve, or degrade matching quality.

### Metrics

The baseline records:

- Average match score
- Top-1 relevance
- Top-3 relevance
- Ranking consistency
- High-quality match rate
- Low-quality match rate
- Overall baseline quality
- Model version

### Quality thresholds

High-quality match:

`match_score >= 0.80`

Low-quality match:

`match_score < 0.50`

### Validation

The system also repeats the same ranking inputs to verify that the current matching behavior is deterministic and consistent.

### Purpose for future monetization work

This baseline acts as the pre-monetization control measurement.

Future payment or monetization changes can be evaluated against this baseline to identify:

- Matching quality improvement
- Matching quality degradation
- Ranking instability
- Changes in relevance
- Changes in high-quality match rate

### Model Version

`v1`

### Definition of Done

A match-quality baseline is recorded successfully and can be used as a reference for future monetization experiments.