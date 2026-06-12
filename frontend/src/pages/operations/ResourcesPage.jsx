import { useEffect, useState } from "react";
import { operationsApi } from "../../api/operations";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";

export function ResourcesPage() {
  const [resources, setResources] = useState([]);

  useEffect(() => {
    operationsApi.resources().then((res) => setResources(res.data));
  }, []);

  const columns = [
    { key: "resource_id", label: "ID" },
    { key: "resource_name", label: "Resource" },
    { key: "category", label: "Category" },
    { key: "quantity_available", label: "Available" },
    { key: "quantity_in_use", label: "In Use" },
    { key: "maintenance_status", label: "Maintenance" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Resource Inventory" subtitle="Critical hospital inventory and usage monitoring." />
      <DataTable columns={columns} rows={resources} emptyText="No resources found." />
    </div>
  );
}

