import pytest


def test_precision_at_k_basic():
    try:
        from src.metrics import precision_at_k
    except ImportError:
        pytest.skip(
            "src.metrics.precision_at_k is not available."
        )

    ranked = [
        "a",
        "b",
        "c",
        "d",
        "e",
    ]

    relevant = {
        "a",
        "c",
        "e",
    }

    score = precision_at_k(
        ranked,
        relevant,
        k=5,
    )

    assert 0.0 <= score <= 1.0
    assert score == 3 / 5


def test_precision_at_k_perfect():
    try:
        from src.metrics import precision_at_k
    except ImportError:
        pytest.skip(
            "src.metrics.precision_at_k is not available."
        )

    ranked = [
        "a",
        "b",
        "c",
    ]

    relevant = {
        "a",
        "b",
        "c",
    }

    score = precision_at_k(
        ranked,
        relevant,
        k=3,
    )

    assert score == 1.0


def test_coverage_is_bounded():
    try:
        from src.metrics import coverage
    except ImportError:
        pytest.skip(
            "src.metrics.coverage is not available."
        )

    recommendations = [
        ["a", "b"],
        ["b", "c"],
    ]

    score = coverage(
        recommendations,
        catalog_size=3,
    )

    assert 0.0 <= score <= 1.0


def test_diversity_is_bounded():
    try:
        from src.metrics import diversity
    except ImportError:
        pytest.skip(
            "src.metrics.diversity is not available."
        )

    recommendations = [
        ["a", "b", "c"],
        ["d", "e", "f"],
    ]

    score = diversity(recommendations)

    assert 0.0 <= score <= 1.0