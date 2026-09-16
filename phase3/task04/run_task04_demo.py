from __future__ import annotations

import json
import sys
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent

if str(TASK_DIR) not in sys.path:
    sys.path.insert(0, str(TASK_DIR))

from src.failure_test import run_failure_path_test
from src.inference import SkillMatchingModel


DATA_FILE = TASK_DIR / "data" / "inference_requests.json"
LOG_DIR = TASK_DIR / "logs"


def load_records() -> list[dict]:
    with DATA_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, list) or not data:
        raise ValueError(
            "inference_requests.json must contain a non-empty JSON list."
        )

    return data


def write_json(
    path: Path,
    payload: dict,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            payload,
            file,
            indent=2,
        )


def main() -> None:
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    records = load_records()

    model = SkillMatchingModel()

    example = records[0]

    result = model.predict(
        request_id=example["request_id"],
        student_id=example["student_id"],
        candidate_skills=example.get(
            "candidate_skills",
            [],
        ),
        required_skills=example.get(
            "required_skills",
            [],
        ),
    )

    explainability = {
        "status": "success",
        "request_id": result.request_id,
        "student_id": result.student_id,
        "score": result.score,
        "decision": result.decision,
        "matched_skills": result.matched_skills,
        "missing_skills": result.missing_skills,
        "explanation": result.explanation,
    }

    write_json(
        LOG_DIR / "explainability_example.json",
        explainability,
    )

    failure_result = run_failure_path_test()

    write_json(
        LOG_DIR / "failure_path.json",
        failure_result,
    )

    print("=" * 70)
    print("TASK 04 DEMO")
    print("=" * 70)

    print("\nExplainability example:")
    print(json.dumps(
        explainability,
        indent=2,
    ))

    print("\nMODEL_UNAVAILABLE failure-path test:")
    print(json.dumps(
        failure_result,
        indent=2,
    ))

    print("\nGenerated:")
    print(
        LOG_DIR / "explainability_example.json"
    )
    print(
        LOG_DIR / "failure_path.json"
    )


if __name__ == "__main__":
    main()