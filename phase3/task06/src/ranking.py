from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List


MODEL_VERSION = "skill-ranker-v1.0.0"


def _values(record: Dict[str, Any], keys: Iterable[str]) -> List[Any]:
    values: List[Any] = []

    for key in keys:
        value = record.get(key)

        if isinstance(value, list):
            values.extend(value)
        elif value not in (None, ""):
            values.append(value)

    return values


def extract_skills(record: Dict[str, Any]) -> List[str]:
    raw = _values(
        record,
        [
            "skills",
            "required_skills",
            "candidate_skills",
            "job_skills",
            "matched_skills",
            "missing_skills",
            "technologies",
        ],
    )

    skills: List[str] = []

    for value in raw:
        if isinstance(value, dict):
            for nested in value.values():
                if isinstance(nested, list):
                    skills.extend(str(x).lower() for x in nested)
                elif nested not in (None, ""):
                    skills.append(str(nested).lower())
        else:
            text = str(value).lower()
            parts = re.split(r"[,|;/]+", text)
            skills.extend(part.strip() for part in parts if part.strip())

    return sorted(set(skills))


def stable_item_id(record: Dict[str, Any], index: int) -> str:
    for key in [
        "item_id",
        "job_id",
        "candidate_id",
        "application_id",
        "student_id",
        "id",
    ]:
        value = record.get(key)
        if value not in (None, ""):
            return str(value)

    digest = hashlib.sha256(
        repr(sorted(record.items())).encode("utf-8")
    ).hexdigest()[:12]

    return f"item_{index}_{digest}"


def stable_user_id(record: Dict[str, Any], index: int) -> str:
    for key in [
        "user_id",
        "student_id",
        "candidate_id",
        "applicant_id",
    ]:
        value = record.get(key)
        if value not in (None, ""):
            return str(value)

    return f"user_{index + 1}"


def ranking_score(
    query_skills: List[str],
    item_skills: List[str],
    item_index: int,
) -> float:
    query = set(query_skills)
    item = set(item_skills)

    overlap = len(query.intersection(item))
    union = len(query.union(item))

    similarity = overlap / union if union else 0.0
    prior = 1.0 / (item_index + 1)

    return round(
        min(
            1.0,
            similarity * 0.85 + prior * 0.15,
        ),
        6,
    )


def rank_records(
    request: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    model_version: str = MODEL_VERSION,
) -> Dict[str, Any]:
    request_id = str(
        request.get(
            "request_id",
            request.get("id", "request_1"),
        )
    )

    user_id = stable_user_id(request, 0)
    query_skills = extract_skills(request)

    ranked = []

    for index, candidate in enumerate(candidates):
        item_id = stable_item_id(candidate, index)
        item_skills = extract_skills(candidate)

        score = ranking_score(
            query_skills=query_skills,
            item_skills=item_skills,
            item_index=index,
        )

        ranked.append(
            {
                "item_id": item_id,
                "position": 0,
                "score": score,
                "model_version": model_version,
                "explanation": {
                    "query_skills": query_skills,
                    "item_skills": item_skills,
                    "reason": (
                        "The item is ranked using skill overlap with the "
                        "request and a deterministic tie-breaking prior."
                    ),
                },
            }
        )

    ranked.sort(
        key=lambda x: (
            -x["score"],
            x["item_id"],
        )
    )

    for position, result in enumerate(ranked, start=1):
        result["position"] = position

    ranked_list_id = (
        f"rank_{request_id}_{model_version.replace('.', '_')}"
    )

    return {
        "ranked_list_id": ranked_list_id,
        "request_id": request_id,
        "user_id": user_id,
        "model_version": model_version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "results": ranked,
    }