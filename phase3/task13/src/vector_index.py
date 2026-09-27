from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np


class VectorIndex:
    def __init__(self, dimension: int | None = None) -> None:
        if dimension is not None and dimension <= 0:
            raise ValueError("dimension must be positive")

        self.dimension = dimension
        self.ids: list[str] = []
        self.vectors: np.ndarray | None = None
        self.metadata: dict[str, dict] = {}

    def add(
        self,
        document_id: str,
        vector: np.ndarray,
        metadata: dict | None = None,
    ) -> None:
        vector = np.asarray(vector, dtype=float).reshape(-1)

        if self.dimension is None:
            self.dimension = len(vector)

        if len(vector) != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch: expected "
                f"{self.dimension}, got {len(vector)}"
            )

        if self.vectors is None:
            self.vectors = vector.reshape(1, -1)
        else:
            self.vectors = np.vstack(
                [self.vectors, vector]
            )

        self.ids.append(document_id)

        if metadata is not None:
            self.metadata[document_id] = dict(metadata)

    def build(
        self,
        ids: list[str],
        vectors: np.ndarray,
        metadata: dict[str, dict],
    ) -> None:
        vectors = np.asarray(vectors, dtype=float)

        if vectors.ndim != 2:
            raise ValueError("vectors must be a 2D array")

        if len(ids) != len(vectors):
            raise ValueError(
                "IDs and vectors must have the same length."
            )

        if self.dimension is None:
            self.dimension = vectors.shape[1]

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                "Vector dimension mismatch."
            )

        self.ids = list(ids)
        self.vectors = vectors
        self.metadata = dict(metadata)

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
    ) -> list[dict]:

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        if self.vectors is None or not self.ids:
            return []

        query = np.asarray(
            query_vector,
            dtype=float,
        ).reshape(-1)

        if self.dimension is not None and len(query) != self.dimension:
            raise ValueError(
                f"Query dimension mismatch: expected "
                f"{self.dimension}, got {len(query)}"
            )

        query_norm = np.linalg.norm(query)

        if query_norm == 0:
            scores = np.zeros(len(self.ids))
        else:
            query = query / query_norm

            matrix = self.vectors.copy()

            norms = np.linalg.norm(
                matrix,
                axis=1,
                keepdims=True,
            )

            norms[norms == 0] = 1.0

            matrix = matrix / norms

            scores = matrix @ query

        order = np.argsort(-scores)[:top_k]

        return [
            {
                "document_id": self.ids[i],
                "doc_id": self.ids[i],
                "score": float(scores[i]),
                "metadata": self.metadata.get(
                    self.ids[i],
                    {},
                ),
            }
            for i in order
        ]

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(self, path)

    @staticmethod
    def load(path: str | Path) -> "VectorIndex":
        return joblib.load(path)
