# Phase 2 — Task 1
## Company Onboarding & Marketplace Data Model

**Project:** Altrodav  
**Phase:** 2 — Industry Immersion  
**Task:** 1  
**Focus:** Student ↔ Job Matching Foundation

---

## Objective

The objective of Task 1 is to define the foundation for the marketplace
matching system that connects students with suitable job opportunities.

This task focuses on:

1. Defining the student feature space.
2. Defining the job feature space.
3. Identifying comparable student-job matching signals.
4. Defining the initial matching API contract for Backend integration.
5. Creating a machine-readable schema for the matching request and response.

---

## Matching Concept

The marketplace matching system compares a student's profile against
the requirements and preferences of a job.

The initial matching flow is:

Student Profile
        ↓
Student Features
        ↓
        ├──────────────┐
        │              │
        ▼              ▼
 Matching Signals ← Job Features
        │
        ▼
 Match Score
        │
        ▼
 Ranked Job Matches

---

## Student Feature Groups

The student profile contains the following feature groups:

- Student identity
- Skills
- Education
- Experience
- Projects
- Certifications
- Location
- Work preferences
- Role preferences
- Verified scores

---

## Job Feature Groups

The job profile contains the following feature groups:

- Job identity
- Required skills
- Preferred skills
- Education requirements
- Experience requirements
- Job role
- Location
- Work mode
- Employment type
- Compensation information
- Verified requirements

---

## Matching Signals

The initial matching system should support the following comparable
signals:

- Skill match
- Education match
- Experience match
- Location match
- Role match
- Work preference match
- Verified score compatibility

These signals provide the foundation for a future ranking model.

The final weighting strategy is intentionally not fixed in Task 1 because
the ranking methodology may evolve after marketplace and Backend
requirements are finalized.

---

## API Contract

The proposed matching endpoint is:

POST /api/v1/matches

The endpoint accepts a student identifier and a job identifier and
returns a matching result containing:

- Student ID
- Job ID
- Overall match score
- Individual matching signals
- Model/version information

The detailed contract is documented in:

`matching_api_contract.md`

---

## Schema

The machine-readable request and response definitions are stored in:

`schemas/matching_schema.json`

---

## Versioning

Initial API version:

`v1`

The API contract should be versioned so that future changes do not
unexpectedly break Backend integrations.

---

## Task 1 Deliverables

- [x] Student feature space defined
- [x] Job feature space defined
- [x] Matching signals defined
- [x] Initial API contract defined
- [x] JSON schema created
- [ ] Backend contract agreement
- [ ] Production matching implementation

---

## Status

**Task 1 — Feature-space and API contract foundation completed.**

The API documented in this task is a proposed v1 contract and should be
treated as a draft until formally agreed with the Backend team.