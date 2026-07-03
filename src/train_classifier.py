"""
train_classifier.py
--------------------
Trains a text classification model that predicts the complaint category from
the free-text complaint narrative. This mirrors a real use-case at RBI's
Consumer Education and Protection Department: automatically classifying
incoming complaints so that trends and emerging issues can be tracked
systematically rather than manually.

Pipeline: TF-IDF vectorization -> Logistic Regression (multi-class)

Outputs:
  - models/complaint_classifier.joblib   (trained pipeline: vectorizer + model)
  - outputs/classification_report.txt    (precision/recall/F1 per category)
  - outputs/confusion_matrix.csv
"""

import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

DATA_PATH = "data/complaints.csv"
MODEL_PATH = "models/complaint_classifier.joblib"
REPORT_PATH = "outputs/classification_report.txt"
CONFUSION_PATH = "outputs/confusion_matrix.csv"


def main():
    os.makedirs("models", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["narrative", "category"])

    X = df["narrative"]
    y = df["category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            min_df=2,
        )),
        ("clf", LogisticRegression(max_iter=1000, C=5.0)),
    ])

    print("Training model...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test accuracy: {acc:.4f}")

    report = classification_report(y_test, y_pred)
    print(report)

    with open(REPORT_PATH, "w") as f:
        f.write(f"Test accuracy: {acc:.4f}\n\n")
        f.write(report)

    labels = sorted(y.unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    cm_df.to_csv(CONFUSION_PATH)

    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nSaved model -> {MODEL_PATH}")
    print(f"Saved classification report -> {REPORT_PATH}")
    print(f"Saved confusion matrix -> {CONFUSION_PATH}")

    # Quick sanity-check predictions on a few example complaints
    samples = [
        "Money was deducted from my account through UPI but the transaction failed on my screen.",
        "The bank branch staff was very rude to me and did not resolve my issue.",
        "I am being charged a penalty even though I maintained the minimum balance required.",
    ]
    print("\nSample predictions:")
    for s in samples:
        pred = pipeline.predict([s])[0]
        print(f"  '{s[:60]}...' -> {pred}")


if __name__ == "__main__":
    main()
