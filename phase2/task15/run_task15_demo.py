import json

from src.trust_signoff import (
    create_signed_offer,
    verify_offer,
    build_trust_signoff
)


BASE = "phase2/task15"


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


print("=" * 64)
print("PlaceMux Phase 2 - Task 15")
print("Trust Layer Integration & Dry Run")
print("=" * 64)


# ---------------------------------------------------------
# Load dry-run data
# ---------------------------------------------------------

dry_run = load_json(
    f"{BASE}/data/dry_run_cases.json"
)


# ---------------------------------------------------------
# Parsing + Ontology
# ---------------------------------------------------------

parsing = dry_run["parsing"]

parsing_status = parsing["status"]

ontology_coverage = parsing[
    "mapping_coverage"
]

print("\n--- PARSING & ONTOLOGY ---")

print(
    "Parsing status:",
    parsing_status
)

print(
    "Profiles checked:",
    parsing["profiles_checked"]
)

print(
    "Ontology mapping coverage:",
    f"{ontology_coverage * 100:.2f}%"
)


# ---------------------------------------------------------
# Proctoring
# ---------------------------------------------------------

proctoring = dry_run["proctoring"]

baseline_fpr = proctoring[
    "baseline_false_positive_rate"
]

hardened_fpr = proctoring[
    "hardened_false_positive_rate"
]

detection_rate = proctoring[
    "detection_rate"
]


print("\n--- PROCTORING TRUST CHECK ---")

print(
    "Sessions checked:",
    proctoring["sessions_checked"]
)

print(
    "Baseline false-positive rate:",
    f"{baseline_fpr * 100:.2f}%"
)

print(
    "Hardened false-positive rate:",
    f"{hardened_fpr * 100:.2f}%"
)

print(
    "Detection rate:",
    f"{detection_rate * 100:.2f}%"
)


# ---------------------------------------------------------
# Application -> Job match
# ---------------------------------------------------------

application = dry_run["application"]


print("\n--- APPLICATION -> JOB ---")

print(
    "Student:",
    application["student_id"]
)

print(
    "Job:",
    application["job_id"]
)

print(
    "Match score:",
    f"{application['match_score'] * 100:.2f}%"
)

print(
    "Match status:",
    application["match_status"]
)

print(
    "Reason:",
    application["reason"]
)


# ---------------------------------------------------------
# Offer signing
# ---------------------------------------------------------

offer = dry_run["offer"]


print("\n--- OFFER INTEGRITY ---")

signed_offer = create_signed_offer(
    offer
)

original_verified = verify_offer(
    signed_offer
)

print(
    "Offer created:",
    "PASS"
    if signed_offer.get("integrity")
    else "FAIL"
)

print(
    "Original offer verification:",
    "PASS"
    if original_verified
    else "FAIL"
)

print(
    "Integrity algorithm:",
    signed_offer[
        "integrity"
    ]["algorithm"]
)


# ---------------------------------------------------------
# Tamper test
# ---------------------------------------------------------

tampered_offer = dict(
    signed_offer
)

tampered_offer["role"] = (
    "Tampered Role"
)

tampered_verified = verify_offer(
    tampered_offer
)

tampered_offer_rejected = (
    not tampered_verified
)


print(
    "Tampered offer rejected:",
    "PASS"
    if tampered_offer_rejected
    else "FAIL"
)


# ---------------------------------------------------------
# Build AI trust sign-off
# ---------------------------------------------------------

signoff = build_trust_signoff(
    parsing_status=parsing_status,
    ontology_coverage=ontology_coverage,
    proctoring_baseline_fpr=baseline_fpr,
    proctoring_hardened_fpr=hardened_fpr,
    offer_verified=original_verified,
    tampered_offer_rejected=tampered_offer_rejected
)


# ---------------------------------------------------------
# Persist final sign-off
# ---------------------------------------------------------

with open(
    f"{BASE}/data/trust_signoff.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        signoff,
        file,
        indent=2
    )


# ---------------------------------------------------------
# Final validation
# ---------------------------------------------------------

print("\n--- AI TRUST SIGN-OFF ---")

print(
    "Trust layer version:",
    signoff["trust_layer_version"]
)

print(
    "Status:",
    signoff["status"]
)

print(
    "False-positive reduction:",
    f"{signoff['metrics']['false_positive_reduction_percent']:.2f}%"
)

print(
    "Parsing check:",
    "PASS"
    if signoff["checks"]["parsing"]
    else "FAIL"
)

print(
    "Ontology check:",
    "PASS"
    if signoff["checks"]["ontology_mapping"]
    else "FAIL"
)

print(
    "Proctoring check:",
    "PASS"
    if signoff["checks"][
        "proctoring_false_positive_reduction"
    ]
    else "FAIL"
)

print(
    "Offer verification check:",
    "PASS"
    if signoff["checks"]["offer_verification"]
    else "FAIL"
)

print(
    "Tamper detection check:",
    "PASS"
    if signoff["checks"]["tamper_detection"]
    else "FAIL"
)


final_pass = (
    signoff["status"] == "APPROVED"
    and all(signoff["checks"].values())
)


print("\n--- FINAL DRY RUN ---")

print(
    "Application -> Offer:",
    "PASS"
    if final_pass
    else "FAIL"
)

print(
    "AI Trust Sign-off:",
    "PASS"
    if final_pass
    else "FAIL"
)

if final_pass:
    print("\nTASK 15 STATUS: PASS")
else:
    print("\nTASK 15 STATUS: REVIEW")


print("=" * 64)