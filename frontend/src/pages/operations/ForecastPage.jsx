import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { CategoryScale, Chart as ChartJS, LinearScale, LineElement, PointElement, Tooltip, Legend } from "chart.js";
import { operationsApi } from "../../api/operations";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Button } from "../../components/ui/Button";
import { StatCard } from "../../components/shared/StatCard";

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Tooltip, Legend);

export function ForecastPage() {
  const [resourceName, setResourceName] = useState("Ventilators");
  const [forecast, setForecast] = useState([]);
  const [comparison, setComparison] = useState([]);
  const [modelUsed, setModelUsed] = useState("");

  const load = async () => {
    const [forecastRes, comparisonRes] = await Promise.all([
      operationsApi.forecast(resourceName),
      operationsApi.forecastComparison(resourceName),
    ]);
    setForecast(forecastRes.data.predictions || []);
    setComparison(comparisonRes.data.comparison || []);
    setModelUsed(forecastRes.data.model_used || comparisonRes.data.model_used || "");
  };

  useEffect(() => {
    load();
  }, []);

  const labels = forecast.map((item) => item.forecast_date);
  const values = forecast.map((item) => item.predicted_demand);
  const comparisonRows = comparison.map((item) => ({
    id: item.model_name,
    model_name: item.model_name,
    mae: item.metrics?.mae?.toFixed?.(2) ?? item.metrics?.mae ?? "-",
    rmse: item.metrics?.rmse?.toFixed?.(2) ?? item.metrics?.rmse ?? "-",
    mape: item.metrics?.mape?.toFixed?.(2) ?? item.metrics?.mape ?? "-",
    path: item.path,
  }));

  const comparisonColumns = [
    { key: "model_name", label: "Model" },
    { key: "mae", label: "MAE" },
    { key: "rmse", label: "RMSE" },
    { key: "mape", label: "MAPE" },
    { key: "path", label: "Artifact" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Resource Forecast" subtitle="Predict demand for beds and critical supplies." />
      <Card>
        <div className="flex flex-col gap-3 md:flex-row">
          <Input value={resourceName} onChange={(e) => setResourceName(e.target.value)} />
          <Button type="button" onClick={load}>Run Comparison</Button>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Best Model" value={modelUsed || "Pending"} note="Selected by lowest evaluation error." />
        <StatCard label="Forecast Horizon" value={`${forecast.length} days`} note="Daily demand projection." />
        <StatCard label="Compared Models" value={comparison.length} note="ARIMA, Prophet, XGBoost, LSTM when available." />
      </div>

      <Card>
        <Line
          data={{
            labels,
            datasets: [
              {
                label: "Predicted Demand",
                data: values,
                borderColor: "#2563eb",
                backgroundColor: "rgba(37, 99, 235, 0.12)",
              },
            ],
          }}
        />
      </Card>

      <Card>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">Model Comparison</h3>
        <DataTable columns={comparisonColumns} rows={comparisonRows} emptyText="No comparison data available." />
      </Card>
    </div>
  );
}
