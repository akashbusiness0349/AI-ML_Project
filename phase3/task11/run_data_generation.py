from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

SEED = 42

random.seed(SEED)


CANDIDATES = [
    {
        "candidate_id": f"candidate_{i:03d}",
        "skills": skills,
        "experience_level": level,
        "location": location,
        "history": [],
    }
    for i, skills, level, location in [
        (1, ["python", "sql", "machine learning"], "entry", "Delhi"),
        (2, ["react", "javascript", "css"], "entry", "Bangalore"),
        (3, ["java", "spring", "sql"], "entry", "Pune"),
        (4, ["python", "fastapi", "postgresql"], "entry", "Hyderabad"),
        (5, ["data analysis", "sql", "excel"], "entry", "Mumbai"),
        (6, ["python", "django", "sql"], "junior", "Delhi"),
        (7, ["react", "typescript", "node"], "junior", "Bangalore"),
        (8, ["java", "spring", "aws"], "junior", "Pune"),
        (9, ["python", "pandas", "ml"], "junior", "Hyderabad"),
        (10, ["sql", "tableau", "excel"], "entry", "Mumbai"),
        (11, ["python", "fastapi", "sql"], "mid", "Delhi"),
        (12, ["react", "javascript", "node"], "mid", "Bangalore"),
        (13, ["java", "spring", "docker"], "mid", "Pune"),
        (14, ["python", "ml", "pandas"], "mid", "Hyderabad"),
        (15, ["sql", "powerbi", "excel"], "mid", "Mumbai"),
        (16, ["python", "aws", "docker"], "senior", "Delhi"),
        (17, ["react", "typescript", "nextjs"], "senior", "Bangalore"),
        (18, ["java", "spring", "kubernetes"], "senior", "Pune"),
        (19, ["python", "ml", "tensorflow"], "senior", "Hyderabad"),
        (20, ["sql", "analytics", "powerbi"], "senior", "Mumbai"),
    ]
]


JOBS = [
    {
        "job_id": f"job_{i:03d}",
        "title": title,
        "company": company,
        "skills": skills,
        "location": location,
        "experience_level": level,
        "popularity": popularity,
    }
    for i, title, company, skills, location, level, popularity in [
        (1, "Junior Python Developer", "TechNova", ["python", "sql", "fastapi"], "Delhi", "entry", 92),
        (2, "Machine Learning Engineer", "DataWorks", ["python", "machine learning", "pandas"], "Bangalore", "entry", 88),
        (3, "Frontend React Developer", "WebCraft", ["react", "javascript", "css"], "Bangalore", "entry", 90),
        (4, "Java Backend Developer", "CloudCore", ["java", "spring", "sql"], "Pune", "entry", 86),
        (5, "Data Analyst", "InsightLabs", ["data analysis", "sql", "excel"], "Mumbai", "entry", 94),
        (6, "Python API Engineer", "ApiWorks", ["python", "fastapi", "postgresql"], "Hyderabad", "junior", 84),
        (7, "React Full Stack Developer", "FrontendLab", ["react", "javascript", "node"], "Bangalore", "junior", 87),
        (8, "Spring Backend Engineer", "CloudCore", ["java", "spring", "aws"], "Pune", "junior", 82),
        (9, "ML Data Scientist", "DataWorks", ["python", "ml", "pandas"], "Hyderabad", "junior", 91),
        (10, "Business Data Analyst", "InsightLabs", ["sql", "tableau", "excel"], "Mumbai", "entry", 89),
        (11, "Senior Python Engineer", "TechNova", ["python", "aws", "docker"], "Delhi", "senior", 85),
        (12, "Senior React Engineer", "WebCraft", ["react", "typescript", "nextjs"], "Bangalore", "senior", 83),
        (13, "Senior Java Engineer", "CloudCore", ["java", "spring", "kubernetes"], "Pune", "senior", 81),
        (14, "Senior ML Engineer", "DataWorks", ["python", "ml", "tensorflow"], "Hyderabad", "senior", 95),
        (15, "Senior Analytics Engineer", "InsightLabs", ["sql", "analytics", "powerbi"], "Mumbai", "senior", 88),
        (16, "Python Platform Engineer", "PlatformX", ["python", "docker", "aws"], "Delhi", "mid", 79),
        (17, "Frontend Platform Engineer", "WebCraft", ["react", "typescript", "node"], "Bangalore", "mid", 80),
        (18, "Java Cloud Engineer", "CloudCore", ["java", "spring", "aws"], "Pune", "mid", 78),
        (19, "Applied ML Engineer", "DataWorks", ["python", "machine learning", "tensorflow"], "Hyderabad", "mid", 93),
        (20, "Product Data Analyst", "InsightLabs", ["sql", "analytics", "excel"], "Mumbai", "mid", 90),
    ]
]


