from __future__ import annotations

import re


TOKEN_RE = re.compile(r"[a-zA-Z0-9+#.]+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "build",
    "can",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    return [
        token
        for token in TOKEN_RE.findall(normalized)
        if token not in STOPWORDS
    ]


def keyword_set(text: str) -> set[str]:
    return set(tokenize(text))


def overlap_terms(query: str, document_text: str) -> list[str]:
    query_terms = keyword_set(query)
    document_terms = keyword_set(document_text)

    return sorted(query_terms.intersection(document_terms))