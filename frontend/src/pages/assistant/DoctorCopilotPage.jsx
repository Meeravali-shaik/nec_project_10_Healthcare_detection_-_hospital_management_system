import { useState } from "react";
import { assistantApi } from "../../api/assistant";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Button } from "../../components/ui/Button";
import { Disclaimer } from "../../components/ai/Disclaimer";
import { Badge } from "../../components/ui/Badge";

export function DoctorCopilotPage() {
  const [patientId, setPatientId] = useState("");
  const [result, setResult] = useState(null);

  const load = async () => {
    if (!patientId) return;
    const { data } = await assistantApi.doctorCopilot(patientId);
    setResult(data);
  };

  return (
    <div className="space-y-6">
      <SectionHeader title="Doctor AI Copilot" subtitle="Patient summary generation, risk review, and treatment guidance." />
      <Disclaimer />
      <Card>
        <div className="flex flex-col gap-3 md:flex-row">
          <Input placeholder="Patient ID" value={patientId} onChange={(e) => setPatientId(e.target.value)} />
          <Button type="button" onClick={load}>Generate Clinical Summary</Button>
        </div>
      </Card>
      {result ? (
        <Card>
          <div className="flex flex-wrap items-center gap-3">
            <h3 className="text-lg font-semibold text-slate-900">{result.title}</h3>
            <Badge tone="info">{result.audience}</Badge>
          </div>
          <p className="mt-2 text-sm text-slate-600">{result.summary}</p>
          <div className="mt-4 space-y-2">
            {result.recommendations.map((item) => (
              <div key={item} className="rounded-2xl bg-brand-50 px-4 py-3 text-sm text-brand-900">{item}</div>
            ))}
          </div>
          <div className="mt-4 space-y-2">
            {result.citations.map((citation) => (
              <div key={`${citation.document_title}-${citation.chunk_index}`} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                {citation.document_title} · {citation.excerpt}
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}

