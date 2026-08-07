from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_curve,
    auc,
    precision_recall_curve
)


def evaluate_model(model, X, y):
    predictions = model.predict(X)
    accuracy = accuracy_score(y, predictions)
    return accuracy


def detailed_evaluation(model, X, y):
    predictions = model.predict(X)

    cm = confusion_matrix(y, predictions)

    report = classification_report(y, predictions)

    return predictions, cm, report


def binary_metrics(model, X, y):
    predictions = model.predict(X)

    probabilities = model.predict_proba(X)[:, 1]

    precision = precision_score(y, predictions)

    recall = recall_score(y, predictions)

    f1 = f1_score(y, predictions)

    fpr, tpr, roc_thresholds = roc_curve(y, probabilities)

    roc_auc = auc(fpr, tpr)

    pr_precision, pr_recall, pr_thresholds = precision_recall_curve(
        y,
        probabilities
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "tpr": tpr,
        "roc_auc": roc_auc,
        "pr_precision": pr_precision,
        "pr_recall": pr_recall,
        "probabilities": probabilities
    }