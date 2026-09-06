import json
import sys
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(TASK_DIR))


from src.item_quality import (
    load_items,
    analyze_item_bank,
    filter_items_by_college,
    validate_college_isolation,
    save_report,
)


DATA_PATH = TASK_DIR / "data" / "item_bank.json"
REPORT_PATH = TASK_DIR / "logs" / "quality_report.json"


def print_item_flags(report):
    print("\n========== ADMIN WEAK-ITEM FLAGS ==========")

    for item in report["items"]:
        print(
            f"{item['item_id']} | "
            f"{item['status']} | "
            f"college={item['college_id']} | "
            f"accuracy={item['accuracy']:.2f} | "
            f"discrimination={item['discrimination']:.2f}"
        )

        if item["reasons"]:
            for reason in item["reasons"]:
                print(f"   - {reason}")


def main():
    print("=" * 60)
    print("TASK 19 — BULK ONBOARDING & RECRUITER VIEWS")
    print("ITEM-BANK QUALITY SUPPORT")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. Load item bank
    # ---------------------------------------------------------

    items = load_items(DATA_PATH)

    print(f"\nItem bank records loaded : {len(items)}")

    data_loaded = len(items) > 0

    print(
        "Real-shaped item data    : "
        + ("PASS" if data_loaded else "FAIL")
    )

    # ---------------------------------------------------------
    # 2. Run item analytics
    # ---------------------------------------------------------

    report = analyze_item_bank(items)

    print("\n========== ITEM ANALYTICS ==========")

    print(
        f"Total items              : "
        f"{report['total_items']}"
    )

    print(
        f"Weak items               : "
        f"{report['weak_item_count']}"
    )

    print(
        f"Weak-item rate           : "
        f"{report['weak_item_rate'] * 100:.2f}%"
    )

    print(
        f"Items kept               : "
        f"{report['keep_item_count']}"
    )

    print(
        f"Model version            : "
        f"{report['model_version']}"
    )

    analytics_pass = (
        report["total_items"] == len(items)
        and report["total_items"] > 0
    )

    print(
        "Item analytics           : "
        + ("PASS" if analytics_pass else "FAIL")
    )

    # ---------------------------------------------------------
    # 3. Show admin weak-item flags
    # ---------------------------------------------------------

    print_item_flags(report)

    weak_flags_pass = report["weak_item_count"] > 0

    print(
        "\nWeak-item flags available : "
        + ("PASS" if weak_flags_pass else "FAIL")
    )

    # ---------------------------------------------------------
    # 4. Validate admin statuses
    # ---------------------------------------------------------

    valid_statuses = all(
        item["status"] in {"REVIEW", "KEEP"}
        for item in report["items"]
    )

    explainable_flags = all(
        isinstance(item["reasons"], list)
        for item in report["items"]
    )

    print(
        "Admin statuses valid      : "
        + ("PASS" if valid_statuses else "FAIL")
    )

    print(
        "Explainable reasons       : "
        + ("PASS" if explainable_flags else "FAIL")
    )

    # ---------------------------------------------------------
    # 5. College isolation
    # ---------------------------------------------------------

    isolation = validate_college_isolation(report)

    print("\n========== COLLEGE ISOLATION ==========")

    print(
        f"Colleges represented      : "
        f"{isolation['college_count']}"
    )

    print(
        f"College IDs               : "
        f"{', '.join(isolation['college_ids'])}"
    )

    print(
        "College ownership present : "
        + (
            "PASS"
            if isolation["college_isolation_supported"]
            else "FAIL"
        )
    )

    # ---------------------------------------------------------
    # 6. Verify college-specific filtering
    # ---------------------------------------------------------

    college_a_items = filter_items_by_college(
        report,
        "college_a"
    )

    college_b_items = filter_items_by_college(
        report,
        "college_b"
    )

    college_a_isolated = all(
        item["college_id"] == "college_a"
        for item in college_a_items
    )

    college_b_isolated = all(
        item["college_id"] == "college_b"
        for item in college_b_items
    )

    isolation_filter_pass = (
        len(college_a_items) > 0
        and len(college_b_items) > 0
        and college_a_isolated
        and college_b_isolated
    )

    print(
        "College A scoped view     : "
        + ("PASS" if college_a_isolated else "FAIL")
    )

    print(
        "College B scoped view     : "
        + ("PASS" if college_b_isolated else "FAIL")
    )

    print(
        "Tenant data isolation     : "
        + ("PASS" if isolation_filter_pass else "FAIL")
    )

    # ---------------------------------------------------------
    # 7. Persist quality report
    # ---------------------------------------------------------

    save_report(
        report,
        REPORT_PATH
    )

    persisted = REPORT_PATH.exists()

    print("\n========== PERSISTENCE ==========")

    print(
        f"Report path               : "
        f"{REPORT_PATH}"
    )

    print(
        "Quality report persisted   : "
        + ("PASS" if persisted else "FAIL")
    )

    # ---------------------------------------------------------
    # 8. Reload persisted report
    # ---------------------------------------------------------

    reload_pass = False

    if persisted:
        with open(
            REPORT_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            saved_report = json.load(file)

        reload_pass = (
            saved_report["total_items"]
            == report["total_items"]
            and saved_report["weak_item_count"]
            == report["weak_item_count"]
        )

    print(
        "Persisted report verified  : "
        + ("PASS" if reload_pass else "FAIL")
    )

    # ---------------------------------------------------------
    # 9. Final validation
    # ---------------------------------------------------------

    overall_pass = all(
        [
            data_loaded,
            analytics_pass,
            weak_flags_pass,
            valid_statuses,
            explainable_flags,
            isolation["college_isolation_supported"],
            isolation_filter_pass,
            persisted,
            reload_pass,
        ]
    )

    print("\n========== END-TO-END VALIDATION ==========")

    print(
        "Item bank -> analytics     : "
        + ("PASS" if analytics_pass else "FAIL")
    )

    print(
        "Analytics -> weak flags   : "
        + ("PASS" if weak_flags_pass else "FAIL")
    )

    print(
        "Admin explainability      : "
        + (
            "PASS"
            if explainable_flags
            else "FAIL"
        )
    )

    print(
        "College isolation         : "
        + (
            "PASS"
            if isolation_filter_pass
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
        "TASK 19 STATUS: "
        + ("PASS" if overall_pass else "FAIL")
    )

    print("=" * 60)


if __name__ == "__main__":
    main()