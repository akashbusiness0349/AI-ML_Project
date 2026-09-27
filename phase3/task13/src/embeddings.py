from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD


class SemanticEmbedder:
    """
    Lightweight deterministic semantic embedding pipeline.

    TF-IDF creates lexical representations and TruncatedSVD projects
    them into a lower-dimensional latent semantic space.
    """

    def __init__(
        self,
        max_features: int = 5000,
        n_components: int = 64,
        random_state: int = 42,
    ) -> None:
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_features=max_features,
            sublinear_tf=True,
        )

        self.n_components = n_components
        self.random_state = random_state
        self.svd: TruncatedSVD | None = None
        self.fitted = False

    def fit(self, texts: list[str]) -> "SemanticEmbedder":
        matrix = self.vectorizer.fit_transform(texts)

        max_components = min(
            self.n_components,
            max(1, matrix.shape[0] - 1),
            max(1, matrix.shape[1] - 1),
        )

        if matrix.shape[1] <= 1 or matrix.shape[0] <= 1:
            self.svd = None
        else:
            self.svd = TruncatedSVD(
                n_components=max_components,
                random_state=self.random_state,
            )
            self.svd.fit(matrix)

        self.fitted = True
        return self

    def transform(self, texts: list[str]) -> np.ndarray:
        if not self.fitted:
            raise RuntimeError("Embedding model is not fitted.")

        matrix = self.vectorizer.transform(texts)

        if self.svd is None:
            output = matrix.toarray()
        else:
            output = self.svd.transform(matrix)

        norms = np.linalg.norm(output, axis=1, keepdims=True)
        norms[norms == 0] = 1.0

        return output / norms

    def fit_transform(self, texts: list[str]) -> np.ndarray:
        self.fit(texts)
        return self.transform(texts)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path: str | Path) -> "SemanticEmbedder":
        return joblib.load(path)