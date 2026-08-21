"""
PlaceMux Phase 2 — Task 3
Search & Discovery Demo

Demonstrates:
1. Job ranking for a student.
2. Candidate ranking for a job.
"""

import json
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from ranking_engine import (
    rank_jobs_for_student,
    rank_candidates_for_job,
)


# ============================================================
# STUDENT 1 — USED FOR JOB SEARCH
# ============================================================

student_001 = {
    "student_id": "student_001",
    "name": "Student One",

    "skills": [
        "Python",
        "SQL",
        "Machine Learning",
        "Pandas",
        "Scikit-learn",
        "Flask",
        "Docker"
    ],

    "years_experience": 1.0,

    "desired_roles": [
        "ML Engineer",
        "Data Scientist"
    ],

    "work_modes": [
        "remote",
        "hybrid"
    ],

    "verified_scores": {
        "coding": 85,
        "machine_learning": 90
    }
}


# ============================================================
# JOBS FOR STUDENT SEARCH
# ============================================================

jobs = [
    {
        "job_id": "job_001",
        "company": "AI Labs",
        "job_role": "ML Engineer",

        "required_skills": [
            "Python",
            "Machine Learning",
            "Docker"
        ],

        "preferred_skills": [
            "SQL",
            "Scikit-learn"
        ],

        "minimum_years_experience": 1.0,

        "work_mode": "remote",

        "required_verified_scores": {
            "coding": 70,
            "machine_learning": 80
        }
    },

    {
        "job_id": "job_002",
        "company": "DataWorks",
        "job_role": "Data Scientist",

        "required_skills": [
            "Python",
            "SQL",
            "Pandas"
        ],

        "preferred_skills": [
            "Machine Learning",
            "Scikit-learn"
        ],

        "minimum_years_experience": 1.0,

        "work_mode": "hybrid",

        "required_verified_scores": {
            "coding": 75,
            "machine_learning": 80
        }
    },

    {
        "job_id": "job_003",
        "company": "Web Systems",
        "job_role": "Software Engineer",

        "required_skills": [
            "Java",
            "Spring",
            "Docker"
        ],

        "preferred_skills": [
            "Git"
        ],

        "minimum_years_experience": 2.0,

        "work_mode": "onsite",

        "required_verified_scores": {
            "coding": 80
        }
    }
]


# ============================================================
# CANDIDATES FOR COMPANY SEARCH
# ============================================================

student_002 = {
    "student_id": "student_002",
    "name": "Student Two",

    "skills": [
        "Python",
        "SQL",
        "Pandas"
    ],

    "years_experience": 1.5,

    "desired_roles": [
        "Data Scientist"
    ],

    "work_modes": [
        "hybrid",
        "remote"
    ],

    "verified_scores": {
        "coding": 82,
        "machine_learning": 78
    }
}


student_003 = {
    "student_id": "student_003",
    "name": "Student Three",

    "skills": [
        "Python",
        "Machine Learning",
        "Docker",
        "Scikit-learn"
    ],

    "years_experience": 2.0,

    "desired_roles": [
        "ML Engineer"
    ],

    "work_modes": [
        "remote"
    ],

    "verified_scores": {
        "coding": 92,
        "machine_learning": 95
    }
}


student_004 = {
    "student_id": "student_004",
    "name": "Student Four",

    "skills": [
        "Java",
        "Spring",
        "Docker",
        "Git"
    ],

    "years_experience": 2.5,

    "desired_roles": [
        "Software Engineer"
    ],

    "work_modes": [
        "onsite",
        "hybrid"
    ],

    "verified_scores": {
        "coding": 88,
        "machine_learning": 60
    }
}


candidates = [
    student_001,
    student_002,
    student_003,
    student_004
]


# ============================================================
# JOB RANKING FOR STUDENT
# ============================================================

ranked_jobs = rank_jobs_for_student(
    student_001,
    jobs
)


# ============================================================
# CANDIDATE RANKING FOR JOB
# ============================================================

target_job = jobs[0]

ranked_candidates = rank_candidates_for_job(
    target_job,
    candidates
)


# ============================================================
# OUTPUT
# ============================================================

print("=" * 70)
print("TASK 3 — SEARCH & DISCOVERY")
print("=" * 70)


print("\n========== STUDENT ==========")

print("Student ID :", student_001["student_id"])
print("Name       :", student_001["name"])
print(
    "Skills     :",
    ", ".join(student_001["skills"])
)


print("\n========== JOB RANKING FOR STUDENT ==========")

for item in ranked_jobs:

    print(
        f"{item['rank']}. "
        f"{item['job_id']} | "
        f"{item['job_role']} | "
        f"{item['company']} | "
        f"{item['match_score_percentage']:.2f}%"
    )


print("\n========== JOB ==========")

print("Job ID :", target_job["job_id"])
print("Role   :", target_job["job_role"])
print(
    "Required skills :",
    ", ".join(target_job["required_skills"])
)


print("\n========== CANDIDATE RANKING FOR JOB ==========")

for item in ranked_candidates:

    print(
        f"{item['rank']}. "
        f"{item['student_id']} | "
        f"{item['candidate_name']} | "
        f"{item['match_score_percentage']:.2f}%"
    )


print("\n========== API-STYLE JOB SEARCH RESPONSE ==========")

print(
    json.dumps(
        {
            "student_id": student_001["student_id"],
            "results": ranked_jobs,
            "model_version": "v1"
        },
        indent=2
    )
)


print("\n========== API-STYLE CANDIDATE SEARCH RESPONSE ==========")

print(
    json.dumps(
        {
            "job_id": target_job["job_id"],
            "results": ranked_candidates,
            "model_version": "v1"
        },
        indent=2
    )
)


print("\n========== VERIFICATION ==========")

if ranked_jobs:
    print("Ranked jobs returned       : PASS")
else:
    print("Ranked jobs returned       : FAIL")


if ranked_candidates:
    print("Ranked candidates returned : PASS")
else:
    print("Ranked candidates returned : FAIL")


job_scores = [
    item["match_score"]
    for item in ranked_jobs
]

candidate_scores = [
    item["match_score"]
    for item in ranked_candidates
]


if job_scores == sorted(
    job_scores,
    reverse=True
):
    print("Job ranking order          : PASS")
else:
    print("Job ranking order          : FAIL")


if candidate_scores == sorted(
    candidate_scores,
    reverse=True
):
    print("Candidate ranking order    : PASS")
else:
    print("Candidate ranking order    : FAIL")


print("\nTask 3 search and discovery completed successfully.")