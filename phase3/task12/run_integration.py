from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


SCRIPTS = [
    "run_data_validation.py",
    "run_training.py",
    "run_evaluation.py",
    "run_explainability.py",
    "run_latency_benchmark.py",
    "run_failure_test.py",
    "run_demo.py",
]


def run_script(script):
    print()
    print("=" * 80)
    print(f"RUNNING: {script}")
    print("=" * 80)

    result = subprocess.run(
        [
            sys.executable,
            script,
        ],
        cwd=ROOT,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FAILED: {script}"
        )


def main():
    for script in SCRIPTS:
        run_script(script)

    print()
    print("=" * 80)
    print("TASK 12 INTEGRATION: PASS")
    print("=" * 80)


if __name__ == "__main__":
    main()