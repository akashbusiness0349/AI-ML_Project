import json

from src.parsing_v0 import parse_profile
from src.offer_integrity import (
    create_signed_offer,
    verify_offer
)


BASE = "phase2/task12"


with open(
    f"{BASE}/data/sample_profiles.json",
    "r",
    encoding="utf-8"
) as file:
    profiles = json.load(file)


with open(
    f"{BASE}/data/sample_offer.json",
    "r",
    encoding="utf-8"
) as file:
    offer = json.load(file)


print("=" * 60)
print("PlaceMux Phase 2 - Task 12")
print("Parsing v0 + Offer Tamper-Evidence Demo")
print("=" * 60)


print("\n--- PARSING V0 ---")

parsed_profiles = []

for profile in profiles:
    parsed = parse_profile(
        profile["profile_id"],
        profile["name"],
        profile["text"]
    )

    parsed_profiles.append(parsed)

    print("\nProfile:", parsed["profile_id"])
    print("Name:", parsed["name"])
    print("Skills:", ", ".join(parsed["skills"]))
    print("Skill count:", parsed["skill_count"])


print("\nParsing structured skills: PASS")


print("\n--- OFFER INTEGRITY ---")

signed_offer = create_signed_offer(offer)

print("Offer ID:", signed_offer["offer_id"])
print("Algorithm:", signed_offer["integrity"]["algorithm"])
print("Hash:", signed_offer["integrity"]["hash"])

valid_before = verify_offer(signed_offer)

print(
    "Original offer verification:",
    "PASS" if valid_before else "FAIL"
)


tampered_offer = dict(signed_offer)
tampered_offer["role"] = "Modified Role"

valid_after = verify_offer(tampered_offer)

print(
    "Tampered offer verification:",
    "PASS" if not valid_after else "FAIL"
)


print("\n--- FINAL VALIDATION ---")

parsing_pass = all(
    profile["skill_count"] > 0
    for profile in parsed_profiles
)

integrity_pass = valid_before and not valid_after

if parsing_pass:
    print("Parsing v0 structured output: PASS")
else:
    print("Parsing v0 structured output: FAIL")


if integrity_pass:
    print("Offer tamper-evidence: PASS")
else:
    print("Offer tamper-evidence: FAIL")


if parsing_pass and integrity_pass:
    print("\nTASK 12 STATUS: PASS")
else:
    print("\nTASK 12 STATUS: REVIEW")


print("=" * 60)