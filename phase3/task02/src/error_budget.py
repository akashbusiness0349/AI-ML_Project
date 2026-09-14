
from .slo_monitor import AVAILABILITY_SLO


def build_error_budget(
    total_events,
    failed_events,
    window_name="go-live-rehearsal",
):
    allowed_failure_rate = 1.0 - AVAILABILITY_SLO

    allowed_failures = total_events * allowed_failure_rate
    remaining_failures = max(
        0.0,
        allowed_failures - failed_events
    )

    consumed = (
        failed_events / allowed_failures
        if allowed_failures > 0
        else 1.0
    )

    remaining_percent = max(
        0.0,
        1.0 - consumed
    )

    return {
        "task": "Phase 3 Task 02",
        "window": window_name,
        "slo": {
            "availability_target": AVAILABILITY_SLO,
            "allowed_failure_rate": allowed_failure_rate,
        },
        "traffic": {
            "total_events": total_events,
            "failed_events": failed_events,
        },
        "error_budget": {
            "allowed_failures": round(
                allowed_failures,
                4
            ),
            "failures_consumed": failed_events,
            "remaining_failures": round(
                remaining_failures,
                4
            ),
            "consumed_fraction": round(
                min(consumed, 1.0),
                4
            ),
            "remaining_fraction": round(
                remaining_percent,
                4
            ),
        },
        "status": (
            "BUDGET_EXHAUSTED"
            if failed_events > allowed_failures
            else "WITHIN_BUDGET"
        ),
        "interpretation":
            "For a 99% availability SLO, the error budget permits up to 1% failed inference events in the measurement window.",
    }
