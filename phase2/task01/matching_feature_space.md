# Student ↔ Job Matching Feature Space

## 1. Purpose

This document defines the feature space used to compare student profiles
with job opportunities in the marketplace.

The goal is to create a consistent representation where student
attributes and job requirements can be transformed into comparable
matching signals.

---

# 2. Student Feature Space

## 2.1 Student Identity

| Feature | Type | Description |
|---|---|---|
| student_id | string | Unique student identifier |

The student identifier is used for tracking and API requests. It is not
itself a matching signal.

---

## 2.2 Skills

| Feature | Type | Description |
|---|---|---|
| skills | array[string] | Skills possessed by the student |

Examples:

- Python
- SQL
- Machine Learning
- Java
- Docker
- AWS

Skills are one of the primary inputs to the matching process.

---

## 2.3 Education

| Feature | Type | Description |
|---|---|---|
| degree | string | Highest or relevant degree |
| field_of_study | string | Academic specialization |
| graduation_year | integer | Expected or completed graduation year |

Education information can be compared with the education requirements
specified by a job.

---

## 2.4 Experience

| Feature | Type | Description |
|---|---|---|
| years_experience | number | Relevant professional experience |
| experience_roles | array[string] | Previous roles or job titles |

Experience is compared against the minimum or preferred experience
requirements of a job.

---

## 2.5 Projects

| Feature | Type | Description |
|---|---|---|
| project_domains | array[string] | Domains represented by student projects |
| project_technologies | array[string] | Technologies used in projects |

Examples of project domains:

- Machine Learning
- NLP
- Computer Vision
- Web Development

---

## 2.6 Certifications

| Feature | Type | Description |
|---|---|---|
| certifications | array[string] | Relevant certifications |

Certifications may provide additional evidence of technical or
domain-specific capability.

---

## 2.7 Location

| Feature | Type | Description |
|---|---|---|
| city | string | Student city |
| country | string | Student country |

Location can be compared with job location requirements.

---

## 2.8 Work Preferences

| Feature | Type | Description |
|---|---|---|
| work_modes | array[string] | Preferred work modes |
| preferred_locations | array[string] | Preferred work locations |

Supported work modes:

- remote
- hybrid
- onsite

---

## 2.9 Role Preferences

| Feature | Type | Description |
|---|---|---|
| desired_roles | array[string] | Roles the student is interested in |

Examples:

- ML Engineer
- Data Scientist
- Data Analyst
- Backend Developer

---

## 2.10 Verified Scores

| Feature | Type | Description |
|---|---|---|
| verified_scores | object | Scores obtained through verified assessments or models |

Examples may include:

- coding score
- ML assessment score
- communication score
- domain assessment score

The exact scoring system should be finalized according to marketplace
requirements.

---

# 3. Job Feature Space

## 3.1 Job Identity

| Feature | Type | Description |
|---|---|---|
| job_id | string | Unique job identifier |

The job identifier is used for tracking and API requests. It is not
itself a matching signal.

---

## 3.2 Required Skills

| Feature | Type | Description |
|---|---|---|
| required_skills | array[string] | Skills required for the job |
| preferred_skills | array[string] | Skills that provide additional value |

Required skills should have higher matching importance than preferred
skills.

---

## 3.3 Education Requirements

| Feature | Type | Description |
|---|---|---|
| required_degree | string | Required degree |
| required_fields | array[string] | Relevant academic fields |

---

## 3.4 Experience Requirements

| Feature | Type | Description |
|---|---|---|
| minimum_years_experience | number | Minimum required experience |
| preferred_roles | array[string] | Relevant previous roles |

---

## 3.5 Job Role

| Feature | Type | Description |
|---|---|---|
| job_role | string | Primary role/title of the position |

Examples:

- ML Engineer
- Software Engineer
- Data Analyst
- Data Scientist

---

## 3.6 Location

| Feature | Type | Description |
|---|---|---|
| city | string | Job location |
| country | string | Job country |

---

## 3.7 Work Mode

| Feature | Type | Description |
|---|---|---|
| work_mode | string | Job working arrangement |

Supported values:

- remote
- hybrid
- onsite

---

## 3.8 Employment Type

| Feature | Type | Description |
|---|---|---|
| employment_type | string | Employment arrangement |

Examples:

- internship
- full_time
- part_time
- contract

---

## 3.9 Compensation

| Feature | Type | Description |
|---|---|---|
| salary_min | number | Minimum salary |
| salary_max | number | Maximum salary |
| currency | string | Salary currency |

Compensation is included in the job representation but should not
automatically be treated as a matching signal until marketplace
requirements define how student expectations and employer ranges should
be compared.

---

## 3.10 Verified Requirements

| Feature | Type | Description |
|---|---|---|
| required_verified_scores | object | Minimum verified scores required by the job |

---

# 4. Comparable Matching Signals

The student and job feature spaces are converted into comparable
signals.

| Matching Signal | Student Input | Job Input |
|---|---|---|
| skill_match | skills | required/preferred skills |
| education_match | degree, field | required degree/fields |
| experience_match | years, roles | minimum years, preferred roles |
| location_match | location/preferences | job location |
| role_match | desired roles | job role |
| work_mode_match | work preferences | job work mode |
| verified_score_match | verified scores | required scores |

---

# 5. Signal Definitions

## Skill Match

Measures the compatibility between student skills and the skills
required or preferred by the job.

Conceptually:

Student Skills
        ↕
Job Skills
        ↓
Skill Match Signal

---

## Education Match

Compares the student's degree and academic field with job education
requirements.

---

## Experience Match

Compares relevant student experience with the minimum and preferred job
experience.

---

## Location Match

Determines whether the student's location and preferences are compatible
with the job's location requirements.

---

## Role Match

Compares the student's desired roles with the job role.

---

## Work Mode Match

Compares student preferences such as remote, hybrid, or onsite with the
job's supported work mode.

---

## Verified Score Match

Compares verified student assessment scores with job-specific verified
requirements.

---

# 6. Overall Match Score

The matching system may combine individual signals into an overall
match score.

Conceptually:

Overall Match
      ↓
Skill Match
Education Match
Experience Match
Location Match
Role Match
Work Mode Match
Verified Score Match

The exact weighting and ranking algorithm are intentionally left open in
Task 1.

Weights should be agreed based on marketplace requirements and validated
using real matching outcomes.

---

# 7. Design Principles

The matching feature space follows these principles:

1. Student and job features should use compatible representations.
2. Required job requirements should be distinguishable from preferences.
3. Identity fields should not automatically become matching signals.
4. Matching signals should be independently measurable.
5. Feature definitions should be versionable.
6. Missing values should be handled explicitly.
7. The matching system should be extensible as new marketplace features
   are introduced.

---

# 8. Initial Version

Feature-space version:

`v1`

Status:

**Draft — ready for Backend review and agreement.**