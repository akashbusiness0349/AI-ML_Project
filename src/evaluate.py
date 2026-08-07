from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


def evaluate_model(model, X, y):
    """
    Returns model accuracy.
    """
    predictions = model.predict(X)
    accuracy = accuracy_score(y, predictions)
    return accuracy


def detailed_evaluation(model, X, y):
    """
    Returns predictions, confusion matrix and classification report.
    """
    predictions = model.predict(X)

    cm = confusion_matrix(y, predictions)

    report = classification_report(y, predictions)

    return predictions, cm, report