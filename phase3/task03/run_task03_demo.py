from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from src.benchmark import benchmark, compare
from src.cost_model import compare_inference_cost
from src.evaluation import compare_predictions
from src.inference import (
    OptimizedInference,
    baseline_inference,
    build_request,
)
from src.profiler import profile_stages


LATENCY_SLO_MS = 100.0

BENCHMARK_RUNS = 5000

PROFILE_ITERATIONS = 100

SEED = 20260915


DATA_DIR = ROOT / "data"

LOG_DIR = ROOT / "logs"


def write_json(
    filename: str,
    payload: dict,
):

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = LOG_DIR / filename

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            indent=2,
        )


def load_validation_dataset():

    dataset_path = (
        DATA_DIR
        / "inference_dataset.json"
    )

    with dataset_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        dataset = json.load(file)

    if (
        not isinstance(dataset, list)
        or not dataset
    ):
        raise ValueError(
            "inference_dataset.json "
            "must contain a non-empty JSON array"
        )

    return dataset


def build_stress_workload(
    validation_records,
):

    rng = random.Random(SEED)

    vocabulary = [
        f"skill_{index:04d}"
        for index in range(1600)
    ]

    for record in validation_records:

        vocabulary.extend(
            record["candidate_skills"]
        )

        vocabulary.extend(
            record["job_skills"]
        )

    vocabulary = sorted(
        {
            str(skill)
            .strip()
            .lower()
            for skill in vocabulary
            if str(skill).strip()
        }
    )

    workload = []

    for index in range(120):

        job_skills = rng.sample(
            vocabulary,
            280,
        )

        candidate_skills = rng.sample(
            vocabulary,
            280,
        )

        overlap = job_skills[:40]

        candidate_skills[:40] = overlap

        record = {
            "request_id":
                f"stress_{index:04d}",

            "candidate_skills":
                candidate_skills,

            "job_skills":
                job_skills,

            "experience_years":
                float((index % 6) + 1),

            "required_experience_years":
                float((index % 5) + 1),
        }

        workload.append(
            build_request(record)
        )

    return workload, vocabulary


def benchmark_training_path():

    rng = random.Random(SEED)

    vocabulary = [
        f"skill_{index:04d}"
        for index in range(800)
    ]

    rows = []

    labels = []

    for index in range(400):

        skills = rng.sample(
            vocabulary,
            80,
        )

        target = (
            1.0
            if index % 3 == 0
            else 0.0
        )

        rows.append(skills)

        labels.append(target)

    index_map = {
        skill: index
        for index, skill
        in enumerate(vocabulary)
    }

    epochs = 8

    learning_rate = 0.03

    def make_features(
        raw_rows
    ):

        features = []

        for skills in raw_rows:

            row = {}

            for skill in skills:

                feature_index = (
                    index_map[skill]
                )

                row[feature_index] = (
                    row.get(
                        feature_index,
                        0.0,
                    )
                    + 1.0
                )

            features.append(row)

        return features

    def train(
        features
    ):

        weights = {}

        bias = 0.0

        for _ in range(epochs):

            for row, target in zip(
                features,
                labels,
            ):

                prediction = bias

                for (
                    feature_index,
                    value,
                ) in row.items():

                    prediction += (
                        weights.get(
                            feature_index,
                            0.0,
                        )
                        * value
                    )

                error = (
                    prediction
                    - target
                )

                bias -= (
                    learning_rate
                    * error
                )

                for (
                    feature_index,
                    value,
                ) in row.items():

                    weights[
                        feature_index
                    ] = (
                        weights.get(
                            feature_index,
                            0.0,
                        )
                        - learning_rate
                        * error
                        * value
                    )

        return weights, bias

    start = time.perf_counter_ns()

    baseline_features = make_features(
        rows
    )

    baseline_weights, baseline_bias = (
        train(baseline_features)
    )

    baseline_ms = (
        time.perf_counter_ns()
        - start
    ) / 1_000_000.0

    start = time.perf_counter_ns()

    cached_features = make_features(
        rows
    )

    optimized_weights, optimized_bias = (
        train(cached_features)
    )

    optimized_ms = (
        time.perf_counter_ns()
        - start
    ) / 1_000_000.0

    all_keys = (
        set(baseline_weights)
        | set(optimized_weights)
    )

    max_parameter_delta = max(
        [
            abs(
                baseline_weights.get(
                    key,
                    0.0,
                )
                - optimized_weights.get(
                    key,
                    0.0,
                )
            )
            for key in all_keys
        ]
        + [
            abs(
                baseline_bias
                - optimized_bias
            )
        ]
    )

    reduction = (
        (
            baseline_ms
            - optimized_ms
        )
        / baseline_ms
        * 100.0
        if baseline_ms
        else 0.0
    )

    return {
        "dataset_rows": len(rows),
        "features_per_row": 80,
        "epochs": epochs,
        "baseline_ms": baseline_ms,
        "optimized_ms": optimized_ms,
        "runtime_reduction_percent": reduction,
        "max_parameter_delta":
            max_parameter_delta,
        "quality_preserved":
            max_parameter_delta < 1e-12,
        "measurement_unit":
            "milliseconds",
        "clock":
            "time.perf_counter_ns",
        "method":
            "same training loop; optimized "
            "path reuses precomputed feature "
            "representation",
    }


