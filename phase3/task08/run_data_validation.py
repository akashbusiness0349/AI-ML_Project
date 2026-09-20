from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.data_ingestion import (
    load_events,
    summarize_events,
)
from src.validation import (
    validate_event_dataframe,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_DATA = (
    ROOT
    / "data"
    / "demo_events.json"
)

LOG_PATH = (
    ROOT
    / "logs"
    / "data_validation.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Task 08 event data."
    )

    parser.add_argument(
        "--data",
        default=str(DEFAULT_DATA),
        help=(
            "Path to event JSON. "
            "Defaults to synthetic demo data."
        ),
    )

    parser.add_argument(
        "--source-type",
        default="synthetic_demo",
        choices=[
            "synthetic_demo",
            "production",
        ],
        help="Data provenance label.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    data_path = Path(
        args.data
    )

    print("=" * 72)
    print("PHASE 3 / TASK 08 — DATA VALIDATION")
    print("=" * 72)

    print(
        f"Data source           : {args.source_type}"
    )

    events = load_events(
        data_path
    )

    errors = validate_event_dataframe(
        events
    )

    if errors:
        print()

        for error in errors:
            print(
                f"[ERROR] {error}"
            )

        raise SystemExit(1)

    summary = summarize_events(
        events
    )

    summary["data_source_type"] = (
        args.source_type
    )

    summary["data_path"] = str(
        data_path
    )

    LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with LOG_PATH.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            summary,
            handle,
            indent=2,
        )

    print()
    print(
        f"Rows                  : "
        f"{summary['rows']}"
    )

    print(
        f"Entities              : "
        f"{summary['entities']}"
    )

    print(
        f"Candidate entities    : "
        f"{summary['unique_candidate_entities']}"
    )

    print(
        f"Company entities      : "
        f"{summary['unique_company_entities']}"
    )

    print(
        f"First event           : "
        f"{summary['first_event']}"
    )

    print(
        f"Last event            : "
        f"{summary['last_event']}"
    )

    print(
        f"Event types           : "
        f"{len(summary['event_types'])}"
    )

    print()
    print("DATA VALIDATION: PASS")
    print(
        f"Evidence              : {LOG_PATH}"
    )


if __name__ == "__main__":
    main()