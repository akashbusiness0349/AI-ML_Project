# PlaceMux Phase 2 — Task 2
## Job Posting with Skill Thresholds

### Objective

Build matching feature vectors from real job skill thresholds and validate the mapping between thresholds and student competency levels.

### What this task implements

This task provides a deterministic threshold-based matching foundation.

The system:

1. Accepts job skill requirements with minimum competency thresholds.
2. Accepts student competency scores.
3. Validates job thresholds.
4. Maps numerical scores to competency levels.
5. Compares student scores against job thresholds.
6. Generates a binary match vector.
7. Calculates an overall vector match score.
8. Produces an API-style matching response.

### Competency Mapping

| Score Range | Competency Level |
|---|---|
| 0–49 | Beginner |
| 50–69 | Intermediate |
| 70–84 | Advanced |
| 85–100 | Expert |

### Example

Student competency:

- Python: 85
- SQL: 55
- Machine Learning: 90
- Docker: 70
- Git: 80

Job thresholds:

- Python: 70
- SQL: 60
- Machine Learning: 75
- Docker: 50
- Git: 70

Generated match vector:

```text
Python            → 1
SQL               → 0
Machine Learning  → 1
Docker            → 1
Git               → 1