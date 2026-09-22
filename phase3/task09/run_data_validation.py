from __future__ import annotations

import argparse
from pathlib import Path

from src.data_ingestion import load_logged_data, save_json
from src.validation import validate_logged_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        required=True,
    )
    args = parser.parse_args()

    frame = load_logged_data(args.data)
    result = validate_logged_data(frame)

    output = Path(
        "phase3/task09/logs/data_validation.json"
    )

    save_json(result, output)

    print("=" * 70)
    print("TASK 09 — DATA VALIDATION")
    print("=" * 70)
    print(f"Status            : {result['status']}")
    print(f"Rows              : {result['rows']}")
    print(f"Unique entities   : {result['unique_entities']}")
    print(f"Unique events     : {result['unique_events']}")
    print(f"Date min          : {result['date_min']}")
    print(f"Date max          : {result['date_max']}")

    if result["warnings"]:
        print("\nWarnings:")
        for warning in result["warnings"]:
            print(f" - {warning}")

    if result["errors"]:
        print("\nErrors:")
        for error in result["errors"]:
            print(f" - {error}")

    print(f"\nEvidence          : {output}")
    print("=" * 70)

    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()