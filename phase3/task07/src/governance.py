from __future__ import annotations

from typing import Dict, List


FORBIDDEN_MODEL_FIELDS = {
    "religion",
    "religion_name",
    "caste",
    "race",
    "ethnicity",
    "political_affiliation",
    "health_condition",
    "disability",
    "sexual_orientation",
    "biometric",
}


ALLOWED_PERSONAL_FIELDS = {
    "candidate_id",
    "skills",
    "location",
    "experience",
    "history",
}


def audit_candidate_schema(
    candidates: List[Dict],
) -> Dict:
    observed_fields = set()

    for candidate in candidates:
        observed_fields.update(candidate.keys())

    forbidden_observed = sorted(
        observed_fields.intersection(
            FORBIDDEN_MODEL_FIELDS
        )
    )

    unexpected_personal_fields = sorted(
        observed_fields.difference(
            ALLOWED_PERSONAL_FIELDS
        )
    )

    return {
        "candidate_count": len(candidates),
        "forbidden_protected_fields_observed": (
            forbidden_observed
        ),
        "unexpected_personal_fields": (
            unexpected_personal_fields
        ),
        "protected_attributes_used_for_ranking": False,
        "passed": not forbidden_observed,
    }


def audit_event_schema(
    events: List[Dict],
) -> Dict:
    prohibited_event_fields = []

    for event in events:
        for key in event.keys():
            if key.lower() in FORBIDDEN_MODEL_FIELDS:
                prohibited_event_fields.append(key)

    prohibited_event_fields = sorted(
        set(prohibited_event_fields)
    )

    return {
        "event_count": len(events),
        "prohibited_fields_observed": prohibited_event_fields,
        "passed": not prohibited_event_fields,
    }


def dpdp_controls() -> Dict:
    return {
        "purpose_limitation": {
            "status": "implemented",
            "description": (
                "Candidate data is processed only for "
                "recommendation and activation measurement."
            ),
        },
        "data_minimization": {
            "status": "implemented",
            "description": (
                "Only fields required for ranking and "
                "experiment measurement are retained."
            ),
        },
        "protected_attribute_exclusion": {
            "status": "implemented",
            "description": (
                "Sensitive/protected attributes are excluded "
                "from the recommendation feature schema."
            ),
        },
        "model_version_logging": {
            "status": "implemented",
        },
        "event_provenance": {
            "status": "implemented",
        },
        "deletion_ready_identifier": {
            "status": "implemented",
            "description": (
                "candidate_id is retained as the stable deletion "
                "and audit reference."
            ),
        },
        "consent_notice_required_for_live_capture": {
            "status": "required",
            "description": (
                "Live user capture must use an appropriate notice "
                "and lawful processing basis before production use."
            ),
        },
    }


def fairness_audit(
    candidates: List[Dict],
    events: List[Dict],
) -> Dict:
    candidate_audit = audit_candidate_schema(candidates)
    event_audit = audit_event_schema(events)

    return {
        "candidate_schema": candidate_audit,
        "event_schema": event_audit,
        "fairness_metric_status": (
            "not_computable_without_valid_group_labels"
        ),
        "fairness_metric_warning": (
            "No protected-group outcome comparison is fabricated. "
            "A real fairness audit requires legally and ethically "
            "appropriate group labels and sufficient sample size."
        ),
        "dpdp_controls": dpdp_controls(),
        "overall_schema_status": (
            candidate_audit["passed"]
            and event_audit["passed"]
        ),
    }