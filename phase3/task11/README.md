# Phase 3 Task 11 — Matching & Ranking v2

## Learning-to-Rank

This task implements a reproducible Learning-to-Rank pipeline for job
matching and ranking.

The implementation is independent of Task 07.

## Objectives

The system demonstrates:

1. Pairwise Learning-to-Rank.
2. Logged impression training.
3. Position-bias correction.
4. Held-out offline ranking evaluation.
5. nDCG@5 and nDCG@10.
6. MAP.
7. Precision@5.
8. Comparison against a heuristic ranking baseline.
9. Explainability.
10. Model-unavailable fallback.
11. Executable ranking demo.
12. Reproducible evidence artifacts.

## Architecture

```text
Task 11 Dataset
       |
       v
Data Validation
       |
       v
Position Bias Estimation
       |
       v
Pairwise LTR Training
       |
       v
Held-out Evaluation
       |
       +---- nDCG
       +---- MAP
       +---- Precision@K
       |
       v
Explainability
       |
       v
Failure / Fallback Test
       |
       v
Executable Demo
       |
       v
Integration Summary