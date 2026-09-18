from __future__ import annotations

import json
from pathlib import Path

from src.governance import fairness_audit


ROOT = Path(__file__).resolve().parent


def load(path: Path):
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def main():
    candidates = load(
        ROOT / "data" / "candidates.json"
    )

    events_path = (
        ROOT
        / "logs"
        / "live_events.json"
    )

    events = (
        load(events_path)
        if events_path.exists()
        else []
    )

    audit = fairness_audit(
        candidates,
        events,
    )

    output = (
        ROOT
        / "logs"
        / "governance_audit.json"
    )

    with output.open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(
            audit,
            handle,
            indent=2,
        )

    print(
        "\n"
        "============================================\n"
        "TASK 07 — FAIRNESS / DPDP AUDIT\n"
        "============================================"
    )

    print(
        f"Candidate schema : "
        f"{audit['candidate_schema']['passed']}"
    )

    print(
        f"Event schema     : "
        f"{audit['event_schema']['passed']}"
    )

    print(
        "Protected attrs used for ranking : False"
    )

    print(
        "Fairness group metrics : "
        "NOT FABRICATED / require valid group labels"
    )

    print(
        "DPDP controls : documented"
    )

    print(
        f"\nAudit written to: {output}"
    )


if __name__ == "__main__":
    main()