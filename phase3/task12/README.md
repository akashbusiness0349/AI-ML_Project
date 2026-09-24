# Phase 3 — Task 12: Personalization & Recommendation Engine

## Overview

Phase 3 Task 12 builds a two-sided personalization and recommendation engine for the PlaceMux ecosystem.

The system provides:

1. Candidate → Job recommendations
2. Company → Candidate recommendations
3. Explainable recommendation reasons
4. Offline evaluation against a baseline
5. Coverage and diversity measurement
6. Low-latency serving
7. Safe fallback behavior when the recommendation model/service is unavailable
8. Reproducible data generation, validation, training, evaluation, testing, demo, and integration workflows

### Task goal

> Recommendations should be relevant, diverse, explainable, and fast enough to serve.

The implementation is self-contained under `phase3/task12` and does not depend on Task 07 or Task 11 data files.

---

# 1. Task Structure

```text
phase3/task12/
├── README.md
├── requirements.txt
│
├── data/
│   ├── candidates.json
│   ├── companies.json
│   ├── data_provenance.json
│   ├── heldout.json
│   ├── interactions.json
│   ├── jobs.json
│   └── train.json
│
├── schemas/
│   ├── candidate_schema.json
│   ├── company_schema.json
│   ├── evaluation_schema.json
│   ├── interaction_schema.json
│   ├── job_schema.json
│   └── recommendation_schema.json
│
├── src/
│   ├── __init__.py
│   ├── baseline.py
│   ├── candidate_to_job.py
│   ├── company_to_candidate.py
│   ├── data.py
│   ├── explainability.py
│   ├── fallback.py
│   ├── features.py
│   ├── metrics.py
│   ├── recommender.py
│   ├── serving.py
│   └── validation.py
│
├── tests/
│   ├── __init__.py
│   ├── test_explainability.py
│   ├── test_fallback.py
│   ├── test_metrics.py
│   └── test_recommendations.py
│
├── run_data_generation.py
├── run_data_validation.py
├── run_demo.py
├── run_evaluation.py
├── run_explainability.py
├── run_failure_test.py
├── run_integration.py
├── run_latency_benchmark.py
└── run_training.py
```

---

# 2. Architecture

The Task 12 pipeline is organized as:

```text
                    ┌──────────────────────┐
                    │      Task 12 Data    │
                    │ candidates / jobs / │
                    │ companies / events   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Data Validation      │
                    │ Schema + integrity   │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌───────────────────┐       ┌────────────────────┐
       │ Candidate → Job   │       │ Company → Candidate │
       │ Recommendation    │       │ Recommendation     │
       └─────────┬─────────┘       └──────────┬─────────┘
                 │                            │
                 └─────────────┬──────────────┘
                               ▼
                    ┌──────────────────────┐
                    │ Ranking / Scoring    │
                    │ + Baseline           │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┼──────────────┐
                 │             │              │
                 ▼             ▼              ▼
          Explainability   Evaluation      Serving
                 │             │              │
                 ▼             ▼              ▼
             Why?         P@K / Coverage   Latency
                              Diversity      SLO
                 │             │              │
                 └─────────────┴──────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ Fallback / Safe      │
                    │ Degradation Path     │
                    └──────────────────────┘
```

---

# 3. Two-Sided Recommendation Engine

## Candidate → Job

Given a candidate profile, the system ranks jobs according to candidate-job compatibility.

Relevant ranking signals include:

- Skill overlap
- Experience compatibility
- Location compatibility
- Job/popularity or related ranking signals
- Other task-owned feature signals implemented by the feature layer

The output contains ranked jobs and recommendation metadata.

Example conceptual output:

```json
{
  "candidate_id": "candidate_001",
  "recommendations": [
    {
      "job_id": "job_007",
      "score": 0.91,
      "reason": "Strong skill overlap and matching experience level"
    }
  ]
}
```

---

# 4. Company → Candidate

The second side reverses the recommendation direction.

Given a company/job requirement, the system ranks candidates according to their compatibility with the opportunity.

Signals include:

- Required skill overlap
- Experience compatibility
- Location compatibility
- Candidate relevance/history signals where available

This creates a genuine two-sided recommendation flow rather than implementing only candidate-side recommendations.

---

# 5. Explainability

Explainability is implemented as a first-class component.

For a recommendation, the system can provide a human-readable explanation based on the contributing recommendation features.

Examples of explanation concepts:

- Strong skill overlap
- Matching experience level
- Location match
- Relevant profile characteristics
- Compatibility with the requested job/company

The objective is that the recommendation is not simply:

```text
Recommended Job: job_007
```

but instead communicates:

```text
Recommended because the candidate has strong overlap with the
required skills and matches the expected experience level.
```

The dedicated explainability runner and tests are included to verify this behavior.

---

# 6. Baseline

The recommendation engine is evaluated against a baseline implementation.

