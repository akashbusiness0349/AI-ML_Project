"""
PlaceMux Phase 2 — Task 8
Spend Guardrail Evaluation
"""


def check_high_fit_allowed(
    result
):
    """
    High-quality opportunities should not be
    unnecessarily blocked.
    """

    return (
        result["low_fit"] is False
        and result["action"] == "ALLOW"
        and result["warning"] is None
    )


def check_low_fit_warning(
    result
):
    """
    Low-quality opportunities must provide
    a clear warning.
    """

    return (
        result["low_fit"] is True
        and result["action"] == "WARN"
        and isinstance(
            result["warning"],
            str
        )
        and len(result["warning"]) > 0
    )


def check_warning_reasons(
    result
):
    """
    A low-fit warning should contain meaningful
    reasons explaining the risk.
    """

    if not result["low_fit"]:
        return True

    return len(
        result["reasons"]
    ) > 0


def evaluate_guardrail(
    high_fit_result,
    low_fit_result
):
    """
    Evaluate the effectiveness of the
    spend-quality guardrail.
    """

    high_fit_allowed = (
        check_high_fit_allowed(
            high_fit_result
        )
    )

    low_fit_warning = (
        check_low_fit_warning(
            low_fit_result
        )
    )

    warning_reasons = (
        check_warning_reasons(
            low_fit_result
        )
    )

    overall_pass = all(
        [
            high_fit_allowed,
            low_fit_warning,
            warning_reasons
        ]
    )

    return {
        "high_fit_allowed":
            high_fit_allowed,

        "low_fit_warning":
            low_fit_warning,

        "warning_reasons_available":
            warning_reasons,

        "overall_pass":
            overall_pass
    }