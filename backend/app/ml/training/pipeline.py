from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

try:
    from xgboost import XGBClassifier  # type: ignore
except Exception:  # noqa: BLE001
    XGBClassifier = None

from app.ml.constants import MODEL_NAMES, SUPPORTED_DISEASES
from app.ml.evaluation.metrics import calculate_classification_metrics


@dataclass
class TrainedModelArtifact:
    model_name: str
    metrics: dict
    path: str


class DiseaseModelTrainer:
    def __init__(self, output_dir: str | Path = "ml_models") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _synthetic_dataset(self, n_samples: int = 500) -> pd.DataFrame:
        rng = np.random.default_rng(42)
        data = pd.DataFrame(
            {
                "age": rng.integers(18, 85, size=n_samples),
                "gender": rng.choice(["male", "female"], size=n_samples),
                "bmi": rng.normal(27, 5, size=n_samples).clip(16, 45),
                "blood_pressure": rng.normal(130, 18, size=n_samples).clip(90, 220),
                "glucose_level": rng.normal(120, 35, size=n_samples).clip(60, 300),
                "cholesterol": rng.normal(200, 40, size=n_samples).clip(100, 400),
                "family_history_flag": rng.integers(0, 2, size=n_samples),
                "symptom_score": rng.integers(0, 100, size=n_samples),
                "age_group": rng.choice(["child", "adult", "middle_aged", "senior"], size=n_samples),
            }
        )
        disease_rules = []
        for _, row in data.iterrows():
            if row.glucose_level > 145:
                disease_rules.append("Diabetes")
            elif row.blood_pressure > 150:
                disease_rules.append("Hypertension")
            elif row.cholesterol > 240:
                disease_rules.append("Heart Disease")
            elif row.age > 65 and row.bmi > 30:
                disease_rules.append("Kidney Disease")
            else:
                disease_rules.append(rng.choice(SUPPORTED_DISEASES))
        data["target"] = disease_rules
        return data

    def _build_pipeline(self, model_name: str) -> Pipeline:
        categorical = ["gender", "age_group"]
        numeric = ["age", "bmi", "blood_pressure", "glucose_level", "cholesterol", "family_history_flag", "symptom_score"]
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric),
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ]
        )

        if model_name == "logistic_regression":
            # Keep constructor compatible across scikit-learn versions.
            estimator = LogisticRegression(max_iter=1000)
        elif model_name == "decision_tree":
            estimator = DecisionTreeClassifier(max_depth=8, random_state=42)
        elif model_name == "random_forest":
            estimator = RandomForestClassifier(n_estimators=200, random_state=42)
        elif model_name == "xgboost" and XGBClassifier is not None:
            estimator = XGBClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                objective="multi:softprob",
                num_class=len(SUPPORTED_DISEASES),
                eval_metric="mlogloss",
                random_state=42,
            )
        else:
            raise ValueError(f"Unsupported model: {model_name}")

        return Pipeline([("preprocessor", preprocessor), ("estimator", estimator)])

    def train_all(self) -> list[TrainedModelArtifact]:
        data = self._synthetic_dataset()
        X = data.drop(columns=["target"])
        y = data["target"]
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

        artifacts: list[TrainedModelArtifact] = []
        for model_name in MODEL_NAMES:
            if model_name == "xgboost" and XGBClassifier is None:
                continue
            pipeline = self._build_pipeline(model_name)
            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            y_prob = pipeline.predict_proba(X_test) if hasattr(pipeline, "predict_proba") else None
            metrics = calculate_classification_metrics(y_test, y_pred, y_prob)
            artifact_path = self.output_dir / f"{model_name}.joblib"
            joblib.dump(
                {
                    "model_name": model_name,
                    "pipeline": pipeline,
                    "metrics": metrics.__dict__,
                    "classes": list(label_encoder.classes_),
                    "label_encoder": label_encoder,
                },
                artifact_path,
            )
            artifacts.append(TrainedModelArtifact(model_name=model_name, metrics=metrics.__dict__, path=str(artifact_path)))
        return artifacts
