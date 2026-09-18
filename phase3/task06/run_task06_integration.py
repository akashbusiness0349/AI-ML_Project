from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.attribution import (
    reconstruct_journeys,
    validate_joinability,
)
from src.event_logger import load_events
from src.fallback import (
    safe_model_unavailable_response,
    validate_fallback,
)
from src.monitoring import calculate_metrics
from src.validation import (
    validate_events,
    validate_ranked_lists,
)


ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"

EVENT_LOG_PATH = LOG_DIR / "event_log.json"
RANKED_LIST_PATH = LOG_DIR / "ranked_lists.json"
SIGNOFF_PATH = LOG_DIR / "integration_signoff.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    print(
        "\nPHASE 3 / TASK 06 — END-TO-END INTEGRATION"
    )
    print("=" * 60)

    if not EVENT_LOG_PATH.exists():
        raise RuntimeError(
            "event_log.json not found. Run run_task06_demo.py first."
        )

    if not RANKED_LIST_PATH.exists():
        raise RuntimeError(
            "ranked_lists.json not found. Run run_task06_demo.py first."
        )

    events = load_events(EVENT_LOG_PATH)
    ranked_lists: List[Dict[str, Any]] = read_json(
        RANKED_LIST_PATH
    )

    event_validation = validate_events(events)
    ranked_validation = validate_ranked_lists(
        ranked_lists
    )
    joinability = validate_joinability(events)
    journeys = reconstruct_journeys(events)

    fallback = safe_model_unavailable_response(
        "integration_failure_request"
    )

    checks = {
        "events_present": len(events) > 0,
        "ranked_lists_present": len(ranked_lists) > 0,
        "events_valid": event_validation["all_valid"],
        "positions_valid": ranked_validation[
            "all_positions_contiguous"
        ],
        "model_versions_present": ranked_validation[
            "model_version_present_on_every_result"
        ],
        "outcomes_joinable": joinability["joinable"],
        "journeys_reconstructable": len(journeys) > 0,
        "fallback_safe": validate_fallback(fallback),
    }

    all_passed = all(checks.values())

    result = {
        "task": "Phase 3 Task 06",
        "integration_status": (
            "PASS"
            if all_passed
            else "FAIL"
        ),
        "all_checks_passed": all_passed,
        "checks": checks,
        "event_validation": event_validation,
        "ranked_list_validation": ranked_validation,
        "joinability": joinability,
        "journey_count": len(journeys),
        "north_star_metrics": calculate_metrics(events),
        "failure_path": {
            "response": fallback,
            "safe": validate_fallback(fallback),
        },
    }

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    SIGNOFF_PATH.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print(
        f"Events                 : {len(events)}"
    )
    print(
        f"Ranked lists           : {len(ranked_lists)}"
    )
    print(
        f"Journeys reconstructed : {len(journeys)}"
    )
    print(
        f"Join rate              : "
        f"{joinability['join_rate'] * 100:.2f}%"
    )
    print(
        f"Integration status     : {result['integration_status']}"
    )
    print(
        f"Evidence written       : {SIGNOFF_PATH}"
    )


if __name__ == "__main__":
    main()