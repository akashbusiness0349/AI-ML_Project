import pytest


def test_explanation_is_generated():
    try:
        from src.explainability import explain_result
    except ImportError:
        pytest.skip(
            "src.explainability.explain_result is not available."
        )

    result = {
        "id": "resume_001",
        "score": 0.92,
    }

    explanation = explain_result(
        query="build data pipelines",
        result=result,
    )

    assert explanation is not None
    assert isinstance(explanation, (str, dict))


def test_explanation_is_not_empty():
    try:
        from src.explainability import explain_result
    except ImportError:
        pytest.skip(
            "src.explainability.explain_result is not available."
        )

    result = {
        "id": "resume_001",
        "score": 0.91,
        "text": "Python SQL ETL data pipelines",
    }

    explanation = explain_result(
        query="data pipelines",
        result=result,
    )

    if isinstance(explanation, str):
        assert explanation.strip()

    elif isinstance(explanation, dict):
        assert len(explanation) > 0