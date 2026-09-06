import json
from pathlib import Path


MODEL_VERSION = "v1-recommendation-validation"


def load_validation_data(path):
    """Load recommendation validation records from JSON."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_precision(recommended, relevant):
    """Calculate recommendation precision."""
    if recommended == 0:
        return 0.0

    return relevant / recommended


def calculate_recall(relevant, total_relevant):
    """Calculate recommendation recall."""
    if total_relevant == 0:
        return 0.0

    return relevant / total_relevant


def calculate_false_positive_rate(false_positives, total_negatives):
    """Calculate recommendation false-positive rate."""
    if total_negatives == 0:
        return 0.0

    return false_positives / total_negatives


def calculate_match_score(matched_skills, required_skills):
    """Calculate required-skill match score."""
    if required_skills == 0:
        return 0.0

    return matched_skills / required_skills


def build_explanation(record):
    """Create a plain-English explanation for one recommendation."""

    reasons = []

    if record["matched_required_skills"] > 0:
        reasons.append(
            f"Matched {record['matched_required_skills']} of "
            f"{record['required_skills']} required skills"
        )

    if record.get("verified_skills", False):
        reasons.append("Verified skills were used")

    if record.get("role_match", False):
        reasons.append("Candidate role is relevant")

    if record.get("experience_match", False):
        reasons.append("Experience requirement is satisfied")

    if not reasons:
        reasons.append("Limited evidence of relevance")

    return reasons


def validate_recommendation(record):
    """Validate one student-job recommendation."""

    match_score = calculate_match_score(
        record["matched_required_skills"],
        record["required_skills"],
    )

    recommended = 1 if record["recommended"] else 0
    relevant = 1 if record["relevant"] else 0

    false_positive = (
        recommended == 1
        and relevant == 0
    )

    explanation = build_explanation(record)

    return {
        "student_id": record["student_id"],
        "job_id": record["job_id"],
        "college_id": record["college_id"],
        "recommended": record["recommended"],
        "relevant": record["relevant"],
        "match_score": round(match_score, 4),
        "false_positive": false_positive,
        "explanation": explanation,
    }


def validate_recommendations(records):
    """Validate the complete recommendation set."""

    results = [
        validate_recommendation(record)
        for record in records
    ]

    recommended_count = sum(
        1 for result in results
        if result["recommended"]
    )

    relevant_recommendations = sum(
        1 for result in results
        if result["recommended"] and result["relevant"]
    )

    total_relevant = sum(
        1 for result in results
        if result["relevant"]
    )

    false_positives = sum(
        1 for result in results
        if result["false_positive"]
    )

    total_negatives = sum(
        1 for result in results
        if not result["relevant"]
    )

    precision = calculate_precision(
        recommended_count,
        relevant_recommendations,
    )

    recall = calculate_recall(
        relevant_recommendations,
        total_relevant,
    )

    fpr = calculate_false_positive_rate(
        false_positives,
        total_negatives,
    )

    return {
        "model_version": MODEL_VERSION,
        "total_recommendations": len(results),
        "recommended_count": recommended_count,
        "relevant_recommendations": relevant_recommendations,
        "total_relevant": total_relevant,
        "false_positives": false_positives,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "false_positive_rate": round(fpr, 4),
        "results": results,
    }


def filter_by_college(report, college_id):
    """Return recommendation results for one college."""

    return [
        result
        for result in report["results"]
        if result["college_id"] == college_id
    ]


def validate_college_isolation(report):
    """Verify that every recommendation retains college ownership."""

    college_ids = {
        result["college_id"]
        for result in report["results"]
    }

    ownership_present = all(
        bool(result["college_id"])
        for result in report["results"]
    )

    return {
        "college_count": len(college_ids),
        "college_ids": sorted(college_ids),
        "ownership_present": ownership_present,
        "decision": "PASS" if ownership_present else "FAIL",
    }


def save_validation_report(report, path):
    """Persist recommendation validation results."""

    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=2,
        )


if __name__ == "__main__":
    print("Recommendation validation module loaded.")