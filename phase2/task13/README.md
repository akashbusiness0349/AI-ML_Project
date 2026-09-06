# PlaceMux — Phase 2 Task 13

## Verification & Interview Scheduling

### AI/ML Focus

Proctoring false-positive reduction.

### Objective

Reduce unnecessary REVIEW decisions for normal short-lived proctoring events while preserving detection of persistent or repeated suspicious behaviour.

### Baseline

The baseline marks any detected proctoring event as REVIEW.

This provides a simple reference point but produces false positives for normal short events.

### Hardened Logic

The hardened decision layer applies persistence and repetition thresholds:

- Multiple faces -> REVIEW
- Face missing for 10 seconds or more -> REVIEW
- Three or more tab switches -> REVIEW
- Short isolated events -> NORMAL

### Metrics

The demo reports:

- False-positive rate
- Detection rate
- False-positive reduction
- Normal-case count
- Suspicious-case count
- True positives
- False positives

### Validation
