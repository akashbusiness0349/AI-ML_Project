"""
FastAPI inference service for Task 05.

Provides:
- health
- readiness
- inference
- explicit safe degradation
"""

import time
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .fallback import (
    safe_model_unavailable_response,
)
from .model import (
    ModelUnavailableError,
    SkillMatchingModel,
)


app = FastAPI(
    title="PlaceMux Task 05 Reliability Service",
    version="1.0.0",
)


model = SkillMatchingModel()


class InferenceRequest(BaseModel):
    request_id: str = Field(
        default="task05_request"
    )

    candidate_skills: List[str] = Field(
        default_factory=list
    )

    required_skills: List[str] = Field(
        default_factory=list
    )


@app.get("/")
def root():
    return {
        "service": "task05-reliability-service",
        "status": "ok",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_available": model.model_available,
        "service": "task05-reliability-service",
    }


@app.get("/ready")
def ready():
    return {
        "ready": model.model_available,
        "model_available": model.model_available,
    }


@app.post("/infer")
def infer(
    request: InferenceRequest,
):

    request_started = time.perf_counter()

    try:

        result = model.predict(
            candidate_skills=request.candidate_skills,
            required_skills=request.required_skills,
        )

        request_latency = (
            time.perf_counter()
            - request_started
        ) * 1000.0

        return {
            "request_id": request.request_id,
            "status": "success",
            "model_available": True,
            "decision": result.decision,
            "score": result.score,
            "threshold": result.threshold,
            "matched_skills": result.matched_skills,
            "missing_skills": result.missing_skills,
            "explanation": result.explanation,
            "explanation_method": "skill_overlap",
            "computation_token": result.computation_token,
            "model_latency_ms": result.latency_ms,
            "request_latency_ms": round(
                request_latency,
                6,
            ),
        }

    except ModelUnavailableError:

        return safe_model_unavailable_response(
            request.request_id
        )