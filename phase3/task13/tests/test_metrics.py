from __future__ import annotations

import math

from src.metrics import (
    evaluate_rankings,
    mean_reciprocal_rank,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_precision_at_k():
    ranked = [
        "doc_1",
        "doc_2",
        "doc_3",
        "doc_4",
    ]

    relevant = {
        "doc_1",
        "doc_3",
    }

    value = precision_at_k(
        ranked,
        relevant,
        k=4,
    )

    assert value == 0.5


def test_precision_at_k_partial_cutoff():
    ranked = [
        "doc_1",
        "doc_2",
        "doc_3",
        "doc_4",
    ]

    relevant = {
        "doc_1",
        "doc_3",
    }

    value = precision_at_k(
        ranked,
        relevant,
        k=2,
    )

    assert value == 0.5


def test_recall_at_k():
    ranked = [
        "doc_1",
        "doc_2",
        "doc_3",
        "doc_4",
    ]

    relevant = {
        "doc_1",
        "doc_3",
    }

    value = recall_at_k(
        ranked,
        relevant,
        k=4,
    )

    assert value == 1.0


def test_reciprocal_rank_first_result():
    ranked = [
        "doc_1",
        "doc_2",
        "doc_3",
    ]

    relevant = {"doc_1"}

    value = reciprocal_rank(
        ranked,
        relevant,
    )

    assert value == 1.0


def test_reciprocal_rank_second_result():
    ranked = [
        "doc_1",
        "doc_2",
        "doc_3",
    ]

    relevant = {"doc_2"}

    value = reciprocal_rank(
        ranked,
        relevant,
    )

    assert value == 0.5


def test_reciprocal_rank_no_match():
    ranked = [
        "doc_1",
        "doc_2",
        "doc_3",
    ]

    relevant = {"doc_99"}

    value = reciprocal_rank(
        ranked,
        relevant,
    )

    assert value == 0.0


def test_ndcg_perfect_ranking():
    ranked = [
        "doc_1",
        "doc_2",
        "doc_3",
    ]

    relevance = {
        "doc_1": 3,
        "doc_2": 2,
        "doc_3": 1,
    }

    value = ndcg_at_k(
        ranked,
        relevance,
        k=3,
    )

    assert math.isclose(
        value,
        1.0,
        rel_tol=1e-9,
    )


def test_ndcg_is_bounded():
    ranked = [
        "doc_1",
        "doc_2",
        "doc_3",
    ]

    relevance = {
        "doc_1": 3,
        "doc_2": 2,
        "doc_3": 0,
    }

    value = ndcg_at_k(
        ranked,
        relevance,
        k=3,
    )

    assert 0.0 <= value <= 1.0


def test_mean_reciprocal_rank():
    rankings = [
        (
            ["doc_1", "doc_2"],
            {"doc_1"},
        ),
        (
            ["doc_3", "doc_4"],
            {"doc_4"},
        ),
    ]

    value = mean_reciprocal_rank(rankings)

    expected = (
        1.0 + 0.5
    ) / 2.0

    assert math.isclose(
        value,
        expected,
        rel_tol=1e-9,
    )


def test_evaluate_rankings_returns_metrics():
    rankings = [
        {
            "query_id": "q1",
            "ranked_ids": [
                "doc_1",
                "doc_2",
                "doc_3",
            ],
            "relevant_ids": {
                "doc_1",
                "doc_3",
            },
        },
        {
            "query_id": "q2",
            "ranked_ids": [
                "doc_4",
                "doc_5",
                "doc_6",
            ],
            "relevant_ids": {
                "doc_5",
            },
        },
    ]

    result = evaluate_rankings(
        rankings,
        k=3,
    )

    assert isinstance(result, dict)

    assert "precision@3" in result
    assert "recall@3" in result
    assert "MRR" in result
    assert "nDCG@3" in result

    assert 0.0 <= result["precision@3"] <= 1.0
    assert 0.0 <= result["recall@3"] <= 1.0
    assert 0.0 <= result["MRR"] <= 1.0
    assert 0.0 <= result["nDCG@3"] <= 1.0