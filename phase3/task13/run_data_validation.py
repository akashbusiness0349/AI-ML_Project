from __future__ import annotations

import json

from src.data import load_jobs, load_resumes
from src.validation import validate_documents


def main() -> None:
    resumes = load_resumes()
    jobs = load_jobs()

    result = validate_documents(
        resumes,
        jobs,
    )

    print(json.dumps(
        result,
        indent=2,
    ))

    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()