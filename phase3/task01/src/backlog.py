def build_backlog(defects):
    actions = {
        "INT-001": {
            "action": "Tune recommendation threshold and investigate false-positive candidates.",
            "owner": "ML Engineer",
            "success_metric": "Online false-positive rate <= 10%",
            "evidence": "Re-run live interaction evaluation after threshold/ranking change."
        },
        "INT-002": {
            "action": "Review missed relevant matches and improve ranking recall.",
            "owner": "ML Engineer",
            "success_metric": "Online recall >= 85%",
            "evidence": "Held-out validation plus live-style interaction replay."
        },
        "INT-003": {
            "action": "Investigate feature and distribution differences between offline and online-style traffic.",
            "owner": "ML Engineer + Data",
            "success_metric": "Precision gap <= 10 percentage points",
            "evidence": "Offline-versus-online comparison report."
        },
        "INT-004": {
            "action": "Add production prediction, outcome, latency, and model-version instrumentation.",
            "owner": "Backend/Data",
            "success_metric": "100% prediction events contain model version, score, outcome, and latency fields.",
            "evidence": "Validated production telemetry sample."
        }
    }

    backlog = []

    for defect in defects:
        action = actions.get(defect["defect_id"])

        if action is None:
            continue

        backlog.append({
            "backlog_id": f"PH3-{defect['defect_id']}",
            "defect_id": defect["defect_id"],
            "title": defect["title"],
            "priority": defect["priority"],
            "owner": action["owner"],
            "action": action["action"],
            "success_metric": action["success_metric"],
            "evidence_required": action["evidence"],
            "status": "PLANNED"
        })

    return backlog