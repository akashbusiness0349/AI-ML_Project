from __future__ import annotations

import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

RANDOM_SEED = 42


SKILL_GROUPS = [
    (
        "data engineering",
        [
            "python",
            "sql",
            "airflow",
            "spark",
            "etl",
            "data pipelines",
            "postgresql",
        ],
    ),
    (
        "machine learning",
        [
            "python",
            "scikit-learn",
            "pytorch",
            "tensorflow",
            "machine learning",
            "model training",
            "mlops",
        ],
    ),
    (
        "frontend",
        [
            "react",
            "javascript",
            "typescript",
            "html",
            "css",
            "frontend",
            "nextjs",
        ],
    ),
    (
        "backend",
        [
            "python",
            "fastapi",
            "django",
            "rest api",
            "postgresql",
            "microservices",
            "backend",
        ],
    ),
    (
        "cloud",
        [
            "aws",
            "docker",
            "kubernetes",
            "terraform",
            "ci cd",
            "cloud",
            "linux",
        ],
    ),
    (
        "analytics",
        [
            "sql",
            "excel",
            "tableau",
            "power bi",
            "statistics",
            "data analysis",
            "reporting",
        ],
    ),
]


def write_json(name: str, data) -> None:
    with (DATA / name).open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            data,
            f,
            indent=2,
        )


def generate_resumes(rng: random.Random) -> list[dict]:
    rows = []

    for index in range(1, 61):
        group_name, skills = rng.choice(
            SKILL_GROUPS
        )

        selected = rng.sample(
            skills,
            k=min(5, len(skills)),
        )

        rows.append(
            {
                "resume_id": f"resume_{index:03d}",
                "title": f"{group_name.title()} Specialist",
                "summary": (
                    f"Professional focused on {group_name}, "
                    f"building practical software and data solutions."
                ),
                "skills": selected,
                "experience": [
                    f"{rng.randint(1, 7)} years of professional experience",
                    f"Worked on {group_name} projects",
                ],
            }
        )

    return rows


def generate_jobs(rng: random.Random) -> list[dict]:
    rows = []

    for index in range(1, 41):
        group_name, skills = rng.choice(
            SKILL_GROUPS
        )

        selected = rng.sample(
            skills,
            k=min(5, len(skills)),
        )

        rows.append(
            {
                "job_id": f"job_{index:03d}",
                "title": f"{group_name.title()} Engineer",
                "description": (
                    f"We are looking for an engineer experienced "
                    f"in {group_name} and related engineering practices."
                ),
                "requirements": selected,
            }
        )

    return rows


def build_queries(rng: random.Random) -> list[dict]:
    query_templates = [
        (
            "someone who can build data pipelines",
            "data engineering",
        ),
        (
            "machine learning model development",
            "machine learning",
        ),
        (
            "frontend developer for modern web applications",
            "frontend",
        ),
        (
            "backend API engineer",
            "backend",
        ),
        (
            "cloud infrastructure and deployment engineer",
            "cloud",
        ),
        (
            "business data reporting and analytics",
            "analytics",
        ),
    ]

    queries = []

    query_id = 1

    for template, group_name in query_templates:
        for split in ("train", "heldout"):
            for repeat in range(4):
                queries.append(
                    {
                        "query_id": f"query_{query_id:03d}",
                        "query": template,
                        "target_group": group_name,
                        "split": split,
                    }
                )
                query_id += 1

    rng.shuffle(queries)
    return queries


def create_labels(
    resumes: list[dict],
    jobs: list[dict],
    queries: list[dict],
) -> list[dict]:
    labels = []

    for query in queries:
        group = query["target_group"]

        relevant = []

        for document in resumes:
            if group in document["title"].lower():
                relevant.append(
                    document["resume_id"]
                )

        for document in jobs:
            if group in document["title"].lower():
                relevant.append(
                    document["job_id"]
                )

        labels.append(
            {
                "query_id": query["query_id"],
                "relevant_ids": relevant,
                "relevance": {
                    doc_id: 3
                    for doc_id in relevant
                },
            }
        )

    return labels


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)

    rng = random.Random(RANDOM_SEED)

    resumes = generate_resumes(rng)
    jobs = generate_jobs(rng)
    queries = build_queries(rng)
    labels = create_labels(
        resumes,
        jobs,
        queries,
    )

    train_queries = [
        q for q in queries
        if q["split"] == "train"
    ]

    heldout_queries = [
        q for q in queries
        if q["split"] == "heldout"
    ]

    write_json("resumes.json", resumes)
    write_json("jobs.json", jobs)
    write_json("search_queries.json", queries)
    write_json("relevance_labels.json", labels)

    write_json(
        "train.json",
        {
            "queries": train_queries,
            "labels": [
                x for x in labels
                if x["query_id"]
                in {
                    q["query_id"]
                    for q in train_queries
                }
            ],
        },
    )

    write_json(
        "heldout.json",
        {
            "queries": heldout_queries,
            "labels": [
                x for x in labels
                if x["query_id"]
                in {
                    q["query_id"]
                    for q in heldout_queries
                }
            ],
        },
    )

    provenance = {
        "task": "Phase 3 Task 13",
        "dataset_version": "1.0",
        "source_type": "synthetic_reproducible_search_corpus",
        "production_data_available": False,
        "production_evidence_status": "NOT_PRODUCTION_EVIDENCE",
        "random_seed": RANDOM_SEED,
        "resume_count": len(resumes),
        "job_count": len(jobs),
        "query_count": len(queries),
        "train_query_count": len(train_queries),
        "heldout_query_count": len(heldout_queries),
        "labelled_evaluation": True,
        "note": (
            "Task 13 owns this dataset independently. "
            "No previous task data is required."
        ),
    }

    write_json(
        "data_provenance.json",
        provenance,
    )

    print(json.dumps(
        provenance,
        indent=2,
    ))


if __name__ == "__main__":
    main()