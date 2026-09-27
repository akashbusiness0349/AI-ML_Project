from __future__ import annotations

import numpy as np
import pytest

from src.vector_index import VectorIndex


def test_vector_index_add_and_search():
    index = VectorIndex(dimension=3)

    index.add(
        "doc_001",
        np.array([1.0, 0.0, 0.0]),
    )

    index.add(
        "doc_002",
        np.array([0.0, 1.0, 0.0]),
    )

    results = index.search(
        np.array([1.0, 0.0, 0.0]),
        top_k=2,
    )

    assert len(results) == 2
    assert results[0]["document_id"] == "doc_001"


def test_vector_index_returns_top_k():
    index = VectorIndex(dimension=3)

    for i in range(5):
        vector = np.zeros(3)
        vector[i % 3] = 1.0

        index.add(
            f"doc_{i}",
            vector,
        )

    results = index.search(
        np.array([1.0, 0.0, 0.0]),
        top_k=2,
    )

    assert len(results) == 2


def test_vector_index_dimension_mismatch():
    index = VectorIndex(dimension=3)

    with pytest.raises((ValueError, RuntimeError)):
        index.add(
            "bad_doc",
            np.array([1.0, 0.0]),
        )


def test_vector_index_empty_search():
    index = VectorIndex(dimension=3)

    results = index.search(
        np.array([1.0, 0.0, 0.0]),
        top_k=5,
    )

    assert results == []


def test_vector_index_search_dimension_mismatch():
    index = VectorIndex(dimension=3)

    index.add(
        "doc_001",
        np.array([1.0, 0.0, 0.0]),
    )

    with pytest.raises((ValueError, RuntimeError)):
        index.search(
            np.array([1.0, 0.0]),
            top_k=1,
        )