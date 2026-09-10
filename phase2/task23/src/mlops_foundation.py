import json
from pathlib import Path


MODEL_VERSION = "v1-mlops-baseline"


def load_data(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def create_feature_store(data):
    candidates = {}

    for candidate in data["features"]:
        candidates[candidate["candidate_id"]] = {
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["candidate_name"],
            "college_id": candidate["college_id"],
            "verified_skills": candidate["verified_skills"],
            "experience_years": candidate["experience_years"]
        }

    jobs = {}

    for job in data["jobs"]:
        jobs[job["job_id"]] = {
            "job_id": job["job_id"],
            "job_title": job["job_title"],
            "required_skills": job["required_skills"],
            "minimum_experience_years": job[
                "minimum_experience_years"
            ]
        }

    return {
        "feature_store_version": "v1",
        "candidates": candidates,
        "jobs": jobs
    }


def calculate_match(candidate, job):
    required_skills = job["required_skills"]
    verified_skills = candidate["verified_skills"]

    skill_scores = []

    for skill, required_score in required_skills.items():
        verified_score = verified_skills.get(skill, 0.0)

        if required_score > 0:
            skill_match = min(
                verified_score / required_score,
                1.0
            )
        else:
            skill_match = 1.0

        skill_scores.append(skill_match)

    skill_score = (
        sum(skill_scores) / len(skill_scores)
        if skill_scores
        else 0.0
    )

    experience_score = (
        min(
            candidate["experience_years"]
            / job["minimum_experience_years"],
            1.0
        )
        if job["minimum_experience_years"] > 0
        else 1.0
    )

    final_score = (
        0.8 * skill_score
        + 0.2 * experience_score
    )

    return round(final_score, 4)


def explain_match(candidate, job):
    matched_skills = []
    partial_skills = []
    missing_skills = []

    for skill, required_score in job["required_skills"].items():
        verified_score = candidate["verified_skills"].get(skill, 0.0)

        if verified_score >= required_score:
            matched_skills.append(skill)
        elif verified_score > 0:
            partial_skills.append(skill)
        else:
            missing_skills.append(skill)

    experience_ok = (
        candidate["experience_years"]
        >= job["minimum_experience_years"]
    )

    reasons = []

    if matched_skills:
        reasons.append(
            "Verified skills meet the required level for: "
            + ", ".join(matched_skills)
        )

    if partial_skills:
        reasons.append(
            "Partial skill coverage for: "
            + ", ".join(partial_skills)
        )

    if experience_ok:
        reasons.append(
            "Candidate meets the minimum experience requirement."
        )
    else:
        reasons.append(
            "Candidate is below the minimum experience requirement."
        )

    return {
        "matched_skills": matched_skills,
        "partial_skills": partial_skills,
        "missing_skills": missing_skills,
        "experience_requirement_met": experience_ok,
        "reason": " ".join(reasons)
    }


def run_inference(feature_store, candidate_id, job_id):
    candidate = feature_store["candidates"].get(candidate_id)
    job = feature_store["jobs"].get(job_id)

    if candidate is None:
        raise ValueError(
            f"Candidate not found: {candidate_id}"
        )

    if job is None:
        raise ValueError(
            f"Job not found: {job_id}"
        )

    score = calculate_match(candidate, job)
    explanation = explain_match(candidate, job)

    return {
        "candidate_id": candidate_id,
        "job_id": job_id,
        "model_version": MODEL_VERSION,
        "match_score": score,
        "explanation": explanation
    }


def evaluate_predictions(data, feature_store):
    tp = 0
    fp = 0
    fn = 0
    tn = 0

    prediction_rows = []

    for label in data["labels"]:
        result = run_inference(
            feature_store,
            label["candidate_id"],
            label["job_id"]
        )

        predicted = result["match_score"] >= 0.70
        actual = label["relevant"]

        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1

        prediction_rows.append({
            "candidate_id": label["candidate_id"],
            "job_id": label["job_id"],
            "match_score": result["match_score"],
            "predicted_relevant": predicted,
            "actual_relevant": actual
        })

    precision = (
        tp / (tp + fp)
        if (tp + fp)
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn)
        else 0.0
    )

    fpr = (
        fp / (fp + tn)
        if (fp + tn)
        else 0.0
    )

    return {
        "records": len(data["labels"]),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "fpr": round(fpr, 4),
        "predictions": prediction_rows
    }


def create_registry(data, evaluation):
    registered_model = {
        "model_name": "placemux-matcher",
        "model_version": MODEL_VERSION,
        "stage": "production",
        "status": "active",
        "framework": "deterministic-python",
        "metrics": {
            "precision": evaluation["precision"],
            "recall": evaluation["recall"],
            "fpr": evaluation["fpr"]
        },
        "feature_store_version": "v1",
        "training_records": len(data["labels"]),
        "explainability": True
    }

    return {
        "registry_version": "v1",
        "models": [registered_model]
    }


def validate_registry(registry):
    if not registry["models"]:
        return False

    model = registry["models"][0]

    required_fields = [
        "model_name",
        "model_version",
        "stage",
        "status",
        "metrics",
        "feature_store_version"
    ]

    return all(
        field in model
        for field in required_fields
    )


def build_mlops_report(
    registry,
    feature_store,
    evaluation,
    inference_result
):
    return {
        "model_registry": registry,
        "feature_store": {
            "version": feature_store["feature_store_version"],
            "candidate_count": len(
                feature_store["candidates"]
            ),
            "job_count": len(
                feature_store["jobs"]
            )
        },
        "evaluation": {
            "records": evaluation["records"],
            "precision": evaluation["precision"],
            "recall": evaluation["recall"],
            "fpr": evaluation["fpr"]
        },
        "demo_inference": inference_result,
        "pipeline_status": "LIVE"
    }