from src.explainability import (
    explain_candidate_job,
)


def test_candidate_job_explanation():
    text = explain_candidate_job(
        {
            "skills": ["python", "sql"],
            "experience_level": "entry",
            "location": "Delhi",
        },
        {
            "skills": ["python", "sql"],
            "experience_level": "entry",
            "location": "Delhi",
        },
        {
            "skill_overlap": 1.0,
            "experience_match": 1.0,
            "location_match": 1.0,
            "popularity": 0.9,
        },
    )

    assert "Recommended because" in text
    assert "skills" in text