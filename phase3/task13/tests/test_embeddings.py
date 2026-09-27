import numpy as np
import pytest


def test_embedding_output_is_numeric():
    try:
        from src.embeddings import embed_text
    except ImportError:
        pytest.skip(
            "src.embeddings.embed_text is not available "
            "in the current implementation."
        )

    vector = embed_text("Python data engineering")

    assert vector is not None

    array = np.asarray(vector, dtype=float)

    assert array.ndim == 1
    assert array.size > 0
    assert np.isfinite(array).all()


def test_similar_texts_produce_compatible_vectors():
    try:
        from src.embeddings import embed_text
    except ImportError:
        pytest.skip(
            "src.embeddings.embed_text is not available."
        )

    first = np.asarray(
        embed_text("build data pipelines"),
        dtype=float,
    )

    second = np.asarray(
        embed_text("develop ETL pipelines"),
        dtype=float,
    )

    assert first.shape == second.shape
    assert first.size > 0


def test_embedding_is_deterministic():
    try:
        from src.embeddings import embed_text
    except ImportError:
        pytest.skip(
            "src.embeddings.embed_text is not available."
        )

    first = np.asarray(
        embed_text("machine learning engineer"),
        dtype=float,
    )

    second = np.asarray(
        embed_text("machine learning engineer"),
        dtype=float,
    )

    np.testing.assert_allclose(
        first,
        second,
        rtol=1e-6,
        atol=1e-8,
    )