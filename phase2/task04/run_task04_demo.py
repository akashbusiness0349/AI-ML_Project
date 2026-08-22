"""
PlaceMux Phase 2 — Task 4
Applications & Shortlisting
Match Explainability Demo
"""

import json
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from explainability_engine import (
    generate_match_explanation
)


# ============================================================
# STUDENT
# ============================================================

student = {
    "student_id": "student_001",

    "skills": [
        "Python",
        "SQL",
        "Machine Learning",
        "Pandas",
        "Scikit-learn",
        "Flask"
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
# JOB
# ============================================================

job = {
    "job_id": "job_001",

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
}


# ============================================================
# MATCH SCORE
# ============================================================

# This represents the score produced by the matching/ranking
# layer from the previous Phase 2 tasks.

match_score = 0.85


# ============================================================
# GENERATE EXPLANATION
# ============================================================

result = generate_match_explanation(
    student,
    job,
    match_score
)


# ============================================================
# OUTPUT
# ============================================================

print("=" * 70)
print("TASK 4 — APPLICATIONS & SHORTLISTING")
print("=" * 70)

print("\n========== MATCH ==========")

print(
    "Student ID :",
    student["student_id"]
)

print(
    "Job ID     :",
    job["job_id"]
)

print(
    f"Match Score : {result['match_score']:.4f}"
)

print(
    f"Match Score % : "
    f"{result['match_score_percentage']:.2f}%"
)


print("\n========== EXPLANATION ==========")

print(
    "Summary :",
    result["explanation"]["summary"]
)


print("\n========== POSITIVE FACTORS ==========")

for factor in result["explanation"]["positive_factors"]:
    print(f"+ {factor}")


print("\n========== NEGATIVE FACTORS ==========")

for factor in result["explanation"]["negative_factors"]:
    print(f"- {factor}")


print("\n========== SKILL EVIDENCE ==========")

skill_evidence = result[
    "explanation"
]["skill_evidence"]

print(
    "Matched required skills :",
    ", ".join(
        skill_evidence[
            "matched_required_skills"
        ]
    )
    or "None"
)

print(
    "Missing required skills :",
    ", ".join(
        skill_evidence[
            "missing_required_skills"
        ]
    )
    or "None"
)

print(
    "Matched preferred skills :",
    ", ".join(
        skill_evidence[
            "matched_preferred_skills"
        ]
    )
    or "None"
)


print("\n========== EXPERIENCE EVIDENCE ==========")

experience = result[
    "explanation"
]["experience_evidence"]

print(
    "Student years :",
    experience["student_years"]
)

print(
    "Required years:",
    experience["required_years"]
)

print(
    "Requirement met:",
    experience["requirement_met"]
)


print("\n========== ROLE EVIDENCE ==========")

role = result[
    "explanation"
]["role_evidence"]

print(
    "Job role :",
    role["job_role"]
)

print(
    "Role match:",
    role["match"]
)


print("\n========== WORK MODE EVIDENCE ==========")

work_mode = result[
    "explanation"
]["work_mode_evidence"]

print(
    "Job work mode :",
    work_mode["job_work_mode"]
)

print(
    "Work mode match:",
    work_mode["match"]
)


print("\n========== VERIFIED SCORE EVIDENCE ==========")

verified = result[
    "explanation"
]["verified_score_evidence"]

print(
    "Passed:",
    ", ".join(verified["passed"])
    or "None"
)

print(
    "Failed:",
    ", ".join(verified["failed"])
    or "None"
)

print(
    "Verified score match:",
    verified["score_match"]
)


print("\n========== STRUCTURED EXPLANATION PAYLOAD ==========")

print(
    json.dumps(
        result,
        indent=2
    )
)


print("\n========== VERIFICATION ==========")

if result["explanation"]["summary"]:
    print(
        "Explanation payload generated : PASS"
    )
else:
    print(
        "Explanation payload generated : FAIL"
    )


if result["explanation"]["positive_factors"]:
    print(
        "Positive factors identified   : PASS"
    )
else:
    print(
        "Positive factors identified   : FAIL"
    )


if result["explanation"]["negative_factors"]:
    print(
        "Negative factors identified   : PASS"
    )
else:
    print(
        "Negative factors identified   : FAIL"
    )


if (
    result["match_score"]
    == match_score
):
    print(
        "Explanation linked to match   : PASS"
    )
else:
    print(
        "Explanation linked to match   : FAIL"
    )


if (
    result["model_version"]
    == "v1"
):
    print(
        "Model version tracking        : PASS"
    )
else:
    print(
        "Model version tracking        : FAIL"
    )


print(
    "\nTask 4 match explainability "
    "completed successfully."
)