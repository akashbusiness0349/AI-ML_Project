# ============================================================
# TASK 20 — FLASK PREDICTION API
# ============================================================

from flask import Flask, request, jsonify
import joblib
import pandas as pd
import time
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path("/home/akash/Projects/Altrodav")

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "task19_iris_pipeline_v1.joblib"
)

MODEL_VERSION = "v1"

FEATURE_NAMES = [
    "sepal length (cm)",
    "sepal width (cm)",
    "petal length (cm)",
    "petal width (cm)"
]

CLASS_NAMES = {
    0: "setosa",
    1: "versicolor",
    2: "virginica"
}


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# LOAD SERIALIZED MODEL
# ============================================================

try:
    model = joblib.load(MODEL_PATH)
    MODEL_LOAD_ERROR = None

except Exception as exc:
    model = None
    MODEL_LOAD_ERROR = str(exc)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():
    """
    Health endpoint for checking whether
    the API and model are available.
    """

    if model is None:
        return jsonify({
            "status": "unhealthy",
            "model_version": MODEL_VERSION,
            "error": MODEL_LOAD_ERROR
        }), 503

    return jsonify({
        "status": "healthy",
        "model_version": MODEL_VERSION,
        "model_loaded": True
    }), 200


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict Iris flower class from four measurements.
    """

    if model is None:
        return jsonify({
            "error": "Model is not available.",
            "model_version": MODEL_VERSION
        }), 503

    try:
        data = request.get_json()

        if data is None:
            return jsonify({
                "error": "Request body must contain valid JSON."
            }), 400

        # ----------------------------------------------------
        # Validate required fields
        # ----------------------------------------------------

        missing_fields = [
            feature
            for feature in FEATURE_NAMES
            if feature not in data
        ]

        if missing_fields:
            return jsonify({
                "error": "Missing required fields.",
                "missing_fields": missing_fields
            }), 400

        # ----------------------------------------------------
        # Convert input values to float
        # ----------------------------------------------------

        values = []

        for feature in FEATURE_NAMES:

            try:
                value = float(data[feature])

            except (TypeError, ValueError):
                return jsonify({
                    "error": f"Invalid numeric value for '{feature}'."
                }), 400

            # Basic validation
            if value < 0:
                return jsonify({
                    "error": f"'{feature}' cannot be negative."
                }), 400

            values.append(value)

        # ----------------------------------------------------
        # Create DataFrame with correct feature names
        # ----------------------------------------------------

        input_data = pd.DataFrame(
            [values],
            columns=FEATURE_NAMES
        )

        # ----------------------------------------------------
        # Prediction + latency measurement
        # ----------------------------------------------------

        start_time = time.perf_counter()

        prediction = model.predict(input_data)

        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        predicted_class = int(prediction[0])

        predicted_name = CLASS_NAMES.get(
            predicted_class,
            "unknown"
        )

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return jsonify({
            "prediction": predicted_class,
            "class_name": predicted_name,
            "model_version": MODEL_VERSION,
            "latency_ms": round(elapsed_ms, 4)
        }), 200

    except Exception as exc:

        return jsonify({
            "error": "Prediction failed.",
            "details": str(exc)
        }), 500


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("TASK 20 — IRIS FLASK API")
    print("=" * 70)

    print("Model:", MODEL_PATH)
    print("Model version:", MODEL_VERSION)

    if model is not None:
        print("Model loading: PASS")
    else:
        print("Model loading: FAIL")
        print("Error:", MODEL_LOAD_ERROR)

    print("\nStarting Flask server...")
    print("Health endpoint : http://127.0.0.1:5000/health")
    print("Prediction endpoint : http://127.0.0.1:5000/predict")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )