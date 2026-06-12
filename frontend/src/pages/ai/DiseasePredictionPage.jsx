import { useEffect, useState } from "react";
import { aiApi } from "../../api/ai";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Textarea } from "../../components/ui/Textarea";
import { Button } from "../../components/ui/Button";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";
import { Disclaimer } from "../../components/ai/Disclaimer";
import { Badge } from "../../components/ui/Badge";

const emptyForm = {
  patient_id: "",
  age: "",
  gender: "female",
  bmi: "",
  blood_pressure: "",
  glucose_level: "",
  cholesterol: "",
  family_history: "",
  symptoms: "",
  medical_history: "",
};

export function DiseasePredictionPage() {
  const [form, setForm] = useState(emptyForm);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const loadHistory = async () => {
    const { data } = await aiApi.diseaseHistory(form.patient_id || undefined);
    setHistory(data);
  };

  useEffect(() => {
    loadHistory().catch(() => setHistory([]));
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      patient_id: Number(form.patient_id),
      age: Number(form.age),
      bmi: Number(form.bmi),
      blood_pressure: Number(form.blood_pressure),
      glucose_level: Number(form.glucose_level),
      cholesterol: Number(form.cholesterol),
      symptoms: form.symptoms.split(",").map((item) => item.trim()).filter(Boolean),
    };
    const { data } = await aiApi.predictDisease(payload);
    setResult(data);
    await loadHistory();
  };

  const columns = [
    { key: "prediction_id", label: "ID" },
    { key: "model_used", label: "Model" },
    { key: "disease", label: "Disease" },
    { key: "risk_score", label: "Risk Score" },
    { key: "confidence_score", label: "Confidence" },
    { key: "severity_level", label: "Severity" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Disease Prediction" subtitle="Predict disease risk from patient information." />
      <Disclaimer />
      <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input placeholder="Patient ID" type="number" value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} />
          <Input placeholder="Age" type="number" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} />
          <Select value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })}>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="other">Other</option>
          </Select>
          <Input placeholder="BMI" type="number" value={form.bmi} onChange={(e) => setForm({ ...form, bmi: e.target.value })} />
          <Input placeholder="Blood pressure" type="number" value={form.blood_pressure} onChange={(e) => setForm({ ...form, blood_pressure: e.target.value })} />
          <Input placeholder="Glucose level" type="number" value={form.glucose_level} onChange={(e) => setForm({ ...form, glucose_level: e.target.value })} />
          <Input placeholder="Cholesterol" type="number" value={form.cholesterol} onChange={(e) => setForm({ ...form, cholesterol: e.target.value })} />
          <Input placeholder="Family history" value={form.family_history} onChange={(e) => setForm({ ...form, family_history: e.target.value })} />
          <Textarea placeholder="Symptoms comma separated" rows="3" value={form.symptoms} onChange={(e) => setForm({ ...form, symptoms: e.target.value })} />
          <Textarea placeholder="Medical history" rows="3" value={form.medical_history} onChange={(e) => setForm({ ...form, medical_history: e.target.value })} />
          <div className="md:col-span-2">
            <Button type="submit">Predict Disease Risk</Button>
          </div>
        </form>
      </Card>
      {result ? (
        <Card>
          <div className="grid gap-4 md:grid-cols-4">
            <Metric label="Predicted Disease" value={result.disease} />
            <Metric label="Risk Score" value={`${result.risk_score}%`} />
            <Metric label="Confidence" value={`${Math.round(result.confidence_score * 100)}%`} />
            <Metric label="Severity" value={result.severity_level} />
          </div>
        </Card>
      ) : null}
      <DataTable columns={columns} rows={history} emptyText="No prediction history available." />
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

