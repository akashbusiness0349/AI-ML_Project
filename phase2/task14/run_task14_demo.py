import json

from src.ontology_mapper import (
    load_ontology,
    build_skill_mapping,
    extract_skills,
    map_skills_to_ontology,
    calculate_mapping_coverage
)


BASE = "phase2/task14"


with open(
    f"{BASE}/data/sample_profiles.json",
    "r",
    encoding="utf-8"
) as file:
    profiles = json.load(file)


ontology = load_ontology(
    f"{BASE}/data/ontology.json"
)

skill_mapping = build_skill_mapping(ontology)


print("=" * 60)
print("PlaceMux Phase 2 - Task 14")
print("Parsing v0 -> Skills Ontology Demo")
print("=" * 60)


all_profiles_pass = True
coverage_values = []


print("\n--- PROFILE ONTOLOGY MAPPING ---")


for profile in profiles:

    parsed_skills = extract_skills(
        profile["text"],
        skill_mapping
    )

    result = map_skills_to_ontology(
        parsed_skills,
        skill_mapping
    )

    coverage = calculate_mapping_coverage(
        parsed_skills,
        result
    )

    coverage_values.append(coverage)

    print(
        f"\nProfile: {profile['profile_id']}"
    )

    print(
        f"Name: {profile['name']}"
    )

    print(
        "Parsed skills:",
        ", ".join(parsed_skills)
    )

    print("Ontology categories:")

    for category, skills in result[
        "mapped_categories"
    ].items():

        print(
            f"  {category}: "
            f"{', '.join(skills)}"
        )

    if result["unmapped_skills"]:

        print(
            "Unmapped skills:",
            ", ".join(
                result["unmapped_skills"]
            )
        )

    else:

        print(
            "Unmapped skills: None"
        )

    print(
        "Mapping coverage:",
        f"{coverage * 100:.2f}%"
    )

    if coverage < 1.0:
        all_profiles_pass = False


average_coverage = (
    sum(coverage_values)
    / len(coverage_values)
    if coverage_values
    else 0.0
)


print("\n--- ONTOLOGY VALIDATION ---")


ontology_pass = (
    ontology.get("ontology_version")
    and len(ontology.get("categories", {})) > 0
)


print(
    "Ontology loaded:",
    "PASS" if ontology_pass else "FAIL"
)


print(
    "All parsed skills mapped:",
    "PASS"
    if all_profiles_pass
    else "FAIL"
)


print(
    "Average mapping coverage:",
    f"{average_coverage * 100:.2f}%"
)


print("\n--- EDGE CASE VALIDATION ---")


known_skill = "python"
unknown_skill = "unknown skill"


edge_result = map_skills_to_ontology(
    [
        known_skill,
        unknown_skill
    ],
    skill_mapping
)


known_skill_pass = (
    known_skill
    in edge_result["mapped_categories"].get(
        "programming",
        []
    )
)


unknown_skill_pass = (
    unknown_skill
    in edge_result["unmapped_skills"]
)


print(
    "Known skill mapped:",
    "PASS" if known_skill_pass else "FAIL"
)


print(
    "Unknown skill handled:",
    "PASS"
    if unknown_skill_pass
    else "FAIL"
)


print("\n--- FINAL VALIDATION ---")


final_pass = (
    ontology_pass
    and all_profiles_pass
    and known_skill_pass
    and unknown_skill_pass
)


print(
    "Parsing -> ontology integration:",
    "PASS" if final_pass else "FAIL"
)


if final_pass:
    print("\nTASK 14 STATUS: PASS")
else:
    print("\nTASK 14 STATUS: REVIEW")


print("=" * 60)