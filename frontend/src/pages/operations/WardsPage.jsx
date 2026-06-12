import { useEffect, useState } from "react";
import { operationsApi } from "../../api/operations";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";
import { StatCard } from "../../components/shared/StatCard";
import { Card } from "../../components/ui/Card";

export function WardsPage() {
  const [wards, setWards] = useState([]);
  const [analytics, setAnalytics] = useState([]);

  useEffect(() => {
    Promise.all([operationsApi.wards(), operationsApi.wardAnalytics()]).then(([wardsRes, analyticsRes]) => {
      setWards(wardsRes.data);
      setAnalytics(analyticsRes.data);
    });
  }, []);

  const columns = [
    { key: "ward_id", label: "ID" },
    { key: "ward_name", label: "Name" },
    { key: "ward_type", label: "Type" },
    { key: "capacity", label: "Capacity" },
    { key: "occupied_beds", label: "Occupied" },
    { key: "available_beds", label: "Available" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Ward Dashboard" subtitle="Occupancy monitoring and ward capacity tracking." />
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Total Wards" value={wards.length} />
        <StatCard label="High Utilization" value={analytics.filter((ward) => ward.utilization >= 90).length} />
        <StatCard label="Avg Utilization" value={`${analytics.length ? (analytics.reduce((sum, ward) => sum + ward.utilization, 0) / analytics.length).toFixed(1) : "0.0"}%`} />
      </div>
      <DataTable columns={columns} rows={wards} emptyText="No wards found." />
      <Card>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">Ward Analytics</h3>
        <DataTable
          columns={[
            { key: "ward_name", label: "Ward" },
            { key: "ward_type", label: "Type" },
            { key: "capacity", label: "Capacity" },
            { key: "occupied_beds", label: "Occupied" },
            { key: "available_beds", label: "Available" },
            { key: "utilization", label: "Utilization" },
          ]}
          rows={analytics.map((ward) => ({ ...ward, utilization: `${ward.utilization}%` }))}
          emptyText="No analytics available."
        />
      </Card>
    </div>
  );
}
