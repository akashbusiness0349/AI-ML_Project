def baseline_decision(events):
    """Simple baseline: any detected event triggers review."""

    for event in events:
        if event["signal"] in [
            "face_missing",
            "multiple_faces",
            "tab_switch",
            "camera_obstruction"
        ]:
            return "REVIEW"

    return "NORMAL"


def hardened_decision(events):
    """Hardened logic reduces false positives using persistence."""

    for event in events:
        signal = event["signal"]
        duration = event["duration"]

        if signal == "multiple_faces" and duration >= 2:
            return "REVIEW"

        if signal in [
            "face_missing",
            "tab_switch",
            "camera_obstruction"
        ] and duration >= 2:
            return "REVIEW"

    return "NORMAL"


def evaluate_cases(cases):
    """Compare baseline and hardened decisions."""

    results = []

    for case in cases:
        baseline = baseline_decision(case["events"])
        hardened = hardened_decision(case["events"])

        results.append({
            "case_id": case["case_id"],
            "category": case["category"],
            "baseline": baseline,
            "hardened": hardened
        })

    normal_cases = [
        result for result in results
        if result["category"] == "normal"
    ]

    suspicious_cases = [
        result for result in results
        if result["category"] == "suspicious"
    ]

    baseline_false_positives = sum(
        result["baseline"] == "REVIEW"
        for result in normal_cases
    )

    hardened_false_positives = sum(
        result["hardened"] == "REVIEW"
        for result in normal_cases
    )

    baseline_true_positives = sum(
        result["baseline"] == "REVIEW"
        for result in suspicious_cases
    )

    hardened_true_positives = sum(
        result["hardened"] == "REVIEW"
        for result in suspicious_cases
    )

    baseline_fpr = (
        baseline_false_positives / len(normal_cases)
    )

    hardened_fpr = (
        hardened_false_positives / len(normal_cases)
    )

    baseline_detection = (
        baseline_true_positives / len(suspicious_cases)
    )

    hardened_detection = (
        hardened_true_positives / len(suspicious_cases)
    )

    if baseline_fpr > 0:
        false_positive_reduction = (
            (baseline_fpr - hardened_fpr)
            / baseline_fpr
        )
    else:
        false_positive_reduction = 0

    detection_preserved = (
        hardened_detection >= baseline_detection
    )

    return {
        "results": results,
        "baseline_fpr": baseline_fpr,
        "hardened_fpr": hardened_fpr,
        "false_positive_reduction": false_positive_reduction,
        "baseline_detection": baseline_detection,
        "hardened_detection": hardened_detection,
        "detection_preserved": detection_preserved
    }