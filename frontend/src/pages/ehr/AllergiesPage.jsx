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

const emptyForm = {
  patient_id: "",
  allergy_name: "",
  severity: "Mild",
  reaction: "",
  notes: "",
};

export function AllergiesPage() {
  const { user } = useAuth();
  const canEdit = ["Admin", "Hospital Staff", "Doctor"].includes(user?.role);
  const [items, setItems] = useState([]);
  const [pageInfo, setPageInfo] = useState({ page: 1, size: 10, total: 0, pages: 0 });
  const [search, setSearch] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);

  const load = async (page = 1) => {
    const { data } = await ehrApi.allergies({ search, page, size: pageInfo.size });
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
    };
    if (editingId) {
      await ehrApi.updateAllergy(editingId, payload);
    } else {
      await ehrApi.createAllergy(payload);
    }
    setEditingId(null);
    setForm(emptyForm);
    await load(pageInfo.page);
  };

  const edit = (row) => {
    setEditingId(row.allergy_id);
    setForm({
      patient_id: row.patient_id,
      allergy_name: row.allergy_name || "",
      severity: row.severity || "Mild",
      reaction: row.reaction || "",
      notes: row.notes || "",
    });
  };

  const columns = [
    { key: "allergy_id", label: "ID" },
    { key: "patient_id", label: "Patient" },
    { key: "allergy_name", label: "Allergy" },
    { key: "severity", label: "Severity" },
    { key: "reaction", label: "Reaction" },
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
      <SectionHeader title="Allergies" subtitle="Record and track patient allergy severity and reactions." />
      <Card>
        <div className="flex gap-3">
          <Input placeholder="Search allergies" value={search} onChange={(e) => setSearch(e.target.value)} />
          <Button type="button" onClick={() => load(1)}>
            Search
          </Button>
        </div>
      </Card>
      {canEdit ? (
        <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input placeholder="Patient ID" type="number" value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} />
          <Input placeholder="Allergy name" value={form.allergy_name} onChange={(e) => setForm({ ...form, allergy_name: e.target.value })} />
          <Select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
            <option>Mild</option>
            <option>Moderate</option>
            <option>Severe</option>
          </Select>
          <Textarea placeholder="Reaction" rows="2" value={form.reaction} onChange={(e) => setForm({ ...form, reaction: e.target.value })} />
          <Textarea placeholder="Notes" rows="2" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          <div className="md:col-span-2 flex gap-3">
            <Button type="submit">{editingId ? "Update Allergy" : "Create Allergy"}</Button>
            {editingId ? (
              <Button type="button" variant="secondary" onClick={() => { setEditingId(null); setForm(emptyForm); }}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>
        </Card>
      ) : null}
      <DataTable columns={columns} rows={items} emptyText="No allergies found." />
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