The baseline provides a simpler reference ranking strategy.

The purpose of the baseline is to establish a measurable comparison point instead of reporting recommendation quality without context.

Offline evaluation therefore compares:

```text
Baseline
   vs.
Task 12 Recommendation Engine
```

The comparison is based on the evaluation metrics implemented by the task.

---

# 7. Offline Evaluation

Task 12 evaluates recommendation quality using:

## Precision@K

Measures the fraction of recommended items in the top K that are relevant.

```text
Precision@K =
relevant recommended items / K
```

Higher values indicate that more of the returned recommendations are relevant.

---

## Coverage

Coverage measures how much of the available recommendation catalog is surfaced.

This helps detect popularity collapse.

A recommendation system should not recommend the same small set of items to every user.

---

## Diversity

Diversity measures variation among the recommended items.

This is important because a recommendation system can achieve good relevance while still producing repetitive recommendations.

The task specifically warns against:

> Popularity collapse — the same items recommended to everyone.

Therefore coverage and diversity are evaluated alongside relevance.

---

# 8. Held-Out Evaluation

The evaluation pipeline uses a held-out dataset separate from the training data.

Conceptually:

```text
All Task 12 interaction data
          │
          ├──────────────► Training data
          │
          └──────────────► Held-out evaluation data
```

The held-out portion is not used for tuning the final evaluation result.

This provides a cleaner offline estimate of recommendation quality.

---

# 9. Data Ownership

Task 12 owns its own data architecture.

The implementation does not modify or depend on Task 07 data architecture.

Task 12 contains its own:

```text
data/candidates.json
data/companies.json
data/jobs.json
data/interactions.json
data/train.json
data/heldout.json
data/data_provenance.json
```

This keeps Task 12 reproducible and independently verifiable.

---

# 10. Data Provenance

`data/data_provenance.json` records information about the Task 12 dataset and its generation.

The project distinguishes between:

```text
Task-owned evaluation data
```

and

```text
real production traffic
```

Synthetic or task-generated data must not be presented as verified production evidence.

If production/live data is unavailable, this limitation should remain explicitly documented.

---

# 11. Serving Path

The project contains a dedicated serving layer:

```text
src/serving.py
```

The serving path connects recommendation generation with a measurable latency benchmark.

The objective is not only to build an offline recommender but also to demonstrate that recommendations can be generated quickly enough for serving.

The latency benchmark is executed using:

```bash
python run_latency_benchmark.py
```

The benchmark should report the measured serving performance and whether the configured latency SLO is satisfied.

---

# 12. Failure Handling

A recommendation system must have a safe behavior when the model or recommendation service is unavailable.

Task 12 includes:

```text
src/fallback.py
run_failure_test.py
tests/test_fallback.py
```

The failure path verifies that the system does not simply crash when recommendation generation is unavailable.

Instead, the system degrades through the designed fallback behavior.

This makes the recommendation flow safer for integration with downstream consumers.

---

# 13. Demo

The end-to-end demo is provided by:

```bash
python run_demo.py
```

The demo should demonstrate:

1. Candidate → Job recommendations
2. Company → Candidate recommendations
3. Recommendation scores
4. Explainable reasons
5. Fallback behavior where applicable

This provides a direct demonstration of the recommendation engine rather than relying only on static documentation.

---

# 14. Explainability Demo

Run:

```bash
python run_explainability.py
```

This validates the explainability path and provides recommendation explanations.

A useful worked example should communicate:

```text
Input
  ↓
Recommended item
  ↓
Why it was recommended
```

The explanation should remain grounded in the actual features used by the recommendation implementation.

---

# 15. Data Validation

Run:

```bash
python run_data_validation.py
```

The validation stage checks the Task 12 dataset and validates important data integrity conditions.

The validation layer is implemented in:

```text
src/validation.py
```

Schemas are available under:

```text
schemas/
```

---

# 16. Training / Model Preparation

Run:

```bash
python run_training.py
```

This prepares the recommendation model/components used by the Task 12 recommendation pipeline.

The exact model behavior is implemented by the project source files under:

```text
src/
```

The training process is intentionally reproducible through the dedicated runner.

---

# 17. Offline Evaluation Runner

Run:

```bash
python run_evaluation.py
```

This evaluates the recommendation engine against the baseline using the implemented offline metrics.

The evaluation should report the recommendation quality metrics and comparison results.

---

# 18. Latency Benchmark

Run:

```bash
python run_latency_benchmark.py
```

This measures the serving path.

The important result is the measured latency and whether it satisfies the configured SLO.

The benchmark should be interpreted as an offline/local serving measurement unless verified production traffic exists.

---

# 19. Failure Test

Run:

```bash
python run_failure_test.py
```

This intentionally exercises the failure path.

Expected behavior:

