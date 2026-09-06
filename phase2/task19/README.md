# PlaceMux Phase 2 Task 19 — Bulk Onboarding & Recruiter Views

## Task Objective

Build item-bank quality support for administrators and provide explainable weak-item flags.

## AI / ML Focus

Support item-bank quality through deterministic item analytics and explainable weak-item detection.

## Founder Verification

The founder should be able to verify:

1. Bulk student/item onboarding support.
2. Recruiter/admin quality analytics.
3. Weak-item flags.
4. Explainable reasons behind every review flag.
5. College-level data isolation.

---

# 1. Problem Statement

A placement platform may contain a large number of assessment questions.

Not every question remains useful over time.

An item can become problematic because:

- Too few students attempted it.
- Very few students answered it correctly.
- Almost everyone answered it correctly.
- Strong and weak performers answer it at similar rates.
- The question may be ambiguous.

Task 19 provides an explainable baseline that identifies these cases and exposes them as administrator review flags.

---

# 2. Pipeline

```text
Item Bank
    |
    v
Item Analytics
    |
    +--> Attempt Count
    |
    +--> Overall Accuracy
    |
    +--> High Performer Accuracy
    |
    +--> Low Performer Accuracy
    |
    +--> Discrimination
    |
    v
Weak Item Detection
    |
    v
Explainable Review Reasons
    |
    v
Admin REVIEW / KEEP Flag
    |
    v
Persisted Quality Report