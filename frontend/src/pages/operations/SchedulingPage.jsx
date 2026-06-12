import { useState } from "react";
import { operationsApi } from "../../api/operations";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { Button } from "../../components/ui/Button";
import { DataTable } from "../../components/shared/DataTable";

export function SchedulingPage() {
  const [form, setForm] = useState({ patient_load: "", bed_occupancy: "", emergency_cases: "", department_demand: "" });
  const [result, setResult] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    const department_demand = {};
    form.department_demand.split(",").map((item) => item.trim()).filter(Boolean).forEach((pair) => {
      const [dept, value] = pair.split(":").map((part) => part.trim());
      if (dept) department_demand[dept] = Number(value);
    });
    const { data } = await operationsApi.scheduleRecommendations({
      patient_load: Number(form.patient_load),
      bed_occupancy: Number(form.bed_occupancy),
      emergency_cases: Number(form.emergency_cases),
      department_demand,
    });
    setResult(data);
  };

  const shiftRows = result
    ? Object.entries(result.shift_allocation).map(([shift, value]) => ({ id: shift, shift, doctors: value.doctors, nurses: value.nurses }))
    : [];

  const columns = [
    { key: "shift", label: "Shift" },
    { key: "doctors", label: "Doctors" },
    { key: "nurses", label: "Nurses" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Scheduling Dashboard" subtitle="AI-assisted staffing recommendations and shift allocation." />
      <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input placeholder="Patient load" type="number" value={form.patient_load} onChange={(e) => setForm({ ...form, patient_load: e.target.value })} />
          <Input placeholder="Bed occupancy %" type="number" value={form.bed_occupancy} onChange={(e) => setForm({ ...form, bed_occupancy: e.target.value })} />
          <Input placeholder="Emergency cases" type="number" value={form.emergency_cases} onChange={(e) => setForm({ ...form, emergency_cases: e.target.value })} />
          <Textarea placeholder="Department demand format: ICU:20, ER:15" rows="2" value={form.department_demand} onChange={(e) => setForm({ ...form, department_demand: e.target.value })} />
          <div className="md:col-span-2">
            <Button type="submit">Generate Staffing Recommendations</Button>
          </div>
        </form>
      </Card>
      {result ? (
        <Card>
          <p className="text-sm text-slate-600">Peak Hour: {result.peak_hour_prediction}</p>
          <p className="mt-2 text-sm text-slate-600">{result.staffing_recommendations.join(" ")}</p>
        </Card>
      ) : null}
      <DataTable columns={columns} rows={shiftRows} emptyText="No allocation yet." />
    </div>
  );
}

