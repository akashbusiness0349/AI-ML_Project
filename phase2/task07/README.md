# PlaceMux Phase 2 — Task 7
## Pay-per-Application Flow

### Focus

Tune marketplace ranking to support paid-application conversion while protecting overall match quality.

### Objective

The current Task 6 match-quality baseline is used as the reference point.

A conversion-oriented ranking layer introduces additional signals while keeping match relevance as the primary ranking factor.

### Ranking Signals

The tuned ranking uses:

- Match score
- Relevance score
- Application intent score
- Application value score

Match relevance receives the highest weight so that conversion optimization does not completely override candidate-job relevance.

### Conversion Proxy

Because real paid-application history is not available in the current representative dataset, a conversion proxy is used.

An opportunity is considered conversion-ready when its conversion priority score reaches the defined threshold.

This proxy is used only for ranking evaluation and is not presented as actual payment conversion data.

### Baseline Comparison

The tuned ranking is compared against the Task 6 baseline:

- Average match quality
- Conversion proxy
- Ranking order
- Rank sequence
- Match-quality protection

### Match Quality Protection

The tuned configuration must not reduce average match quality by more than the configured tolerance.

### Definition of Done

The ranking is tuned for conversion and evaluated against the existing baseline while monitoring match relevance and quality.

### Model Version

`v1-conversion`