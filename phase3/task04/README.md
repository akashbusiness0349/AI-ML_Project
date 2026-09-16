# Phase 3 — Task 04

# Horizontal Scale & Load Readiness

## 1. Objective

This task evaluates the horizontal scale and load readiness of the inference-serving path.

The objectives are to:

1. Measure inference latency and throughput at increasing concurrency levels.
2. Identify the first observed concurrency level where the inference SLO is breached.
3. Determine the highest safe tested concurrency and a conservative operating capacity with headroom.
4. Define a horizontal scaling strategy using autoscaling, model caching, precomputation, and optional batching.
5. Preserve explainable inference outputs during serving.
6. Verify that the `MODEL_UNAVAILABLE` failure path does not fabricate scores or recommendations.
7. Produce runtime-generated evidence that is reproducible from the repository.

---

# 2. System Under Test

The system under test is the Phase 3 Task 04 HTTP inference service.

### Service

* Framework: FastAPI
* Runtime: Python / Uvicorn
* Endpoint: `POST /infer`
* Health endpoint: `GET /health`
* Readiness endpoint: `GET /ready`
* Service URL used during testing:

```text
http://127.0.0.1:8000
```

### Inference behavior

The inference path performs deterministic skill-matching using the candidate and required skill sets.

The response contains:

* inference score
* match decision
* matched skills
* missing skills
* threshold
* explainability information
* model availability state

The model availability state is explicitly represented so that unavailable-model behavior can be tested without generating a fabricated inference result.

---

# 3. Inference SLO

The serving SLO used for this experiment is:

| Metric                |         SLO |
| --------------------- | ----------: |
| p95 inference latency | `<= 100 ms` |
| Error rate            |     `<= 1%` |

A concurrency level is considered **SLO-compliant only when both conditions pass**:

```text
p95 latency <= 100 ms
AND
error rate <= 1%
```

The first tested concurrency level where either condition fails is treated as the observed breaking point.

---

# 4. Experimental Methodology

The experiment uses an actual HTTP load test against the running FastAPI service.

The load generator sends concurrent HTTP `POST /infer` requests using the inference request dataset.

For each concurrency level, the experiment records:

* concurrency
* requests attempted
* completed requests
* failed requests
* wall-clock duration
* p50 latency
* p95 latency
* p99 latency
* throughput / QPS
* error rate
* SLO pass/fail status
* sample errors, when present

The experiment begins with a service health check followed by warm-up requests.

### Warm-up

```text
10 warm-up requests
```

### Requests per concurrency level

```text
100 requests
```

### Tested concurrency levels

```text
1
2
4
8
16
32
64
128
```

This produces an actual concurrency sweep rather than a single-point benchmark.

---

# 5. Dataset

The load test uses:

```text
phase3/task04/data/inference_requests.json
```

The dataset contains:

```text
10 inference request records
```

The dataset is explicitly treated as a:

> Starter/control dataset for reproducible load testing.

It is not represented as production traffic.

The same request records can be reused across concurrency levels so that the experiment isolates serving behavior rather than changing the input population between load levels.

---

# 6. Load Test Results

The following results were generated from the actual HTTP load test.

| Concurrency | p50 (ms) | p95 (ms) | p99 (ms) |     QPS | Error Rate | SLO        |
| ----------: | -------: | -------: | -------: | ------: | ---------: | ---------- |
|           1 |    2.685 |    4.860 |    5.605 | 330.891 |         0% | PASS       |
|           2 |    6.863 |   12.032 |   12.971 | 267.771 |         0% | PASS       |
|           4 |   17.113 |   47.829 |   53.787 | 196.114 |         0% | PASS       |
|           8 |   55.821 |  110.283 |  118.985 | 129.314 |         0% | **BREACH** |
|          16 |  167.753 |  210.614 |  228.485 |  93.834 |         0% | **BREACH** |
|          32 |  282.484 |  351.640 |  354.144 | 110.968 |         0% | **BREACH** |
|          64 |  553.864 |  583.448 |  614.749 | 123.181 |         0% | **BREACH** |
|         128 |  933.224 |  938.288 |  939.854 | 104.310 |         0% | **BREACH** |

### Observations

The service remained within the defined SLO through concurrency `4`.

At concurrency `8`, p95 latency increased to approximately:

```text
110.283 ms
```

which exceeds the:

```text
100 ms p95 SLO
```

The measured error rate remained:

