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

const emptyForm = { patient_id: "", disease: "Diabetes", symptoms: "" };

export function TreatmentRecommendationPage() {
  const [form, setForm] = useState(emptyForm);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const loadHistory = async () => {
    const { data } = await aiApi.treatmentHistory(form.patient_id || undefined);
    setHistory(data);
  };

  useEffect(() => {
    loadHistory().catch(() => setHistory([]));
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const payload = {
      patient_id: Number(form.patient_id),
      disease: form.disease,
      symptoms: form.symptoms.split(",").map((item) => item.trim()).filter(Boolean),
    };
    const { data } = await aiApi.recommendTreatment(payload);
    setResult(data);
    await loadHistory();
  };

  const columns = [
    { key: "recommendation_id", label: "ID" },
    { key: "disease", label: "Disease" },
    { key: "recommended_specialist", label: "Specialist" },
    { key: "suggested_tests", label: "Tests" },
    { key: "rule_version", label: "Rule" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Treatment Recommendation" subtitle="Rule-based guidance ready for future LLM integration." />
      <Disclaimer />
      <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input placeholder="Patient ID" type="number" value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} />
          <Select value={form.disease} onChange={(e) => setForm({ ...form, disease: e.target.value })}>
            <option>Diabetes</option>
            <option>Heart Disease</option>
            <option>Kidney Disease</option>
            <option>Liver Disease</option>
            <option>Hypertension</option>
          </Select>
          <Textarea placeholder="Symptoms comma separated" rows="3" value={form.symptoms} onChange={(e) => setForm({ ...form, symptoms: e.target.value })} />
          <div className="md:col-span-2">
            <Button type="submit">Generate Recommendation</Button>
          </div>
        </form>
      </Card>
      {result ? (
        <Card>
          <div className="grid gap-4 md:grid-cols-2">
            <Info label="Recommended Specialist" value={result.recommended_specialist} />
            <Info label="Suggested Tests" value={result.suggested_tests} />
            <Info label="Lifestyle Recommendations" value={result.lifestyle_recommendations} />
            <Info label="Preliminary Guidance" value={result.preliminary_treatment_guidance} />
            <Info label="Follow-up Suggestions" value={result.follow_up_suggestions} />
          </div>
        </Card>
      ) : null}
      <DataTable columns={columns} rows={history} emptyText="No recommendations available." />
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="rounded-2xl bg-slate-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.15em] text-slate-500">{label}</p>
      <p className="mt-2 text-sm text-slate-800">{value}</p>
    </div>
  );
}

