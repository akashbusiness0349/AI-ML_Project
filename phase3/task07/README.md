# Phase 3 — Task 07

## Activation & Onboarding Funnel Optimization

**AI / ML Engineer · Sprint B — Growth & Experimentation**

---

## Objective

The objective of Task 07 is to improve first-session activation for cold-start candidates who have no previous interaction history.

The system provides:

1. Cold-start recommendations using candidate profile, skills, job relevance, popularity and controlled exploration.
2. Popularity-only baseline comparison.
3. True held-out offline evaluation using a separate candidate split.
4. First-session impression, click and application event capture.
5. Randomized local A/B experiment infrastructure.
6. A non-empty fallback when the recommendation model is unavailable.
7. Plain-English recommendation explanations.
8. Reproducible training, evaluation, governance and integration evidence.
9. End-to-end validation and failure testing.

---

## System Architecture

```text
Candidate Onboarding
        |
        v
Candidate Profile + Skills
        |
        v
Cold-Start Recommender
        |
        +--------------------------+
        |                          |
        v                          v
Popularity Baseline        v4 Cold-Start Model
                                   |
                                   +--> Controlled Exploration
        |                          |
        +------------+-------------+
                     |
                     v
              Job Recommendations
                     |
                     v
          Impression / Click / Apply
                     |
                     v
             Experiment Metrics
```

---

## Cold-Start Strategy

The ranking system is designed for candidates with no historical interaction data.

The v4 model uses profile and job-derived signals including:

* Skill/profile relevance
* Location compatibility
* Experience compatibility
* Job popularity prior
* Controlled exploration

Historical clicks, applications or shortlist history are not required for a new candidate.

The recommendation interface supports controlled exploration so the system can balance relevant recommendations with exploration of additional eligible jobs.

---

## Baseline

The baseline uses **popularity-only ranking**.

It provides a simple comparison point for evaluating whether the cold-start model produces more relevant recommendations than a popularity-based strategy.

The same popularity-based strategy is also available as the fallback path when the recommendation model is unavailable.

---

# Model Training

## Model Version

```text
cold-start-trained-v4.0.0
```

Training dataset:

```text
data/training_data.json
```

### Training Summary

| Metric                 | Result |
| ---------------------- | -----: |
| Training examples      |     96 |
| Positive examples      |     46 |
| Negative examples      |     50 |
| Training candidates    |      8 |
| Held-out data excluded |   True |
| Production data        |  False |

The v4 training implementation uses a dependency-free logistic regression model.

The training pipeline produces:

```text
models/cold-start-trained-v4.0.0.json
models/active_model.json
models/model_registry.json
logs/training_result_v4.json
```

The held-out evaluation dataset is explicitly excluded from training.

---

# True Held-Out Evaluation

The model is evaluated against a separate held-out dataset:

```text
data/heldout_data.json
```

The training and evaluation candidate IDs have no overlap.

```text
Candidate overlap : 0
Held-out records  : 8
```

This prevents the evaluation candidates from being directly reused during model training.

## Offline Results

| Metric      | Cold-Start Model | Popularity Baseline |
| ----------- | ---------------: | ------------------: |
| Mean nDCG@5 |         0.974656 |            0.347224 |

### Mean nDCG@5 Delta

```text
0.627432
```

Recommendation validation:

```text
PASS
Errors: 0
```

Evidence:

```text
logs/offline_evaluation_v4.json
```

These results represent a local held-out offline evaluation and are not presented as production performance.

---

# Activation & Experiment Infrastructure

The Task 07 service is implemented using FastAPI.

Available endpoints:

```text
GET  /health
POST /onboarding
POST /recommendations
POST /events
GET  /experiment/events
GET  /experiment/summary
GET  /fallback-test
```

The experiment infrastructure supports randomized assignment between:

```text
Control Group
      |
      v
Popularity Baseline


Treatment Group
      |
      v
v4 Cold-Start Model
```

