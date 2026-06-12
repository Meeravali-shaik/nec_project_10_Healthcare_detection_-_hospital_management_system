import { useEffect, useState } from "react";
import { ehrApi } from "../../api/ehr";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { Select } from "../../components/ui/Select";
import { DataTable } from "../../components/shared/DataTable";
import { SectionHeader } from "../../components/shared/SectionHeader";

const emptyForm = { patient_id: "", report_type: "Blood Test", description: "", file: null };

async function downloadBlob(request, filename) {
  const response = await request;
  const blob = new Blob([response.data], { type: response.headers["content-type"] || "application/octet-stream" });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  window.URL.revokeObjectURL(url);
}

export function LabReportsPage() {
  const { user } = useAuth();
  const canEdit = ["Admin", "Hospital Staff"].includes(user?.role);
  const [items, setItems] = useState([]);
  const [pageInfo, setPageInfo] = useState({ page: 1, size: 10, total: 0, pages: 0 });
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(emptyForm);

  const load = async (page = 1) => {
    const { data } = await ehrApi.labReports({ search, page, size: pageInfo.size });
    setItems(data.items);
    setPageInfo(data.meta);
  };

  useEffect(() => {
    load(1);
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("patient_id", form.patient_id);
    formData.append("report_type", form.report_type);
    if (form.description) formData.append("description", form.description);
    formData.append("upload", form.file);
    await ehrApi.createLabReport(formData);
    setForm(emptyForm);
    await load(pageInfo.page);
  };

  const columns = [
    { key: "report_id", label: "ID" },
    { key: "patient_id", label: "Patient" },
    { key: "report_type", label: "Type" },
    { key: "file_name", label: "File" },
    { key: "upload_date", label: "Uploaded" },
  ];
  columns.push({
    key: "actions",
    label: "Actions",
    render: (row) => (
      <button
        type="button"
        className="font-medium text-brand-700 hover:underline"
        onClick={() => downloadBlob(ehrApi.downloadLabReport(row.report_id), row.file_name)}
      >
        Download
      </button>
    ),
  });

  return (
    <div className="space-y-6">
      <SectionHeader title="Lab Reports" subtitle="Secure upload, download, and file categorization." />
      <Card>
        <div className="flex gap-3">
          <Input placeholder="Search reports" value={search} onChange={(e) => setSearch(e.target.value)} />
          <Button type="button" onClick={() => load(1)}>
            Search
          </Button>
        </div>
      </Card>
      {canEdit ? (
        <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input placeholder="Patient ID" type="number" value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} />
          <Select value={form.report_type} onChange={(e) => setForm({ ...form, report_type: e.target.value })}>
            <option>Blood Test</option>
            <option>Urine Test</option>
            <option>ECG</option>
            <option>MRI</option>
            <option>CT Scan</option>
            <option>X-Ray</option>
            <option>Other</option>
          </Select>
          <Textarea placeholder="Description" rows="2" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <Input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={(e) => setForm({ ...form, file: e.target.files?.[0] || null })} />
          <div className="md:col-span-2">
            <Button type="submit">Upload Report</Button>
          </div>
        </form>
        </Card>
      ) : null}
      <DataTable columns={columns} rows={items} emptyText="No lab reports found." />
      <div className="flex items-center justify-between">
        <Button type="button" variant="secondary" disabled={pageInfo.page <= 1} onClick={() => load(pageInfo.page - 1)}>
          Previous
        </Button>
        <p className="text-sm text-slate-500">
          Page {pageInfo.page} of {pageInfo.pages || 1}
        </p>
        <Button type="button" variant="secondary" disabled={pageInfo.page >= pageInfo.pages} onClick={() => load(pageInfo.page + 1)}>
          Next
        </Button>
      </div>
    </div>
  );
}
