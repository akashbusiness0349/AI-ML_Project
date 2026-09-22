def make_decision(
    preregistration,
    guardrails,
    provenance,
):
    reasons = []

    if not provenance["production_data_available"]:
        reasons.append(
            "Verified production/live data is unavailable."
        )

    if provenance["production_evidence_status"] != "PRODUCTION_EVIDENCE":
        reasons.append(
            "The evaluated dataset is explicitly synthetic/demo data."
        )

    if not guardrails["all_pass"]:
        reasons.append(
            "One or more preregistered statistical guardrails failed."
        )

    reasons.append(
        "A historical offline replay cannot establish a causal online intervention effect."
    )

    decision = "DO_NOT_SHIP"

    return {
        "decision": decision,
        "reasons": reasons,
        "ship_rule": preregistration[
            "ship_rule"
        ],
        "online_causal_effect_established": False,
    }