The live event path captures:

* Impression
* Click
* Application

Events include experiment assignment, candidate/job identifiers, model version and event provenance.

---

# Local Live Experiment Evidence

The current local demonstration captured:

| Event                    | Count |
| ------------------------ | ----: |
| Total events             |     7 |
| Impressions              |     5 |
| Clicks                   |     1 |
| Applications             |     1 |
| Fallback recommendations |     5 |

Evidence:

```text
logs/live_events.json
```

The local demonstration confirms that recommendation events can flow through the experiment instrumentation path.

## Production Experiment Limitation

The current experiment is **local demonstration evidence**, not production traffic.

Therefore:

* Production activation lift has not been measured.
* Production-scale statistical significance has not been established.
* The local event counts must not be interpreted as production conversion results.

A production experiment would require a real eligible population, persistent experiment assignment, sufficient sample size and statistical analysis.

---

# Primary Metrics

## Offline Recommendation Metrics

The evaluation framework supports:

* Precision@5
* Recall@5
* nDCG@5
* MAP@5

The current v4 signoff reports the held-out nDCG@5 comparison.

## Activation Metrics

The activation instrumentation supports:

* First-session relevant-action rate
* First-session click rate
* First-session application rate
* First-session shortlist rate

The current local evidence contains impression, click and application events.

Production activation lift is not claimed because no production experiment has been conducted.

---

# Safety & Fallback

If the recommendation model becomes unavailable, the system uses a popularity-based fallback recommendation strategy.

The fallback is designed to provide a non-empty recommendation list whenever eligible jobs are available.

The failure path is exposed through:

```text
GET /fallback-test
```

Fallback behavior is included in the end-to-end integration validation.

---

# Explainability

The recommendation system provides plain-English explanations based on observable recommendation factors.

Examples of explanation factors include:

* Matching skills
* Profile/job relevance
* Popularity signal

Sensitive or protected attributes are not used as ranking features.

---

# Governance & Privacy

Task 07 includes candidate and event schema validation.

Current governance status:

```text
Candidate schema              : PASS
Event schema                  : PASS
Protected attributes in rank  : False
Overall schema status         : PASS
```

Implemented controls include:

* Purpose limitation
* Data minimization
* Protected attribute exclusion
* Model version logging
* Event provenance
* Deletion-ready candidate identifier

Evidence:

```text
logs/governance_audit.json
```

## Privacy / DPDP Controls

The implementation documents controls for:

### Purpose Limitation

Candidate data is processed only for recommendation and activation measurement.

### Data Minimization

Only fields required for ranking and experiment measurement are retained.

### Protected Attribute Exclusion

Sensitive/protected attributes are excluded from the recommendation feature schema.

### Model Version Logging

Recommendation events retain model version information for auditability.

### Event Provenance

Events retain source and experiment information to distinguish local experiment evidence from other data.

### Deletion-Ready Identifier

`candidate_id` is retained as the stable deletion and audit reference.

### Live Capture Notice

Live production capture requires an appropriate user notice and lawful processing basis before production use.

---

# Fairness Evaluation

Fairness group metrics are **not fabricated**.

The current local dataset does not contain valid protected-group labels with sufficient sample size for a meaningful fairness outcome comparison.

Therefore:

```text
Fairness metric status:
not_computable_without_valid_group_labels
```

A production fairness audit should use legally and ethically appropriate group labels, sufficient sample size and an approved evaluation methodology.

---

# End-to-End Integration

The final integration validation produced:

```text
Events                   : 7
Impressions              : 5
Clicks                   : 1
Applications             : 1
Fallback recommendations : 5
Event validation         : True
Held-out evaluation      : True
Governance audit         : True
Integration status       : PASS
```

Evidence:

```text
logs/integration_signoff_v4.json
```

---

# Final Signoff

