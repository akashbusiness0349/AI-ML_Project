"""
Task 13 — Model Score Extraction

Validated scoring interface for the binary classification model.
Supports single-record and batch scoring.
"""

from pathlib import Path
from typing import List

import joblib
import pandas as pd
from pydantic import BaseModel, Field, ValidationError


# =========================================================
# PATHS AND MODEL VERSION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "task12_calibrated_model.pkl"
PREPROCESSOR_PATH = BASE_DIR / "models" / "task12_preprocessor.pkl"
THRESHOLD_PATH = BASE_DIR / "models" / "task12_threshold.pkl"

MODEL_VERSION = "task12-calibrated-logistic-v1.0"


# =========================================================
# LOAD MODEL ARTIFACTS
# =========================================================

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)
threshold = float(joblib.load(THRESHOLD_PATH))


# =========================================================
# INPUT CONTRACT
# =========================================================

class ScoreInput(BaseModel):
    sepal_length: float = Field(..., ge=0)
    sepal_width: float = Field(..., ge=0)
    petal_length: float = Field(..., ge=0)
    petal_width: float = Field(..., ge=0)


# =========================================================
# OUTPUT CONTRACT
# =========================================================

class ScoreOutput(BaseModel):
    score: float
    score_meaning: str
    prediction: int
    threshold: float
    model_version: str


# =========================================================
# CONVERT VALIDATED INPUT TO MODEL FORMAT
# =========================================================

def _to_dataframe(inputs: List[ScoreInput]) -> pd.DataFrame:

    return pd.DataFrame([
        {
            "sepal length (cm)": item.sepal_length,
            "sepal width (cm)": item.sepal_width,
            "petal length (cm)": item.petal_length,
            "petal width (cm)": item.petal_width,
        }
        for item in inputs
    ])


# =========================================================
# SINGLE RECORD SCORING
# =========================================================

def predict_single(data: ScoreInput) -> ScoreOutput:
    """
    Generate a score for one validated input record.
    """

    df = _to_dataframe([data])

    processed_data = preprocessor.transform(df)

    probability = float(
        model.predict_proba(processed_data)[0, 1]
    )

    prediction = int(
        probability >= threshold
    )

    return ScoreOutput(
        score=probability,
        score_meaning="Calibrated probability of positive class (class 1)",
        prediction=prediction,
        threshold=threshold,
        model_version=MODEL_VERSION,
    )


# =========================================================
# BATCH SCORING
# =========================================================

def predict_batch(
    data: List[ScoreInput]
) -> List[ScoreOutput]:
    """
    Generate scores for multiple validated input records.
    """

    if not data:
        raise ValueError(
            "Batch input cannot be empty."
        )

    df = _to_dataframe(data)

    processed_data = preprocessor.transform(df)

    probabilities = model.predict_proba(
        processed_data
    )[:, 1]

    results = []

    for probability in probabilities:

        probability = float(probability)

        results.append(
            ScoreOutput(
                score=probability,
                score_meaning=(
                    "Calibrated probability of positive class (class 1)"
                ),
                prediction=int(
                    probability >= threshold
                ),
                threshold=threshold,
                model_version=MODEL_VERSION,
            )
        )

    return results


# =========================================================
# INPUT VALIDATION
# =========================================================

def validate_single(data: dict) -> ScoreInput:
    """
    Validate a raw dictionary against the input contract.
    """

    try:

        return ScoreInput(**data)

    except ValidationError as exc:

        raise ValueError(
            f"Invalid input: {exc}"
        ) from exc