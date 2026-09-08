from pathlib import Path
import json

from src.drift_retraining import (
    build_report,
    load_data,
    load_report,
    retrain_model,
    save_report
)


BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "drift_test_data.json"
REPORT_PATH = BASE_DIR / "logs" / "drift_retraining_report.json"


def pct(value):
    return f"{value * 100:.2f}%"


def main():
    print("=" * 60)
    print("PlaceMux Phase 3 - Task 22")
    print("Drift Monitoring + Retraining Pipeline")
    print("=" * 60)

    data = load_data(DATA_PATH)

    reference = data["reference"]
    current = data["current"]

    print(f"\nReference records : {len(reference)}")
    print(f"Current records   : {len(current)}")

    assert len(reference) >= 5
    assert len(current) >= 5

    print("Sufficient monitoring sample : PASS")

    report = build_report(reference, current)

    ref_quality = report["reference_quality"]
    cur_quality = report["current_quality"]

    print("\n--- Reference Quality ---")
    print(f"Precision : {pct(ref_quality['precision'])}")
    print(f"Recall    : {pct(ref_quality['recall'])}")
    print(f"FPR       : {pct(ref_quality['fpr'])}")

    print("\n--- Current Quality ---")
    print(f"Precision : {pct(cur_quality['precision'])}")
    print(f"Recall    : {pct(cur_quality['recall'])}")
    print(f"FPR       : {pct(cur_quality['fpr'])}")

    print("\n--- Drift Monitoring ---")

    print(
        f"Reference mean score : "
        f"{report['drift']['mean_shift']['reference_mean']:.4f}"
    )

    print(
        f"Current mean score   : "
        f"{report['drift']['mean_shift']['current_mean']:.4f}"
    )

    print(
        f"Mean shift           : "
        f"{report['drift']['mean_shift']['absolute_shift']:.4f}"
    )

    print(f"PSI                  : {report['drift']['psi']:.4f}")
    print(
        f"Drift threshold      : "
        f"{report['drift']['threshold']:.2f}"
    )

    print(
        "Drift detected       : "
        f"{'PASS' if report['drift']['detected'] else 'NO DRIFT'}"
    )

    print("\n--- Quality Regression ---")

    print(
        f"Precision drop       : "
        f"{pct(report['quality_regression']['precision_drop'])}"
    )

    print(
        f"Recall drop          : "
        f"{pct(report['quality_regression']['recall_drop'])}"
    )

    print(
        "Quality regression   : "
        f"{'DETECTED' if report['quality_regression']['detected'] else 'NONE'}"
    )

    report = retrain_model(report)

    print("\n--- Retraining Decision ---")

    print(
        "Retraining required  : "
        f"{'YES' if report['retraining']['required'] else 'NO'}"
    )

    print(
        "Retraining performed : "
        f"{'YES' if report['retraining']['performed'] else 'NO'}"
    )

    print(
        "New model version    : "
        f"{report['retraining']['new_model_version']}"
    )

    print(
        "Trigger reason       : "
        f"{', '.join(report['retraining']['reason'])}"
    )

    save_report(report, REPORT_PATH)

    print("\nReport persisted      : PASS")

    persisted = load_report(REPORT_PATH)

    assert persisted["model_version"] == report["model_version"]
    assert persisted["drift"]["psi"] == report["drift"]["psi"]
    assert persisted["retraining"]["performed"] is True

    print("Persistence validation: PASS")

    assert report["drift"]["detected"] is True
    print("Drift detection       : PASS")

    assert report["retraining"]["required"] is True
    print("Retraining trigger    : PASS")

    assert report["retraining"]["performed"] is True
    print("Retraining execution  : PASS")

    assert report["retraining"]["new_model_version"] is not None
    print("Model version refresh : PASS")

    print("\nPipeline status       :", report["pipeline_status"])

    print("\n" + "=" * 60)
    print("TASK 22 STATUS: PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()