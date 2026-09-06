def baseline_decision(session):
    """
    Baseline:
    Any detected event causes a REVIEW decision.
    This intentionally produces false positives on normal short events.
    """

    has_event = (
        session["face_missing_seconds"] > 0
        or session["multiple_faces"] > 0
        or session["tab_switches"] > 0
        or session["camera_obstruction_seconds"] > 0
    )

    return "REVIEW" if has_event else "NORMAL"


def hardened_decision(session):
    """
    Hardened logic:
    Short isolated events are treated as normal.
    Persistent or repeated suspicious behaviour remains REVIEW.
    """

    if session["multiple_faces"] >= 2:
        return "REVIEW"

    if session["face_missing_seconds"] >= 10:
        return "REVIEW"

    if session["tab_switches"] >= 3:
        return "REVIEW"

    return "NORMAL"


def calculate_metrics(sessions, decision_function):
    normal_cases = 0
    suspicious_cases = 0

    false_positives = 0
    true_positives = 0

    for session in sessions:
        prediction = decision_function(session)

        if session["case_type"] == "normal":
            normal_cases += 1

            if prediction == "REVIEW":
                false_positives += 1

        elif session["case_type"] == "suspicious":
            suspicious_cases += 1

            if prediction == "REVIEW":
                true_positives += 1

    false_positive_rate = (
        false_positives / normal_cases
        if normal_cases
        else 0
    )

    detection_rate = (
        true_positives / suspicious_cases
        if suspicious_cases
        else 0
    )

    return {
        "normal_cases": normal_cases,
        "suspicious_cases": suspicious_cases,
        "false_positives": false_positives,
        "true_positives": true_positives,
        "false_positive_rate": false_positive_rate,
        "detection_rate": detection_rate
    }


def calculate_fp_reduction(baseline_fpr, hardened_fpr):
    if baseline_fpr == 0:
        return 0.0

    return (
        (baseline_fpr - hardened_fpr)
        / baseline_fpr
    )