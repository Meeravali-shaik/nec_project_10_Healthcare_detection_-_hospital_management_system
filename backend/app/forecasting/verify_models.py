from __future__ import annotations

import json
import sys

from app.forecasting.service import ForecastingService, ForecastRegistry


def main() -> int:
    registry = ForecastRegistry()
    status = registry.status("Ventilators")
    print(json.dumps({"artifacts": status}, indent=2))

    loaded = [item for item in status if item["loaded_from_disk"]]
    if not loaded:
        print("No trained forecast artifacts were loaded from disk.", file=sys.stderr)
        return 1

    service = ForecastingService()
    result = service.train_and_forecast(
        "Ventilators",
        [
            {"usage_date": "2026-06-01", "quantity": 10},
            {"usage_date": "2026-06-02", "quantity": 12},
            {"usage_date": "2026-06-03", "quantity": 14},
            {"usage_date": "2026-06-04", "quantity": 16},
            {"usage_date": "2026-06-05", "quantity": 18},
            {"usage_date": "2026-06-06", "quantity": 20},
            {"usage_date": "2026-06-07", "quantity": 21},
            {"usage_date": "2026-06-08", "quantity": 22},
        ],
        horizon_days=7,
    )
    print(json.dumps({"forecast": result}, indent=2))
    print(f"Selected model: {result['model_used']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
