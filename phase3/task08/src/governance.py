from __future__ import annotations

from datetime import datetime, timezone

from .validation import detect_sensitive_fields


def build_governance_report(
    raw_columns: list[str],
    feature_columns: list[str],
) -> dict:
    sensitive_fields = detect_sensitive_fields(
        raw_columns
    )

    return {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "sensitive_fields_detected": sensitive_fields,
        "sensitive_fields_used_by_model": [
            field
            for field in sensitive_fields
            if field in feature_columns
        ],
        "behavioral_feature_policy": (
            "Model features are restricted to observed behavioral "
            "activity features constructed before prediction time."
        ),
        "target_leakage_policy": (
            "Future activity is used only for label construction and "
            "never for prediction-time features."
        ),
        "human_review_policy": (
            "At-risk predictions are prioritization signals for Growth, "
            "not automatic adverse decisions about users."
        ),
        "online_validation_policy": (
            "Offline predictive performance must not be presented as "
            "causal online intervention impact."
        ),
    }


def assert_governance_safe(
    raw_columns: list[str],
    feature_columns: list[str],
) -> None:
    sensitive = detect_sensitive_fields(
        raw_columns
    )

    used_sensitive = [
        field
        for field in sensitive
        if field in feature_columns
    ]

    if used_sensitive:
        raise ValueError(
            "Sensitive/protected fields are being used as model features: "
            + ", ".join(used_sensitive)
        )