```text
0%
```

Therefore, the first observed SLO breach was caused by latency rather than request errors.

---

# 7. Observed Breaking Point

The experiment identifies:

```text
Breaking point concurrency: 8
```

Reason:

```text
p95 latency SLO breach
```

Observed values at the breaking point:

```text
Concurrency: 8
p95 latency: 110.283 ms
Error rate: 0%
p95 SLO: <= 100 ms
Error-rate SLO: <= 1%
```

Therefore:

```text
8 concurrent requests
```

is the first tested load level that violates the serving SLO.

The machine remained responsive and no request errors were recorded at this point. The failure condition is specifically latency-based.

Evidence:

```text
logs/breaking_point.json
```

---

# 8. Highest Safe Tested Capacity

The highest tested concurrency that satisfied both SLO conditions was:

```text
Concurrency = 4
```

At concurrency `4`:

```text
p95 = 47.829 ms
error rate = 0%
```

Both values satisfy the defined SLO.

Therefore:

```text
Highest safe tested concurrency = 4
```

The next tested level, concurrency `8`, breached the p95 latency SLO.

---

# 9. Headroom Analysis

A conservative headroom target of:

```text
30%
```

is applied to the measured safe capacity.

The experiment records:

```text
Highest safe tested concurrency = 4
```

The operating-capacity calculation is:

```text
recommended operating concurrency
    = highest safe tested concurrency × (1 - headroom target)
```

Therefore:

```text
4 × (1 - 0.30)
= 4 × 0.70
= 2.8
```

Because concurrency is represented as a whole-number operating level, the result is conservatively rounded down:

```text
Recommended operating concurrency = 2
```

This provides a conservative operating target below the highest safe tested capacity.

### Headroom summary

```text
Highest safe tested concurrency : 4
Headroom target                 : 30%
Recommended operating level     : 2
Measured breaking point         : 8
```

The measured breaking point of `8` is retained as the capacity reference for the experiment, while the operating recommendation uses the highest SLO-safe tested level as its baseline.

Evidence:

```text
logs/headroom_analysis.json
```

---

# 10. Throughput Behavior

Measured throughput across the concurrency sweep:

| Concurrency |     QPS |
| ----------: | ------: |
|           1 | 330.891 |
|           2 | 267.771 |
|           4 | 196.114 |
|           8 | 129.314 |
|          16 |  93.834 |
|          32 | 110.968 |
|          64 | 123.181 |
|         128 | 104.310 |

The experiment shows that increasing concurrency does not produce unlimited throughput growth.

As concurrency increases beyond the SLO-safe region, latency increases substantially and throughput becomes constrained by serving contention/queueing behavior.

The important capacity boundary for this task is therefore the latency SLO rather than maximizing raw QPS at the highest possible concurrency.

Evidence:

```text
logs/throughput_results.json
logs/latency_curve.json
logs/load_test_results.json
```

---

# 11. Horizontal Scaling Strategy

The recommended production scaling approach is horizontal scaling.

The objective is to add inference replicas before the serving layer consistently violates the latency or error-rate SLO.

## Autoscaling signals

The following metrics should be exposed to the autoscaling layer:

```text
request_concurrency
p95_latency_ms
error_rate_percent
cpu_utilization
```

Latency and concurrency should be treated as primary serving signals because CPU utilization alone may not capture queueing or model-serving saturation.

---

# 12. Replica Policy

Recommended initial policy:

| Setting                  | Recommendation |
| ------------------------ | -------------: |
| Minimum replicas         |              1 |
| Initial maximum replicas |              4 |
| Scale-out step           |     +1 replica |
| Scale-in step            |     -1 replica |
| Scale-out cooldown       |     60 seconds |
| Scale-in cooldown        |    300 seconds |

The initial maximum of four replicas is a starting configuration for the demonstrated local serving path, not a production capacity guarantee.

Production replica limits should be recalibrated using production traffic measurements.

---

# 13. Autoscaling Behavior

A practical scaling policy is:

### Scale out when

One or more of the following persist for the configured observation window:

```text
p95 latency approaches or exceeds the 100 ms SLO
request concurrency approaches the safe operating threshold
error rate approaches the 1% SLO
CPU utilization indicates sustained saturation
```

### Scale in when

```text
traffic remains low
p95 latency is comfortably below the SLO
error rate remains within the SLO
replica health/readiness remains stable
```

