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
  vaccine_name: "",
  dose_number: "",
  vaccination_date: "",
  next_due_date: "",
  remarks: "",
};

export function VaccinationsPage() {
  const { user } = useAuth();
  const canEdit = ["Admin", "Hospital Staff", "Doctor"].includes(user?.role);
  const [items, setItems] = useState([]);
  const [pageInfo, setPageInfo] = useState({ page: 1, size: 10, total: 0, pages: 0 });
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);

  const load = async (page = 1) => {
    const { data } = await ehrApi.vaccinations({ search, page, size: pageInfo.size });
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
      dose_number: Number(form.dose_number),
      next_due_date: form.next_due_date || null,
    };
    if (editingId) {
      await ehrApi.updateVaccination(editingId, payload);
    } else {
      await ehrApi.createVaccination(payload);
    }
    setEditingId(null);
    setForm(emptyForm);
    await load(pageInfo.page);
  };

  const edit = (row) => {
    setEditingId(row.vaccination_id);
    setForm({
      patient_id: row.patient_id,
      vaccine_name: row.vaccine_name || "",
      dose_number: row.dose_number,
      vaccination_date: row.vaccination_date || "",
      next_due_date: row.next_due_date || "",
      remarks: row.remarks || "",
    });
  };

  const columns = [
    { key: "vaccination_id", label: "ID" },
    { key: "patient_id", label: "Patient" },
    { key: "vaccine_name", label: "Vaccine" },
    { key: "dose_number", label: "Dose" },
    { key: "vaccination_date", label: "Date" },
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
      <SectionHeader title="Vaccinations" subtitle="Track vaccine doses and future due dates." />
      <Card>
        <div className="flex gap-3">
          <Input placeholder="Search vaccinations" value={search} onChange={(e) => setSearch(e.target.value)} />
          <Button type="button" onClick={() => load(1)}>
            Search
          </Button>
        </div>
      </Card>
      {canEdit ? (
        <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input placeholder="Patient ID" type="number" value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} />
          <Input placeholder="Vaccine name" value={form.vaccine_name} onChange={(e) => setForm({ ...form, vaccine_name: e.target.value })} />
          <Input placeholder="Dose number" type="number" value={form.dose_number} onChange={(e) => setForm({ ...form, dose_number: e.target.value })} />
          <Input type="date" value={form.vaccination_date} onChange={(e) => setForm({ ...form, vaccination_date: e.target.value })} />
          <Input type="date" value={form.next_due_date} onChange={(e) => setForm({ ...form, next_due_date: e.target.value })} />
          <Textarea placeholder="Remarks" rows="2" value={form.remarks} onChange={(e) => setForm({ ...form, remarks: e.target.value })} />
          <div className="md:col-span-2 flex gap-3">
            <Button type="submit">{editingId ? "Update Vaccination" : "Create Vaccination"}</Button>
            {editingId ? (
              <Button type="button" variant="secondary" onClick={() => { setEditingId(null); setForm(emptyForm); }}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>
        </Card>
      ) : null}
      <DataTable columns={columns} rows={items} emptyText="No vaccinations found." />
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
