import json
import sys
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(TASK_DIR))


from src.recommendation_validation import (
    load_validation_data,
    validate_recommendations,
    filter_by_college,
    validate_college_isolation,
    save_validation_report,
)


DATA_PATH = (
    TASK_DIR
    / "data"
    / "recommendation_data.json"
)

REPORT_PATH = (
    TASK_DIR
    / "logs"
    / "recommendation_validation_report.json"
)


def print_recommendation_results(report):
    """Display recommendation validation results."""

    print("\n========== RECOMMENDATION RESULTS ==========")

    for result in report["results"]:
        status = (
            "RECOMMENDED"
            if result["recommended"]
            else "NOT RECOMMENDED"
        )

        relevance = (
            "RELEVANT"
            if result["relevant"]
            else "NOT RELEVANT"
        )

        print(
            f"{result['student_id']} -> "
            f"{result['job_id']} | "
            f"{status} | "
            f"{relevance} | "
            f"match={result['match_score']:.2f}"
        )

        for reason in result["explanation"]:
            print(f"   - {reason}")


def main():
    print("=" * 60)
    print("TASK 20 — PORTALS INTEGRATION & DRY RUN")
    print("RECOMMENDATION QUALITY VALIDATION")
    print("=" * 60)

    # 1. Load validation data
    records = load_validation_data(DATA_PATH)

    print(
        f"\nValidation records loaded : "
        f"{len(records)}"
    )

    data_loaded = len(records) > 0

    print(
        "Integrated sample data     : "
        + ("PASS" if data_loaded else "FAIL")
    )

    # 2. Validate recommendations
    report = validate_recommendations(records)

    print("\n========== QUALITY METRICS ==========")

    print(
        f"Total records             : "
        f"{report['total_recommendations']}"
    )

    print(
        f"Recommendations           : "
        f"{report['recommended_count']}"
    )

    print(
        f"Relevant recommendations  : "
        f"{report['relevant_recommendations']}"
    )

    print(
        f"Total relevant            : "
        f"{report['total_relevant']}"
    )

    print(
        f"False positives           : "
        f"{report['false_positives']}"
    )

    print(
        f"Precision                 : "
        f"{report['precision'] * 100:.2f}%"
    )

    print(
        f"Recall                    : "
        f"{report['recall'] * 100:.2f}%"
    )

    print(
        f"False-positive rate       : "
        f"{report['false_positive_rate'] * 100:.2f}%"
    )

    print(
        f"Model version             : "
        f"{report['model_version']}"
    )

    metrics_pass = (
        report["total_recommendations"] == len(records)
        and report["recommended_count"] > 0
        and 0 <= report["precision"] <= 1
        and 0 <= report["recall"] <= 1
        and 0 <= report["false_positive_rate"] <= 1
    )

    print(
        "Recommendation metrics    : "
        + ("PASS" if metrics_pass else "FAIL")
    )

    # 3. Display explainable recommendations
    print_recommendation_results(report)

    explanations_pass = all(
        isinstance(result["explanation"], list)
        and len(result["explanation"]) > 0
        for result in report["results"]
    )

    print(
        "\nExplainable recommendations : "
        + ("PASS" if explanations_pass else "FAIL")
    )

    # 4. Validate college ownership
    isolation = validate_college_isolation(report)

    print("\n========== COLLEGE ISOLATION ==========")

    print(
        f"Colleges represented       : "
        f"{isolation['college_count']}"
    )

    print(
        f"College IDs                : "
        f"{', '.join(isolation['college_ids'])}"
    )

    print(
        "College ownership present  : "
        + (
            "PASS"
            if isolation["ownership_present"]
            else "FAIL"
        )
    )

    # 5. Test college-specific views
    college_a = filter_by_college(
        report,
        "college_a"
    )

    college_b = filter_by_college(
        report,
        "college_b"
    )

    college_a_pass = (
        len(college_a) > 0
        and all(
            result["college_id"] == "college_a"
            for result in college_a
        )
    )

    college_b_pass = (
        len(college_b) > 0
        and all(
            result["college_id"] == "college_b"
            for result in college_b
        )
    )

    tenant_isolation_pass = (
        college_a_pass
        and college_b_pass
    )

    print(
        "College A scoped view      : "
        + ("PASS" if college_a_pass else "FAIL")
    )

    print(
        "College B scoped view      : "
        + ("PASS" if college_b_pass else "FAIL")
    )

    print(
        "Tenant data isolation      : "
        + (
            "PASS"
            if tenant_isolation_pass
            else "FAIL"
        )
    )

    # 6. Persist validation report
    save_validation_report(
        report,
        REPORT_PATH
    )

    persisted = REPORT_PATH.exists()

    print("\n========== PERSISTENCE ==========")

    print(
        f"Report path                : "
        f"{REPORT_PATH}"
    )

    print(
        "Validation report persisted : "
        + ("PASS" if persisted else "FAIL")
    )

    # 7. Reload persisted report
    reload_pass = False

    if persisted:
        with open(
            REPORT_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            saved_report = json.load(file)

        reload_pass = (
            saved_report["total_recommendations"]
            == report["total_recommendations"]
            and saved_report["precision"]
            == report["precision"]
            and saved_report["recall"]
            == report["recall"]
        )

    print(
        "Persisted report verified   : "
        + ("PASS" if reload_pass else "FAIL")
    )

    # 8. End-to-end validation
    overall_pass = all(
        [
            data_loaded,
            metrics_pass,
            explanations_pass,
            isolation["ownership_present"],
            tenant_isolation_pass,
            persisted,
            reload_pass,
        ]
    )

    print("\n========== END-TO-END VALIDATION ==========")

    print(
        "Integrated data -> validation : "
        + ("PASS" if data_loaded else "FAIL")
    )

    print(
        "Recommendation metrics       : "
        + ("PASS" if metrics_pass else "FAIL")
    )

    print(
        "Recommendation explainability: "
        + (
            "PASS"
            if explanations_pass
            else "FAIL"
        )
    )

    print(
        "College isolation            : "
        + (
            "PASS"
            if tenant_isolation_pass
            else "FAIL"
        )
    )

    print(
        "Persistence                  : "
        + (
            "PASS"
            if reload_pass
            else "FAIL"
        )
    )

    print("\n" + "=" * 60)

    print(
        "TASK 20 STATUS: "
        + ("PASS" if overall_pass else "FAIL")
    )

    print("=" * 60)


if __name__ == "__main__":
    main()