```text
Task                    : PHASE_3_TASK_07
Status                  : READY_FOR_REVIEW
Model                   : cold-start-trained-v4.0.0
Held-out nDCG@5         : 0.974656
Baseline nDCG@5         : 0.347224
Mean nDCG delta         : 0.627432
Integration             : PASS
Governance              : PASS
Production A/B lift     : NOT MEASURED
```

Final signoff evidence:

```text
logs/final_signoff_v4.json
```

---

# Reproducibility

All commands below should be executed from:

```text
phase3/task07/
```

## 1. Train the Model

```bash
python run_training.py
```

## 2. Run True Held-Out Evaluation

```bash
python run_task07_evaluation.py
```

## 3. Run Governance Audit

```bash
python run_governance_audit.py
```

## 4. Run End-to-End Integration

```bash
python run_task07_integration.py
```

## 5. Compile the Implementation

```bash
python -m compileall -q api.py run_training.py run_task07_demo.py run_task07_evaluation.py run_task07_integration.py run_live_experiment.py run_governance_audit.py src
```

## 6. Start the FastAPI Service

```bash
uvicorn api:app --host 127.0.0.1 --port 8017
```

FastAPI documentation:

```text
http://127.0.0.1:8017/docs
```

---

# Project Structure

```text
task07/
├── README.md
├── api.py
├── data/
│   ├── candidates.json
│   ├── heldout_data.json
│   ├── interaction_logs.json
│   ├── jobs.json
│   └── training_data.json
├── logs/
│   ├── .gitkeep
│   ├── final_signoff_v4.json
│   ├── governance_audit.json
│   ├── integration_signoff_v4.json
│   ├── live_events.json
│   ├── offline_evaluation_v4.json
│   └── training_result_v4.json
├── models/
│   ├── active_model.json
│   ├── cold-start-trained-v4.0.0.json
│   └── model_registry.json
├── requirements.txt
├── run_governance_audit.py
├── run_live_experiment.py
├── run_task07_demo.py
├── run_task07_evaluation.py
├── run_task07_integration.py
├── run_training.py
├── schemas/
│   ├── activation_event_schema.json
│   ├── candidate_schema.json
│   ├── job_schema.json
│   └── recommendation_schema.json
└── src/
    ├── __init__.py
    ├── activation_metrics.py
    ├── baseline.py
    ├── cold_start.py
    ├── data_ingestion.py
    ├── explainability.py
    ├── fallback.py
    ├── governance.py
    ├── recommender.py
    ├── training.py
    └── validation.py
```

---

# Evidence Files

## Training

```text
logs/training_result_v4.json
```

## Offline Evaluation

```text
logs/offline_evaluation_v4.json
```

## Live Experiment

```text
logs/live_events.json
```

## Governance

```text
logs/governance_audit.json
```

## Integration

```text
logs/integration_signoff_v4.json
```

## Final Signoff

```text
logs/final_signoff_v4.json
```

## Model Artifacts

```text
models/cold-start-trained-v4.0.0.json
models/active_model.json
models/model_registry.json
```

---

# Limitations

The current implementation is a reproducible local Task 07 evaluation and demonstration.

Known limitations:

1. Offline evaluation uses a local held-out dataset rather than production traffic.
2. Live experiment events are locally captured demonstration evidence.
3. Production A/B activation lift has not been measured.
4. Production-scale statistical significance has not been established.
5. Fairness group metrics are not computed because valid group labels and sufficient sample size are unavailable.
6. Production deployment would require appropriate user notice/lawful processing basis, privacy controls, monitoring and a real experiment population.
7. The current dataset and live experiment are not a substitute for production-scale validation.

---

# Status

## READY_FOR_REVIEW

Task 07 includes:

* Cold-start model training
* Popularity baseline
* True held-out evaluation
* Controlled exploration
* Live event instrumentation
* Randomized experiment infrastructure
* Activation measurement
* Explainability
* Fallback handling
* Governance and privacy controls
* End-to-end integration validation
* Reproducible evidence artifacts
* Final signoff
