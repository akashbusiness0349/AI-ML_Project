# PlaceMux — Phase 2 Task 11
## Proctoring Hardening

### Objective

Begin hardening the PlaceMux AI/ML proctoring layer with a focus on reducing false-positive review signals while preserving detection capability.

### Proctoring Signals

The evaluation considers:

- Face visibility
- Multiple-face detection
- Tab switching
- Camera obstruction

These signals are treated as review indicators and are not considered proof of misconduct.

### Baseline

The baseline logic creates a review signal whenever a configured event is detected.

This provides a simple baseline but can incorrectly escalate short-lived legitimate events.

### Hardening Approach

The hardened logic introduces persistence requirements.

Short-lived isolated events are not immediately escalated.

Persistent events are escalated for review.

### Evaluation

The test dataset contains:

- Normal scenarios
- Persistent scenarios
- Edge-relevant detection scenarios

### Metrics

#### False-positive rate

Percentage of normal scenarios incorrectly escalated for review.

#### Detection rate

Percentage of synthetic suspicious scenarios escalated for review.

#### False-positive reduction

Reduction in false-positive rate after applying the hardening logic.

### Demo

Run:

```bash
python phase2/task11/run_task11_demo.py