import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { patientsApi } from "../../api/patients";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Card } from "../../components/ui/Card";
import { DataTable } from "../../components/shared/DataTable";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Textarea } from "../../components/ui/Textarea";

export function PatientsPage() {
  const [search, setSearch] = useState("");
  const [patients, setPatients] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({
    full_name: "",
    age: "",
    gender: "",
    blood_group: "",
    emergency_contact: "",
    allergies: "",
    medical_history: "",
    family_history: "",
    insurance_provider: "",
    insurance_number: "",
  });

  const loadPatients = async (query = "") => {
    const { data } = await patientsApi.list(query);
    setPatients(data);
  };

  useEffect(() => {
    loadPatients();
  }, []);

  const resetForm = () => {
    setEditingId(null);
    setForm({
      full_name: "",
      age: "",
      gender: "",
      blood_group: "",
      emergency_contact: "",
      allergies: "",
      medical_history: "",
      family_history: "",
      insurance_provider: "",
      insurance_number: "",
    });
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      age: form.age ? Number(form.age) : null,
    };
    if (editingId) {
      await patientsApi.update(editingId, payload);
    } else {
      await patientsApi.create(payload);
    }
    resetForm();
    await loadPatients(search);
  };

  const startEdit = (row) => {
    setEditingId(row.patient_id);
    setForm({
      full_name: row.full_name || "",
      age: row.age ?? "",
      gender: row.gender || "",
      blood_group: row.blood_group || "",
      emergency_contact: row.emergency_contact || "",
      allergies: row.allergies || "",
      medical_history: row.medical_history || "",
      family_history: row.family_history || "",
      insurance_provider: row.insurance_provider || "",
      insurance_number: row.insurance_number || "",
    });
  };

  const removePatient = async (id) => {
    await patientsApi.remove(id);
    await loadPatients(search);
  };

  const columns = [
    { key: "patient_id", label: "ID" },
    { key: "full_name", label: "Name" },
    { key: "blood_group", label: "Blood Group" },
    { key: "emergency_contact", label: "Emergency Contact" },
    {
      key: "actions",
      label: "Actions",
      render: (row) => (
        <div className="flex gap-3">
          <Link className="font-medium text-brand-700 hover:underline" to={`/patients/${row.patient_id}`}>
            View
          </Link>
          <button type="button" className="font-medium text-slate-700 hover:underline" onClick={() => startEdit(row)}>
            Edit
          </button>
          <button type="button" className="font-medium text-rose-600 hover:underline" onClick={() => removePatient(row.patient_id)}>
            Delete
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Patient Management" subtitle="Search and review patient records." />
      <Card>
        <div className="flex flex-col gap-3 sm:flex-row">
          <Input placeholder="Search patients" value={search} onChange={(e) => setSearch(e.target.value)} />
          <Button onClick={() => loadPatients(search)}>Search</Button>
        </div>
      </Card>
      <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={onSubmit}>
          <Input placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          <Input placeholder="Age" type="number" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} />
          <Input placeholder="Gender" value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })} />
          <Input placeholder="Blood group" value={form.blood_group} onChange={(e) => setForm({ ...form, blood_group: e.target.value })} />
          <Input placeholder="Emergency contact" value={form.emergency_contact} onChange={(e) => setForm({ ...form, emergency_contact: e.target.value })} />
          <Input placeholder="Insurance provider" value={form.insurance_provider} onChange={(e) => setForm({ ...form, insurance_provider: e.target.value })} />
          <Input placeholder="Insurance number" value={form.insurance_number} onChange={(e) => setForm({ ...form, insurance_number: e.target.value })} />
          <Textarea placeholder="Allergies" rows="2" value={form.allergies} onChange={(e) => setForm({ ...form, allergies: e.target.value })} />
          <Textarea placeholder="Medical history" rows="2" value={form.medical_history} onChange={(e) => setForm({ ...form, medical_history: e.target.value })} />
          <Textarea placeholder="Family history" rows="2" value={form.family_history} onChange={(e) => setForm({ ...form, family_history: e.target.value })} />
          <div className="flex gap-3 md:col-span-2">
            <Button type="submit">{editingId ? "Update Patient" : "Add Patient"}</Button>
            {editingId ? (
              <Button type="button" variant="secondary" onClick={resetForm}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>
      </Card>
      <DataTable columns={columns} rows={patients} emptyText="No patient records available." />
    </div>
  );
}
