def evaluate_guardrails(
    result,
    preregistration,
):
    ab = result["ab_effect"]

    checks = {
        "minimum_relative_effect": (
            ab["relative_effect"]
            >= preregistration["minimum_relative_effect"]
        ),
        "statistical_significance": (
            ab["p_value"]
            < preregistration["alpha"]
        ),
        "confidence_interval_supports_effect": (
            ab["ci95_low"]
            >= 0
        ),
    }

    return {
        "checks": checks,
        "all_pass": all(checks.values()),
        "thresholds": {
            "minimum_relative_effect": preregistration[
                "minimum_relative_effect"
            ],
            "alpha": preregistration["alpha"],
        },
    }