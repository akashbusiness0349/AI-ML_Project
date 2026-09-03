import json

from src.proctoring_hardening import evaluate_cases


DATA_PATH = "phase2/task11/data/proctoring_test_cases.json"


with open(DATA_PATH, "r", encoding="utf-8") as file:
    cases = json.load(file)


report = evaluate_cases(cases)


print("=" * 60)
print("PlaceMux Phase 2 - Task 11")
print("Proctoring Hardening Demo")
print("=" * 60)

print("\nTotal test cases:", len(cases))

print("\n--- BASELINE ---")

print(
    "False-positive rate:",
    f"{report['baseline_fpr'] * 100:.2f}%"
)

print(
    "Detection rate:",
    f"{report['baseline_detection'] * 100:.2f}%"
)


print("\n--- HARDENED ---")

print(
    "False-positive rate:",
    f"{report['hardened_fpr'] * 100:.2f}%"
)

print(
    "Detection rate:",
    f"{report['hardened_detection'] * 100:.2f}%"
)


print("\n--- FALSE-POSITIVE REDUCTION ---")

print(
    "Reduction:",
    f"{report['false_positive_reduction'] * 100:.2f}%"
)


print("\n--- CASE RESULTS ---")

for result in report["results"]:
    print(
        result["case_id"],
        "|",
        result["category"],
        "| baseline:",
        result["baseline"],
        "| hardened:",
        result["hardened"]
    )


print("\n--- VALIDATION ---")

if report["false_positive_reduction"] > 0:
    print("False-positive reduction: PASS")
else:
    print("False-positive reduction: FAIL")


if report["detection_preserved"]:
    print("Detection capability preserved: PASS")
else:
    print("Detection capability preserved: FAIL")


if (
    report["false_positive_reduction"] > 0
    and report["detection_preserved"]
):
    print("\nTASK 11 STATUS: PASS")
    print("False-positive reduction is underway.")
else:
    print("\nTASK 11 STATUS: REVIEW")


print("=" * 60)