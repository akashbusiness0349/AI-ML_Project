import json

from src.fp_reduction import (
    baseline_decision,
    hardened_decision,
    calculate_metrics,
    calculate_fp_reduction
)


BASE = "phase2/task13"

with open(
    f"{BASE}/data/flagged_sessions.json",
    "r",
    encoding="utf-8"
) as file:
    sessions = json.load(file)


print("=" * 60)
print("PlaceMux Phase 2 - Task 13")
print("Proctoring False-Positive Reduction Demo")
print("=" * 60)


print("\n--- SESSION DECISIONS ---")

for session in sessions:
    baseline = baseline_decision(session)
    hardened = hardened_decision(session)

    print(
        f"{session['session_id']}: "
        f"expected={session['case_type']}, "
        f"baseline={baseline}, "
        f"hardened={hardened}"
    )


print("\n--- BASELINE METRICS ---")

baseline_metrics = calculate_metrics(
    sessions,
    baseline_decision
)

print(
    "Normal cases:",
    baseline_metrics["normal_cases"]
)

print(
    "Suspicious cases:",
    baseline_metrics["suspicious_cases"]
)

print(
    "False positives:",
    baseline_metrics["false_positives"]
)

print(
    "True positives:",
    baseline_metrics["true_positives"]
)

print(
    "False-positive rate:",
    f"{baseline_metrics['false_positive_rate'] * 100:.2f}%"
)

print(
    "Detection rate:",
    f"{baseline_metrics['detection_rate'] * 100:.2f}%"
)


print("\n--- HARDENED METRICS ---")

hardened_metrics = calculate_metrics(
    sessions,
    hardened_decision
)

print(
    "Normal cases:",
    hardened_metrics["normal_cases"]
)

print(
    "Suspicious cases:",
    hardened_metrics["suspicious_cases"]
)

print(
    "False positives:",
    hardened_metrics["false_positives"]
)

print(
    "True positives:",
    hardened_metrics["true_positives"]
)

print(
    "False-positive rate:",
    f"{hardened_metrics['false_positive_rate'] * 100:.2f}%"
)

print(
    "Detection rate:",
    f"{hardened_metrics['detection_rate'] * 100:.2f}%"
)


print("\n--- FP REDUCTION ---")

fp_reduction = calculate_fp_reduction(
    baseline_metrics["false_positive_rate"],
    hardened_metrics["false_positive_rate"]
)

print(
    "False-positive reduction:",
    f"{fp_reduction * 100:.2f}%"
)


print("\n--- FINAL VALIDATION ---")

fp_reduction_pass = (
    hardened_metrics["false_positive_rate"]
    < baseline_metrics["false_positive_rate"]
)

detection_preserved = (
    hardened_metrics["detection_rate"]
    >= baseline_metrics["detection_rate"]
)

edge_case_pass = (
    hardened_decision(sessions[0]) == "NORMAL"
    and hardened_decision(sessions[3]) == "REVIEW"
    and hardened_decision(sessions[4]) == "REVIEW"
    and hardened_decision(sessions[5]) == "REVIEW"
)


print(
    "False-positive reduction:",
    "PASS" if fp_reduction_pass else "FAIL"
)

print(
    "Detection capability preserved:",
    "PASS" if detection_preserved else "FAIL"
)

print(
    "Normal/suspicious edge cases:",
    "PASS" if edge_case_pass else "FAIL"
)


if (
    fp_reduction_pass
    and detection_preserved
    and edge_case_pass
):
    print("\nTASK 13 STATUS: PASS")
else:
    print("\nTASK 13 STATUS: REVIEW")


print("=" * 60)