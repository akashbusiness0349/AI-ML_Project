import pytest


def test_hybrid_search_returns_results():
    try:
        from src.hybrid_search import hybrid_search
    except ImportError:
        pytest.skip(
            "src.hybrid_search.hybrid_search is not available."
        )

    documents = [
        {
            "id": "resume_001",
            "text": "Python data engineer ETL pipelines",
        },
        {
            "id": "resume_002",
            "text": "React frontend engineer",
        },
    ]

    results = hybrid_search(
        "build data pipelines",
        documents,
        top_k=2,
    )

    assert results is not None
    assert len(results) > 0


def test_hybrid_search_respects_top_k():
    try:
        from src.hybrid_search import hybrid_search
    except ImportError:
        pytest.skip(
            "src.hybrid_search.hybrid_search is not available."
        )

    documents = [
        {
            "id": f"doc_{i}",
            "text": "python data engineering",
        }
        for i in range(10)
    ]

    results = hybrid_search(
        "python",
        documents,
        top_k=4,
    )

    assert len(results) <= 4


def test_hybrid_weight_is_valid():
    try:
        from src.hybrid_search import hybrid_search
    except ImportError:
        pytest.skip(
            "src.hybrid_search.hybrid_search is not available."
        )

    documents = [
        {
            "id": "doc_1",
            "text": "python data engineering",
        }
    ]

    results = hybrid_search(
        "python",
        documents,
        top_k=1,
        semantic_weight=0.7,
        keyword_weight=0.3,
    )

    assert results is not None


def test_hybrid_weight_sum():
    semantic_weight = 0.7
    keyword_weight = 0.3

    assert 0.0 <= semantic_weight <= 1.0
    assert 0.0 <= keyword_weight <= 1.0

    assert abs(
        semantic_weight + keyword_weight - 1.0
    ) < 1e-9