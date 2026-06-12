import { useEffect, useState } from "react";
import { assistantApi } from "../../api/assistant";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { StatCard } from "../../components/shared/StatCard";
import { Card } from "../../components/ui/Card";
import { Disclaimer } from "../../components/ai/Disclaimer";

export function ExecutiveInsightsPage() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    assistantApi.executiveInsights().then((res) => setSummary(res.data));
  }, []);

  return (
    <div className="space-y-6">
      <SectionHeader title="Executive Insights Dashboard" subtitle="Automated narratives for occupancy, resources, disease trends, and staffing." />
      <Disclaimer />
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Confidence" value={summary ? `${Math.round(summary.confidence_score * 100)}%` : "0%"} />
        <StatCard label="Occupancy" value={summary?.occupancy_trend ? "Live" : "Pending"} />
        <StatCard label="Staff Performance" value={summary?.staff_performance ? "Tracked" : "Pending"} />
      </div>
      {summary ? (
        <div className="grid gap-4 xl:grid-cols-2">
          <Card><h3 className="text-lg font-semibold text-slate-900">Occupancy Trend</h3><p className="mt-2 text-sm text-slate-600">{summary.occupancy_trend}</p></Card>
          <Card><h3 className="text-lg font-semibold text-slate-900">Resource Utilization</h3><p className="mt-2 text-sm text-slate-600">{summary.resource_utilization}</p></Card>
          <Card><h3 className="text-lg font-semibold text-slate-900">Disease Trend</h3><p className="mt-2 text-sm text-slate-600">{summary.disease_trend}</p></Card>
          <Card><h3 className="text-lg font-semibold text-slate-900">Revenue Trend</h3><p className="mt-2 text-sm text-slate-600">{summary.revenue_trend}</p></Card>
          <Card><h3 className="text-lg font-semibold text-slate-900">Staff Performance</h3><p className="mt-2 text-sm text-slate-600">{summary.staff_performance}</p></Card>
          <Card><h3 className="text-lg font-semibold text-slate-900">Narrative</h3><p className="mt-2 text-sm text-slate-600">{summary.narrative}</p></Card>
        </div>
      ) : null}
    </div>
  );
}

