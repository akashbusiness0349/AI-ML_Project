from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def load_json(filename: str) -> Any:
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing data file: {path}")

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(filename: str, data: Any) -> None:
    path = DATA_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def load_candidates() -> list[dict]:
    return load_json("candidates.json")


def load_companies() -> list[dict]:
    return load_json("companies.json")


def load_jobs() -> list[dict]:
    return load_json("jobs.json")


def load_interactions() -> list[dict]:
    return load_json("interactions.json")


def load_train() -> list[dict]:
    return load_json("train.json")


def load_heldout() -> list[dict]:
    return load_json("heldout.json")


def candidate_map() -> dict[str, dict]:
    return {
        row["candidate_id"]: row
        for row in load_candidates()
    }


def company_map() -> dict[str, dict]:
    return {
        row["company_id"]: row
        for row in load_companies()
    }


def job_map() -> dict[str, dict]:
    return {
        row["job_id"]: row
        for row in load_jobs()
    }