Scale-in should use a longer cooldown than scale-out to avoid oscillation.

The recommended initial cooldowns are:

```text
Scale out: 60 seconds
Scale in : 300 seconds
```

---

# 14. Model Caching

Each serving replica should load the model/artifacts once and reuse them across requests.

Recommended behavior:

```text
Replica starts
      ↓
Load model/artifacts
      ↓
Validate readiness
      ↓
Serve requests from cached model
```

The model should not be repeatedly initialized for every inference request.

This reduces avoidable per-request overhead and makes horizontal replicas independently ready to serve traffic.

---

# 15. Precomputation

The inference path contains reusable information that can be prepared before request-time processing.

Recommended precomputation includes:

* normalized skill vocabulary
* reusable feature mappings
* immutable model artifacts
* reusable lookup structures

This keeps request-time work focused on request-specific inference.

---

# 16. Batching Strategy

Batching is **not enabled by default** for this experiment.

Micro-batching may be introduced if request volume becomes high enough to benefit from grouped inference.

However, batching must not be enabled solely to increase throughput.

The key constraint remains:

```text
queueing delay + inference time <= p95 SLO
```

If batching increases queueing delay enough to violate the 100 ms p95 SLO, batching should be reduced or disabled.

---

# 17. Explainability Evidence

The inference response includes explainability fields rather than returning only a numeric score.

The recorded explainability evidence contains:

```text
request_id
student_id
score
decision
matched_skills
missing_skills
threshold
required_count
matched_count
missing_count
explanation_method
candidate_mask
required_mask
computation_token
```

Example recorded result:

```text
Request ID        : task04_req_001
Score             : 1.0
Decision          : MATCH
Matched skills    : machine learning, python, sql
Missing skills    : none
Threshold         : 0.7
Explanation       : skill_overlap
Required count    : 3
Matched count     : 3
Missing count     : 0
```

This makes the decision traceable to the skill overlap rather than presenting an unexplained recommendation.

Evidence:

```text
logs/explainability_example.json
```

The explainability artifact is a concrete inference example. It should not be interpreted as proof that every production request will have identical explanation content.

---

# 18. MODEL_UNAVAILABLE Safety Test

The failure path was explicitly tested by forcing the model to become unavailable.

The expected behavior is:

```text
MODEL_UNAVAILABLE
        ↓
NO_RECOMMENDATION
```

The system must not fabricate:

* a score
* a match decision
* a recommendation

The recorded failure-path test passed the following assertions:

```text
no_fabricated_score = true
no_recommendation = true
model_marked_unavailable = true
```

Observed failure response characteristics:

```text
error_code : MODEL_UNAVAILABLE
score      : null
decision   : NO_RECOMMENDATION
```

The fallback instructs the caller to retry inference when the model service becomes available.

Evidence:

```text
logs/failure_path.json
```

---

# 19. Rollback / Safety Triggers

Scaling or serving changes should be treated as unsafe if they cause any of the following:

```text
p95 latency > 100 ms
error rate > 1%
model readiness failure
```

Recommended rollback/safety actions:

1. Stop scale-in.
2. Preserve the minimum healthy replica count.
3. Route traffic only to ready replicas.
4. Keep the `MODEL_UNAVAILABLE` safe fallback active.
5. Investigate the latency/error condition before reducing serving capacity again.

This prevents an unhealthy scaling event from immediately reducing available serving capacity.

---

# 20. Reproducibility

The complete experiment can be reproduced from the repository.

## Start the service

From the project root:

```bash
source .venv/bin/activate
uvicorn phase3.task04.src.server:app --host 127.0.0.1 --port 8000
```

Verify health:

```bash
curl http://127.0.0.1:8000/health
```

Expected healthy response includes:

```json
{
  "status": "ok",
  "model_available": true,
  "service": "task04-inference"
}
```

## Run the Task 04 demo

From the project root:

```bash
python phase3/task04/run_task04_demo.py
```

This generates:

```text
logs/explainability_example.json
logs/failure_path.json
```

## Run the HTTP load experiment

From the project root:

```bash
python phase3/task04/run_task04_load_test.py
```

The experiment generates runtime evidence including:

```text
logs/load_test_results.json
logs/latency_curve.json
logs/throughput_results.json
logs/breaking_point.json
logs/headroom_analysis.json
logs/scaling_plan.json
logs/task04_summary.json
logs/experiment_log.csv
```

