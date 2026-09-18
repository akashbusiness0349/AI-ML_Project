# Phase 3 — Task 07
## Activation & Onboarding Funnel Optimization

AI / ML Engineer · Sprint B - Growth & Experimentation

### Objective

Improve first-session activation for cold-start candidates with no interaction history.

The system provides:

1. Cold-start recommendations using candidate profile, skills, job relevance, popularity and controlled exploration.
2. Baseline comparison using popularity-only ranking.
3. Offline evaluation on held-out interaction data.
4. First-session relevant-action measurement.
5. A non-empty fallback when the recommendation model is unavailable.
6. Plain-English recommendation explanations.
7. Reproducible experiment and validation evidence.
8. End-to-end failure testing.

### Cold-start strategy

The ranking score combines:

- Skill/profile relevance
- Popularity prior
- Controlled exploration

No historical clicks, applications or shortlist history are required.

### Baseline

The baseline is popularity-only ranking.

### Primary metrics

Offline:

- Precision@5
- Recall@5
- nDCG@5
- MAP@5

Activation:

- First-session relevant-action rate
- First-session click rate
- First-session application rate
- First-session shortlist rate

### Safety

If the recommendation model is unavailable, the system falls back to a non-empty popularity-based recommendation set.

The fallback is never allowed to return an empty list when eligible jobs exist.

### Reproducibility

Run:

    python -m py_compile phase3/task07/run_task07_demo.py phase3/task07/run_task07_integration.py phase3/task07/src/*.py

    python phase3/task07/run_task07_demo.py

    python phase3/task07/run_task07_integration.py

Evidence is written to:

    phase3/task07/logs/