from src.candidate_to_job import recommend_jobs
from src.company_to_candidate import recommend_candidates


def test_candidate_to_job():
    candidate = {
        "candidate_id": "candidate_001",
        "skills": ["python", "sql"],
        "experience_level": "entry",
        "location": "Delhi",
    }

    jobs = [
        {
            "job_id": "job_001",
            "skills": ["python", "sql"],
            "experience_level": "entry",
            "location": "Delhi",
            "popularity": 90,
        },
        {
            "job_id": "job_002",
            "skills": ["java"],
            "experience_level": "senior",
            "location": "Mumbai",
            "popularity": 90,
        },
    ]

    result = recommend_jobs(
        candidate,
        jobs,
        1,
    )

    assert len(result) == 1
    assert result[0]["job_id"] == "job_001"


def test_company_to_candidate():
    company = {
        "company_id": "company_001",
        "skills": ["python", "sql"],
        "preferred_experience": "entry",
        "location": "Delhi",
    }

    candidates = [
        {
            "candidate_id": "candidate_001",
            "skills": ["python", "sql"],
            "experience_level": "entry",
            "location": "Delhi",
        },
        {
            "candidate_id": "candidate_002",
            "skills": ["java"],
            "experience_level": "senior",
            "location": "Mumbai",
        },
    ]

    result = recommend_candidates(
        company,
        candidates,
        1,
    )

    assert len(result) == 1
    assert result[0]["candidate_id"] == "candidate_001"