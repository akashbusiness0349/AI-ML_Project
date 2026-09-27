# Phase 3 — Task 13
# Live Semantic / Hybrid Search

## Overview

Phase 3 Task 13 implements a reproducible semantic and hybrid search system for matching natural-language search queries against a combined corpus of resumes and job documents.

The system supports:

- Reproducible synthetic search data generation
- Labelled train and held-out evaluation queries
- TF-IDF + TruncatedSVD semantic embeddings
- Persistent vector indexing
- BM25-style keyword retrieval
- Semantic retrieval
- Hybrid semantic + keyword retrieval
- Hybrid weight tuning on training data
- Held-out labelled evaluation
- Precision@5
- Recall@5
- MRR
- nDCG@5
- Live search inference
- Explainable search outputs
- Failure/fallback validation
- Automated integration testing

The implementation is self-contained within Task 13 and does not depend on data from previous tasks.

---

# 1. Task Objective

The objective of Task 13 is to build and validate a semantic/hybrid search capability that can retrieve relevant resumes and jobs from natural-language queries.

Example query:

```text
someone who can build data pipelines

The system converts the query into a searchable representation and returns ranked documents with:

document ID
final score
semantic score
keyword score
result position
2. System Architecture
                    ┌─────────────────────┐
                    │   Search Query      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Query Preprocessing │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │ Semantic Search │        │ Keyword Search  │
        │ TF-IDF + SVD    │        │ BM25-style      │
        └────────┬────────┘        └────────┬────────┘
                 │                          │
                 └────────────┬─────────────┘
                              ▼
                    ┌─────────────────────┐
                    │ Hybrid Ranker       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Ranked Search       │
                    │ Results             │
                    └─────────────────────┘
3. Dataset

Task 13 owns an independent reproducible synthetic search corpus.

Dataset configuration:

Property	Value
Dataset version	1.0
Random seed	42
Resumes	60
Jobs	40
Total documents	100
Search queries	48
Training queries	24
Held-out queries	24
Labelled evaluation	Yes
Production data	No

The dataset is explicitly identified as:

synthetic_reproducible_search_corpus

This means the evaluation results are reproducible but should not be interpreted as production-traffic evidence.

4. Data Generation

Run:

python run_data_generation.py

Expected result includes:

dataset_version: 1.0
random_seed: 42
resume_count: 60
job_count: 40
query_count: 48
train_query_count: 24
heldout_query_count: 24
labelled_evaluation: true
5. Data Validation

Run:

python run_data_validation.py

Verified result:

{
  "status": "PASS",
  "resume_count": 60,
  "job_count": 40,
  "errors": []
}
6. Semantic Embedding Model

The semantic embedding pipeline uses:

TF-IDF
   +
TruncatedSVD
   =
Latent Semantic Embedding

The trained embedding model is persisted using joblib.

Model artifact:

models/task13_embedder.joblib

Training can be reproduced with:

python run_training.py

The training pipeline uses 24 training queries.

7. Vector Indexing

The indexing stage builds the persistent searchable vector index.

Run:

python run_indexing.py

Verified configuration:

documents_indexed : 100
embedding_dimension : 64

Generated artifacts:

models/task13_embedder.joblib
indexes/task13_vector_index.joblib
8. Keyword Search

The system also implements a lightweight BM25-style keyword retrieval layer.

Keyword retrieval performs:

Query tokenization
Document tokenization
Term-frequency calculation
Document-frequency calculation
IDF calculation
BM25-style scoring
Ranked result generation

This provides a lexical retrieval path alongside semantic retrieval.

9. Semantic Search

Semantic search uses the persisted embedding model and vector index.

It allows queries to be compared against indexed documents using latent semantic representations.

The live search output exposes the semantic score for every returned document.

Example:

{
  "doc_id": "job_008",
  "semantic_score": 1.0
}
10. Hybrid Search

The system combines semantic and keyword retrieval.

Conceptually:

Hybrid Score =
    semantic_weight × semantic_score
    +
    keyword_weight × keyword_score

The weights are selected using the training split.

The held-out evaluation set is not used for weight tuning.

This prevents the held-out set from being used to select the model configuration.

11. Hybrid Weight Tuning

Run:

python run_hybrid_tuning.py

The tuning process evaluates candidate semantic weights:

0.0
0.1
0.2
0.3
0.4
0.5
0.6
0.7
0.8
0.9
1.0

Metric:

MRR

Verified training result:

selected_semantic_weight = 0.0
selected_keyword_weight  = 1.0
selected_train_MRR       = 1.0

Important:

heldout_data_used_for_tuning = false

The selected configuration is therefore determined using the training split rather than the held-out evaluation set.

Tuning artifact:

logs/hybrid_tuning.json
12. Held-Out Evaluation

Run:

python run_evaluation.py

The evaluation uses:

24 held-out queries

The following retrieval metrics are reported:

Precision@5
Recall@5
MRR
nDCG@5
Keyword Search
Precision@5 : 1.0
Recall@5    : 0.32245442036463706
MRR         : 1.0
nDCG@5      : 1.0
Semantic Search
Precision@5 : 1.0
Recall@5    : 0.32245442036463706
MRR         : 1.0
nDCG@5      : 1.0
Hybrid Search
Precision@5 : 1.0
Recall@5    : 0.32245442036463706
MRR         : 1.0
nDCG@5      : 1.0

The measured differences between semantic/hybrid and keyword retrieval were:

semantic_minus_keyword:
    Precision@5 = 0.0
    Recall@5    = 0.0
    MRR         = 0.0
    nDCG@5      = 0.0

hybrid_minus_keyword:
    Precision@5 = 0.0
    Recall@5    = 0.0
    MRR         = 0.0
    nDCG@5      = 0.0

The results therefore document the observed behaviour of all three retrieval paths on the current held-out synthetic dataset.

13. Online Validation Status

No verified production/live-traffic dataset was available for Task 13.

Therefore:

online_validation.status = NOT_ESTABLISHED

and:

production_evidence_status = NOT_PRODUCTION_EVIDENCE

The evaluation results should therefore be interpreted as reproducible offline/held-out evaluation results, not production performance measurements.

14. Live Search

The search system can be executed directly using:

python run_live_search.py "someone who can build data pipelines"

Example verified result:

[
  {
    "doc_id": "job_008",
    "score": 1.0,
    "semantic_score": 1.0,
    "keyword_score": 1.0,
    "position": 1
  },
  {
    "doc_id": "job_010",
    "score": 1.0,
    "semantic_score": 0.8251837113575746,
    "keyword_score": 1.0,
    "position": 2
  },
  {
    "doc_id": "job_019",
    "score": 1.0,
    "semantic_score": 0.8895994417577707,
    "keyword_score": 1.0,
    "position": 3
  }
]

The output demonstrates that the system can execute a natural-language query and return ranked search results.

15. Live Demo

Run:

python run_demo.py

The demo executes multiple natural-language queries.

Verified demo queries include:

someone who can build data pipelines
machine learning model development
cloud infrastructure deployment

The demo prints ranked results with:

doc_id
score
semantic_score
keyword_score
position
16. Search Examples
Query 1
someone who can build data pipelines

Top result:

job_008
Query 2
machine learning model development

Top result:

job_006
Query 3
cloud infrastructure deployment

Top result:

resume_022

These examples demonstrate live inference across both job and resume documents.

17. Explainability

The search result format exposes separate retrieval signals:

{
  "doc_id": "job_008",
  "score": 1.0,
  "semantic_score": 1.0,
  "keyword_score": 1.0,
  "position": 1
}

This allows the output to be inspected beyond the final ranking score.

The repository also contains:

run_explainability.py
src/explainability.py

for the explainability workflow.

18. Failure and Fallback Handling

Task 13 includes fallback and failure-handling components.

Relevant modules:

src/fallback.py
run_failure_test.py

The repository includes automated tests covering failure/fallback behaviour.

19. Repository Structure
phase3/task13/
│
├── models/
│   └── task13_embedder.joblib
│
├── indexes/
│   └── task13_vector_index.joblib
│
├── logs/
│   └── hybrid_tuning.json
│
├── src/
│   ├── __init__.py
│   ├── data.py
│   ├── embeddings.py
│   ├── explainability.py
│   ├── fallback.py
│   ├── features.py
│   ├── hybrid_search.py
│   ├── keyword_search.py
│   ├── metrics.py
│   ├── semantic_search.py
│   ├── serving.py
│   ├── validation.py
│   └── vector_index.py
│
├── tests/
│   ├── test_data.py
│   ├── test_embeddings.py
│   ├── test_evaluation.py
│   ├── test_explainability.py
│   ├── test_fallback.py
│   ├── test_hybrid_search.py
│   ├── test_integration.py
│   ├── test_keyword_search.py
│   ├── test_metrics.py
│   ├── test_semantic_search.py
│   ├── test_serving.py
│   └── test_vector_index.py
│
├── run_data_generation.py
├── run_data_validation.py
├── run_training.py
├── run_indexing.py
├── run_hybrid_tuning.py
├── run_evaluation.py
├── run_live_search.py
├── run_demo.py
├── run_explainability.py
├── run_failure_test.py
├── run_latency_benchmark.py
├── run_integration.py
└── README.md
20. Automated Testing

The complete test suite was executed successfully.

Command:

python -m pytest -q tests

Verified result:

33 passed, 16 skipped

No tests failed.

21. Final Verification Commands

For a complete Task 13 verification run:

python run_data_generation.py
python run_data_validation.py
python run_training.py
python run_indexing.py
python run_hybrid_tuning.py
python run_evaluation.py
python run_live_search.py "someone who can build data pipelines"
python run_demo.py
python -m pytest -q tests
22. Generated Evidence Artifacts

The following artifacts were generated and verified:

Semantic model
models/task13_embedder.joblib

Approximate verified size:

236 KB
Vector index
indexes/task13_vector_index.joblib

Approximate verified size:

56 KB
Hybrid tuning evidence
logs/hybrid_tuning.json

Approximate verified size:

925 bytes
23. Final Verification Summary
Verification	Result
Data generation	PASS
Data validation	PASS
Semantic training pipeline	PASS
Vector indexing	PASS
Hybrid weight tuning	PASS
Held-out evaluation	PASS
Live search	PASS
Live demo	PASS
Automated tests	PASS
Production evidence	NOT AVAILABLE
Online validation	NOT ESTABLISHED

Final automated test result:

33 passed, 16 skipped
24. Reproducibility

The complete pipeline is reproducible using the repository scripts.

The dataset generation uses:

random_seed = 42

The training and evaluation data are separated into:

24 training queries
24 held-out queries

The hybrid tuning stage operates only on the training split, while the final evaluation operates on the held-out split.

25. Limitations

The current Task 13 implementation has several documented limitations:

The dataset is synthetic rather than production data.
Online/production validation has not been established.
The current corpus contains 100 documents.
Evaluation uses 24 held-out queries.
The observed semantic and hybrid metrics do not exceed the keyword baseline on this dataset.
Production-scale latency, throughput, infrastructure cost, and live user behaviour have not been measured.
The selected hybrid configuration is based on the reproducible training corpus.

These limitations are intentionally documented so that offline evaluation results are not presented as production evidence.

26. Technology Stack
Python
scikit-learn
NumPy
joblib
pytest
TF-IDF
TruncatedSVD
BM25-style keyword retrieval
Vector indexing
Semantic search
Hybrid retrieval
27. Final Status
TASK 13 — IMPLEMENTATION COMPLETE

The complete Task 13 pipeline has been implemented and verified locally.

Verified:

✓ Reproducible dataset
✓ Data validation
✓ Semantic embedding pipeline
✓ Persistent model artifact
✓ Vector index
✓ Keyword retrieval
✓ Semantic retrieval
✓ Hybrid retrieval
✓ Training-based weight tuning
✓ Held-out evaluation
✓ Retrieval metrics
✓ Live search
✓ Live demo
✓ Explainability components
✓ Failure/fallback components
✓ Automated test suite

Final test status:

33 passed
16 skipped
0 failed
