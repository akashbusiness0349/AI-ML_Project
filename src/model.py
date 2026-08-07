from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression


def build_baseline():
    """
    Build the baseline Dummy Classifier.
    """
    return DummyClassifier(strategy="most_frequent")


def build_model():
    """
    Build the first real ML model.
    """
    return LogisticRegression(random_state=42, max_iter=200)


def train_model(model, X_train, y_train):
    """
    Train any given model.
    """
    model.fit(X_train, y_train)
    return model