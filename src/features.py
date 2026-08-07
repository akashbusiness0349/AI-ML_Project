from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import joblib


def build_preprocessor(numerical_features):
    """
    Creates a preprocessing pipeline for numerical features.
    """

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler())
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_pipeline, numerical_features)
    ])

    return preprocessor


def fit_preprocessor(preprocessor, X_train):
    """
    Fit the preprocessing pipeline using only training data.
    """
    return preprocessor.fit(X_train)


def transform_data(preprocessor, X):
    """
    Transform any dataset using the fitted preprocessor.
    """
    return preprocessor.transform(X)


def save_preprocessor(preprocessor, path):
    """
    Save the fitted preprocessor for future inference.
    """
    joblib.dump(preprocessor, path)