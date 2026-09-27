from __future__ import annotations

from collections import Counter
import math

from .data import document_text
from .features import tokenize


class KeywordSearcher:
    """
    Lightweight BM25-style keyword retrieval.

    Supports Task 13 document identifiers:
    - doc_id
    - resume_id
    - job_id
    - id
    """

    @staticmethod
    def _get_doc_id(document: dict) -> str:
        doc_id = (
            document.get("doc_id")
            or document.get("resume_id")
            or document.get("job_id")
            or document.get("id")
        )

        if not doc_id:
            raise ValueError(
                "Document must contain one of: "
                "doc_id, resume_id, job_id, id"
            )

        return str(doc_id)

    def __init__(self, documents: list[dict]) -> None:
        self.documents = documents
        self.doc_tokens: dict[str, list[str]] = {}
        self.df: Counter[str] = Counter()

        for document in documents:
            doc_id = self._get_doc_id(document)

            tokens = tokenize(document_text(document))
            self.doc_tokens[doc_id] = tokens

            for token in set(tokens):
                self.df[token] += 1

        self.N = len(documents)

        self.avgdl = (
            sum(len(x) for x in self.doc_tokens.values()) / self.N
            if self.N
            else 0.0
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[dict]:
        query_tokens = tokenize(query)

        if not query_tokens:
            return []

        scores = []

        k1 = 1.5
        b = 0.75

        for document in self.documents:
            doc_id = self._get_doc_id(document)
            tokens = self.doc_tokens.get(doc_id, [])

            if not tokens:
                scores.append((doc_id, 0.0))
                continue

            counts = Counter(tokens)
            score = 0.0

            for token in query_tokens:
                tf = counts.get(token, 0)

                if tf == 0:
                    continue

                df = self.df.get(token, 0)

                idf = math.log(
                    1.0
                    + (self.N - df + 0.5)
                    / (df + 0.5)
                )

                denominator = (
                    tf
                    + k1
                    * (
                        1
                        - b
                        + b
                        * len(tokens)
                        / max(self.avgdl, 1.0)
                    )
                )

                score += idf * (
                    tf * (k1 + 1)
                ) / denominator

            scores.append((doc_id, score))

        scores.sort(
            key=lambda x: (-x[1], x[0])
        )

        return [
            {
                "doc_id": doc_id,
                "score": float(score),
            }
            for doc_id, score in scores[:top_k]
        ]
