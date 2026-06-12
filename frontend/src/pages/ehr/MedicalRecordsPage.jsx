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
  visit_date: "",
  chief_complaint: "",
  diagnosis: "",
  symptoms: "",
  treatment_plan: "",
  follow_up_date: "",
  notes: "",
};

export function MedicalRecordsPage() {
  const { user } = useAuth();
  const canEdit = ["Admin", "Hospital Staff", "Doctor"].includes(user?.role);
  const [items, setItems] = useState([]);
  const [pageInfo, setPageInfo] = useState({ page: 1, size: 10, total: 0, pages: 0 });
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);

  const load = async (page = 1) => {
    const { data } = await ehrApi.medicalRecords({ search, page, size: pageInfo.size });
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
      follow_up_date: form.follow_up_date || null,
    };
    if (editingId) {
      await ehrApi.updateMedicalRecord(editingId, payload);
    } else {
      await ehrApi.createMedicalRecord(payload);
    }
    setForm(emptyForm);
    setEditingId(null);
    await load(pageInfo.page);
  };

  const edit = (row) => {
    setEditingId(row.record_id);
    setForm({
      patient_id: row.patient_id,
      doctor_id: row.doctor_id,
      visit_date: row.visit_date || "",
      chief_complaint: row.chief_complaint || "",
      diagnosis: row.diagnosis || "",
      symptoms: row.symptoms || "",
      treatment_plan: row.treatment_plan || "",
      follow_up_date: row.follow_up_date || "",
      notes: row.notes || "",
    });
  };

  const columns = [
    { key: "record_id", label: "ID" },
    { key: "patient_id", label: "Patient" },
    { key: "doctor_id", label: "Doctor" },
    { key: "visit_date", label: "Visit Date" },
    { key: "chief_complaint", label: "Complaint" },
    { key: "diagnosis", label: "Diagnosis" },
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
      <SectionHeader title="Medical Records" subtitle="Clinical encounters, diagnoses, and treatment plans." />
      <Card>
        <div className="flex gap-3">
          <Input placeholder="Search records" value={search} onChange={(e) => setSearch(e.target.value)} />
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
          <Input type="date" value={form.visit_date} onChange={(e) => setForm({ ...form, visit_date: e.target.value })} />
          <Input type="date" placeholder="Follow-up date" value={form.follow_up_date} onChange={(e) => setForm({ ...form, follow_up_date: e.target.value })} />
          <Input placeholder="Chief complaint" value={form.chief_complaint} onChange={(e) => setForm({ ...form, chief_complaint: e.target.value })} />
          <Input placeholder="Diagnosis" value={form.diagnosis} onChange={(e) => setForm({ ...form, diagnosis: e.target.value })} />
          <Textarea placeholder="Symptoms" rows="2" value={form.symptoms} onChange={(e) => setForm({ ...form, symptoms: e.target.value })} />
          <Textarea placeholder="Treatment plan" rows="2" value={form.treatment_plan} onChange={(e) => setForm({ ...form, treatment_plan: e.target.value })} />
          <Textarea placeholder="Notes" rows="2" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          <div className="md:col-span-2 flex gap-3">
            <Button type="submit">{editingId ? "Update Record" : "Create Record"}</Button>
            {editingId ? (
              <Button type="button" variant="secondary" onClick={() => { setEditingId(null); setForm(emptyForm); }}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>
        </Card>
      ) : null}

      <DataTable columns={columns} rows={items} emptyText="No medical records found." />

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
