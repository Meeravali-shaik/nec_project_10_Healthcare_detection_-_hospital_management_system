import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, Line } from "react-chartjs-2";
import {
  CategoryScale,
  Chart as ChartJS,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Activity, BrainCircuit, ShieldAlert, Sparkles } from "lucide-react";
import { aiApi } from "../../api/ai";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { StatCard } from "../../components/shared/StatCard";
import { Card } from "../../components/ui/Card";
import { Disclaimer } from "../../components/ai/Disclaimer";
import { Badge } from "../../components/ui/Badge";

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

export function AiDashboard() {
  const [summary, setSummary] = useState({
    total_predictions: 0,
    top_disease: null,
    high_risk_patients: 0,
    avg_risk_score: 0,
    disease_distribution: {},
  });

  useEffect(() => {
    aiApi.summary().then((res) => setSummary(res.data));
  }, []);

  const labels = Object.keys(summary.disease_distribution || {});
  const values = Object.values(summary.disease_distribution || {});

  return (
    <div className="space-y-6">
      <SectionHeader
        title="AI intelligence studio"
        subtitle="Predictive analytics, decision support, and risk visibility designed for clinical trust and executive clarity."
      />
      <Disclaimer />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Predictions" value={summary.total_predictions} accent="brand" icon={Activity} trend="Model usage" />
        <StatCard label="High Risk Patients" value={summary.high_risk_patients} accent="violet" icon={ShieldAlert} trend="Watchlist count" />
        <StatCard label="Average Risk Score" value={summary.avg_risk_score} accent="medical" icon={BrainCircuit} trend="System average" />
        <StatCard label="Top Disease" value={summary.top_disease || "N/A"} accent="emerald" icon={Sparkles} trend="Most surfaced" />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Distribution</p>
              <h3 className="mt-2 text-xl font-semibold text-slate-950">Disease signals</h3>
            </div>
            <Badge tone="info">Interactive</Badge>
          </div>
          <Bar
            data={{
              labels,
              datasets: [
                {
                  label: "Predictions",
                  data: values,
                  backgroundColor: "#2563eb",
                  borderRadius: 16,
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: { legend: { display: false } },
              scales: { x: { grid: { display: false } }, y: { beginAtZero: true } },
            }}
          />
        </Card>

        <Card>
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Risk trend</p>
              <h3 className="mt-2 text-xl font-semibold text-slate-950">Average score over time</h3>
            </div>
            <Badge tone="success">Stable</Badge>
          </div>
          <Line
            data={{
              labels: ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6"],
              datasets: [
                {
                  label: "Risk score",
                  data: [42, 44, 41, 39, 38, 36],
                  borderColor: "#0891b2",
                  backgroundColor: "rgba(8, 145, 178, 0.12)",
                  tension: 0.45,
                  pointRadius: 3,
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: { legend: { display: false } },
              scales: { x: { grid: { display: false } }, y: { beginAtZero: true, max: 100 } },
            }}
          />
        </Card>
      </div>

      <Card>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/ai/disease-prediction">
            Disease Prediction
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/ai/outcome-prediction">
            Outcome Prediction
          </Link>
          <Link
            className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100"
            to="/ai/treatment-recommendation"
          >
            Treatment Recommendation
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-600 px-4 py-3 font-medium text-white transition hover:bg-brand-700" to="/ai/report-analysis">
            Report Analysis
          </Link>
        </div>
      </Card>
    </div>
  );
}
