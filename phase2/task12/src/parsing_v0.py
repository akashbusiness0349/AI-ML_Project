import re


SKILLS = [
    "python",
    "sql",
    "machine learning",
    "scikit-learn",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "docker",
    "git",
    "fastapi",
    "faiss",
    "nlp",
    "deep learning"
]


def extract_skills(text):
    text_lower = text.lower()

    found = []

    for skill in SKILLS:
        if skill in text_lower:
            found.append(skill)

    return sorted(found)


def parse_profile(profile_id, name, text):
    skills = extract_skills(text)

    return {
        "profile_id": profile_id,
        "name": name,
        "type": "profile",
        "skills": skills,
        "skill_count": len(skills)
    }


def parse_job(job_id, title, text):
    skills = extract_skills(text)

    return {
        "job_id": job_id,
        "title": title,
        "type": "job",
        "required_skills": skills,
        "required_skill_count": len(skills)
    }