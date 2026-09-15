# Phase 3 — Task 03: Performance Profiling & Bottleneck Elimination

## Objective

Profile the inference path, identify the dominant latency stage, optimize the serving path without changing prediction quality, and produce runtime-generated before/after latency and cost evidence.

## Latency SLO

The intelligence-layer latency target used for this task is:

- p95 inference latency <= 100 ms

Task 03 independently measures its own baseline. It does not reuse Task 01 or Task 02 benchmark measurements.

## Implementation

The baseline implementation performs straightforward nested skill matching.

The optimized implementation:

1. Builds a reusable skill vocabulary.
2. Assigns each skill an integer index.
3. Converts skill sets into integer bitsets.
4. Calculates overlap using bitwise AND.
5. Uses the same scoring formula.
6. Uses the same recommendation threshold.

Therefore the optimization changes the computational representation, not the prediction policy.

## Validation

The original 10-record dataset is used for functional quality validation.

The benchmark runner additionally creates a deterministic stress workload with a fixed seed. The stress workload contains larger skill vectors so that the algorithmic difference between nested matching and indexed matching can be measured.

The stress workload is explicitly benchmark data and is not represented as production traffic.

## Runtime Evidence

The runner generates:

- `logs/latency_profile.json`
- `logs/benchmark_results.json`
- `logs/quality_comparison.json`
- `logs/explainability_example.json`
- `logs/cost_comparison.json`
- `logs/training_benchmark.json`
- `logs/failure_path.json`
- `logs/task03_summary.json`

All performance numbers are generated at runtime.

No latency, quality, cost, or training-runtime result is hard-coded.

## Run

From the task directory:

```bash
python run_task03_demo.py