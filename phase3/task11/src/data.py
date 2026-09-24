from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def load_json(path: str | Path) -> Any:
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_candidates() -> list[dict]:
    return load_json(DATA_DIR / "candidates.json")


def load_jobs() -> list[dict]:
    return load_json(DATA_DIR / "jobs.json")


def load_impressions() -> list[dict]:
    return load_json(DATA_DIR / "impression_logs.json")


def load_train() -> list[dict]:
    return load_json(DATA_DIR / "train.json")


def load_heldout() -> list[dict]:
    return load_json(DATA_DIR / "heldout.json")


def candidate_map(candidates: list[dict]) -> dict[str, dict]:
    return {
        row["candidate_id"]: row
        for row in candidates
    }


def job_map(jobs: list[dict]) -> dict[str, dict]:
    return {
        row["job_id"]: row
        for row in jobs
    }