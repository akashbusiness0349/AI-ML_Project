from pathlib import Path
import subprocess
import sys


TASK_DIR = Path(__file__).resolve().parents[1]


def run_script(script_name: str):
    script = TASK_DIR / script_name

    if not script.exists():
        return None

    result = subprocess.run(
        [
            sys.executable,
            str(script),
        ],
        cwd=TASK_DIR,
        capture_output=True,
        text=True,
    )

    return result


def test_data_validation_script():
    result = run_script(
        "run_data_validation.py"
    )

    if result is None:
        return

    assert result.returncode == 0, (
        result.stdout + "\n" + result.stderr
    )


def test_evaluation_script():
    result = run_script(
        "run_evaluation.py"
    )

    if result is None:
        return

    assert result.returncode == 0, (
        result.stdout + "\n" + result.stderr
    )


def test_demo_script():
    result = run_script(
        "run_demo.py"
    )

    if result is None:
        return

    assert result.returncode == 0, (
        result.stdout + "\n" + result.stderr
    )