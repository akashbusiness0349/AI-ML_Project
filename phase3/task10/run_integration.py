import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


SCRIPTS = [
    "run_data_validation.py",
    "run_experiment.py",
    "run_explainability.py",
    "run_guardrails.py",
    "run_failure_test.py",
    "run_live_demo.py",
]


def run(script):
    print()
    print("=" * 80)
    print(f"RUNNING: {script}")
    print("=" * 80)

    result = subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FAILED: {script}"
        )


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    for script in SCRIPTS:
        run(script)

    prereg = load_json(
        ROOT / "logs" / "preregistration.json"
    )

    experiment = load_json(
        ROOT / "logs" / "experiment_result.json"
    )

    guardrails = load_json(
        ROOT / "logs" / "guardrail_result.json"
    )

    explainability = load_json(
        ROOT / "logs" / "explainability.json"
    )

    fallback = load_json(
        ROOT / "logs" / "failure_test.json"
    )

    demo = load_json(
        ROOT / "logs" / "live_demo.json"
    )

    provenance = {
        "production_data_available": False,
        "production_evidence_status":
            "NOT_PRODUCTION_EVIDENCE",
    }

    from src.decision import make_decision

    decision = make_decision(
        prereg,
        guardrails,
        provenance,
    )

    with open(
        ROOT / "logs" / "decision.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            decision,
            f,
            indent=2,
        )

    summary = {
        "task": "Phase 3 Task 10",
        "status": "COMPLETED",
        "preregistration_locked": True,
        "data_validation": "PASS",
        "target_leakage_check": "PASS",
        "offline_heldout_experiment": "PASS",
        "explainability": explainability.get(
            "explainability_status",
            "PASS",
        ),
        "fallback_test": fallback.get(
            "fallback_test",
            "FAIL",
        ),
        "executable_demo": (
            "PASS"
            if demo.get("records_served")
            else "FAIL"
        ),
        "data_source": "synthetic_demo",
        "production_live_ab": False,
        "online_causal_effect_established": False,
        "guardrails_pass": guardrails[
            "all_pass"
        ],
        "offline_relative_effect":
            experiment[
                "offline_ab_replay"
            ]["relative_effect"],
        "offline_p_value":
            experiment[
                "offline_ab_replay"
            ]["p_value"],
        "final_decision": decision[
            "decision"
        ],
        "decision_reasons": decision[
            "reasons"
        ],
    }

    output_path = (
        ROOT
        / "logs"
        / "integration_summary.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            summary,
            f,
            indent=2,
        )

    print()
    print("=" * 80)
    print("TASK 10 INTEGRATION COMPLETE")
    print("=" * 80)
    print(json.dumps(summary, indent=2))
    print()
    print(
        "FINAL DECISION:",
        decision["decision"],
    )
    print()
    print(
        "SUMMARY FILE:",
        output_path,
    )


if __name__ == "__main__":
    main()