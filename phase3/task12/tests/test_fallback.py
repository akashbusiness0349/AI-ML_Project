from src.fallback import fallback_recommendations


def test_fallback():
    result = fallback_recommendations(
        [
            {"job_id": "job_002"},
            {"job_id": "job_001"},
        ],
        "job_id",
        2,
    )

    assert result["status"] == "FALLBACK"
    assert result["reason"] == "MODEL_UNAVAILABLE"
    assert len(result["recommendations"]) == 2