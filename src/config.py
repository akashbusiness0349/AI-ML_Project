from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG = {
    "random_seed": 42,
    "test_size": 0.15,
    "validation_size": 0.15,
    "dataset": "iris",
    "target_column": "target",
    "experiment_log": BASE_DIR / "logs" / "experiment_log.csv"
}