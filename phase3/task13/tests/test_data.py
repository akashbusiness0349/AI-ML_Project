from pathlib import Path
import json


TASK_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = TASK_DIR / "data"


def load_json(name: str):
    path = DATA_DIR / name

    assert path.exists(), f"Missing data file: {path}"

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_required_data_files_exist():
    required = [
        "resumes.json",
        "jobs.json",
        "evaluation.json",
    ]

    for name in required:
        assert (DATA_DIR / name).exists(), (
            f"Required Task 13 data file missing: {name}"
        )


def test_resumes_dataset_is_non_empty():
    data = load_json("resumes.json")

    assert isinstance(data, list)
    assert len(data) > 0


def test_jobs_dataset_is_non_empty():
    data = load_json("jobs.json")

    assert isinstance(data, list)
    assert len(data) > 0


def test_resume_records_have_identifiers():
    resumes = load_json("resumes.json")

    for row in resumes:
        assert "resume_id" in row
        assert row["resume_id"]


def test_job_records_have_identifiers():
    jobs = load_json("jobs.json")

    for row in jobs:
        assert "job_id" in row
        assert row["job_id"]


def test_evaluation_dataset_is_non_empty():
    data = load_json("evaluation.json")

    assert isinstance(data, list)
    assert len(data) > 0