The experiment log is generated from the actual execution rather than being manually populated.

---

# 21. Generated Evidence

The following artifacts support the Task 04 conclusions:

| Artifact                           | Purpose                                 |
| ---------------------------------- | --------------------------------------- |
| `logs/load_test_results.json`      | Complete HTTP load-test results         |
| `logs/latency_curve.json`          | Latency behavior across concurrency     |
| `logs/throughput_results.json`     | QPS/throughput across concurrency       |
| `logs/breaking_point.json`         | First observed SLO-breaking concurrency |
| `logs/headroom_analysis.json`      | Safe capacity and headroom calculation  |
| `logs/scaling_plan.json`           | Horizontal scaling configuration        |
| `logs/explainability_example.json` | Concrete explainable inference result   |
| `logs/failure_path.json`           | MODEL_UNAVAILABLE safety evidence       |
| `logs/task04_summary.json`         | Experiment summary                      |
| `logs/experiment_log.csv`          | Runtime experiment log                  |

---

# 22. Evidence Traceability

The main Task 04 claims map directly to generated evidence.

### SLO performance

```text
Claim:
Concurrency 1, 2 and 4 satisfy the SLO.

Evidence:
logs/load_test_results.json
logs/experiment_log.csv
```

### Breaking point

```text
Claim:
The first observed SLO breach occurs at concurrency 8.

Evidence:
logs/breaking_point.json
```

### Headroom

```text
Claim:
Highest safe tested concurrency is 4 and the conservative
recommended operating level is 2 with a 30% headroom target.

Evidence:
logs/headroom_analysis.json
```

### Scaling strategy

```text
Claim:
Horizontal scaling should use concurrency/latency/error signals,
model caching, controlled replica limits and safe rollback behavior.

Evidence:
logs/scaling_plan.json
```

### Explainability

```text
Claim:
The inference response contains concrete explanation fields
such as matched skills, missing skills, threshold and method.

Evidence:
logs/explainability_example.json
```

### Failure safety

```text
Claim:
MODEL_UNAVAILABLE does not fabricate a score or recommendation.

Evidence:
logs/failure_path.json
```

---

# 23. Limitations and Evidence Boundary

The following limitations are explicitly acknowledged.

### Local environment

The load experiment measures the tested local HTTP inference service.

Therefore, the measured concurrency capacity should not be presented as a production traffic guarantee.

### Starter/control dataset

The experiment uses a 10-record starter/control dataset for reproducibility.

It does not represent the diversity or volume of production traffic.

### Hardware dependency

Latency and throughput are affected by the machine, operating system, Python runtime, CPU scheduling, network stack, and server configuration used during the experiment.

### Synthetic load

The concurrency sweep is generated by the repository's load generator.

It is designed to exercise serving behavior reproducibly and should not be interpreted as a prediction of real-world traffic patterns.

### Scaling validation

The horizontal scaling policy is a documented deployment strategy based on the measured local behavior.

A production deployment should recalibrate:

* replica limits
* autoscaling thresholds
* cooldown periods
* batching configuration
* operating concurrency

using production telemetry and representative traffic.

---

# 24. Final Task 04 Conclusion

The Task 04 experiment provides a reproducible HTTP load-readiness measurement for the inference service.

The observed results show:

```text
SLO:
p95 <= 100 ms
error rate <= 1%

Highest safe tested concurrency:
4

First observed SLO breach:
8 concurrent requests

Breaking-point reason:
p95 latency

p95 at breaking point:
110.283 ms

Error rate at breaking point:
0%

Conservative headroom target:
30%

Recommended operating concurrency:
2
```

The experiment therefore establishes a measured local capacity boundary:

```text
Safe tested region:
1 → 4 concurrency

First observed SLO breach:
8 concurrency
```

The recommended horizontal scaling approach is to add replicas based on serving pressure, expose latency/concurrency/error metrics to the autoscaling layer, cache model artifacts per replica, precompute reusable inference structures, and introduce batching only when queueing remains within the latency SLO.

The system also preserves a safe `MODEL_UNAVAILABLE` path that returns `NO_RECOMMENDATION` without fabricating a score.

All major conclusions are backed by runtime-generated JSON/CSV artifacts in:

```text
phase3/task04/logs/
```

The evidence boundary remains explicit: these results demonstrate the behavior of the tested local HTTP service and provide a reproducible scaling-readiness baseline; they are not a claim of production capacity.
