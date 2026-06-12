from __future__ import annotations

import json
import sys

from app.ml.inference.service import DiseasePredictionService, ModelRegistry


def main() -> int:
    registry = ModelRegistry()
    status = registry.status()
    print(json.dumps({"artifacts": status}, indent=2))

    loaded = [item for item in status if item["loaded_from_disk"] and item["has_pipeline"]]
    if not loaded:
        print("No trained disease model artifacts were loaded from disk.", file=sys.stderr)
        return 1

    sample_payload = {
        "patient_id": 1,
        "age": 56,
        "gender": "male",
        "bmi": 28.4,
        "blood_pressure": 148,
        "glucose_level": 162,
        "cholesterol": 232,
        "family_history": "diabetes",
        "symptoms": ["fatigue", "thirst"],
        "medical_history": "hypertension",
    }
    service = DiseasePredictionService(registry=registry)
    result = service.predict(sample_payload)
    print(json.dumps({"prediction": result}, indent=2))
    print(f"Selected model: {result['model_used']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
