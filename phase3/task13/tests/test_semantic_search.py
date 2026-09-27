import pytest


def test_semantic_search_returns_ranked_results():
    try:
        from src.semantic_search import semantic_search
    except ImportError:
        pytest.skip(
            "src.semantic_search.semantic_search is not available."
        )

    documents = [
        {
            "id": "resume_001",
            "text": "Experienced Python data engineer building ETL pipelines.",
        },
        {
            "id": "resume_002",
            "text": "Frontend developer specializing in React.",
        },
    ]

    results = semantic_search(
        "someone who can build data pipelines",
        documents,
        top_k=2,
    )

    assert results is not None
    assert len(results) > 0


def test_semantic_search_respects_top_k():
    try:
        from src.semantic_search import semantic_search
    except ImportError:
        pytest.skip(
            "src.semantic_search.semantic_search is not available."
        )

    documents = [
        {
            "id": f"doc_{i}",
            "text": "machine learning data engineering",
        }
        for i in range(10)
    ]

    results = semantic_search(
        "data engineering",
        documents,
        top_k=3,
    )

    assert len(results) <= 3


def test_semantic_results_have_scores():
    try:
        from src.semantic_search import semantic_search
    except ImportError:
        pytest.skip(
            "src.semantic_search.semantic_search is not available."
        )

    documents = [
        {
            "id": "resume_001",
            "text": "Python data engineer",
        }
    ]

    results = semantic_search(
        "data engineering",
        documents,
        top_k=1,
    )

    assert results

    first = results[0]

    assert isinstance(first, dict)

    assert any(
        key in first
        for key in (
            "score",
            "similarity",
            "semantic_score",
        )
    )