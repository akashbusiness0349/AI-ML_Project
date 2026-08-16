
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

from fastapi import FastAPI
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path("/home/akash/Projects/Altrodav")
MODEL_PATH = PROJECT_ROOT / "models" / "task19_iris_pipeline_v1.joblib"

# ---------------------------------------------------------
# Model
# ---------------------------------------------------------

model = joblib.load(MODEL_PATH)

# ---------------------------------------------------------
# FastAPI
# ---------------------------------------------------------

app = FastAPI(
    title="Task 19 Iris Prediction API",
    version="v1"
)


# ---------------------------------------------------------
# Input schema
# ---------------------------------------------------------

class IrisInput(BaseModel):

    sepal_length: float = Field(..., gt=0)
    sepal_width: float = Field(..., gt=0)
    petal_length: float = Field(..., gt=0)
    petal_width: float = Field(..., gt=0)


# ---------------------------------------------------------
# Prediction endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_version": "v1"
    }


@app.post("/predict")
def predict(data: IrisInput):

    input_data = pd.DataFrame(
        [[
            data.sepal_length,
            data.sepal_width,
            data.petal_length,
            data.petal_width
        ]],
        columns=[
            "sepal length (cm)",
            "sepal width (cm)",
            "petal length (cm)",
            "petal width (cm)"
        ]
    )

    prediction = int(
        model.predict(input_data)[0]
    )

    class_names = [
        "setosa",
        "versicolor",
        "virginica"
    ]

    return {
        "predicted_class_id": prediction,
        "predicted_class": class_names[prediction],
        "model_version": "v1"
    }
