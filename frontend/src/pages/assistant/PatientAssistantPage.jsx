import { useState } from "react";
import { assistantApi } from "../../api/assistant";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Button } from "../../components/ui/Button";
import { Disclaimer } from "../../components/ai/Disclaimer";

export function PatientAssistantPage() {
  const [patientId, setPatientId] = useState("");
  const [result, setResult] = useState(null);

  const load = async () => {
    if (!patientId) return;
    const { data } = await assistantApi.patientCopilot(patientId);
    setResult(data);
  };

  return (
    <div className="space-y-6">
      <SectionHeader title="Patient Virtual Assistant" subtitle="Personalized guidance, medication reminders, and follow-up suggestions." />
      <Disclaimer />
      <Card>
        <div className="flex flex-col gap-3 md:flex-row">
          <Input placeholder="Patient ID" value={patientId} onChange={(e) => setPatientId(e.target.value)} />
          <Button type="button" onClick={load}>Load Assistant Summary</Button>
        </div>
      </Card>
      {result ? (
        <Card>
          <h3 className="text-lg font-semibold text-slate-900">{result.title}</h3>
          <p className="mt-2 text-sm text-slate-600">{result.summary}</p>
          <div className="mt-4 space-y-2">
            {result.recommendations.map((item) => (
              <div key={item} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">{item}</div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}

