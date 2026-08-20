"""
PlaceMux Phase 2 — Task 2
Job Posting with Skill Thresholds
"""

import json
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from threshold_engine import build_threshold_match


student = {
    "student_id": "student_001",

    "competency_scores": {
        "Python": 85,
        "SQL": 55,
        "Machine Learning": 90,
        "Docker": 70,
        "Git": 80,
    },
}


job = {
    "job_id": "job_001",

    "title": "Junior ML Engineer",

    "skill_thresholds": {
        "Python": 70,
        "SQL": 60,
        "Machine Learning": 75,
        "Docker": 50,
        "Git": 70,
    },
}


result = build_threshold_match(
    student_id=student["student_id"],
    job_id=job["job_id"],
    student_scores=student["competency_scores"],
    job_thresholds=job["skill_thresholds"],
)


print("=" * 70)
print("TASK 2 — JOB POSTING WITH SKILL THRESHOLDS")
print("=" * 70)

print("\n========== JOB ==========")
print("Job ID :", job["job_id"])
print("Title  :", job["title"])

print("\n========== JOB THRESHOLDS ==========")

for skill, threshold in job["skill_thresholds"].items():
    print(f"{skill:<22}: >= {threshold}")

print("\n========== STUDENT COMPETENCY ==========")

for skill, score in student["competency_scores"].items():
    print(f"{skill:<22}: {score}")

print("\n========== MATCH VECTOR ==========")

for skill, value in result["match_vector"].items():
    status = "PASS" if value == 1 else "FAIL"
    print(f"{skill:<22}: {value} ({status})")

print("\n========== THRESHOLD → COMPETENCY MAPPING ==========")

for skill, data in result["threshold_mapping"].items():

    print(f"\n{skill}")
    print(
        f"  Student score       : {data['student_score']}"
    )
    print(
        f"  Required threshold  : {data['required_threshold']}"
    )
    print(
        f"  Student competency  : {data['student_competency']}"
    )
    print(
        f"  Required competency : {data['threshold_competency']}"
    )
    print(
        f"  Threshold met       : {data['threshold_met']}"
    )

print("\n========== FINAL VECTOR SCORE ==========")

print(
    f"Vector score : {result['vector_score']:.4f}"
)

print(
    f"Vector score % : "
    f"{result['vector_score_percentage']:.2f}%"
)

print(
    f"Model version : {result['model_version']}"
)

print("\n========== API-STYLE RESULT ==========")

print(
    json.dumps(
        result,
        indent=2,
    )
)

print("\nTask 2 threshold matching completed successfully.")