def save(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def relevance_for(candidate: dict, job: dict) -> int:
    candidate_skills = set(candidate["skills"])
    job_skills = set(job["skills"])

    overlap = len(
        candidate_skills & job_skills
    )

    same_location = (
        candidate["location"]
        == job["location"]
    )

    same_experience = (
        candidate["experience_level"]
        == job["experience_level"]
    )

    score = (
        overlap * 3
        + int(same_location) * 2
        + int(same_experience)
    )

    if score >= 6:
        return 3

    if score >= 4:
        return 2

    if score >= 2:
        return 1

    return 0


def generate() -> None:
    impressions = []

    start = datetime(
        2026,
        1,
        1,
        9,
        0,
        tzinfo=timezone.utc,
    )

    session_counter = 0

    for candidate in CANDIDATES:
        for session_number in range(8):
            session_counter += 1

            session_id = (
                f"session_{session_counter:04d}"
            )

            jobs = JOBS.copy()
            random.shuffle(jobs)

            for position, job in enumerate(
                jobs[:10],
                start=1,
            ):
                relevance = relevance_for(
                    candidate,
                    job,
                )

                probability = {
                    0: 0.03,
                    1: 0.15,
                    2: 0.45,
                    3: 0.80,
                }[relevance]

                clicked = (
                    random.random()
                    < probability
                )

                if clicked:
                    event_type = (
                        "apply"
                        if relevance >= 2
                        and random.random() < 0.35
                        else "click"
                    )
                else:
                    event_type = "impression"

                timestamp = (
                    start
                    + timedelta(
                        minutes=len(impressions)
                    )
                )

                impressions.append(
                    {
                        "session_id": session_id,
                        "timestamp": timestamp.isoformat(),
                        "candidate_id": candidate[
                            "candidate_id"
                        ],
                        "job_id": job["job_id"],
                        "position": position,
                        "event_type": event_type,
                        "clicked": int(clicked),
                        "relevance": relevance,
                    }
                )

    random.shuffle(impressions)

    # Re-establish deterministic chronological ordering
    impressions.sort(
        key=lambda x: (
            x["session_id"],
            x["position"],
        )
    )

    # Grouped session split: first 80% sessions train,
    # final 20% sessions heldout.
    sessions = sorted(
        {
            row["session_id"]
            for row in impressions
        }
    )

    split = int(
        len(sessions) * 0.8
    )

    train_sessions = set(
        sessions[:split]
    )

    train = [
        row for row in impressions
        if row["session_id"]
        in train_sessions
    ]

    heldout = [
        row for row in impressions
        if row["session_id"]
        not in train_sessions
    ]

    provenance = {
        "task": "Phase 3 Task 11",
        "dataset_version": "1.0",
        "source_type": "synthetic_logged_impressions",
        "production_data_available": False,
        "production_evidence_status": "NOT_PRODUCTION_EVIDENCE",
        "random_seed": SEED,
        "candidate_count": len(CANDIDATES),
        "job_count": len(JOBS),
        "impression_count": len(impressions),
        "train_impression_count": len(train),
        "heldout_impression_count": len(heldout),
        "split_strategy": (
            "session_grouped_deterministic_holdout"
        ),
        "note": (
            "Task 11 owns this dataset independently. "
            "No Task 07 files are modified or required."
        ),
    }

    save(
        DATA_DIR / "candidates.json",
        CANDIDATES,
    )

    save(
        DATA_DIR / "jobs.json",
        JOBS,
    )

    save(
        DATA_DIR / "impression_logs.json",
        impressions,
    )

    save(
        DATA_DIR / "train.json",
        train,
    )

    save(
        DATA_DIR / "heldout.json",
        heldout,
    )

    save(
        DATA_DIR / "data_provenance.json",
        provenance,
    )

    print(
        json.dumps(
            provenance,
            indent=2,
        )
    )


if __name__ == "__main__":
    generate()