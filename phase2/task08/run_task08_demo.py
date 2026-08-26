"""
PlaceMux Phase 2 — Task 8
Receipts, Refunds & Reconciliation
Spend-Quality Guardrail Demo
"""

import json
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"

sys.path.insert(
    0,
    str(SRC_DIR)
)

from spend_guardrail import (
    MODEL_VERSION,
    evaluate_spend_guardrail
)

from guardrail_evaluator import (
    evaluate_guardrail
)


# ============================================================
# HIGH-FIT OPPORTUNITY
# ============================================================

high_fit_signals = {
    "match_score": 0.92,
    "skill_match": 0.90,
    "experience_match": 1.00,
    "role_match": 1.00,
    "verified_score_match": 0.90,
    "work_mode_match": 1.00
}


# ============================================================
# LOW-FIT OPPORTUNITY
# ============================================================

low_fit_signals = {
    "match_score": 0.42,
    "skill_match": 0.35,
    "experience_match": 0.40,
    "role_match": 0.50,
    "verified_score_match": 0.45,
    "work_mode_match": 1.00
}


# ============================================================
# GUARDRAIL EVALUATION
# ============================================================

high_fit_result = evaluate_spend_guardrail(
    high_fit_signals
)

low_fit_result = evaluate_spend_guardrail(
    low_fit_signals
)


evaluation = evaluate_guardrail(
    high_fit_result=high_fit_result,
    low_fit_result=low_fit_result
)


final_status = (
    "PASS"
    if evaluation["overall_pass"]
    else "FAIL"
)


# ============================================================
# STRUCTURED RESULT
# ============================================================

result = {
    "task":
        "Task 8 — Receipts, Refunds & Reconciliation",

    "model_version":
        MODEL_VERSION,

    "high_fit_result":
        high_fit_result,

    "low_fit_result":
        low_fit_result,

    "evaluation":
        evaluation,

    "final_status":
        final_status
}


# ============================================================
# DISPLAY
# ============================================================

print("=" * 70)
print(
    "TASK 8 — SPEND-QUALITY GUARDRAIL"
)
print("=" * 70)


print(
    "\n========== HIGH-FIT OPPORTUNITY =========="
)

print(
    "Spend quality score : "
    f"{high_fit_result['spend_quality_score'] * 100:.2f}%"
)

print(
    "Low fit             : "
    f"{high_fit_result['low_fit']}"
)

print(
    "Action              : "
    f"{high_fit_result['action']}"
)

print(
    "Warning             : "
    f"{high_fit_result['warning']}"
)


print(
    "\n========== LOW-FIT OPPORTUNITY =========="
)

print(
    "Spend quality score : "
    f"{low_fit_result['spend_quality_score'] * 100:.2f}%"
)

print(
    "Low fit             : "
    f"{low_fit_result['low_fit']}"
)

print(
    "Action              : "
    f"{low_fit_result['action']}"
)

print(
    "Warning             : "
    f"{low_fit_result['warning']}"
)


print(
    "\n========== LOW-FIT REASONS =========="
)

for reason in low_fit_result["reasons"]:

    print(
        f"- {reason}"
    )


print(
    "\n========== GUARDRAIL VALIDATION =========="
)

print(
    "High-fit opportunity allowed : "
    f"{'PASS' if evaluation['high_fit_allowed'] else 'FAIL'}"
)

print(
    "Low-fit warning generated    : "
    f"{'PASS' if evaluation['low_fit_warning'] else 'FAIL'}"
)

print(
    "Warning reasons available    : "
    f"{'PASS' if evaluation['warning_reasons_available'] else 'FAIL'}"
)

print(
    "Overall guardrail evaluation : "
    f"{'PASS' if evaluation['overall_pass'] else 'FAIL'}"
)


print(
    "\n========== STRUCTURED RESULT =========="
)

print(
    json.dumps(
        result,
        indent=2
    )
)


print(
    "\n========== FINAL STATUS =========="
)

print(
    "Low-fit warning available : "
    f"{final_status}"
)

print(
    "High-fit opportunities protected : "
    f"{'PASS' if evaluation['high_fit_allowed'] else 'FAIL'}"
)

print(
    "Guardrail consistency : "
    f"{'PASS' if evaluation['overall_pass'] else 'FAIL'}"
)


if final_status == "PASS":

    print(
        "\nTask 8 spend-quality guardrail "
        "completed successfully."
    )

else:

    print(
        "\nTask 8 guardrail failed validation."
    )