```text
Recommendation service/model failure
            ↓
Fallback mechanism
            ↓
Safe response
```

The goal is to prove that the recommendation system has a controlled degradation path.

---

# 20. Automated Tests

Task 12 includes tests for:

```text
tests/test_explainability.py
tests/test_fallback.py
tests/test_metrics.py
tests/test_recommendations.py
```

Run:

```bash
pytest -q
```

These tests cover important recommendation, metric, explainability, and fallback behavior.

---

# 21. Full Integration

The complete workflow is orchestrated through:

```bash
python run_integration.py
```

The integration flow is intended to verify the Task 12 journey end-to-end.

The overall workflow is:

```text
Data
 ↓
Validation
 ↓
Recommendation preparation
 ↓
Training
 ↓
Offline evaluation
 ↓
Explainability
 ↓
Failure handling
 ↓
Latency benchmark
 ↓
Demo
```

---

# 22. Recommended Verification Sequence

From the repository root:

```bash
cd /home/akash/Projects/Altrodav/phase3/task12
```

Then run:

```bash
python -m py_compile run_data_generation.py run_data_validation.py run_training.py run_evaluation.py run_explainability.py run_failure_test.py run_demo.py run_latency_benchmark.py run_integration.py src/*.py tests/*.py
```

Run tests:

```bash
pytest -q
```

Generate/verify data:

```bash
python run_data_generation.py
python run_data_validation.py
```

Train:

```bash
python run_training.py
```

Evaluate:

```bash
python run_evaluation.py
```

Explainability:

```bash
python run_explainability.py
```

Failure path:

```bash
python run_failure_test.py
```

Latency:

```bash
python run_latency_benchmark.py
```

Demo:

```bash
python run_demo.py
```

Finally:

```bash
python run_integration.py
```

---

# 23. Reproducibility

The Task 12 implementation is organized into deterministic, independently runnable stages.

Important reproducibility artifacts include:

- Owned dataset files
- Data provenance
- Schemas
- Training runner
- Evaluation runner
- Explainability runner
- Failure test
- Latency benchmark
- Unit tests
- Integration runner

This allows another reviewer to reproduce the workflow from the repository.

---

# 24. Safety and Limitations

## Production data limitation

If the dataset is synthetic/task-generated, results must be interpreted as offline evidence rather than production evidence.

Real production logs would provide stronger evidence of real-world recommendation performance.

## Online experiment limitation

Offline metrics do not establish actual online impact.

A production A/B test would be required to measure changes in real-world:

- Click-through rate
- Application rate
- Engagement
- Candidate/company conversion

## Serving limitation

A local latency benchmark demonstrates measured serving performance in the tested environment. It should not automatically be interpreted as a production SLO guarantee.

---

# 25. Expected End State

Task 12 is designed to satisfy the following completion criteria:

### Two-sided recommendation engine

```text
Candidate → Jobs
Company → Candidates
```

### Explainability

```text
Recommendation
      +
Plain-English reason
```

### Offline evaluation

```text
Precision@K
Coverage
Diversity
Baseline comparison
```

### Serving

```text
Recommendation API/path
      ↓
Latency measurement
      ↓
SLO validation
```

### Reliability

```text
Failure
   ↓
Fallback
   ↓
Safe response
```

### Verification

```text
Unit tests
Integration test
Demo
Latency benchmark
```

---

# 26. Submission Summary

Phase 3 Task 12 implements an end-to-end two-sided personalization and recommendation engine for the PlaceMux intelligence layer.

The system supports both candidate-to-job and company-to-candidate recommendations, provides explainable recommendation reasons, evaluates recommendation quality against a baseline using relevance, coverage, and diversity metrics, and includes a dedicated serving path with latency benchmarking.

The project also includes explicit fallback handling, data validation, reproducible task-owned datasets, automated tests, an end-to-end integration runner, and a demonstration path.

The implementation is structured so that the recommendation pipeline can be handed off to the frontend/API integration layer.

---

# 27. Important Evidence to Include in Submission

For the strongest submission, include actual terminal output/evidence for:

1. `run_data_generation.py`
2. `run_data_validation.py`
3. `run_training.py`
4. `run_evaluation.py`
5. `run_explainability.py`
6. `run_failure_test.py`
7. `run_latency_benchmark.py`
8. `pytest -q`
9. `run_demo.py`
10. `run_integration.py`

Also include a short worked recommendation example showing:

```text
Input
→ Recommendation
→ Score
→ Explanation / Why
```

And clearly distinguish offline/task-generated evidence from verified production/live evidence.

---

# 28. GitHub Submission Commands

Run these from the repository root:

```bash
git add phase3/task12
```

```bash
git commit -m "Complete Phase 3 Task 12 personalization recommendation engine"
```

```bash
git push origin main
```

If your repository uses another branch, replace `main` with that branch name.

---

# END OF TASK 12 README CONTENT