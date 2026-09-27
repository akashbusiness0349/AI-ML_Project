from __future__ import annotations

import json
from pathlib import Path

from src.data import all_documents, document_text
from src.embeddings import SemanticEmbedder
from src.vector_index import VectorIndex


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "task13_embedder.joblib"
INDEX_PATH = ROOT / "indexes" / "task13_vector_index.joblib"


def main() -> None:
    documents = all_documents()

    texts = [
        document_text(document)
        for document in documents
    ]

    embedder = SemanticEmbedder()
    vectors = embedder.fit_transform(texts)

    metadata = {
        document["doc_id"]: {
            "doc_type": document["doc_type"],
            "title": document.get(
                "title",
                document["doc_id"],
            ),
        }
        for document in documents
    }

    index = VectorIndex()

    index.build(
        ids=[
            document["doc_id"]
            for document in documents
        ],
        vectors=vectors,
        metadata=metadata,
    )

    embedder.save(MODEL_PATH)
    index.save(INDEX_PATH)

    result = {
        "status": "PASS",
        "documents_indexed": len(documents),
        "embedding_dimension": vectors.shape[1],
        "model_path": str(MODEL_PATH),
        "index_path": str(INDEX_PATH),
    }

    print(json.dumps(
        result,
        indent=2,
    ))


if __name__ == "__main__":
    main()