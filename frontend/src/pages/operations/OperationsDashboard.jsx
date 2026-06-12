import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, Line } from "react-chartjs-2";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";
import { BedDouble, BellRing, ShieldAlert, Workflow } from "lucide-react";
import { operationsApi } from "../../api/operations";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { StatCard } from "../../components/shared/StatCard";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Tooltip, Legend);

export function OperationsDashboard() {
  const [summary, setSummary] = useState({
    total_beds: 0,
    available_beds: 0,
    occupied_beds: 0,
    icu_occupancy: 0,
    resource_usage: {},
    staff_available: 0,
    emergency_alerts: 0,
  });
  const [alerts, setAlerts] = useState([]);
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    Promise.all([operationsApi.summary(), operationsApi.alerts(), operationsApi.optimizationRecommendations()]).then(
      ([summaryRes, alertsRes, recRes]) => {
        setSummary(summaryRes.data);
        setAlerts(alertsRes.data);
        setRecommendations(recRes.data);
      },
    );
  }, []);

  const resourceLabels = Object.keys(summary.resource_usage || {});
  const resourceValues = Object.values(summary.resource_usage || {});

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Hospital operations center"
        subtitle="Beds, staff, resources, forecasts, and emergency signals in one command-grade workspace."
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Beds" value={summary.total_beds} accent="brand" icon={BedDouble} />
        <StatCard label="Available Beds" value={summary.available_beds} accent="emerald" icon={Workflow} />
        <StatCard label="ICU Occupancy" value={`${summary.icu_occupancy}%`} accent="violet" icon={ShieldAlert} />
        <StatCard label="Staff Available" value={summary.staff_available} accent="medical" icon={BellRing} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <h3 className="mb-4 text-xl font-semibold text-slate-950">Resource usage</h3>
          <Bar
            data={{
              labels: resourceLabels,
              datasets: [{ label: "In Use", data: resourceValues, backgroundColor: "#2563eb", borderRadius: 16 }],
            }}
            options={{ responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { beginAtZero: true } } }}
          />
        </Card>
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-xl font-semibold text-slate-950">Emergency alerts</h3>
            <Badge tone={alerts.length ? "warning" : "success"}>{alerts.length ? `${alerts.length} active` : "Clear"}</Badge>
          </div>
          <div className="space-y-3">
            {alerts.slice(0, 5).map((alert) => (
              <div key={alert.alert_id} className="flex items-center justify-between rounded-[1.5rem] border border-slate-200/70 bg-slate-50/70 p-4">
                <div>
                  <p className="font-semibold text-slate-950">{alert.alert_type}</p>
                  <p className="text-sm text-slate-500">{alert.recipient}</p>
                </div>
                <Badge tone={alert.severity === "Critical" ? "danger" : "warning"}>{alert.severity}</Badge>
              </div>
            ))}
            {!alerts.length ? <p className="text-sm text-slate-500">No active alerts.</p> : null}
          </div>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {recommendations.slice(0, 4).map((item) => (
          <Card key={item.recommendation_id}>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-700">{item.recommendation_type}</p>
            <h3 className="mt-2 text-lg font-semibold text-slate-950">{item.title}</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">{item.message}</p>
          </Card>
        ))}
      </div>

      <Card>
        <div className="mb-5 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Forecast readiness</p>
            <h3 className="mt-2 text-xl font-semibold text-slate-950">Operational trend</h3>
          </div>
          <Badge tone="info">Live</Badge>
        </div>
        <Line
          data={{
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            datasets: [
              {
                label: "Alert volume",
                data: [4, 6, 5, 7, 4, 3],
                borderColor: "#0891b2",
                backgroundColor: "rgba(8, 145, 178, 0.12)",
                tension: 0.45,
              },
            ],
          }}
          options={{ responsive: true, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { beginAtZero: true } } }}
        />
      </Card>

      <Card>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/operations/beds">
            Beds
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/operations/wards">
            Wards
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/operations/resources">
            Resources
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/operations/forecast">
            Forecasts
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/operations/staff">
            Staff
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/operations/scheduling">
            Scheduling
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/operations/emergency">
            Emergency
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/operations/notifications">
            Notifications
          </Link>
        </div>
      </Card>
    </div>
  );
}
