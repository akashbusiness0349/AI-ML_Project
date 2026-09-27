import pytest


def test_fallback_is_available():
    try:
        from src.fallback import fallback_search
    except ImportError:
        pytest.skip(
            "src.fallback.fallback_search is not available."
        )

    documents = [
        {
            "id": "resume_001",
            "text": "Python SQL data engineering",
        }
    ]

    results = fallback_search(
        "data engineering",
        documents,
        top_k=1,
    )

    assert results is not None


def test_fallback_does_not_crash():
    try:
        from src.fallback import fallback_search
    except ImportError:
        pytest.skip(
            "src.fallback.fallback_search is not available."
        )

    documents = []

    results = fallback_search(
        "data engineering",
        documents,
        top_k=5,
    )

    assert results is not None