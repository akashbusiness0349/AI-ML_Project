from __future__ import annotations

import json
import subprocess
import sys


def main() -> None:
    queries = [
        "someone who can build data pipelines",
        "machine learning model development",
        "cloud infrastructure deployment",
    ]

    print("=" * 80)
    print("TASK 13 — LIVE SEMANTIC / HYBRID SEARCH DEMO")
    print("=" * 80)

    for query in queries:
        print()
        print(f"QUERY: {query}")

        completed = subprocess.run(
            [
                sys.executable,
                "run_live_search.py",
                query,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        result = json.loads(
            completed.stdout
        )

        print(
            json.dumps(
                result,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()