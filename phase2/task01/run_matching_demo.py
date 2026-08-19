"""
PlaceMux Phase 2 — Task 1
Student ↔ Job Matching Demo
"""

import json
import sys
from pathlib import Path


# Allow importing from phase2/task01/src
CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR / "src"

sys.path.insert(0, str(SRC_DIR))

from matching_engine import calculate_match


student = {
    "student_id": "student_001",

    "skills": [
        "Python",
        "SQL",
        "Machine Learning",
        "Pandas",
        "Scikit-learn"
    ],

    "degree": "B.Tech",
    "field_of_study": "Computer Science",
    "graduation_year": 2026,

    "years_experience": 1.0,
    "experience_roles": [
        "ML Intern"
    ],

    "project_domains": [
        "Machine Learning",
        "NLP"
    ],

    "project_technologies": [
        "Python",
        "Scikit-learn",
        "Flask"
    ],

    "certifications": [
        "Machine Learning Certification"
    ],

    "city": "Raipur",
    "country": "India",

    "work_modes": [
        "remote",
        "hybrid"
    ],

    "preferred_locations": [
        "India"
    ],

    "desired_roles": [
        "ML Engineer",
        "Data Scientist"
    ],

    "verified_scores": {
        "coding": 85,
        "machine_learning": 90
    }
}


job = {
    "job_id": "job_001",

    "required_skills": [
        "Python",
        "Machine Learning",
        "Docker"
    ],

    "preferred_skills": [
        "SQL",
        "Scikit-learn"
    ],

    "required_degree": "B.Tech",

    "required_fields": [
        "Computer Science"
    ],

    "minimum_years_experience": 1.0,

    "preferred_roles": [
        "ML Engineer",
        "Software Engineer"
    ],

    "job_role": "ML Engineer",

    "city": "Raipur",
    "country": "India",

    "work_mode": "remote",

    "employment_type": "full_time",

    "salary_min": 600000,
    "salary_max": 1000000,
    "currency": "INR",

    "required_verified_scores": {
        "coding": 70,
        "machine_learning": 80
    }
}


result = calculate_match(student, job)


print("=" * 70)
print("TASK 1 — STUDENT ↔ JOB MATCHING DEMO")
print("=" * 70)

print("\n========== STUDENT ==========")
print("Student ID :", student["student_id"])
print("Skills     :", ", ".join(student["skills"]))
print("Role       :", ", ".join(student["desired_roles"]))
print("Experience :", student["years_experience"], "years")
print("Work modes :", ", ".join(student["work_modes"]))

print("\n========== JOB ==========")
print("Job ID     :", job["job_id"])
print("Role       :", job["job_role"])
print("Required skills :", ", ".join(job["required_skills"]))
print("Experience requirement :", job["minimum_years_experience"], "years")
print("Work mode  :", job["work_mode"])

print("\n========== MATCH SIGNALS ==========")

for signal, value in result["signals"].items():
    print(f"{signal:<25}: {value:.4f}")

print("\n========== FINAL MATCH ==========")
print(f"Match Score : {result['match_score']:.4f}")
print(f"Match Score % : {result['match_score'] * 100:.2f}%")
print(f"Model Version : {result['model_version']}")

print("\n========== API RESPONSE ==========")

print(
    json.dumps(
        result,
        indent=2
    )
)

print("\nMatching demonstration completed successfully.")