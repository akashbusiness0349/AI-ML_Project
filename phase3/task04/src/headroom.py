from __future__ import annotations

import math
from typing import Any, Dict


DEFAULT_HEADROOM_PERCENT = 30.0


def calculate_headroom(
    breaking_point: Dict[str, Any],
    headroom_percent: float = DEFAULT_HEADROOM_PERCENT,
    target_qps: float | None = None,
) -> Dict[str, Any]:

    sustainable = breaking_point.get("sustainable_result")

    if sustainable:
        sustainable_qps = float(
            sustainable.get("qps", 0.0)
        )
        sustainable_concurrency = int(
            sustainable.get("concurrency", 0)
        )
    else:
        sustainable_qps = 0.0
        sustainable_concurrency = 0

    break_qps = breaking_point.get("breaking_point_qps")

    if break_qps is not None:
        breaking_qps = float(break_qps)
    else:
        breaking_qps = None

    operating_qps = sustainable_qps * (
        1.0 - headroom_percent / 100.0
    )

    if target_qps is None:
        target_qps = operating_qps

    if sustainable_qps > 0:
        projected_replicas = max(
            1,
            math.ceil(target_qps / sustainable_qps),
        )
    else:
        projected_replicas = None

    return {
        "headroom_percent": headroom_percent,
        "sustainable_qps": round(sustainable_qps, 6),
        "sustainable_concurrency": sustainable_concurrency,
        "breaking_point_qps": (
            round(breaking_qps, 6)
            if breaking_qps is not None
            else None
        ),
        "recommended_operating_qps": round(
            operating_qps,
            6,
        ),
        "target_qps": round(
            float(target_qps),
            6,
        ),
        "projected_replicas_for_target": projected_replicas,
        "capacity_basis": (
            "Measured sustainable QPS from the highest passing "
            "load level."
        ),
    }