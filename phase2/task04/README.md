# PlaceMux Phase 2 — Task 4
## Applications & Shortlisting — Match Explainability

### Objective

Add explainability to the PlaceMux marketplace matching system.

### What was implemented

The system generates a structured explanation payload alongside the match result.

The explanation identifies:

- Matched required skills
- Missing required skills
- Matched preferred skills
- Experience compatibility
- Role compatibility
- Work-mode compatibility
- Verified competency results
- Positive matching factors
- Negative matching factors
- Human-readable match summary

### Explanation Output

Every match contains:

- Student ID
- Job ID
- Match score
- Match score percentage
- Explanation payload
- Model version

### Verification

The demo verifies:

- Explanation payload generated.
- Positive factors identified.
- Negative factors identified.
- Explanation linked to the actual match score.
- Model version tracked.

### Definition of Done

Matches include a structured explanation payload that identifies the important factors contributing to the generated match.

### Model Version

`v1`