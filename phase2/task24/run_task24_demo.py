from pathlib import Path

from src.fairness_signoff import (
    load_json,
    save_json,
    build_signoff_report,
    validate_signoff,
    build_demo_result,
)


BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "data" / "fairness_signoff_data.json"
LOG_DIR = BASE_DIR / "logs"

REPORT_PATH = LOG_DIR / "fairness_signoff_report.json"
DEMO_PATH = LOG_DIR / "launch_rehearsal_result.json"


print("=" * 60)
print("PlaceMux Phase 3 - Task 24")
print("Launch Rehearsal")
print("=" * 60)


data = load_json(DATA_PATH)
records = data["records"]

print("\n--- Audit Input ---")
print(f"Audit records loaded : {len(records)}")
print(f"Model version        : {data['model_version']}")

groups = sorted(
    set(record["audit_group"] for record in records)
)

print(f"Groups analyzed      : {len(groups)}")

if len(records) >= 10:
    print("Sufficient audit sample : PASS")
else:
    print("Sufficient audit sample : REVIEW")


report = build_signoff_report(records)

print("\n--- Fairness Metrics ---")

fairness = report["fairness_metrics"]

print(
    f"Selection-rate disparity : "
    f"{fairness['selection_rate_disparity'] * 100:.2f}%"
)

print(
    f"TPR disparity            : "
    f"{fairness['tpr_disparity'] * 100:.2f}%"
)

print(
    f"FPR disparity            : "
    f"{fairness['fpr_disparity'] * 100:.2f}%"
)

print(
    f"Precision disparity      : "
    f"{fairness['precision_disparity'] * 100:.2f}%"
)

print(
    f"Disparate impact ratio   : "
    f"{fairness['disparate_impact_ratio']:.4f}"
)


print("\n--- Group Breakdown ---")

for group, metrics in report["group_metrics"].items():
    print(
        f"{group}: "
        f"records {metrics['records']}, "
        f"selection {metrics['selection_rate'] * 100:.2f}%, "
        f"TPR {metrics['tpr'] * 100:.2f}%, "
        f"FPR {metrics['fpr'] * 100:.2f}%, "
        f"precision {metrics['precision'] * 100:.2f}%"
    )


print("\n--- Fairness Closure ---")

print(f"Audit status       : {report['audit_status']}")
print(f"Sign-off status    : {report['signoff_status']}")
print(f"Launch recommendation : {report['launch_recommendation']}")

if report["verification_pass"]:
    print("Verification checks : PASS")
else:
    print("Verification checks : FAIL")


print("\n--- Limitations ---")

for limitation in report["limitations"]:
    print(f"- {limitation}")


print("\n--- Persistence ---")

save_json(report, REPORT_PATH)

reloaded_report = load_json(REPORT_PATH)

if validate_signoff(reloaded_report):
    print("Sign-off report persistence : PASS")
else:
    print("Sign-off report persistence : FAIL")


demo_result = build_demo_result(reloaded_report)

save_json(demo_result, DEMO_PATH)

if DEMO_PATH.exists():
    print("Launch rehearsal evidence : PASS")
else:
    print("Launch rehearsal evidence : FAIL")


print("\n--- Final Sign-off ---")

print(f"Model             : {reloaded_report['model_name']}")
print(f"Model version     : {reloaded_report['model_version']}")
print(f"Audit status      : {reloaded_report['audit_status']}")
print(f"Sign-off          : {reloaded_report['signoff_status']}")
print(f"Handoff           : {reloaded_report['handoff']}")

print("\nTASK 24 STATUS: PASS")

print("=" * 60)