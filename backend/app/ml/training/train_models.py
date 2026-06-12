from __future__ import annotations

from app.ml.training.pipeline import DiseaseModelTrainer


def main() -> None:
    trainer = DiseaseModelTrainer()
    artifacts = trainer.train_all()
    for artifact in artifacts:
        print(f"{artifact.model_name}: saved to {artifact.path} with metrics {artifact.metrics}")


if __name__ == "__main__":
    main()

