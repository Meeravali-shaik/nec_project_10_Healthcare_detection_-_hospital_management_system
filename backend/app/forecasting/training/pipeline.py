from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import joblib
import numpy as np

try:
    from prophet import Prophet  # type: ignore
except Exception:  # noqa: BLE001
    Prophet = None

try:
    from xgboost import XGBRegressor  # type: ignore
except Exception:  # noqa: BLE001
    XGBRegressor = None

try:
    from tensorflow.keras import Sequential  # type: ignore
    from tensorflow.keras.layers import Dense, LSTM  # type: ignore
except Exception:  # noqa: BLE001
    Sequential = None
    Dense = None
    LSTM = None


@dataclass
class ForecastArtifact:
    model_name: str
    path: str
    metrics: dict
    forecast: list[float]


class ForecastTrainer:
    def __init__(self, output_dir: str | Path = "forecast_models") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def train(self, series: list[float], resource_name: str) -> list[ForecastArtifact]:
        artifacts: list[ForecastArtifact] = []
        forecasts = {
            "arima": self._forecast_arima(series),
            "prophet": self._forecast_prophet(series),
            "xgboost": self._forecast_xgboost(series),
            "lstm": self._forecast_lstm(series),
        }
        actual = np.asarray(series[-7:] or series, dtype=float)
        actual_mean = float(actual.mean()) if len(actual) else 0.0
        for model_name, forecast in forecasts.items():
            if forecast is None:
                continue
            metrics = {
                "mae": float(np.mean(np.abs(np.asarray(forecast) - actual_mean))),
                "rmse": float(np.sqrt(np.mean((np.asarray(forecast) - actual_mean) ** 2))),
                "mape": float(np.mean(np.abs((np.asarray(forecast) - actual_mean) / max(actual_mean, 1e-6))) * 100),
            }
            path = self.output_dir / f"{resource_name}_{model_name}.joblib"
            joblib.dump({"model_name": model_name, "forecast": forecast, "metrics": metrics}, path)
            artifacts.append(ForecastArtifact(model_name=model_name, path=str(path), metrics=metrics, forecast=list(forecast)))
        return artifacts

    def _forecast_arima(self, series: list[float]) -> list[float] | None:
        if len(series) < 7:
            return self._moving_average(series)
        try:
            from statsmodels.tsa.arima.model import ARIMA  # type: ignore

            model = ARIMA(series, order=(1, 1, 1)).fit()
            return [float(value) for value in model.forecast(steps=7)]
        except Exception:  # noqa: BLE001
            return self._moving_average(series)

    def _forecast_prophet(self, series: list[float]) -> list[float] | None:
        if Prophet is None:
            return self._moving_average(series)
        try:
            import pandas as pd

            df = pd.DataFrame({"ds": pd.date_range(end=date.today(), periods=len(series)), "y": series})
            model = Prophet()
            model.fit(df)
            future = model.make_future_dataframe(periods=7)
            forecast = model.predict(future).tail(7)["yhat"].tolist()
            return [float(value) for value in forecast]
        except Exception:  # noqa: BLE001
            return self._moving_average(series)

    def _forecast_xgboost(self, series: list[float]) -> list[float] | None:
        if XGBRegressor is None or len(series) < 10:
            return self._moving_average(series)
        try:
            X = np.arange(len(series)).reshape(-1, 1)
            y = np.asarray(series, dtype=float)
            model = XGBRegressor(n_estimators=50, max_depth=4, random_state=42)
            model.fit(X, y)
            future_X = np.arange(len(series), len(series) + 7).reshape(-1, 1)
            return [float(value) for value in model.predict(future_X)]
        except Exception:  # noqa: BLE001
            return self._moving_average(series)

    def _forecast_lstm(self, series: list[float]) -> list[float] | None:
        if Sequential is None or len(series) < 14:
            return self._moving_average(series)
        try:
            import numpy as np

            X = np.asarray(series, dtype=float)
            X = (X - X.mean()) / max(X.std(), 1e-6)
            X = X.reshape((-1, 1, 1))
            model = Sequential([LSTM(16, input_shape=(1, 1)), Dense(1)])
            model.compile(optimizer="adam", loss="mse")
            model.fit(X[:-1], X[1:], epochs=5, verbose=0)
            last = X[-1:].copy()
            preds = []
            for _ in range(7):
                pred = float(model.predict(last, verbose=0).ravel()[0])
                preds.append(pred * max(np.asarray(series).std(), 1e-6) + np.asarray(series).mean())
                last = np.asarray([[[pred]]])
            return preds
        except Exception:  # noqa: BLE001
            return self._moving_average(series)

    def _moving_average(self, series: list[float]) -> list[float]:
        if not series:
            return [0.0] * 7
        window = series[-7:]
        base = float(sum(window) / len(window))
        trend = 0.0 if len(series) < 2 else (series[-1] - series[0]) / max(len(series) - 1, 1)
        return [max(base + trend * step, 0.0) for step in range(1, 8)]
