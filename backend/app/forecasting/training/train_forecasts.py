from __future__ import annotations

from app.forecasting.training.pipeline import ForecastTrainer


def main() -> None:
    trainer = ForecastTrainer()
    sample_series = [42, 44, 43, 46, 47, 48, 49, 51, 53, 54, 56, 57, 58, 60]
    artifacts = trainer.train(sample_series, "Ventilators")
    for artifact in artifacts:
        print(f"{artifact.model_name}: saved to {artifact.path} with metrics {artifact.metrics}")


if __name__ == "__main__":
    main()

