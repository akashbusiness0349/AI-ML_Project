import json


def load_ontology(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_skill_mapping(ontology):
    mapping = {}

    for category, skills in ontology["categories"].items():
        for skill in skills:
            mapping[skill.lower()] = category

    return mapping


def extract_skills(text, skill_mapping):
    text_lower = text.lower()

    found = []

    for skill in skill_mapping:
        if skill in text_lower:
            found.append(skill)

    return sorted(set(found))


def map_skills_to_ontology(skills, skill_mapping):
    mapped = {}
    unmapped = []

    for skill in skills:
        normalized = skill.lower()

        if normalized in skill_mapping:
            category = skill_mapping[normalized]

            mapped.setdefault(category, []).append(skill)
        else:
            unmapped.append(skill)

    return {
        "mapped_categories": mapped,
        "unmapped_skills": unmapped
    }


def calculate_mapping_coverage(skills, result):
    if not skills:
        return 0.0

    mapped_count = sum(
        len(values)
        for values in result["mapped_categories"].values()
    )

    return mapped_count / len(skills)