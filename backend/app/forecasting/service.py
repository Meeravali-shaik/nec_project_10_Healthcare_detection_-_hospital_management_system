from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

try:
    from statsmodels.tsa.arima.model import ARIMA  # type: ignore
except Exception:  # noqa: BLE001
    ARIMA = None

from app.forecasting.training.pipeline import ForecastTrainer


def _default_model_dir() -> Path:
    # Resolve relative to the backend package so inference works from any CWD.
    return Path(__file__).resolve().parents[2] / "forecast_models"


class ForecastRegistry:
    def __init__(self, model_dir: str | Path = "forecast_models") -> None:
        self.model_dir = Path(model_dir)
        if not self.model_dir.is_absolute():
            self.model_dir = _default_model_dir()
        self._cache: dict[str, list[dict]] = {}

    def _artifact_paths(self, resource_name: str) -> list[Path]:
        if not self.model_dir.exists():
            return []
        return sorted(self.model_dir.glob(f"{resource_name}_*.joblib"))

    def load(self, resource_name: str) -> list[dict]:
        if resource_name not in self._cache:
            artifacts: list[dict] = []
            for path in self._artifact_paths(resource_name):
                artifact = joblib.load(path)
                artifact["artifact_path"] = str(path)
                artifact["loaded_from_disk"] = True
                artifacts.append(artifact)
            self._cache[resource_name] = artifacts
        return self._cache[resource_name]

    def status(self, resource_name: str | None = None) -> list[dict]:
        if resource_name is not None:
            resources = [resource_name]
        else:
            resources = sorted({path.name.split("_", 1)[0] for path in self.model_dir.glob("*.joblib")})
        status: list[dict] = []
        for name in resources:
            for artifact in self.load(name):
                status.append(
                    {
                        "resource_name": name,
                        "artifact_path": artifact["artifact_path"],
                        "loaded_from_disk": bool(artifact.get("loaded_from_disk")),
                        "model_name": artifact.get("model_name"),
                        "mae": artifact.get("metrics", {}).get("mae"),
                        "rmse": artifact.get("metrics", {}).get("rmse"),
                    }
                )
        return status

    def best(self, resource_name: str) -> dict | None:
        artifacts = self.load(resource_name)
        if not artifacts:
            return None
        return sorted(
            artifacts,
            key=lambda artifact: (
                artifact.get("metrics", {}).get("rmse", float("inf")),
                artifact.get("metrics", {}).get("mae", float("inf")),
            ),
        )[0]


class ForecastingService:
    def __init__(self, model_dir: str | Path = "forecast_models") -> None:
        self.model_dir = Path(model_dir)
        if not self.model_dir.is_absolute():
            self.model_dir = _default_model_dir()
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.trainer = ForecastTrainer(output_dir=self.model_dir)
        self.registry = ForecastRegistry(self.model_dir)

    def _history_to_series(self, history: list[dict]) -> pd.Series:
        if not history:
            today = pd.Timestamp.today().normalize()
            dates = pd.date_range(end=today, periods=30, freq="D")
            values = np.linspace(40, 60, num=30) + np.random.default_rng(42).normal(0, 3, size=30)
            return pd.Series(values, index=dates)
        df = pd.DataFrame(history)
        df["usage_date"] = pd.to_datetime(df["usage_date"])
        series = df.groupby("usage_date")["quantity"].sum().sort_index()
        return series

    def train_and_forecast(self, resource_name: str, history: list[dict], horizon_days: int = 7) -> dict:
        series = self._history_to_series(history)
        best_artifact = self.registry.best(resource_name)
        if best_artifact is not None:
            model_name = best_artifact["model_name"]
            forecast_values = list(best_artifact.get("forecast", [])[:horizon_days])
            comparison = self.registry.status(resource_name)
            if len(forecast_values) < horizon_days:
                forecast_values.extend(self._moving_average_forecast(series, horizon_days - len(forecast_values)))
        else:
            artifacts = self.trainer.train(series.tolist(), resource_name)
            if not artifacts:
                forecast_values = self._moving_average_forecast(series, horizon_days)
                comparison = []
                model_name = "heuristic"
            else:
                artifacts = sorted(
                    artifacts,
                    key=lambda artifact: (
                        artifact.metrics.get("rmse", float("inf")),
                        artifact.metrics.get("mae", float("inf")),
                    ),
                )
                best = artifacts[0]
                model_name = best.model_name
                forecast_values = list(best.forecast[:horizon_days])
                comparison = [
                    {
                        "model_name": artifact.model_name,
                        "path": artifact.path,
                        "metrics": artifact.metrics,
                    }
                    for artifact in artifacts
                ]

                if len(forecast_values) < horizon_days:
                    forecast_values.extend(self._moving_average_forecast(series, horizon_days - len(forecast_values)))

        if not forecast_values:
            forecast_values = self._moving_average_forecast(series, horizon_days)

        predictions = []
        for idx, predicted in enumerate(forecast_values, start=1):
            predictions.append(
                {
                    "resource_name": resource_name,
                    "forecast_date": (date.today() + timedelta(days=idx)).isoformat(),
                    "horizon": f"{horizon_days}d",
                    "model_used": model_name,
                    "predicted_demand": round(float(predicted), 2),
                    "lower_bound": round(float(predicted) * 0.9, 2),
                    "upper_bound": round(float(predicted) * 1.1, 2),
                }
            )
        return {"model_used": model_name, "comparison": comparison, "predictions": predictions}

    def _moving_average_forecast(self, series: pd.Series, horizon_days: int) -> list[float]:
        window = series.tail(min(7, len(series)))
        base = float(window.mean()) if not window.empty else 0.0
        trend = float((series.iloc[-1] - series.iloc[0]) / max(len(series) - 1, 1)) if len(series) > 1 else 0.0
        return [max(base + trend * step, 0.0) for step in range(1, horizon_days + 1)]
