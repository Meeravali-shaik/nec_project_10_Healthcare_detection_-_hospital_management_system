from app.forecasting.service import ForecastingService
from app.emergency.service import EmergencyService
from app.forecasting.training.pipeline import ForecastTrainer
from app.optimization.service import OptimizationService
from app.scheduling.service import SchedulingService


def test_emergency_detection_triggers_critical_alert() -> None:
    service = EmergencyService()
    alerts = service.detect_alerts(
        {
            "oxygen_level": 80,
            "icu_occupancy": 96,
            "bed_availability": 5,
            "emergency_patient_arrival": True,
            "equipment_failure": True,
        }
    )
    assert len(alerts) >= 4


def test_staffing_recommendation_returns_shift_allocation() -> None:
    service = SchedulingService()
    result = service.recommend_staffing(
        {
            "patient_load": 120,
            "bed_occupancy": 92,
            "emergency_cases": 12,
            "department_demand": {"ICU": 20, "ER": 15},
        }
    )
    assert result["required_doctors"] >= 1
    assert "morning" in result["shift_allocation"]


def test_optimization_recommendation_rules_trigger() -> None:
    service = OptimizationService()
    recommendations = service.recommend({"icu_occupancy": 95, "oxygen_usage": 90, "emergency_cases": 5})
    assert len(recommendations) >= 3


def test_forecast_trainer_produces_artifacts() -> None:
    trainer = ForecastTrainer(output_dir="C:/tmp/forecast_models_test")
    artifacts = trainer.train([10, 12, 11, 13, 15, 16, 18, 19, 20, 21, 22, 23], "Ventilators")
    assert artifacts
    assert artifacts[0].forecast


def test_forecasting_service_compares_models() -> None:
    service = ForecastingService(model_dir="C:/tmp/forecast_models_service_test")
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
    assert result["model_used"]
    assert result["comparison"]
    assert len(result["predictions"]) == 7
