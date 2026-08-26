# PlaceMux Phase 2 — Task 8
## Receipts, Refunds & Reconciliation

### Focus

Add a spend-quality guardrail to protect users from spending money on low-fit opportunities.

### Objective

The guardrail evaluates opportunity quality before a potentially paid application decision.

It uses existing matching signals to identify situations where an opportunity may provide insufficient value to the student.

### Quality Signals

The guardrail evaluates:

- Overall match score
- Skill compatibility
- Experience compatibility
- Role compatibility
- Verified competency compatibility
- Work-mode compatibility

### Guardrail Behavior

High-quality opportunities are allowed without a warning.

Low-quality opportunities generate a clear warning explaining the factors that caused the low-fit classification.

The guardrail does not automatically block the opportunity.

### Low-Fit Criteria

A warning is triggered when:

- The calculated spend-quality score falls below the configured threshold, or
- Multiple important matching signals indicate low compatibility.

### Warning

The warning informs the user that the opportunity may not provide sufficient match quality for a paid application and recommends reviewing the match factors before spending money.

### Validation

The implementation validates:

1. High-fit opportunities are not unnecessarily blocked.
2. Low-fit opportunities generate a warning.
3. Low-fit warnings contain meaningful reasons.
4. The guardrail behaves consistently.

### Model Version

`v1-spend-guardrail`

### Definition of Done

A low-fit warning is available and the spend-quality guardrail is validated against both high-fit and low-fit representative opportunities.