import { useEffect, useState } from "react";
import { aiApi } from "../../api/ai";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";
import { Disclaimer } from "../../components/ai/Disclaimer";

const emptyForm = { patient_id: "", report_id: "", report_text: "" };

export function ReportAnalysisPage() {
  const [form, setForm] = useState(emptyForm);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const loadHistory = async () => {
    const { data } = await aiApi.reportHistory(form.patient_id || undefined);
    setHistory(data);
  };

  useEffect(() => {
    loadHistory().catch(() => setHistory([]));
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    const payload = {
      patient_id: Number(form.patient_id),
      report_id: form.report_id ? Number(form.report_id) : null,
      report_text: form.report_text,
    };
    const { data } = await aiApi.analyzeReport(payload);
    setResult(data);
    await loadHistory();
  };

  const columns = [
    { key: "analysis_id", label: "ID" },
    { key: "patient_id", label: "Patient" },
    { key: "report_id", label: "Report" },
    { key: "summary", label: "Summary" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Report Analysis" subtitle="Extract text, identify abnormalities, and generate alerts." />
      <Disclaimer />
      <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input placeholder="Patient ID" type="number" value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} />
          <Input placeholder="Report ID (optional)" type="number" value={form.report_id} onChange={(e) => setForm({ ...form, report_id: e.target.value })} />
          <Textarea placeholder="Paste report text here" rows="8" value={form.report_text} onChange={(e) => setForm({ ...form, report_text: e.target.value })} />
          <div className="md:col-span-2">
            <Button type="submit">Analyze Report</Button>
          </div>
        </form>
      </Card>
      {result ? (
        <Card>
          <div className="grid gap-4 md:grid-cols-2">
            <Info label="Alert" value={result.alert_message || "None"} />
            <Info label="Summary" value={result.summary} />
          </div>
        </Card>
      ) : null}
      <DataTable columns={columns} rows={history} emptyText="No report analyses available." />
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

