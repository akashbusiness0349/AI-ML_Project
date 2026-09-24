from __future__ import annotations


def explain_candidate_job(
    candidate: dict,
    job: dict,
    features: dict[str, float],
) -> str:
    reasons = []

    if features.get("skill_overlap", 0) > 0:
        overlap = features["skill_overlap"] * 100
        reasons.append(
            f"{overlap:.0f}% of the job's required skills match your profile"
        )

    if features.get("experience_match", 0) > 0:
        reasons.append("your experience level matches the role")

    if features.get("location_match", 0) > 0:
        reasons.append("the job location matches your location")

    if not reasons:
        reasons.append(
            "the recommendation is based on the available profile and job signals"
        )

    return "Recommended because " + "; ".join(reasons) + "."


def explain_company_candidate(
    company: dict,
    candidate: dict,
    features: dict[str, float],
) -> str:
    reasons = []

    if features.get("skill_overlap", 0) > 0:
        reasons.append(
            f"{features['skill_overlap'] * 100:.0f}% of preferred skills are present"
        )

    if features.get("experience_match", 0) > 0:
        reasons.append("the candidate matches the preferred experience level")

    if features.get("location_match", 0) > 0:
        reasons.append("the candidate is in the preferred location")

    if not reasons:
        reasons.append(
            "the recommendation is based on the available company and candidate signals"
        )

    return "Recommended because " + "; ".join(reasons) + "."


def build_explanation(
    direction: str,
    subject: dict,
    item: dict,
    features: dict[str, float],
) -> str:
    if direction == "candidate_to_job":
        return explain_candidate_job(
            subject,
            item,
            features,
        )

    return explain_company_candidate(
        subject,
        item,
        features,
    )