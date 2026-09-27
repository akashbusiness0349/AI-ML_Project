from __future__ import annotations

import pytest

from src.serving import SearchService


class DummySearcher:
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        return [
            {
                "document_id": "resume_001",
                "score": 0.95,
                "document_type": "resume",
                "title": "Data Engineer",
            },
            {
                "document_id": "resume_002",
                "score": 0.80,
                "document_type": "resume",
                "title": "ML Engineer",
            },
        ][:top_k]


def test_search_service_returns_results():
    service = SearchService(
        searcher=DummySearcher()
    )

    result = service.search(
        "data pipeline engineer",
        top_k=2,
    )

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["document_id"] == "resume_001"


def test_search_service_respects_top_k():
    service = SearchService(
        searcher=DummySearcher()
    )

    result = service.search(
        "python engineer",
        top_k=1,
    )

    assert len(result) == 1


def test_search_service_rejects_empty_query():
    service = SearchService(
        searcher=DummySearcher()
    )

    with pytest.raises((ValueError, RuntimeError)):
        service.search("", top_k=5)


def test_search_service_rejects_invalid_top_k():
    service = SearchService(
        searcher=DummySearcher()
    )

    with pytest.raises((ValueError, RuntimeError)):
        service.search(
            "data engineer",
            top_k=0,
        )