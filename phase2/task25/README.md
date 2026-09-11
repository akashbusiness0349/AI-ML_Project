# PlaceMux Phase 3 - Task 25

## Go-Live — Live Model Monitoring

This task implements a lightweight production-style monitoring layer for the PlaceMux matching model.

## Monitoring signals

The monitoring pipeline tracks:

- Prediction quality
- Precision
- Recall
- False-positive rate
- Match-score distribution
- Prediction drift using PSI
- Average latency
- P95 latency
- Maximum latency
- Error rate
- Model version consistency
- Monitoring alerts
- Plain-English prediction explanation

## Production traffic

The demo uses 20 real-shaped production traffic events representing candidate-to-job matching activity.

The data is intentionally small for a launch rehearsal and does not represent actual production traffic volume.

## Alert thresholds

- PSI: 0.20
- P95 latency: 100 ms
- Error rate: 5%
- Precision: 80%
- Recall: 80%

## Persistence

The monitoring report is persisted to:

`logs/live_monitoring_report.json`

Production evidence is persisted to:

`logs/production_monitoring_evidence.json`

## Failure handling

The demo injects an error event and verifies that the monitoring system detects a non-zero error rate.

## Explainability

The demo produces a plain-English explanation for a candidate-job prediction.

## Important limitation

This is a production-style go-live rehearsal and MLOps foundation, not a claim that the system is connected to a real external production marketplace.

Actual production deployment would require real telemetry ingestion, dashboards, alert routing, access controls, and infrastructure-level monitoring.

## Definition of Done

- Live model monitoring implemented.
- Production-style traffic processed.
- Prediction quality monitored.
- Drift monitored.
- Latency monitored.
- Error rate monitored.
- Model version monitored.
- Alerts implemented.
- Failure handling verified.
- Explainability demonstrated.
- Monitoring evidence persisted.
- End-to-end demo completed.