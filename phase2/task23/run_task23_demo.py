from pathlib import Path

from src.mlops_foundation import (
    load_data,
    save_json,
    load_json,
    create_feature_store,
    evaluate_predictions,
    create_registry,
    validate_registry,
    run_inference,
    build_mlops_report
)


BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "mlops_test_data.json"

REGISTRY_PATH = (
    BASE_DIR
    / "registry"
    / "model_registry.json"
)

FEATURE_STORE_PATH = (
    BASE_DIR
    / "feature_store"
    / "feature_store.json"
)

REPORT_PATH = (
    BASE_DIR
    / "logs"
    / "mlops_foundation_report.json"
)


def pct(value):
    return f"{value * 100:.2f}%"


def main():
    print("=" * 60)
    print("PlaceMux Phase 3 - Task 23")
    print("Hardening, Scale & MLOps")
    print("=" * 60)

    data = load_data(DATA_PATH)

    print("\n--- Input Data ---")
    print(
        f"Candidates : {len(data['features'])}"
    )
    print(
        f"Jobs       : {len(data['jobs'])}"
    )
    print(
        f"Evaluation records : {len(data['labels'])}"
    )

    assert len(data["features"]) >= 3
    assert len(data["jobs"]) >= 2

    print("Real-shaped sample data : PASS")

    # ---------------------------------------------------------
    # Feature Store
    # ---------------------------------------------------------

    feature_store = create_feature_store(data)

    save_json(
        feature_store,
        FEATURE_STORE_PATH
    )

    persisted_feature_store = load_json(
        FEATURE_STORE_PATH
    )

    assert (
        persisted_feature_store["feature_store_version"]
        == "v1"
    )

    assert len(
        persisted_feature_store["candidates"]
    ) == 3

    assert len(
        persisted_feature_store["jobs"]
    ) == 2

    print("\n--- Feature Store ---")
    print(
        "Feature store version : "
        f"{feature_store['feature_store_version']}"
    )
    print(
        "Candidates stored     : "
        f"{len(feature_store['candidates'])}"
    )
    print(
        "Jobs stored           : "
        f"{len(feature_store['jobs'])}"
    )
    print("Feature store persistence : PASS")

    # ---------------------------------------------------------
    # Evaluation
    # ---------------------------------------------------------

    evaluation = evaluate_predictions(
        data,
        feature_store
    )

    print("\n--- Model Evaluation ---")
    print(
        f"Precision : {pct(evaluation['precision'])}"
    )
    print(
        f"Recall    : {pct(evaluation['recall'])}"
    )
    print(
        f"FPR       : {pct(evaluation['fpr'])}"
    )

    assert evaluation["records"] == 6

    print("Evaluation completed : PASS")

    # ---------------------------------------------------------
    # Registry
    # ---------------------------------------------------------

    registry = create_registry(
        data,
        evaluation
    )

    save_json(
        registry,
        REGISTRY_PATH
    )

    persisted_registry = load_json(
        REGISTRY_PATH
    )

    assert validate_registry(
        persisted_registry
    )

    model = persisted_registry["models"][0]

    print("\n--- Model Registry ---")
    print(
        f"Model name    : {model['model_name']}"
    )
    print(
        f"Model version : {model['model_version']}"
    )
    print(
        f"Stage         : {model['stage']}"
    )
    print(
        f"Status        : {model['status']}"
    )
    print(
        f"Feature store : {model['feature_store_version']}"
    )

    print("Registry validation : PASS")
    print("Registry persistence : PASS")

    # ---------------------------------------------------------
    # End-to-end inference
    # ---------------------------------------------------------

    inference_result = run_inference(
        feature_store,
        "student_001",
        "job_001"
    )

    print("\n--- End-to-End Inference ---")

    print(
        f"Candidate    : "
        f"{inference_result['candidate_id']}"
    )

    print(
        f"Job          : "
        f"{inference_result['job_id']}"
    )

    print(
        f"Model        : "
        f"{inference_result['model_version']}"
    )

    print(
        f"Match score  : "
        f"{inference_result['match_score']:.2%}"
    )

    print("\nPlain-English explanation:")
    print(
        inference_result[
            "explanation"
        ]["reason"]
    )

    assert inference_result["match_score"] >= 0.70

    print("\nInference : PASS")

    # ---------------------------------------------------------
    # Edge case validation
    # ---------------------------------------------------------

    try:
        run_inference(
            feature_store,
            "unknown_student",
            "job_001"
        )
        raise AssertionError(
            "Unknown candidate should fail"
        )
    except ValueError:
        print("Unknown candidate handling : PASS")

    try:
        run_inference(
            feature_store,
            "student_001",
            "unknown_job"
        )
        raise AssertionError(
            "Unknown job should fail"
        )
    except ValueError:
        print("Unknown job handling : PASS")

    # ---------------------------------------------------------
    # Final report
    # ---------------------------------------------------------

    report = build_mlops_report(
        registry,
        feature_store,
        evaluation,
        inference_result
    )

    save_json(
        report,
        REPORT_PATH
    )

    persisted_report = load_json(
        REPORT_PATH
    )

    assert (
        persisted_report["pipeline_status"]
        == "LIVE"
    )

    assert (
        persisted_report[
            "model_registry"
        ]["models"][0]["model_version"]
        == "v1-mlops-baseline"
    )

    print("\n--- Final Validation ---")
    print("Report persistence : PASS")
    print("Registry + feature store : PASS")
    print("Explainable inference : PASS")
    print("Edge-case handling : PASS")
    print("End-to-end MLOps flow : PASS")

    print(
        "\nPipeline status : "
        f"{report['pipeline_status']}"
    )

    print("\n" + "=" * 60)
    print("TASK 23 STATUS: PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()