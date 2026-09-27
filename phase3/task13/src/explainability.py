from __future__ import annotations

from .data import document_text
from .features import overlap_terms


def explain_result(
    query: str,
    document: dict | None = None,
    semantic_score: float | None = None,
    keyword_score: float | None = None,
    mode: str = "semantic",
    result: dict | None = None,
) -> dict:
    if document is None:
        document = result

    if document is None:
        raise ValueError("document or result must be provided")

    document = dict(document)

    if "doc_id" not in document and "id" in document:
        document["doc_id"] = document["id"]

    text = document_text(document)

    if not text:
        text = str(document.get("text", ""))

    overlaps = overlap_terms(query, text)

    if overlaps:
        overlap_text = ", ".join(overlaps[:5])
        reason = (
            "The result matches the search through related "
            f"skills or terms including: {overlap_text}."
        )
    else:
        reason = (
            "The result was retrieved because its representation "
            "is semantically similar to the search intent."
        )

    return {
        "query": query,
        "document_id": document.get("doc_id", document.get("id", "unknown")),
        "document_type": document.get("doc_type", "unknown"),
        "retrieval_mode": mode,
        "semantic_score": semantic_score
        if semantic_score is not None
        else document.get("score"),
        "keyword_score": keyword_score,
        "matched_terms": overlaps,
        "reason": reason,
    }
