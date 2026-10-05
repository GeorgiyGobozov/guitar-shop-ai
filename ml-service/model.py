"""Обучение и инференс классификатора обращений."""
from __future__ import annotations

import os
import re
import joblib
import pandas as pd
from collections import Counter
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

HERE = os.path.dirname(__file__)
MODEL_DIR = os.path.join(HERE, "artifacts")
DATA_PATH = os.path.join(HERE, "data", "training_data.csv")

TARGETS = ["category", "priority", "problem_type"]


def preprocess(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-zа-яё0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_features() -> FeatureUnion:
    """word (1-2) + char_wb (3-5). Char-ngram'ы вытягивают морфологию русского."""
    return FeatureUnion([
        ("word", TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            min_df=1,
            max_features=8000,
            sublinear_tf=True,
        )),
        ("char", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=2,
            max_features=8000,
            sublinear_tf=True,
        )),
    ])


@dataclass
class Prediction:
    label: str
    confidence: float


class TicketClassifier:
    def __init__(self) -> None:
        self.pipelines: dict[str, Pipeline] = {}
        self._is_fitted = False

    def fit(self, df: pd.DataFrame, verbose: bool = True) -> dict[str, float]:
        df = df.copy()
        df["text"] = df["text"].map(preprocess)

        metrics: dict[str, float] = {}
        for target in TARGETS:
            y_all = df[target]
            counts = Counter(y_all)
            can_stratify = min(counts.values()) >= 2
            stratify_arg = y_all if can_stratify else None

            if verbose and not can_stratify:
                rare = {c: n for c, n in counts.items() if n < 2}
                print(f"[warn] {target}: редкие классы {rare} — стратификация отключена")

            X_train, X_test, y_train, y_test = train_test_split(
                df["text"], y_all,
                test_size=0.2, random_state=42,
                stratify=stratify_arg,
            )

            pipe = Pipeline([
                ("features", build_features()),
                ("clf", LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    C=3.0,
                    solver="liblinear",
                )),
            ])
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            acc = accuracy_score(y_test, preds)
            metrics[target] = acc
            if verbose:
                print(f"\n=== {target} (accuracy = {acc:.3f}) ===")
                print(classification_report(y_test, preds, zero_division=0))
            self.pipelines[target] = pipe
        self._is_fitted = True
        return metrics

    def predict(self, text: str) -> dict[str, Prediction]:
        if not self._is_fitted:
            raise RuntimeError("Модель не обучена")
        text = preprocess(text)
        out: dict[str, Prediction] = {}
        for target, pipe in self.pipelines.items():
            proba = pipe.predict_proba([text])[0]
            idx = int(proba.argmax())
            out[target] = Prediction(
                label=str(pipe.classes_[idx]),
                confidence=float(proba[idx]),
            )
        return out

    def save(self, path: str = MODEL_DIR) -> None:
        os.makedirs(path, exist_ok=True)
        for target, pipe in self.pipelines.items():
            joblib.dump(pipe, os.path.join(path, f"{target}.joblib"))

    def load(self, path: str = MODEL_DIR) -> None:
        for target in TARGETS:
            f = os.path.join(path, f"{target}.joblib")
            if not os.path.exists(f):
                raise FileNotFoundError(f"Нет модели: {f}")
            self.pipelines[target] = joblib.load(f)
        self._is_fitted = True