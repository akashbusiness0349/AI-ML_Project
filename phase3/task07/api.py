"""
TASK 07 — Activation & Onboarding Optimization API

Standalone FastAPI service.

Flow:
    fresh account
        ↓
    onboarding
        ↓
    randomized experiment assignment
        ↓
    recommendations
        ↓
    impression / click / apply events
        ↓
    persisted live evidence

Important:
- This service captures actual events generated while the service is running.
- Local live events are not claimed to be production traffic.
- Control uses popularity baseline.
- Treatment uses trained cold-start model.
"""

from __future__ import annotations

import hashlib
import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException

from src.baseline import rank_popularity
from src.cold_start import load_model
from src.fallback import popularity_fallback
from src.recommender import recommend
from src.validation import validate_candidate


ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"

CANDIDATES_PATH = DATA_DIR / "candidates.json"
JOBS_PATH = DATA_DIR / "jobs.json"
LIVE_EVENTS_PATH = LOG_DIR / "live_events.json"

LOG_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(
    title="Task 07 — Activation & Onboarding Optimization",
    version="3.0.0",
)


# ---------------------------------------------------------------------
# In-memory session store
# ---------------------------------------------------------------------

SESSIONS: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, value: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(value, f, indent=2)


def load_jobs() -> list[dict[str, Any]]:
    return load_json(JOBS_PATH)


def append_live_event(event: dict[str, Any]) -> None:
    if LIVE_EVENTS_PATH.exists():
        try:
            events = load_json(LIVE_EVENTS_PATH)
            if not isinstance(events, list):
                events = []
        except Exception:
            events = []
    else:
        events = []

    events.append(event)

    save_json(
        LIVE_EVENTS_PATH,
        events,
    )


def create_event(
    *,
    candidate_id: str,
    job_id: str,
    event_type: str,
    experiment_id: str,
    experiment_group: str,
    session_id: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:

    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": utc_now(),
        "candidate_id": candidate_id,
        "job_id": job_id,
        "event_type": event_type,
        "experiment_id": experiment_id,
        "experiment_group": experiment_group,
        "session_id": session_id,
        "source": "task07_live_api",
        "production_data": False,
        "metadata": metadata or {},
    }

    append_live_event(event)

    return event


def assign_experiment_group(
    session_id: str,
    experiment_id: str,
) -> str:
    """
    Stable 50/50 randomized assignment.

    The session ID is random UUID-based, so fresh sessions receive
    independently distributed assignments.
    """

    digest = hashlib.sha256(
        f"{experiment_id}:{session_id}".encode("utf-8")
    ).hexdigest()

    bucket = int(digest[:8], 16) / float(0xFFFFFFFF)

    return "control" if bucket < 0.5 else "treatment"


def find_candidate(
    candidate_id: str,
) -> dict[str, Any] | None:

    candidates = load_json(CANDIDATES_PATH)

    for candidate in candidates:
        if candidate.get("candidate_id") == candidate_id:
            return candidate

    return None


# ---------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------

from pydantic import BaseModel, Field


class OnboardingRequest(BaseModel):
    candidate_id: str = Field(min_length=1)
    experiment_id: str = Field(
        default="task07_activation_v1",
        min_length=1,
    )


class EventRequest(BaseModel):
    session_id: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    job_id: str = Field(min_length=1)

    event_type: Literal[
        "impression",
        "click",
        "apply",
        "shortlist",
        "dismiss",
        "skip",
    ]

    metadata: dict[str, Any] = Field(default_factory=dict)


class RecommendationRequest(BaseModel):
    session_id: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


# ---------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------

@app.get("/health")
def health() -> dict[str, Any]:
    model_available = True

    try:
        model = load_model()
        model_version = model.get("model_version")
    except Exception:
        model_available = False
        model_version = None

    return {
        "status": "ok",
        "service": "task07_activation_onboarding",
        "model_available": model_available,
        "model_version": model_version,
        "active_sessions": len(SESSIONS),
        "live_event_log": str(
            LIVE_EVENTS_PATH.relative_to(ROOT)
        ),
    }


# ---------------------------------------------------------------------
# Fresh onboarding
# ---------------------------------------------------------------------

@app.post("/onboarding")
def onboarding(
    request: OnboardingRequest,
) -> dict[str, Any]:

    candidate = find_candidate(
        request.candidate_id
    )

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found.",
        )

    valid, errors = validate_candidate(candidate)

    if not valid:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Candidate profile failed validation.",
                "errors": errors,
            },
        )

    session_id = str(uuid.uuid4())

    group = assign_experiment_group(
        session_id,
        request.experiment_id,
    )

    session = {
        "session_id": session_id,
        "candidate_id": request.candidate_id,
        "experiment_id": request.experiment_id,
        "experiment_group": group,
        "created_at": utc_now(),
    }

    SESSIONS[session_id] = session

    return {
        "status": "ONBOARDING_STARTED",
        "session_id": session_id,
        "candidate_id": request.candidate_id,
        "experiment_id": request.experiment_id,
        "experiment_group": group,
        "message": (
            "Fresh onboarding session created and randomly "
            "assigned to an experiment group."
        ),
    }


