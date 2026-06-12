import { useEffect, useState } from "react";
import { operationsApi } from "../../api/operations";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";

export function StaffPage() {
  const [staff, setStaff] = useState([]);

  useEffect(() => {
    operationsApi.staff().then((res) => setStaff(res.data));
  }, []);

  const columns = [
    { key: "staff_id", label: "ID" },
    { key: "name", label: "Name" },
    { key: "role", label: "Role" },
    { key: "department", label: "Department" },
    { key: "shift", label: "Shift" },
    { key: "status", label: "Status" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Staff Dashboard" subtitle="Staff directory and shift awareness." />
      <DataTable columns={columns} rows={staff} emptyText="No staff found." />
    </div>
  );
}

