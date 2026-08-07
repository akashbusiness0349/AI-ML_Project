"""
Evaluation Module
-----------------
Responsible for evaluating model performance.
"""

from sklearn.metrics import accuracy_score


def evaluate_model(model, X_test, y_test):
    """
    Evaluate model accuracy.
    """

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    return accuracy