# ---------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------

@app.post("/recommendations")
def get_recommendations(
    request: RecommendationRequest,
) -> dict[str, Any]:

    session = SESSIONS.get(request.session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Start onboarding first.",
        )

    if session["candidate_id"] != request.candidate_id:
        raise HTTPException(
            status_code=400,
            detail="Candidate does not belong to this session.",
        )

    candidate = find_candidate(
        request.candidate_id
    )

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found.",
        )

    jobs = load_jobs()

    group = session["experiment_group"]

    model_available = True

    try:
        load_model()
    except Exception:
        model_available = False

    if group == "control":
        results = rank_popularity(
            jobs,
            top_k=request.top_k,
        )
        strategy = "popularity_baseline"

    else:
        if model_available:
            results = recommend(
                candidate,
                jobs,
                top_k=request.top_k,
                epsilon=0.10,
            )
            strategy = "trained_cold_start_model"

        else:
            results = popularity_fallback(
                jobs,
                top_k=request.top_k,
                reason="MODEL_UNAVAILABLE",
            )
            strategy = "safe_popularity_fallback"

    # Record an impression for every recommendation displayed.
    for position, item in enumerate(results, start=1):
        create_event(
            candidate_id=request.candidate_id,
            job_id=str(item["job_id"]),
            event_type="impression",
            experiment_id=session["experiment_id"],
            experiment_group=group,
            session_id=request.session_id,
            metadata={
                "position": position,
                "strategy": strategy,
                "model_available": model_available,
            },
        )

    return {
        "status": "RECOMMENDATIONS_READY",
        "session_id": request.session_id,
        "candidate_id": request.candidate_id,
        "experiment_id": session["experiment_id"],
        "experiment_group": group,
        "strategy": strategy,
        "model_available": model_available,
        "recommendations": results,
    }


# ---------------------------------------------------------------------
# Event capture
# ---------------------------------------------------------------------

@app.post("/events")
def record_event(
    request: EventRequest,
) -> dict[str, Any]:

    session = SESSIONS.get(request.session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    if session["candidate_id"] != request.candidate_id:
        raise HTTPException(
            status_code=400,
            detail="Candidate does not belong to this session.",
        )

    event = create_event(
        candidate_id=request.candidate_id,
        job_id=request.job_id,
        event_type=request.event_type,
        experiment_id=session["experiment_id"],
        experiment_group=session["experiment_group"],
        session_id=request.session_id,
        metadata=request.metadata,
    )

    return {
        "status": "EVENT_RECORDED",
        "event": event,
    }


# ---------------------------------------------------------------------
# Live metrics
# ---------------------------------------------------------------------

@app.get("/experiment/events")
def get_live_events() -> dict[str, Any]:

    if not LIVE_EVENTS_PATH.exists():
        events = []
    else:
        try:
            events = load_json(LIVE_EVENTS_PATH)
        except Exception:
            events = []

    return {
        "event_count": len(events),
        "production_data": False,
        "events": events,
    }


@app.get("/experiment/summary")
def experiment_summary() -> dict[str, Any]:

    if not LIVE_EVENTS_PATH.exists():
        events = []
    else:
        try:
            events = load_json(LIVE_EVENTS_PATH)
        except Exception:
            events = []

    groups = {
        "control": [],
        "treatment": [],
    }

    for event in events:
        group = event.get("experiment_group")

        if group in groups:
            groups[group].append(event)

    def metrics(group_events: list[dict[str, Any]]) -> dict[str, Any]:

        candidate_ids = {
            event["candidate_id"]
            for event in group_events
        }

        impressions = {
            event["candidate_id"]
            for event in group_events
            if event["event_type"] == "impression"
        }

        clicks = {
            event["candidate_id"]
            for event in group_events
            if event["event_type"] == "click"
        }

        applies = {
            event["candidate_id"]
            for event in group_events
            if event["event_type"] == "apply"
        }

        return {
            "unique_candidates": len(candidate_ids),
            "impression_users": len(impressions),
            "click_users": len(clicks),
            "apply_users": len(applies),
            "activation_rate": (
                len(applies) / len(candidate_ids)
                if candidate_ids
                else 0.0
            ),
            "click_rate": (
                len(clicks) / len(candidate_ids)
                if candidate_ids
                else 0.0
            ),
        }

    return {
        "experiment_id": "task07_activation_v1",
        "production_data": False,
        "control": metrics(groups["control"]),
        "treatment": metrics(groups["treatment"]),
        "note": (
            "These are locally captured live API events, not "
            "production traffic. Do not report them as production lift."
        ),
    }


# ---------------------------------------------------------------------
# Model-unavailable / fallback evidence
# ---------------------------------------------------------------------

@app.get("/fallback-test")
def fallback_test() -> dict[str, Any]:

    jobs = load_jobs()

    fallback = popularity_fallback(
        jobs,
        top_k=5,
        reason="MODEL_UNAVAILABLE_TEST",
    )

    return {
        "status": "FALLBACK_AVAILABLE",
        "reason": "MODEL_UNAVAILABLE_TEST",
        "recommendations": fallback,
    }