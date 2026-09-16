from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .inference import (
    ModelUnavailableError,
    SkillMatchingModel,
    safe_model_unavailable_response,
)


BASE_DIR = Path(__file__).resolve().parents[1]

app = FastAPI(
    title="Task 04 Inference Service",
    description="Horizontal scale and load readiness inference service.",
    version="1.0.0",
)

model = SkillMatchingModel()


class InferenceRequest(BaseModel):
    request_id: str = Field(..., min_length=1)
    student_id: str = Field(..., min_length=1)
    candidate_skills: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    metadata: Optional[dict] = None


@app.get("/health")
def health() -> dict:
    model.refresh_availability()

    return {
        "status": "ok" if model.available else "degraded",
        "model_available": model.available,
        "service": "task04-inference",
    }


@app.get("/ready")
def ready() -> dict:
    model.refresh_availability()

    if not model.available:
        return {
            "ready": False,
            "reason": "MODEL_UNAVAILABLE",
        }

    return {
        "ready": True,
        "model_available": True,
    }


@app.post("/infer")
def infer(request: InferenceRequest) -> dict:
    started = time.perf_counter()

    try:
        result = model.predict(
            request_id=request.request_id,
            student_id=request.student_id,
            candidate_skills=request.candidate_skills,
            required_skills=request.required_skills,
        )

        elapsed_ms = (time.perf_counter() - started) * 1000

        return {
            "status": "success",
            "request_id": result.request_id,
            "student_id": result.student_id,
            "score": result.score,
            "decision": result.decision,
            "matched_skills": result.matched_skills,
            "missing_skills": result.missing_skills,
            "model_available": result.model_available,
            "explanation": result.explanation,
            "latency_ms": round(elapsed_ms, 6),
        }

    except ModelUnavailableError:
        return safe_model_unavailable_response(
            request_id=request.request_id,
            student_id=request.student_id,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INFERENCE_ERROR",
                "message": str(exc),
            },
        ) from exc


@app.get("/")
def root() -> dict:
    return {
        "service": "Task 04 Horizontal Scale & Load Readiness",
        "endpoints": {
            "health": "GET /health",
            "ready": "GET /ready",
            "inference": "POST /infer",
        },
    }