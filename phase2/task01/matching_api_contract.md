# Matching API Contract

## 1. Purpose

This document defines the proposed API contract between the matching
service and the Backend marketplace system.

The API is designed to accept a student-job pair and return a structured
matching result.

---

# 2. API Version

Version:

`v1`

Endpoint:

`POST /api/v1/matches`

---

# 3. Request

## Endpoint

```text
POST /api/v1/matches