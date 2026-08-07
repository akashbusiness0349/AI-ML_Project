"""
Data Module
-----------
Responsible for loading and splitting the dataset.
"""

import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from src.config import CONFIG


def load_data():
    """
    Load the Iris dataset and return a DataFrame.
    """

    iris = load_iris()

    df = pd.DataFrame(
        iris.data,
        columns=iris.feature_names
    )

    df[CONFIG["target_column"]] = iris.target

    return df


def split_data(df):
    """
    Split data into train, validation and test sets.
    """

    X = df.drop(CONFIG["target_column"], axis=1)
    y = df[CONFIG["target_column"]]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=CONFIG["test_size"] + CONFIG["validation_size"],
        random_state=CONFIG["random_seed"],
        stratify=y,
    )

    validation_ratio = CONFIG["validation_size"] / (
        CONFIG["test_size"] + CONFIG["validation_size"]
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=1 - validation_ratio,
        random_state=CONFIG["random_seed"],
        stratify=y_temp,
    )

    return X_train, X_val, X_test, y_train, y_val, y_test