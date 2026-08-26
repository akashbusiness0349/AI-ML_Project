"""
PlaceMux Phase 2 — Task 8
Spend-Quality Guardrail
"""

MODEL_VERSION = "v1-spend-guardrail"

DEFAULT_LOW_FIT_THRESHOLD = 0.60


def calculate_spend_quality_score(
    match_score,
    skill_match,
    experience_match,
    role_match,
    verified_score_match,
    work_mode_match
):
    """
    Calculate an opportunity quality score before
    a potentially paid application.

    Match relevance remains the strongest signal.
    """

    score = (
        match_score * 0.35
        + skill_match * 0.25
        + experience_match * 0.15
        + role_match * 0.10
        + verified_score_match * 0.10
        + work_mode_match * 0.05
    )

    return round(score, 4)


def identify_low_fit_reasons(signals):
    """
    Identify the signals responsible for a low-fit warning.
    """

    reasons = []

    if signals["match_score"] < 0.60:
        reasons.append(
            "Overall match score is below the recommended level."
        )

    if signals["skill_match"] < 0.60:
        reasons.append(
            "Required skill compatibility is low."
        )

    if signals["experience_match"] < 0.60:
        reasons.append(
            "Experience compatibility is low."
        )

    if signals["role_match"] < 0.60:
        reasons.append(
            "Role compatibility is low."
        )

    if signals["verified_score_match"] < 0.60:
        reasons.append(
            "Verified competency compatibility is low."
        )

    if signals["work_mode_match"] < 0.60:
        reasons.append(
            "Work-mode compatibility is low."
        )

    return reasons


def evaluate_spend_guardrail(
    signals,
    threshold=DEFAULT_LOW_FIT_THRESHOLD
):
    """
    Evaluate whether a low-fit warning should be shown.

    The guardrail warns the user but does not block
    the opportunity automatically.
    """

    quality_score = calculate_spend_quality_score(
        match_score=signals["match_score"],
        skill_match=signals["skill_match"],
        experience_match=signals["experience_match"],
        role_match=signals["role_match"],
        verified_score_match=signals["verified_score_match"],
        work_mode_match=signals["work_mode_match"]
    )

    low_fit_reasons = identify_low_fit_reasons(
        signals
    )

    low_fit = (
        quality_score < threshold
        or len(low_fit_reasons) >= 2
    )

    if low_fit:

        warning = (
            "Low-fit warning: this opportunity may "
            "not provide sufficient match quality "
            "for a paid application. Review the "
            "match factors before spending money."
        )

    else:

        warning = None

    return {
        "spend_quality_score": quality_score,
        "low_fit": low_fit,
        "warning": warning,
        "reasons": low_fit_reasons,
        "threshold": threshold,
        "action": (
            "WARN"
            if low_fit
            else "ALLOW"
        ),
        "model_version": MODEL_VERSION
    }