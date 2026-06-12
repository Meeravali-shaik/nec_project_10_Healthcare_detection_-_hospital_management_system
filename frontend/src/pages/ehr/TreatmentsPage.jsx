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
  treatment_name: "",
  diagnosis: "",
  start_date: "",
  end_date: "",
  outcome: "",
  notes: "",
};

export function TreatmentsPage() {
  const { user } = useAuth();
  const canEdit = ["Admin", "Hospital Staff", "Doctor"].includes(user?.role);
  const [items, setItems] = useState([]);
  const [pageInfo, setPageInfo] = useState({ page: 1, size: 10, total: 0, pages: 0 });
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);

  const load = async (page = 1) => {
    const { data } = await ehrApi.treatments({ search, page, size: pageInfo.size });
    setItems(data.items);
    setPageInfo(data.meta);
  };

  useEffect(() => {
    load(1);
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      patient_id: Number(form.patient_id),
      doctor_id: Number(form.doctor_id),
      end_date: form.end_date || null,
    };
    if (editingId) {
      await ehrApi.updateTreatment(editingId, payload);
    } else {
      await ehrApi.createTreatment(payload);
    }
    setEditingId(null);
    setForm(emptyForm);
    await load(pageInfo.page);
  };

  const edit = (row) => {
    setEditingId(row.treatment_id);
    setForm({
      patient_id: row.patient_id,
      doctor_id: row.doctor_id,
      treatment_name: row.treatment_name || "",
      diagnosis: row.diagnosis || "",
      start_date: row.start_date || "",
      end_date: row.end_date || "",
      outcome: row.outcome || "",
      notes: row.notes || "",
    });
  };

  const columns = [
    { key: "treatment_id", label: "ID" },
    { key: "patient_id", label: "Patient" },
    { key: "doctor_id", label: "Doctor" },
    { key: "treatment_name", label: "Treatment" },
    { key: "start_date", label: "Start" },
  ];
  if (canEdit) {
    columns.push({
      key: "actions",
      label: "Actions",
      render: (row) => (
        <button type="button" className="font-medium text-brand-700 hover:underline" onClick={() => edit(row)}>
          Edit
        </button>
      ),
    });
  }

  return (
    <div className="space-y-6">
      <SectionHeader title="Treatment History" subtitle="Chronological treatment tracking linked to the patient profile." />
      <Card>
        <div className="flex gap-3">
          <Input placeholder="Search treatments" value={search} onChange={(e) => setSearch(e.target.value)} />
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
          <Input placeholder="Treatment name" value={form.treatment_name} onChange={(e) => setForm({ ...form, treatment_name: e.target.value })} />
          <Input placeholder="Diagnosis" value={form.diagnosis} onChange={(e) => setForm({ ...form, diagnosis: e.target.value })} />
          <Input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
          <Input type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
          <Textarea placeholder="Outcome" rows="2" value={form.outcome} onChange={(e) => setForm({ ...form, outcome: e.target.value })} />
          <Textarea placeholder="Notes" rows="2" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          <div className="md:col-span-2 flex gap-3">
            <Button type="submit">{editingId ? "Update Treatment" : "Create Treatment"}</Button>
            {editingId ? (
              <Button type="button" variant="secondary" onClick={() => { setEditingId(null); setForm(emptyForm); }}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>
        </Card>
      ) : null}
      <DataTable columns={columns} rows={items} emptyText="No treatments found." />
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
