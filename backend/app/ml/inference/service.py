from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from app.ml.constants import SUPPORTED_DISEASES
from app.ml.preprocessing.feature_engineering import build_features


def _default_model_dir() -> Path:
    # Resolve relative to the backend package so inference works from any CWD.
    return Path(__file__).resolve().parents[3] / "ml_models"


class ModelRegistry:
    def __init__(self, model_dir: str | Path = "ml_models") -> None:
        self.model_dir = Path(model_dir)
        if not self.model_dir.is_absolute():
            self.model_dir = _default_model_dir()
        self._cache: dict[str, dict] = {}

    def load(self, model_name: str) -> dict:
        if model_name not in self._cache:
            path = self.model_dir / f"{model_name}.joblib"
            if path.exists():
                artifact = joblib.load(path)
                artifact["artifact_path"] = str(path)
                artifact["loaded_from_disk"] = True
                self._cache[model_name] = artifact
            else:
                self._cache[model_name] = {
                    "model_name": model_name,
                    "pipeline": None,
                    "metrics": {},
                    "classes": SUPPORTED_DISEASES,
                    "artifact_path": str(path),
                    "loaded_from_disk": False,
                }
        return self._cache[model_name]

    def status(self) -> list[dict]:
        return [
            {
                "model_name": name,
                "artifact_path": artifact["artifact_path"],
                "loaded_from_disk": bool(artifact.get("loaded_from_disk")),
                "has_pipeline": artifact.get("pipeline") is not None,
                "accuracy": artifact.get("metrics", {}).get("accuracy"),
            }
            for name, artifact in ((name, self.load(name)) for name in ("xgboost", "random_forest", "logistic_regression", "decision_tree"))
        ]

    def best_model_name(self) -> str:
        candidates = [self.load(name) for name in ("xgboost", "random_forest", "logistic_regression", "decision_tree")]
        ranked = sorted(candidates, key=lambda item: item.get("metrics", {}).get("accuracy", 0), reverse=True)
        return ranked[0]["model_name"]


class DiseasePredictionService:
    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry()

    def predict(self, payload: dict) -> dict:
        features = build_features(payload)
        model_name = self.registry.best_model_name()
        artifact = self.registry.load(model_name)
        pipeline = artifact.get("pipeline")

        if pipeline is None:
            disease = self._heuristic_disease(payload)
            confidence = 0.61
        else:
            feature_frame = pd.DataFrame([features])
            prediction = pipeline.predict(feature_frame)[0]
            label_encoder = artifact.get("label_encoder")
            disease = str(label_encoder.inverse_transform([prediction])[0]) if label_encoder is not None else str(prediction)
            proba = pipeline.predict_proba(feature_frame)[0]
            confidence = float(max(proba))

        risk_score = self._risk_score(payload, disease)
        severity = self._severity_from_risk(risk_score)
        return {
            "model_used": model_name,
            "disease": disease,
            "risk_score": risk_score,
            "confidence_score": confidence,
            "severity_level": severity,
            "input_features": payload,
        }

    def _heuristic_disease(self, payload: dict) -> str:
        glucose = float(payload.get("glucose_level", 0) or 0)
        pressure = float(payload.get("blood_pressure", 0) or 0)
        cholesterol = float(payload.get("cholesterol", 0) or 0)
        bmi = float(payload.get("bmi", 0) or 0)
        age = int(payload.get("age", 0) or 0)

        if glucose > 145:
            return "Diabetes"
        if pressure > 150:
            return "Hypertension"
        if cholesterol > 240:
            return "Heart Disease"
        if age > 65 and bmi > 30:
            return "Kidney Disease"
        return "Liver Disease"

    def _risk_score(self, payload: dict, disease: str) -> float:
        score = 20.0
        score += min(float(payload.get("glucose_level", 0) or 0) / 3, 30)
        score += min(float(payload.get("blood_pressure", 0) or 0) / 6, 20)
        score += min(float(payload.get("cholesterol", 0) or 0) / 10, 15)
        score += min(float(payload.get("bmi", 0) or 0), 10)
        if payload.get("family_history"):
            score += 10
        symptoms = payload.get("symptoms", [])
        score += min(len(symptoms) * 3, 15)
        if disease in {"Diabetes", "Heart Disease", "Kidney Disease"}:
            score += 5
        return round(min(score, 100.0), 2)

    def _severity_from_risk(self, risk_score: float) -> str:
        if risk_score < 25:
            return "Low"
        if risk_score < 50:
            return "Moderate"
        if risk_score < 75:
            return "High"
        return "Critical"


