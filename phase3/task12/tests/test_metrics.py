from src.metrics import (
    coverage,
    precision_at_k,
)


def test_precision_at_k():
    value = precision_at_k(
        ["a", "b", "c", "d"],
        {"a", "c"},
        4,
    )

    assert value == 0.5


def test_coverage():
    value = coverage(
        [
            ["a", "b"],
            ["b", "c"],
        ],
        4,
    )

    assert value == 0.75