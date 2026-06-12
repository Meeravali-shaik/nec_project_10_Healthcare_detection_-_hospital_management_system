import { useEffect, useState } from "react";
import { aiApi } from "../../api/ai";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { Select } from "../../components/ui/Select";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";
import { Disclaimer } from "../../components/ai/Disclaimer";

const emptyForm = {
  patient_id: "",
  disease: "Diabetes",
  severity: "Moderate",
  age: "",
  existing_conditions: "",
  treatment_history: "",
  lab_values: "",
};

export function OutcomePredictionPage() {
  const [form, setForm] = useState(emptyForm);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const loadHistory = async () => {
    const { data } = await aiApi.outcomeHistory(form.patient_id || undefined);
    setHistory(data);
  };

  useEffect(() => {
    loadHistory().catch(() => setHistory([]));
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const lab_values = {};
    form.lab_values
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean)
      .forEach((pair) => {
        const [key, value] = pair.split(":").map((part) => part.trim());
        if (key) lab_values[key] = Number(value);
      });
    const payload = {
      ...form,
      patient_id: Number(form.patient_id),
      age: Number(form.age),
      existing_conditions: form.existing_conditions.split(",").map((item) => item.trim()).filter(Boolean),
      lab_values,
    };
    const { data } = await aiApi.predictOutcome(payload);
    setResult(data);
    await loadHistory();
  };

  const columns = [
    { key: "outcome_prediction_id", label: "ID" },
    { key: "disease", label: "Disease" },
    { key: "severity", label: "Severity" },
    { key: "recovery_probability", label: "Recovery" },
    { key: "readmission_risk", label: "Readmit" },
    { key: "risk_category", label: "Category" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Outcome Prediction" subtitle="Predict recovery, readmission, ICU, and mortality risk." />
      <Disclaimer />
      <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input placeholder="Patient ID" type="number" value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} />
          <Input placeholder="Age" type="number" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} />
          <Select value={form.disease} onChange={(e) => setForm({ ...form, disease: e.target.value })}>
            <option>Diabetes</option>
            <option>Heart Disease</option>
            <option>Kidney Disease</option>
            <option>Liver Disease</option>
            <option>Hypertension</option>
          </Select>
          <Select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
            <option>Low</option>
            <option>Moderate</option>
            <option>High</option>
            <option>Critical</option>
          </Select>
          <Textarea placeholder="Existing conditions comma separated" rows="2" value={form.existing_conditions} onChange={(e) => setForm({ ...form, existing_conditions: e.target.value })} />
          <Textarea placeholder="Treatment history" rows="2" value={form.treatment_history} onChange={(e) => setForm({ ...form, treatment_history: e.target.value })} />
          <Textarea placeholder="Lab values format: glucose:120, creatinine:1.1" rows="2" value={form.lab_values} onChange={(e) => setForm({ ...form, lab_values: e.target.value })} />
          <div className="md:col-span-2">
            <Button type="submit">Predict Outcome</Button>
          </div>
        </form>
      </Card>
      {result ? (
        <Card>
          <div className="grid gap-4 md:grid-cols-5">
            <Metric label="Recovery" value={`${Math.round(result.recovery_probability * 100)}%`} />
            <Metric label="Readmission" value={`${Math.round(result.readmission_risk * 100)}%`} />
            <Metric label="ICU Risk" value={`${Math.round(result.icu_requirement_risk * 100)}%`} />
            <Metric label="Mortality" value={`${Math.round(result.mortality_risk * 100)}%`} />
            <Metric label="LOS" value={`${result.expected_length_of_stay} days`} />
          </div>
          <p className="mt-4 text-sm text-slate-600">{result.clinical_recommendations}</p>
        </Card>
      ) : null}
      <DataTable columns={columns} rows={history} emptyText="No outcome predictions available." />
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-2xl bg-slate-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.15em] text-slate-500">{label}</p>
      <p className="mt-2 text-lg font-semibold text-slate-900">{value}</p>
    </div>
  );
}

