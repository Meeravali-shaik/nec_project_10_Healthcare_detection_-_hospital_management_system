from __future__ import annotations


def compute_bmi(weight_kg: float | None, height_cm: float | None) -> float | None:
    if not weight_kg or not height_cm:
        return None
    height_m = height_cm / 100
    if height_m <= 0:
        return None
    return round(weight_kg / (height_m * height_m), 2)


def age_group(age: int) -> str:
    if age < 18:
        return "child"
    if age < 40:
        return "adult"
    if age < 60:
        return "middle_aged"
    return "senior"


def symptom_score(symptoms: list[str]) -> float:
    return min(len({s.strip().lower() for s in symptoms if s.strip()}) * 10.0, 100.0)


def encode_family_history(text: str | None) -> int:
    if not text:
        return 0
    keywords = {"diabetes", "heart", "kidney", "liver", "hypertension"}
    return int(any(keyword in text.lower() for keyword in keywords))


def build_features(payload: dict) -> dict:
    symptoms = payload.get("symptoms", [])
    return {
        "age": payload.get("age", 0),
        "gender": payload.get("gender", "unknown").lower(),
        "bmi": payload.get("bmi"),
        "blood_pressure": payload.get("blood_pressure", 0.0),
        "glucose_level": payload.get("glucose_level", 0.0),
        "cholesterol": payload.get("cholesterol", 0.0),
        "family_history_flag": encode_family_history(payload.get("family_history")),
        "symptom_score": symptom_score(symptoms),
        "age_group": age_group(int(payload.get("age", 0) or 0)),
    }

