from __future__ import annotations

from typing import Any, Dict


def build_scaling_plan(
    headroom: Dict[str, Any],
    breaking_point: Dict[str, Any],
) -> Dict[str, Any]:

    sustainable_qps = float(
        headroom.get("sustainable_qps", 0.0)
    )

    operating_qps = float(
        headroom.get("recommended_operating_qps", 0.0)
    )

    projected_replicas = headroom.get(
        "projected_replicas_for_target"
    )

    plan = {
        "strategy": "horizontal_autoscaling",
        "architecture": {
            "load_balancer": True,
            "stateless_inference_replicas": True,
            "model_loaded_per_replica": True,
            "shared_request_state": False,
        },
        "replica_policy": {
            "min_replicas": 1,
            "recommended_initial_replicas": 2,
            "max_replicas": 10,
            "projected_replicas_for_measured_target": projected_replicas,
        },
        "scale_out_signals": [
            {
                "metric": "p95_latency_ms",
                "threshold": 100,
                "action": "scale_out",
            },
            {
                "metric": "request_qps",
                "threshold": round(
                    operating_qps,
                    6,
                ),
                "action": "scale_out",
            },
            {
                "metric": "cpu_utilization_percent",
                "threshold": 70,
                "action": "scale_out",
            },
            {
                "metric": "error_rate_percent",
                "threshold": 1,
                "action": "scale_out_and_investigate",
            },
        ],
        "scale_in_policy": {
            "cpu_target_percent": 45,
            "cooldown_seconds": 300,
            "min_replicas": 1,
            "require_stable_low_load": True,
        },
        "batching": {
            "enabled": False,
            "recommendation": (
                "Enable only for workloads where queueing latency "
                "remains inside the p95 SLO."
            ),
        },
        "precompute": {
            "recommended_for": [
                "stable candidate profiles",
                "stable job requirement embeddings/features",
            ],
            "avoid_for": [
                "rapidly changing candidate/job inputs",
            ],
        },
        "model_cache": {
            "load_on_startup": True,
            "reuse_model_instance": True,
            "invalidate_on_model_version_change": True,
        },
        "rollback": {
            "trigger_conditions": [
                "p95 latency remains above SLO after scale-out",
                "error rate exceeds 1%",
                "model output quality regression",
                "new model version fails health/readiness checks",
            ],
            "action": "rollback_to_last_known_good_model_version",
        },
        "devops_handoff": {
            "required_components": [
                "containerized inference service",
                "load balancer",
                "horizontal pod/instance autoscaler",
                "request-rate metrics",
                "p95 latency metrics",
                "error-rate metrics",
                "CPU and memory metrics",
                "model version health checks",
            ],
        },
        "measured_capacity": {
            "sustainable_qps": round(sustainable_qps, 6),
            "recommended_operating_qps": round(
                operating_qps,
                6,
            ),
            "breaking_point_qps": breaking_point.get(
                "breaking_point_qps"
            ),
        },
    }

    return plan