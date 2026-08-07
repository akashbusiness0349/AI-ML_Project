"""
Model Module
------------
Responsible for creating and training models.
"""

from sklearn.dummy import DummyClassifier


def build_model():
    """
    Create the baseline model.
    """

    return DummyClassifier(strategy="most_frequent")


def train_model(model, X_train, y_train):
    """
    Train the model.
    """

    model.fit(X_train, y_train)

    return model