import json
import sys
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent

sys.path.insert(
    0,
    str(TASK_DIR)
)


from src.fairness_audit import (
    load_data,
    build_fairness_report,
    validate_group_coverage,
    filter_by_group,
    save_report,
)


DATA_PATH = (
    TASK_DIR
    / "data"
    / "fairness_test_data.json"
)

REPORT_PATH = (
    TASK_DIR
    / "logs"
    / "fairness_audit_report.json"
)


def print_group_metrics(report):
    """Display group-level fairness metrics."""

    print(
        "\n========== GROUP METRICS =========="
    )

    for group, metrics in report["group_metrics"].items():

        print(
            f"\n{group}"
        )

        print(
            f"  Records              : "
            f"{metrics['total_records']}"
        )

        print(
            f"  Recommendations      : "
            f"{metrics['recommended']}"
        )

        print(
            f"  Relevant             : "
            f"{metrics['relevant']}"
        )

        print(
            f"  Selection rate       : "
            f"{metrics['selection_rate'] * 100:.2f}%"
        )

        print(
            f"  True-positive rate   : "
            f"{metrics['true_positive_rate'] * 100:.2f}%"
        )

        print(
            f"  False-positive rate  : "
            f"{metrics['false_positive_rate'] * 100:.2f}%"
        )

        print(
            f"  Precision            : "
            f"{metrics['precision'] * 100:.2f}%"
        )


def main():

    print("=" * 60)
    print(
        "TASK 21 — DPDP CONSENT & SECURITY FOUNDATIONS"
    )
    print(
        "INITIAL FAIRNESS / BIAS AUDIT"
    )
    print("=" * 60)

    # 1. Load audit data
    records = load_data(DATA_PATH)

    print(
        f"\nAudit records loaded      : "
        f"{len(records)}"
    )

    data_loaded = len(records) > 0

    print(
        "Sufficient audit sample   : "
        + (
            "PASS"
            if data_loaded
            else "FAIL"
        )
    )

    # 2. Build fairness report
    report = build_fairness_report(records)

    print(
        "\n========== FAIRNESS AUDIT =========="
    )

    print(
        f"Audit status              : "
        f"{report['audit_status']}"
    )

    print(
        f"Model version             : "
        f"{report['model_version']}"
    )

    print(
        f"Groups analyzed           : "
        f"{report['group_count']}"
    )

    # 3. Display group metrics
    print_group_metrics(report)

    # 4. Display fairness metrics
    fairness = report["fairness_metrics"]

    print(
        "\n========== FAIRNESS METRICS =========="
    )

    print(
        f"Selection-rate disparity  : "
        f"{fairness['selection_rate_disparity'] * 100:.2f}%"
    )

    print(
        f"TPR disparity             : "
        f"{fairness['true_positive_rate_disparity'] * 100:.2f}%"
    )

    print(
        f"FPR disparity             : "
        f"{fairness['false_positive_rate_disparity'] * 100:.2f}%"
    )

    print(
        f"Precision disparity       : "
        f"{fairness['precision_disparity'] * 100:.2f}%"
    )

    print(
        f"Disparate impact ratio    : "
        f"{fairness['disparate_impact_ratio']:.4f}"
    )

    metrics_valid = all(
        0 <= fairness[key]
        for key in [
            "selection_rate_disparity",
            "true_positive_rate_disparity",
            "false_positive_rate_disparity",
            "precision_disparity",
        ]
    )

    metrics_valid = (
        metrics_valid
        and 0 <= fairness["disparate_impact_ratio"] <= 1
    )

    print(
        "Fairness metrics valid    : "
        + (
            "PASS"
            if metrics_valid
            else "FAIL"
        )
    )

    # 5. Validate group coverage
    coverage_pass = validate_group_coverage(
        report
    )

    print(
        "\n========== GROUP COVERAGE =========="
    )

    print(
        "All groups represented    : "
        + (
            "PASS"
            if coverage_pass
            else "FAIL"
        )
    )

    # 6. Verify individual group views
    group_a = filter_by_group(
        report,
        "group_a"
    )

    group_b = filter_by_group(
        report,
        "group_b"
    )

    group_views_pass = (
        bool(group_a)
        and bool(group_b)
    )

    print(
        "Group A audit view        : "
        + (
            "PASS"
            if bool(group_a)
            else "FAIL"
        )
    )

    print(
        "Group B audit view        : "
        + (
            "PASS"
            if bool(group_b)
            else "FAIL"
        )
    )

    # 7. Persist report
    save_report(
        report,
        REPORT_PATH
    )

    persisted = REPORT_PATH.exists()

    print(
        "\n========== PERSISTENCE =========="
    )

    print(
        f"Report path               : "
        f"{REPORT_PATH}"
    )

    print(
        "Audit report persisted    : "
        + (
            "PASS"
            if persisted
            else "FAIL"
        )
    )

    # 8. Reload report
    reload_pass = False

    if persisted:

        with open(
            REPORT_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            saved_report = json.load(file)

        reload_pass = (
            saved_report["total_records"]
            == report["total_records"]
            and saved_report["group_count"]
            == report["group_count"]
            and saved_report["audit_status"]
            == report["audit_status"]
        )

    print(
        "Persisted report verified : "
        + (
            "PASS"
            if reload_pass
            else "FAIL"
        )
    )

    # 9. Final validation
    overall_pass = all(
        [
            data_loaded,
            metrics_valid,
            coverage_pass,
            group_views_pass,
            persisted,
            reload_pass,
        ]
    )

    print(
        "\n========== END-TO-END VALIDATION =========="
    )

    print(
        "Audit data -> metrics     : "
        + (
            "PASS"
            if data_loaded
            else "FAIL"
        )
    )

    print(
        "Fairness metrics          : "
        + (
            "PASS"
            if metrics_valid
            else "FAIL"
        )
    )

    print(
        "Group coverage            : "
        + (
            "PASS"
            if coverage_pass
            else "FAIL"
        )
    )

    print(
        "Group audit views         : "
        + (
            "PASS"
            if group_views_pass
            else "FAIL"
        )
    )

    print(
        "Persistence               : "
        + (
            "PASS"
            if reload_pass
            else "FAIL"
        )
    )

    print("\n" + "=" * 60)

    print(
        "TASK 21 STATUS: "
        + (
            "PASS"
            if overall_pass
            else "FAIL"
        )
    )

    print("=" * 60)


if __name__ == "__main__":
    main()