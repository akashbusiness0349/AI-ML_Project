from __future__ import annotations

import subprocess
import sys


SCRIPTS = [
    "run_data_generation.py",
    "run_data_validation.py",
    "run_indexing.py",
    "run_training.py",
    "run_hybrid_tuning.py",
    "run_evaluation.py",
    "run_explainability.py",
    "run_failure_test.py",
    "run_live_search.py",
]


def run_script(script: str) -> None:
    print()
    print("=" * 80)
    print(f"RUNNING: {script}")
    print("=" * 80)

    completed = subprocess.run(
        [sys.executable, script],
        text=True,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            f"FAILED: {script}"
        )


def main() -> None:
    for script in SCRIPTS:
        run_script(script)

    print()
    print("=" * 80)
    print("TASK 13 INTEGRATION: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()