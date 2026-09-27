from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename: str, data: Any) -> None:
    path = DATA_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_resumes() -> list[dict]:
    return load_json("resumes.json")


def load_jobs() -> list[dict]:
    return load_json("jobs.json")


def load_queries(filename: str = "search_queries.json") -> list[dict]:
    return load_json(filename)


def load_labels() -> list[dict]:
    return load_json("relevance_labels.json")


def load_train() -> dict:
    return load_json("train.json")


def load_heldout() -> dict:
    return load_json("heldout.json")


def document_text(document: dict) -> str:
    fields = [
        document.get("title", ""),
        document.get("summary", ""),
        document.get("skills", []),
        document.get("experience", []),
        document.get("description", ""),
        document.get("requirements", []),
    ]

    parts: list[str] = []

    for field in fields:
        if isinstance(field, list):
            parts.extend(str(x) for x in field)
        elif field:
            parts.append(str(field))

    return " ".join(parts)


def all_documents() -> list[dict]:
    resumes = load_resumes()
    jobs = load_jobs()

    documents = []

    for resume in resumes:
        row = dict(resume)
        row["doc_type"] = "resume"
        row["doc_id"] = row["resume_id"]
        documents.append(row)

    for job in jobs:
        row = dict(job)
        row["doc_type"] = "job"
        row["doc_id"] = row["job_id"]
        documents.append(row)

    return documents


def document_map() -> dict[str, dict]:
    return {
        row["doc_id"]: row
        for row in all_documents()
    }