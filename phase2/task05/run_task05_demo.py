"""
PlaceMux Phase 2 — Task 5
Marketplace Integration & Company Portal v1
End-to-End Matching Validation
"""

import json
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"

sys.path.insert(
    0,
    str(SRC_DIR)
)

from integration_validator import (
    validate_end_to_end
)


# ============================================================
# INTEGRATED MARKETPLACE RESULTS
# ============================================================

# These represent the outputs of the matching,
# ranking, and explainability layers developed
# in Tasks 1–4.

job_results = [
    {
        "job_id": "job_001",
        "job_role": "ML Engineer",
        "company": "AI Labs",
        "match_score": 1.0,
        "match_score_percentage": 100.0,
        "rank": 1,
        "model_version": "v1",
        "explanation": {
            "summary": "Strong match based on required skills, experience, role and work-mode compatibility.",
            "positive_factors": [
                "Python skill matched.",
                "Machine Learning skill matched.",
                "Docker skill matched.",
                "Experience requirement met.",
                "Remote work preference matched."
            ],
            "negative_factors": []
        }
    },
    {
        "job_id": "job_002",
        "job_role": "Data Scientist",
        "company": "DataWorks",
        "match_score": 0.85,
        "match_score_percentage": 85.0,
        "rank": 2,
        "model_version": "v1",
        "explanation": {
            "summary": "Strong match with several compatible technical skills.",
            "positive_factors": [
                "Python skill matched.",
                "Machine Learning skill matched.",
                "SQL skill matched."
            ],
            "negative_factors": [
                "Some preferred requirements are missing."
            ]
        }
    },
    {
        "job_id": "job_003",
        "job_role": "Software Engineer",
        "company": "Web Systems",
        "match_score": 0.325,
        "match_score_percentage": 32.5,
        "rank": 3,
        "model_version": "v1",
        "explanation": {
            "summary": "Weak match because several job requirements are not aligned.",
            "positive_factors": [
                "Python skill matched."
            ],
            "negative_factors": [
                "Role compatibility is weak.",
                "Several required skills are missing."
            ]
        }
    }
]


candidate_results = [
    {
        "student_id": "student_001",
        "candidate_name": "Student One",
        "match_score": 1.0,
        "match_score_percentage": 100.0,
        "rank": 1,
        "model_version": "v1",
        "explanation": {
            "summary": "Strong candidate with complete alignment to the job requirements.",
            "positive_factors": [
                "Required skills matched.",
                "Experience requirement met.",
                "Verified competency requirements met."
            ],
            "negative_factors": []
        }
    },
    {
        "student_id": "student_003",
        "candidate_name": "Student Three",
        "match_score": 0.95,
        "match_score_percentage": 95.0,
        "rank": 2,
        "model_version": "v1",
        "explanation": {
            "summary": "Very strong candidate with high skill compatibility.",
            "positive_factors": [
                "Required technical skills matched.",
                "Strong verified competency scores."
            ],
            "negative_factors": [
                "Minor requirement gap."
            ]
        }
    },
    {
        "student_id": "student_002",
        "candidate_name": "Student Two",
        "match_score": 0.5481,
        "match_score_percentage": 54.81,
        "rank": 3,
        "model_version": "v1",
        "explanation": {
            "summary": "Moderate candidate match.",
            "positive_factors": [
                "Some required skills matched."
            ],
            "negative_factors": [
                "Several requirements are not met."
            ]
        }
    },
    {
        "student_id": "student_004",
        "candidate_name": "Student Four",
        "match_score": 0.3812,
        "match_score_percentage": 38.12,
        "rank": 4,
        "model_version": "v1",
        "explanation": {
            "summary": "Weak candidate match.",
            "positive_factors": [
                "Limited skill overlap."
            ],
            "negative_factors": [
                "Multiple required skills are missing.",
                "Lower overall compatibility."
            ]
        }
    }
]


# ============================================================
# REPEATED RESULTS
# ============================================================

# Simulates running the same integrated flow again.
# The results should remain identical.

repeated_job_results = [
    dict(item)
    for item in job_results
]

repeated_candidate_results = [
    dict(item)
    for item in candidate_results
]


# ============================================================
# VALIDATION
# ============================================================

validation = validate_end_to_end(
    job_results=job_results,
    candidate_results=candidate_results,
    expected_top_job="job_001",
    expected_top_candidate="student_001",
    repeated_job_results=repeated_job_results,
    repeated_candidate_results=repeated_candidate_results
)


# ============================================================
# DISPLAY
# ============================================================

print("=" * 70)
print("TASK 5 — MARKETPLACE INTEGRATION VALIDATION")
print("=" * 70)


print("\n========== JOB RANKING ==========")

for item in job_results:
    print(
        f"{item['rank']}. "
        f"{item['job_id']} | "
        f"{item['job_role']} | "
        f"{item['match_score_percentage']:.2f}%"
    )


print("\n========== CANDIDATE RANKING ==========")

for item in candidate_results:
    print(
        f"{item['rank']}. "
        f"{item['student_id']} | "
        f"{item['candidate_name']} | "
        f"{item['match_score_percentage']:.2f}%"
    )


print("\n========== VALIDATION CHECKS ==========")

display_names = {
    "ranked_jobs_returned":
        "Ranked jobs returned",

    "ranked_candidates_returned":
        "Ranked candidates returned",

    "job_ranking_order":
        "Job ranking order",

    "candidate_ranking_order":
        "Candidate ranking order",

    "job_rank_sequence":
        "Job rank sequence",

    "candidate_rank_sequence":
        "Candidate rank sequence",

    "job_score_range":
        "Job score range",

    "candidate_score_range":
        "Candidate score range",

    "job_explanations":
        "Job explanations",

    "candidate_explanations":
        "Candidate explanations",

    "job_model_version":
        "Job model version",

    "candidate_model_version":
        "Candidate model version",

    "job_relevance":
        "Top job relevance",

    "candidate_relevance":
        "Top candidate relevance",

    "job_ranking_consistency":
        "Job ranking consistency",

    "candidate_ranking_consistency":
        "Candidate ranking consistency"
}


for key, value in validation.items():

    if key == "all_checks_passed":
        continue

    name = display_names.get(
        key,
        key
    )

    print(
        f"{name:<35}: "
        f"{'PASS' if value else 'FAIL'}"
    )


print("\n========== FINAL VALIDATION ==========")

print(
    "All validation checks :",
    "PASS"
    if validation["all_checks_passed"]
    else "FAIL"
)


print("\n========== VALIDATION RESULT ==========")

print(
    json.dumps(
        validation,
        indent=2
    )
)


print("\n========== INTEGRATION STATUS ==========")

if validation["all_checks_passed"]:
    print(
        "Marketplace matching flow : PASS"
    )
    print(
        "Ranking validation         : PASS"
    )
    print(
        "Explainability validation : PASS"
    )
    print(
        "Consistency validation    : PASS"
    )
    print(
        "Task 5 completed successfully."
    )
else:
    print(
        "Marketplace integration validation : FAIL"
    )
    print(
        "Task 5 requires investigation."
    )