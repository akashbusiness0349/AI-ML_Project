import os
import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from src.data import load_data, split_data


# -----------------------------
# Create folders if not present
# -----------------------------
os.makedirs("artifacts", exist_ok=True)
os.makedirs("logs", exist_ok=True)


# -----------------------------
# Load dataset
# -----------------------------
df = load_data()

X_train, X_val, X_test, y_train, y_val, y_test = split_data(df)


# -----------------------------
# Build Pipeline
# -----------------------------
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=200, random_state=42))
])


# -----------------------------
# Train
# -----------------------------
pipeline.fit(X_train, y_train)


# -----------------------------
# Predict
# -----------------------------
predictions = pipeline.predict(X_test)


# -----------------------------
# Metrics
# -----------------------------
accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions, average="weighted")
recall = recall_score(y_test, predictions, average="weighted")
f1 = f1_score(y_test, predictions, average="weighted")


# -----------------------------
# Save Model
# -----------------------------
joblib.dump(pipeline, "artifacts/model.pkl")


# -----------------------------
# Save Metrics
# -----------------------------
metrics = pd.DataFrame({
    "Accuracy": [accuracy],
    "Precision": [precision],
    "Recall": [recall],
    "F1 Score": [f1]
})

metrics.to_csv("artifacts/metrics.csv", index=False)


# -----------------------------
# Update Experiment Log
# -----------------------------
log_file = "logs/experiment_log.csv"

new_log = pd.DataFrame({
    "Model": ["Pipeline(LogisticRegression)"],
    "Accuracy": [accuracy]
})

if os.path.exists(log_file):
    old_log = pd.read_csv(log_file)
    old_log = pd.concat([old_log, new_log], ignore_index=True)
    old_log.to_csv(log_file, index=False)
else:
    new_log.to_csv(log_file, index=False)


# -----------------------------
# Summary
# -----------------------------
print("=" * 40)
print("TASK 08 COMPLETED")
print("=" * 40)

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

print("\nModel Saved   : artifacts/model.pkl")
print("Metrics Saved : artifacts/metrics.csv")
print("Experiment Log Updated")