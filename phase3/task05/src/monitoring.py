"""
SLO monitoring and evaluation.
"""

from dataclasses import dataclass


@dataclass
class SLOConfig:
    p95_latency_ms: float = 100.0
    error_rate_percent: float = 1.0
    availability_percent: float = 99.0


def evaluate_slos(
    metrics: dict,
    config: SLOConfig,
) -> dict:

    latency_pass = (
        metrics["p95_ms"]
        <= config.p95_latency_ms
    )

    error_pass = (
        metrics["error_rate_percent"]
        <= config.error_rate_percent
    )

    availability_pass = (
        metrics["availability_percent"]
        >= config.availability_percent
    )

    return {
        "latency": {
            "observed_p95_ms": metrics[
                "p95_ms"
            ],
            "target_p95_ms": config.p95_latency_ms,
            "pass": latency_pass,
        },
        "error_rate": {
            "observed_percent": metrics[
                "error_rate_percent"
            ],
            "target_percent": config.error_rate_percent,
            "pass": error_pass,
        },
        "availability": {
            "observed_percent": metrics[
                "availability_percent"
            ],
            "target_percent": config.availability_percent,
            "pass": availability_pass,
        },
        "all_slos_met": (
            latency_pass
            and error_pass
            and availability_pass
        ),
    }