class OutcomePredictionService:
    def predict(self, payload: dict) -> dict:
        severity_map = {"Low": 0.1, "Moderate": 0.35, "High": 0.6, "Critical": 0.85}
        severity_factor = severity_map.get(payload.get("severity", "Moderate"), 0.35)
        age = float(payload.get("age", 0) or 0)
        recovery_probability = round(max(0.05, 1 - severity_factor - (age / 250)), 3)
        readmission_risk = round(min(0.95, severity_factor * 0.75 + len(payload.get("existing_conditions", [])) * 0.05), 3)
        icu_requirement_risk = round(min(0.95, severity_factor * 0.6), 3)
        mortality_risk = round(min(0.95, severity_factor * 0.45), 3)
        expected_length_of_stay = round(2 + severity_factor * 10 + len(payload.get("treatment_history") or "") / 80, 1)
        risk_category = self._category(mortality_risk, readmission_risk)
        return {
            "recovery_probability": recovery_probability,
            "readmission_risk": readmission_risk,
            "icu_requirement_risk": icu_requirement_risk,
            "mortality_risk": mortality_risk,
            "expected_length_of_stay": expected_length_of_stay,
            "risk_category": risk_category,
            "clinical_recommendations": self._recommendations(risk_category, payload.get("disease", "")),
        }

    def _category(self, mortality_risk: float, readmission_risk: float) -> str:
        score = max(mortality_risk, readmission_risk)
        if score < 0.2:
            return "Low"
        if score < 0.4:
            return "Medium"
        if score < 0.7:
            return "High"
        return "Critical"

    def _recommendations(self, category: str, disease: str) -> str:
        if category == "Critical":
            return f"Immediate specialist review recommended for {disease}."
        if category == "High":
            return "Close monitoring and escalation if symptoms worsen."
        if category == "Medium":
            return "Standard follow-up and lifestyle optimization."
        return "Routine follow-up and preventive care."


class ReportAnalysisService:
    ABNORMAL_MARKERS = {
        "hemoglobin": ("low", 12),
        "blood sugar": ("high", 140),
        "glucose": ("high", 140),
        "cholesterol": ("high", 240),
        "creatinine": ("high", 1.3),
    }

    def analyze(self, report_text: str) -> dict:
        lower = report_text.lower()
        identified_values = {}
        abnormal_values = {}
        alerts = []
        for marker, (direction, threshold) in self.ABNORMAL_MARKERS.items():
            if marker in lower:
                identified_values[marker] = {"direction": direction, "threshold": threshold}
                abnormal_values[marker] = {"direction": direction, "threshold": threshold, "flagged": True}
                alerts.append(f"{marker.title()}: {direction}")
        summary = " ".join(
            [
                "Automated analysis completed.",
                "Potential diabetes risk detected." if "blood sugar" in lower or "glucose" in lower else "",
                "Cardiovascular risk indicators present." if "cholesterol" in lower else "",
            ]
        ).strip()
        return {
            "extracted_text": report_text,
            "identified_values": identified_values,
            "abnormal_values": abnormal_values,
            "alert_message": "; ".join(alerts) if alerts else None,
            "summary": summary or "No abnormal values detected.",
        }


class RecommendationEngine:
    def recommend(self, disease: str, symptoms: list[str]) -> dict:
        disease = disease.lower()
        if "diabetes" in disease:
            specialist = "Endocrinologist"
            tests = "HbA1c, fasting glucose, lipid profile"
            lifestyle = "Reduce refined sugar intake, exercise regularly, monitor blood glucose."
            guidance = "Start with diet control and medication review."
            follow_up = "Review in 2-4 weeks."
        elif "heart" in disease:
            specialist = "Cardiologist"
            tests = "ECG, echocardiogram, lipid profile"
            lifestyle = "Low-sodium diet, smoking cessation, walking program."
            guidance = "Evaluate chest pain and blood pressure promptly."
            follow_up = "Cardiology follow-up within 1 week."
        elif "kidney" in disease:
            specialist = "Nephrologist"
            tests = "Creatinine, eGFR, urine analysis"
            lifestyle = "Hydration guidance, sodium reduction, avoid nephrotoxic drugs."
            guidance = "Monitor renal function closely."
            follow_up = "Renal review in 1-2 weeks."
        elif "liver" in disease:
            specialist = "Hepatologist"
            tests = "LFT, hepatitis panel, ultrasound"
            lifestyle = "Avoid alcohol, maintain healthy weight, review hepatotoxic medications."
            guidance = "Assess for liver inflammation and medication effects."
            follow_up = "Follow up after tests."
        else:
            specialist = "Internal Medicine"
            tests = "CBC, metabolic panel"
            lifestyle = "Balanced diet, rest, hydration."
            guidance = "Symptom-based preliminary guidance."
            follow_up = "Primary care follow-up in 1-2 weeks."
        return {
            "recommended_specialist": specialist,
            "suggested_tests": tests,
            "lifestyle_recommendations": lifestyle,
            "preliminary_treatment_guidance": guidance,
            "follow_up_suggestions": follow_up,
            "rule_version": "v1",
        }