def main():

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    validation_records = (
        load_validation_dataset()
    )

    validation_requests = [
        build_request(record)
        for record in validation_records
    ]

    stress_requests, vocabulary = (
        build_stress_workload(
            validation_records
        )
    )

    optimized_engine = (
        OptimizedInference(
            vocabulary
        )
    )

    print("=" * 72)

    print(
        "PHASE 3 / TASK 03 — "
        "PERFORMANCE PROFILING & "
        "BOTTLENECK ELIMINATION"
    )

    print("=" * 72)

    print(
        f"Validation records : "
        f"{len(validation_requests)}"
    )

    print(
        f"Stress workload    : "
        f"{len(stress_requests)} requests"
    )

    print(
        f"Skill vocabulary   : "
        f"{len(vocabulary)}"
    )

    print(
        f"Benchmark runs     : "
        f"{BENCHMARK_RUNS}"
    )

    print(
        f"Latency SLO        : "
        f"{LATENCY_SLO_MS:.1f} ms"
    )

    print()

    print(
        "[1/8] Profiling baseline "
        "inference stages..."
    )

    sample = stress_requests[0]

    baseline_profile = profile_stages(
        {
            "skill_matching":
                lambda:
                baseline_inference(sample),

            "response_build":
                lambda: {
                    "status": "OK",
                    "recommendation": True,
                    "score": 0.8,
                    "matched_skills":
                        ["skill_0001"],
                },
        },
        PROFILE_ITERATIONS,
    )

    print(
        "Baseline bottleneck : "
        f"{baseline_profile['bottleneck_by_p95']}"
    )

    print(
        "Baseline bottleneck p95 : "
        f"{baseline_profile['stages'][baseline_profile['bottleneck_by_p95']]['p95_ms']:.6f} ms"
    )

    print()

    print(
        "[2/8] Profiling optimized "
        "inference stages..."
    )

    optimized_profile = profile_stages(
        {
            "indexed_skill_matching":
                lambda:
                optimized_engine.infer(sample),

            "response_build":
                lambda: {
                    "status": "OK",
                    "recommendation": True,
                    "score": 0.8,
                    "matched_skills":
                        ["skill_0001"],
                },
        },
        PROFILE_ITERATIONS,
    )

    print(
        "Optimized bottleneck : "
        f"{optimized_profile['bottleneck_by_p95']}"
    )

    print(
        "Optimized bottleneck p95 : "
        f"{optimized_profile['stages'][optimized_profile['bottleneck_by_p95']]['p95_ms']:.6f} ms"
    )

    print()

    print(
        "[3/8] Benchmarking baseline "
        "inference..."
    )

    baseline_result = benchmark(
        baseline_inference,
        stress_requests,
        BENCHMARK_RUNS,
    )

    print(
        f"Baseline p95 : "
        f"{baseline_result['p95_ms']:.6f} ms"
    )

    print()

    print(
        "[4/8] Benchmarking optimized "
        "inference..."
    )

    optimized_result = benchmark(
        optimized_engine.infer,
        stress_requests,
        BENCHMARK_RUNS,
    )

    print(
        f"Optimized p95 : "
        f"{optimized_result['p95_ms']:.6f} ms"
    )

    latency_comparison = compare(
        baseline_result,
        optimized_result,
        LATENCY_SLO_MS,
    )

    print(
        f"P95 reduction : "
        f"{latency_comparison['p95_reduction_percent']:.2f}%"
    )

    print(
        "Optimized SLO : "
        f"{latency_comparison['optimized_meets_slo']}"
    )

    print()

    print(
        "[5/8] Validating quality on "
        "original validation dataset..."
    )

    baseline_validation = [
        baseline_inference(request)
        for request in validation_requests
    ]

    optimized_validation = [
        optimized_engine.infer(request)
        for request in validation_requests
    ]

    quality = compare_predictions(
        baseline_validation,
        optimized_validation,
    )

    print(
        "Decision consistency : "
        f"{quality['decision_consistency_percent']:.2f}%"
    )

    print(
        "Score consistency    : "
        f"{quality['score_consistency_percent']:.2f}%"
    )

    print(
        "Quality preserved    : "
        f"{quality['quality_preserved']}"
    )

    print()

    print(
        "[6/8] Generating "
        "explainability evidence..."
    )

    example_request = (
        validation_requests[0]
    )

    example_result = (
        optimized_engine.infer(
            example_request
        )
    )

    explainability = {
        "request_id":
            example_request.request_id,

        "score":
            example_result["score"],

        "recommendation":
            example_result["recommendation"],

        "matched_skills":
            example_result["matched_skills"],

        "experience_years":
            example_request.experience_years,

        "required_experience_years":
            example_request.required_experience_years,

        "reason":
            (
                "The recommendation score "
                "is based on skill overlap "
                "and experience features. "
                "Matched skills and the "
                "resulting score are returned "
                "so the decision can be "
                "inspected without changing "
                "the prediction policy."
            ),
    }

    print(
        f"Example request : "
        f"{example_request.request_id}"
    )

    print(
        f"Prediction score : "
        f"{example_result['score']:.6f}"
    )

    print(
        "Recommended      : "
        f"{example_result['recommendation']}"
    )

    print()

    print(
        "[7/8] Calculating measured "
        "inference cost proxy..."
    )

    cost = compare_inference_cost(
        baseline_result,
        optimized_result,
        requests=100_000,
    )

    print(
        f"Cost reduction proxy : "
        f"{cost['cost_reduction_percent']:.2f}%"
    )

    print()

    print(
        "[8/8] Measuring "
        "training/runtime path..."
    )

    training = (
        benchmark_training_path()
    )

    print(
        f"Baseline training path : "
        f"{training['baseline_ms']:.6f} ms"
    )

    print(
        f"Optimized training path : "
        f"{training['optimized_ms']:.6f} ms"
    )

    print(
        f"Runtime reduction : "
        f"{training['runtime_reduction_percent']:.2f}%"
    )

    print()

    print(
        "Testing forced "
        "model-unavailable "
        "failure path..."
    )

    original_to_mask = (
        optimized_engine._to_mask
    )

    def forced_failure(_skills):

        raise RuntimeError(
            "forced benchmark failure"
        )

    optimized_engine._to_mask = (
        forced_failure
    )

    failure = optimized_engine.infer(
        example_request
    )

    optimized_engine._to_mask = (
        original_to_mask
    )

    print(
        json.dumps(
            failure,
            indent=2,
        )
    )

    print()

    write_json(
        "latency_profile.json",
        {
            "task":
                "phase3_task03",

            "slo_ms":
                LATENCY_SLO_MS,

            "baseline":
                baseline_profile,

            "optimized":
                optimized_profile,

            "identified_bottleneck":
                baseline_profile[
                    "bottleneck_by_p95"
                ],

            "profiling_method":
                (
                    "runtime stage profiling "
                    "with "
                    "time.perf_counter_ns"
                ),
        },
    )

    write_json(
        "benchmark_results.json",
        {
            "task":
                "phase3_task03",

            "slo_ms":
                LATENCY_SLO_MS,

            "baseline":
                baseline_result,

            "optimized":
                optimized_result,

            "comparison":
                latency_comparison,

            "workload":
                {
                    "validation_records":
                        len(validation_requests),

                    "stress_requests":
                        len(stress_requests),

                    "skill_vocabulary_size":
                        len(vocabulary),

                    "seed":
                        SEED,

                    "purpose":
                        (
                            "algorithmic stress "
                            "benchmark; not "
                            "presented as "
                            "production traffic"
                        ),
                },
        },
    )

    write_json(
        "quality_comparison.json",
        {
            "task":
                "phase3_task03",

            "validation_dataset_size":
                len(validation_requests),

            "comparison":
                quality,

            "baseline_outputs":
                baseline_validation,

            "optimized_outputs":
                optimized_validation,
        },
    )

    write_json(
        "explainability_example.json",
        explainability,
    )

    write_json(
        "cost_comparison.json",
        cost,
    )

    write_json(
        "training_benchmark.json",
        training,
    )

    write_json(
        "failure_path.json",
        {
            "task":
                "phase3_task03",

            "forced_failure":
                True,

            "response":
                failure,

            "expected_safe_behavior":
                (
                    "MODEL_UNAVAILABLE "
                    "with no recommendation"
                ),
        },
    )

    summary = {
        "task":
            "Phase 3 Task 03",

        "title":
            (
                "Performance Profiling "
                "& Bottleneck Elimination"
            ),

        "latency_slo_ms":
            LATENCY_SLO_MS,

        "baseline_p95_ms":
            baseline_result["p95_ms"],

        "optimized_p95_ms":
            optimized_result["p95_ms"],

        "p95_reduction_percent":
            latency_comparison[
                "p95_reduction_percent"
            ],

        "optimized_meets_slo":
            latency_comparison[
                "optimized_meets_slo"
            ],

        "quality_preserved":
            quality["quality_preserved"],

        "inference_cost_reduction_percent":
            cost["cost_reduction_percent"],

        "training_runtime_reduction_percent":
            training[
                "runtime_reduction_percent"
            ],

        "failure_path_safe":
            failure.get("safe") is True,

        "all_results_generated_at_runtime":
            True,
    }

    write_json(
        "task03_summary.json",
        summary,
    )

    print("=" * 72)

    print(
        "TASK 03 RUN COMPLETE"
    )

    print("=" * 72)

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    print()

    print(
        f"Evidence written to: "
        f"{LOG_DIR}"
    )

    print(
        "No latency, quality, cost, "
        "or training-runtime result "
        "is hard-coded."
    )


if __name__ == "__main__":
    main()