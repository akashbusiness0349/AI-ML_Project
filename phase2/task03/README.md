# PlaceMux Phase 2 — Task 3
## Search & Discovery

### Objective

Build v1 ranking functionality for the PlaceMux AI-ML marketplace.

The system supports two search directions:

1. Ranking jobs for a student.
2. Ranking candidates for a company/job.

### Job Ranking

For a given student, multiple jobs are evaluated using:

- Required skill match
- Preferred skill match
- Role match
- Work-mode match
- Experience match
- Verified-score match

Jobs are sorted from highest match score to lowest match score.

### Candidate Ranking

For a given job, multiple students are evaluated using the same matching signals.

Candidates are sorted from highest match score to lowest match score.

### Ranking Model

Version:

v1

The ranking engine uses deterministic weighted scoring.

### Required Deliverables

- Job ranking for students.
- Candidate ranking for companies.

### Verification

The demo verifies:

- Ranked jobs are returned.
- Ranked candidates are returned.
- Job ranking is sorted by descending match score.
- Candidate ranking is sorted by descending match score.
- API-style responses are generated.

### Definition of Done

- Ranked jobs returned for a student.
- Ranked candidates returned for a job.
- Search and discovery demonstration completed successfully.