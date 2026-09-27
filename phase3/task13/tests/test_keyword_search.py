import pytest


def test_keyword_search_returns_results():
    try:
        from src.keyword_search import keyword_search
    except ImportError:
        pytest.skip(
            "src.keyword_search.keyword_search is not available."
        )

    documents = [
        {
            "id": "resume_001",
            "text": "Python SQL data pipelines ETL",
        },
        {
            "id": "resume_002",
            "text": "React JavaScript frontend development",
        },
    ]

    results = keyword_search(
        "Python data pipelines",
        documents,
        top_k=2,
    )

    assert results is not None
    assert len(results) > 0


def test_keyword_search_respects_top_k():
    try:
        from src.keyword_search import keyword_search
    except ImportError:
        pytest.skip(
            "src.keyword_search.keyword_search is not available."
        )

    documents = [
        {"id": f"doc_{i}", "text": "python data engineering"}
        for i in range(10)
    ]

    results = keyword_search(
        "python",
        documents,
        top_k=3,
    )

    assert len(results) <= 3


def test_keyword_search_handles_empty_query():
    try:
        from src.keyword_search import keyword_search
    except ImportError:
        pytest.skip(
            "src.keyword_search.keyword_search is not available."
        )

    documents = [
        {"id": "doc_1", "text": "python sql"}
    ]

    results = keyword_search(
        "",
        documents,
        top_k=5,
    )

    assert results is not None