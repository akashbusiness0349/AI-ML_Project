from __future__ import annotations

import time

from .candidate_to_job import recommend_jobs
from .company_to_candidate import recommend_candidates
from .explainability import build_explanation
from .fallback import fallback_recommendations


class RecommendationEngine:
    def __init__(
        self,
        candidates: list[dict],
        companies: list[dict],
        jobs: list[dict],
    ) -> None:
        self.candidates = candidates
        self.companies = companies
        self.jobs = jobs

        self.candidate_map = {
            row["candidate_id"]: row
            for row in candidates
        }

        self.company_map = {
            row["company_id"]: row
            for row in companies
        }

    def recommend_for_candidate(
        self,
        candidate_id: str,
        top_k: int = 5,
        model_available: bool = True,
    ) -> dict:
        if not model_available:
            return fallback_recommendations(
                self.jobs,
                "job_id",
                top_k,
            )

        candidate = self.candidate_map[candidate_id]

        start = time.perf_counter()

        rows = recommend_jobs(
            candidate,
            self.jobs,
            top_k,
        )

        for row in rows:
            job = next(
                job
                for job in self.jobs
                if job["job_id"] == row["job_id"]
            )

            row["explanation"] = build_explanation(
                "candidate_to_job",
                candidate,
                job,
                row["features"],
            )

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        return {
            "status": "OK",
            "direction": "candidate_to_job",
            "candidate_id": candidate_id,
            "latency_ms": elapsed_ms,
            "recommendations": rows,
        }

    def recommend_for_company(
        self,
        company_id: str,
        top_k: int = 5,
        model_available: bool = True,
    ) -> dict:
        if not model_available:
            return fallback_recommendations(
                self.candidates,
                "candidate_id",
                top_k,
            )

        company = self.company_map[company_id]

        start = time.perf_counter()

        rows = recommend_candidates(
            company,
            self.candidates,
            top_k,
        )

        for row in rows:
            candidate = next(
                candidate
                for candidate in self.candidates
                if candidate["candidate_id"]
                == row["candidate_id"]
            )

            row["explanation"] = build_explanation(
                "company_to_candidate",
                company,
                candidate,
                row["features"],
            )

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        return {
            "status": "OK",
            "direction": "company_to_candidate",
            "company_id": company_id,
            "latency_ms": elapsed_ms,
            "recommendations": rows,
        }