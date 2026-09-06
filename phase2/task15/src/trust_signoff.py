import hashlib
import json


def canonical_json(data):
    """Create deterministic JSON for integrity verification."""
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":")
    )


def calculate_hash(data):
    """Calculate SHA-256 hash of canonical data."""
    content = canonical_json(data).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def create_signed_offer(offer):
    """
    Create a tamper-evident offer record.

    This is an integrity demonstration, not a legal e-signature.
    """
    offer_copy = dict(offer)

    offer_hash = calculate_hash(offer_copy)

    offer_copy["integrity"] = {
        "algorithm": "SHA-256",
        "hash": offer_hash,
        "status": "SIGNED"
    }

    return offer_copy


def verify_offer(offer):
    """Verify whether the offer content matches its stored hash."""
    if "integrity" not in offer:
        return False

    stored_hash = offer["integrity"].get("hash")

    if not stored_hash:
        return False

    content = dict(offer)
    del content["integrity"]

    calculated_hash = calculate_hash(content)

    return stored_hash == calculated_hash


def calculate_fp_reduction(
    baseline_false_positive_rate,
    hardened_false_positive_rate
):
    """Calculate percentage reduction in false-positive rate."""
    if baseline_false_positive_rate == 0:
        return 0.0

    reduction = (
        (
            baseline_false_positive_rate
            - hardened_false_positive_rate
        )
        / baseline_false_positive_rate
    ) * 100

    return reduction


def build_trust_signoff(
    parsing_status,
    ontology_coverage,
    proctoring_baseline_fpr,
    proctoring_hardened_fpr,
    offer_verified,
    tampered_offer_rejected
):
    """Build the final AI trust sign-off record."""

    fp_reduction = calculate_fp_reduction(
        proctoring_baseline_fpr,
        proctoring_hardened_fpr
    )

    checks = {
        "parsing": parsing_status == "PASS",
        "ontology_mapping": ontology_coverage >= 1.0,
        "proctoring_false_positive_reduction": (
            proctoring_hardened_fpr
            <= proctoring_baseline_fpr
        ),
        "offer_verification": offer_verified,
        "tamper_detection": tampered_offer_rejected
    }

    overall_pass = all(checks.values())

    return {
        "trust_layer_version": "v1",
        "status": "APPROVED" if overall_pass else "REVIEW",
        "checks": checks,
        "metrics": {
            "ontology_mapping_coverage": ontology_coverage,
            "proctoring_baseline_fpr": proctoring_baseline_fpr,
            "proctoring_hardened_fpr": proctoring_hardened_fpr,
            "false_positive_reduction_percent": fp_reduction
        },
        "evidence": {
            "offer_verified": offer_verified,
            "tampered_offer_rejected": tampered_offer_rejected
        }
    }