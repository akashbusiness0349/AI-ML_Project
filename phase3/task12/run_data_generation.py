from __future__ import annotations

import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

random.seed(42)


SKILL_POOL = [
    "python",
    "sql",
    "machine learning",
    "fastapi",
    "react",
    "javascript",
    "css",
    "java",
    "spring",
    "data analysis",
    "excel",
    "aws",
    "docker",
    "kubernetes",
    "pandas",
    "tensorflow",
]

LOCATIONS = [
    "Delhi",
    "Bangalore",
    "Pune",
    "Hyderabad",
    "Mumbai",
]

EXPERIENCE = [
    "entry",
    "mid",
    "senior",
]


def write(name, value):
    with (DATA / name).open("w", encoding="utf-8") as f:
        json.dump(value, f, indent=2)


def make_candidates():
    rows = []

    for i in range(1, 21):
        skills = random.sample(
            SKILL_POOL,
            4,
        )

        rows.append(
            {
                "candidate_id": f"candidate_{i:03d}",
                "skills": skills,
                "experience_level": EXPERIENCE[
                    (i - 1) % len(EXPERIENCE)
                ],
                "location": LOCATIONS[
                    (i - 1) % len(LOCATIONS)
                ],
            }
        )

    return rows


def make_companies():
    rows = []

    for i in range(1, 11):
        rows.append(
            {
                "company_id": f"company_{i:03d}",
                "name": f"Company {i:03d}",
                "skills": random.sample(
                    SKILL_POOL,
                    4,
                ),
                "preferred_experience": EXPERIENCE[
                    (i - 1) % len(EXPERIENCE)
                ],
                "location": LOCATIONS[
                    (i - 1) % len(LOCATIONS)
                ],
            }
        )

    return rows


def make_jobs():
    rows = []

    for i in range(1, 21):
        rows.append(
            {
                "job_id": f"job_{i:03d}",
                "title": f"Technology Role {i:03d}",
                "company_id": f"company_{((i - 1) % 10) + 1:03d}",
                "skills": random.sample(
                    SKILL_POOL,
                    4,
                ),
                "experience_level": EXPERIENCE[
                    (i - 1) % len(EXPERIENCE)
                ],
                "location": LOCATIONS[
                    (i - 1) % len(LOCATIONS)
                ],
                "popularity": random.randint(
                    50,
                    99,
                ),
            }
        )

    return rows


def relevance(candidate, job):
    candidate_skills = set(candidate["skills"])
    job_skills = set(job["skills"])

    overlap = len(
        candidate_skills & job_skills
    )

    score = overlap

    if candidate["experience_level"] == job["experience_level"]:
        score += 1

    if candidate["location"] == job["location"]:
        score += 1

    if score >= 4:
        return 3

    if score >= 2:
        return 2

    if score >= 1:
        return 1

    return 0


def make_interactions(candidates, jobs):
    rows = []

    interaction_id = 1

    for candidate in candidates:
        selected_jobs = random.sample(
            jobs,
            16,
        )

        for position, job in enumerate(
            selected_jobs,
            start=1,
        ):
            rel = relevance(
                candidate,
                job,
            )

            if rel >= 3:
                event_type = "apply"
            elif rel >= 1:
                event_type = "click"
            else:
                event_type = "impression"

            rows.append(
                {
                    "interaction_id": f"int_{interaction_id:05d}",
                    "session_id": (
                        f"session_{candidate['candidate_id']}"
                    ),
                    "candidate_id": candidate[
                        "candidate_id"
                    ],
                    "company_id": job["company_id"],
                    "job_id": job["job_id"],
                    "position": position,
                    "event_type": event_type,
                    "relevance": rel,
                }
            )

            interaction_id += 1

    return rows


def main():
    DATA.mkdir(
        parents=True,
        exist_ok=True,
    )

    candidates = make_candidates()
    companies = make_companies()
    jobs = make_jobs()
    interactions = make_interactions(
        candidates,
        jobs,
    )

    session_ids = sorted(
        {
            row["session_id"]
            for row in interactions
        }
    )

    heldout_sessions = set(
        session_ids[-4:]
    )

    train = [
        row
        for row in interactions
        if row["session_id"]
        not in heldout_sessions
    ]

    heldout = [
        row
        for row in interactions
        if row["session_id"]
        in heldout_sessions
    ]

    write("candidates.json", candidates)
    write("companies.json", companies)
    write("jobs.json", jobs)
    write("interactions.json", interactions)
    write("train.json", train)
    write("heldout.json", heldout)

    provenance = {
        "task": "Phase 3 Task 12",
        "dataset_version": "1.0",
        "source_type": "synthetic_logged_recommendation_interactions",
        "production_data_available": False,
        "production_evidence_status": "NOT_PRODUCTION_EVIDENCE",
        "random_seed": 42,
        "candidate_count": len(candidates),
        "company_count": len(companies),
        "job_count": len(jobs),
        "interaction_count": len(interactions),
        "train_count": len(train),
        "heldout_count": len(heldout),
        "split_strategy": "session_grouped_deterministic_holdout",
        "task_ownership": "Task 12 independent dataset",
    }

    write(
        "data_provenance.json",
        provenance,
    )

    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()