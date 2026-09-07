# PlaceMux Phase 2 Task 21
## DPDP Consent & Security Foundations — Initial Fairness / Bias Audit

### Objective

Start the fairness and bias audit for the PlaceMux recommendation layer.

The implementation provides an explainable first-pass audit of recommendation outcomes across synthetic or real-shaped audit groups.

---

## AI / ML Focus

Fairness audit (start).

The audit compares recommendation outcomes across groups using:

- Selection rate
- True-positive rate
- False-positive rate
- Precision
- Selection-rate disparity
- TPR disparity
- FPR disparity
- Precision disparity
- Disparate impact ratio

---

## Data

The demo uses real-shaped recommendation records containing:

- student ID
- job ID
- college ID
- audit group
- recommendation decision
- relevance label

Group labels are synthetic audit segments and are not intended to represent protected attributes.

---

## Method

For each group:

1. Count recommendation decisions.
2. Count relevant recommendations.
3. Calculate selection rate.
4. Calculate true-positive rate.
5. Calculate false-positive rate.
6. Calculate precision.
7. Compare group-level metrics.
8. Calculate disparity measures.
9. Persist the audit report.

---

## Explainability

The audit reports the underlying group-level counts and metrics so an administrator can understand where a disparity comes from.

The audit is not a black-box fairness score.

---

## Important Interpretation

Fairness metrics are diagnostic signals.

A disparity does not automatically prove discrimination or unfair treatment.

Similarly, a low measured disparity does not prove that a production system is completely fair.

Production fairness review should consider:

- sufficient sample size
- feature validity
- label quality
- protected-group definitions where legally appropriate
- intersectional groups
- historical bias
- model drift
- human review
- domain and legal requirements

---

## Persistence

The generated report is stored at:

`logs/fairness_audit_report.json`

The demo reloads the persisted report and verifies its core values.

---

## Running the Demo
