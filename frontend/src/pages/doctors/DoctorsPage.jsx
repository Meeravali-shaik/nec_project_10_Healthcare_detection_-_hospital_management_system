import { useEffect, useState } from "react";
import { doctorsApi } from "../../api/doctors";
import { DataTable } from "../../components/shared/DataTable";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Button } from "../../components/ui/Button";
import { Select } from "../../components/ui/Select";
import { Textarea } from "../../components/ui/Textarea";

export function DoctorsPage() {
  const [doctors, setDoctors] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({
    full_name: "",
    specialization: "",
    department: "",
    qualification: "",
    experience_years: "",
    consultation_fee: "",
    phone_number: "",
    email: "",
    availability_status: true,
  });

  useEffect(() => {
    doctorsApi.list().then((res) => setDoctors(res.data));
  }, []);

  const reload = async () => {
    const { data } = await doctorsApi.list();
    setDoctors(data);
  };

  const resetForm = () => {
    setEditingId(null);
    setForm({
      full_name: "",
      specialization: "",
      department: "",
      qualification: "",
      experience_years: "",
      consultation_fee: "",
      phone_number: "",
      email: "",
      availability_status: true,
    });
  };

  const submit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      experience_years: form.experience_years ? Number(form.experience_years) : null,
      consultation_fee: form.consultation_fee ? Number(form.consultation_fee) : null,
    };
    if (editingId) {
      await doctorsApi.update(editingId, payload);
    } else {
      await doctorsApi.create(payload);
    }
    resetForm();
    await reload();
  };

  const editDoctor = (row) => {
    setEditingId(row.doctor_id);
    setForm({
      full_name: row.full_name || "",
      specialization: row.specialization || "",
      department: row.department || "",
      qualification: row.qualification || "",
      experience_years: row.experience_years ?? "",
      consultation_fee: row.consultation_fee ?? "",
      phone_number: row.phone_number || "",
      email: row.email || "",
      availability_status: Boolean(row.availability_status),
    });
  };

  const removeDoctor = async (id) => {
    await doctorsApi.remove(id);
    await reload();
  };

  const columns = [
    { key: "doctor_id", label: "ID" },
    { key: "full_name", label: "Name" },
    { key: "specialization", label: "Specialization" },
    { key: "department", label: "Department" },
    { key: "availability_status", label: "Available", render: (row) => (row.availability_status ? "Yes" : "No") },
    {
      key: "actions",
      label: "Actions",
      render: (row) => (
        <div className="flex gap-3">
          <button type="button" className="font-medium text-slate-700 hover:underline" onClick={() => editDoctor(row)}>
            Edit
          </button>
          <button type="button" className="font-medium text-rose-600 hover:underline" onClick={() => removeDoctor(row.doctor_id)}>
            Delete
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Doctor Management" subtitle="Review doctor profiles and availability." />
      <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          <Input placeholder="Specialization" value={form.specialization} onChange={(e) => setForm({ ...form, specialization: e.target.value })} />
          <Input placeholder="Department" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
          <Input placeholder="Qualification" value={form.qualification} onChange={(e) => setForm({ ...form, qualification: e.target.value })} />
          <Input placeholder="Experience years" type="number" value={form.experience_years} onChange={(e) => setForm({ ...form, experience_years: e.target.value })} />
          <Input placeholder="Consultation fee" type="number" value={form.consultation_fee} onChange={(e) => setForm({ ...form, consultation_fee: e.target.value })} />
          <Input placeholder="Phone number" value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
          <Input placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <label className="space-y-1.5">
            <span className="text-sm font-medium text-slate-700">Availability</span>
            <Select value={String(form.availability_status)} onChange={(e) => setForm({ ...form, availability_status: e.target.value === "true" })}>
              <option value="true">Available</option>
              <option value="false">Unavailable</option>
            </Select>
          </label>
          <div className="md:col-span-2">
            <Button type="submit">{editingId ? "Update Doctor" : "Add Doctor"}</Button>
            {editingId ? (
              <Button type="button" variant="secondary" className="ml-3" onClick={resetForm}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>
      </Card>
      <DataTable columns={columns} rows={doctors} emptyText="No doctors registered yet." />
    </div>
  );
}
