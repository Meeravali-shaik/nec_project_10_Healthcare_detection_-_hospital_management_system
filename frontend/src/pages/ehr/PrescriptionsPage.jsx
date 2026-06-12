import { useEffect, useState } from "react";
import { ehrApi } from "../../api/ehr";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { DataTable } from "../../components/shared/DataTable";
import { SectionHeader } from "../../components/shared/SectionHeader";

const emptyForm = {
  patient_id: "",
  doctor_id: "",
  issue_date: "",
  dosage: "",
  frequency: "",
  duration: "",
  instructions: "",
  medications_text: "",
};

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

function parseMedications(text) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [name = "", dosage = "", frequency = "", duration = "", instructions = ""] = line.split("|").map((item) => item.trim());
      return { name, dosage, frequency, duration, instructions };
    });
}

export function PrescriptionsPage() {
  const { user } = useAuth();
  const canEdit = ["Admin", "Hospital Staff", "Doctor"].includes(user?.role);
  const [items, setItems] = useState([]);
  const [pageInfo, setPageInfo] = useState({ page: 1, size: 10, total: 0, pages: 0 });
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);

  const load = async (page = 1) => {
    const { data } = await ehrApi.prescriptions({ search, page, size: pageInfo.size });
    setItems(data.items);
    setPageInfo(data.meta);
  };

  useEffect(() => {
    load(1);
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const payload = {
      patient_id: Number(form.patient_id),
      doctor_id: Number(form.doctor_id),
      issue_date: form.issue_date,
      dosage: form.dosage,
      frequency: form.frequency,
      duration: form.duration,
      instructions: form.instructions,
      medications: parseMedications(form.medications_text),
    };
    if (editingId) {
      await ehrApi.updatePrescription(editingId, payload);
    } else {
      await ehrApi.createPrescription(payload);
    }
    setForm(emptyForm);
    setEditingId(null);
    await load(pageInfo.page);
  };

  const edit = (row) => {
    setEditingId(row.prescription_id);
    setForm({
      patient_id: row.patient_id,
      doctor_id: row.doctor_id,
      issue_date: row.issue_date || "",
      dosage: row.dosage || "",
      frequency: row.frequency || "",
      duration: row.duration || "",
      instructions: row.instructions || "",
      medications_text: (row.medications || [])
        .map((m) => [m.name, m.dosage, m.frequency, m.duration, m.instructions].map((part) => part || "").join(" | "))
        .join("\n"),
    });
  };

  const columns = [
    { key: "prescription_id", label: "ID" },
    { key: "patient_id", label: "Patient" },
    { key: "doctor_id", label: "Doctor" },
    { key: "issue_date", label: "Issue Date" },
    {
      key: "medications",
      label: "Medications",
      render: (row) => row.medications?.length || 0,
    },
  ];
  columns.push({
    key: "actions",
    label: "Actions",
    render: (row) => (
      <div className="flex gap-3">
        {canEdit ? (
          <button type="button" className="font-medium text-brand-700 hover:underline" onClick={() => edit(row)}>
            Edit
          </button>
        ) : null}
        <button
          type="button"
          className="font-medium text-slate-700 hover:underline"
          onClick={() => downloadBlob(ehrApi.downloadPrescription(row.prescription_id), `prescription_${row.prescription_id}.pdf`)}
        >
          Download
        </button>
      </div>
    ),
  });

  return (
    <div className="space-y-6">
      <SectionHeader title="Prescriptions" subtitle="Create multi-medication prescriptions and download printable outputs." />
      <Card>
        <div className="flex gap-3">
          <Input placeholder="Search prescriptions" value={search} onChange={(e) => setSearch(e.target.value)} />
          <Button type="button" onClick={() => load(1)}>
            Search
          </Button>
        </div>
      </Card>
      {canEdit ? (
        <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input placeholder="Patient ID" type="number" value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} />
          <Input placeholder="Doctor ID" type="number" value={form.doctor_id} onChange={(e) => setForm({ ...form, doctor_id: e.target.value })} />
          <Input type="date" value={form.issue_date} onChange={(e) => setForm({ ...form, issue_date: e.target.value })} />
          <Input placeholder="Dosage summary" value={form.dosage} onChange={(e) => setForm({ ...form, dosage: e.target.value })} />
          <Input placeholder="Frequency summary" value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })} />
          <Input placeholder="Duration summary" value={form.duration} onChange={(e) => setForm({ ...form, duration: e.target.value })} />
          <Textarea placeholder="Instructions" rows="2" value={form.instructions} onChange={(e) => setForm({ ...form, instructions: e.target.value })} />
          <Textarea placeholder="Medications - one per line: name | dosage | frequency | duration | instructions" rows="4" value={form.medications_text} onChange={(e) => setForm({ ...form, medications_text: e.target.value })} />
          <div className="md:col-span-2 flex gap-3">
            <Button type="submit">{editingId ? "Update Prescription" : "Create Prescription"}</Button>
            {editingId ? (
              <Button type="button" variant="secondary" onClick={() => { setEditingId(null); setForm(emptyForm); }}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>
        </Card>
      ) : null}
      <DataTable columns={columns} rows={items} emptyText="No prescriptions found." />
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
