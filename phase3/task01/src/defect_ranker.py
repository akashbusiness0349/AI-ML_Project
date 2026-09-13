def rank_defects(health_report, live_data):
    events = live_data["events"]

    false_positive_events = [
        event for event in events
        if event["recommended"] and not event["relevant"]
    ]

    false_negative_events = [
        event for event in events
        if not event["recommended"] and event["relevant"]
    ]

    precision_gap = health_report["offline_online_gap"]["precision_gap"]

    defects = [
        {
            "defect_id": "INT-001",
            "title": "False-positive recommendations",
            "category": "ranking",
            "severity": "HIGH",
            "priority": 1,
            "frequency": len(false_positive_events),
            "metric": "false_positive_rate",
            "measured_value": health_report["online_metrics"]["false_positive_rate"],
            "description": "The live-style traffic contains recommendations that are not relevant.",
            "explainable": True,
            "status": "OPEN"
        },
        {
            "defect_id": "INT-002",
            "title": "False-negative recommendations",
            "category": "ranking",
            "severity": "HIGH",
            "priority": 2,
            "frequency": len(false_negative_events),
            "metric": "recall",
            "measured_value": health_report["online_metrics"]["recall"],
            "description": "Relevant candidate-job pairs are not recommended.",
            "explainable": True,
            "status": "OPEN"
        },
        {
            "defect_id": "INT-003",
            "title": "Offline-to-online precision gap",
            "category": "validation",
            "severity": "HIGH",
            "priority": 3,
            "frequency": 1,
            "metric": "precision_gap",
            "measured_value": precision_gap,
            "description": "Offline baseline performance is materially higher than observed online-style performance.",
            "explainable": True,
            "status": "OPEN"
        },
        {
            "defect_id": "INT-004",
            "title": "Production interaction instrumentation gap",
            "category": "observability",
            "severity": "MEDIUM",
            "priority": 4,
            "frequency": len(events),
            "metric": "production_log_coverage",
            "measured_value": 0.0 if live_data["external_production"] is False else 1.0,
            "description": "Current evidence comes from production-shaped rehearsal traffic rather than externally deployed production telemetry.",
            "explainable": True,
            "status": "OPEN"
        }
    ]

    return sorted(defects, key=lambda item: item["priority"])