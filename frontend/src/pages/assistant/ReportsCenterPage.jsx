import { useEffect, useState } from "react";
import { assistantApi } from "../../api/assistant";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { Select } from "../../components/ui/Select";
import { Button } from "../../components/ui/Button";

export function ReportsCenterPage() {
  const [reports, setReports] = useState([]);
  const [form, setForm] = useState({
    report_type: "Executive Summary",
    format: "PDF",
    title: "",
    summary: "",
    metadata_json: "{}",
  });

  const load = async () => {
    const { data } = await assistantApi.reports();
    setReports(data);
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async () => {
    try {
      await assistantApi.createReport({
        report_type: form.report_type,
        format: form.format,
        title: form.title,
        summary: form.summary,
        metadata_json: JSON.parse(form.metadata_json || "{}"),
      });
      setForm({ report_type: "Executive Summary", format: "PDF", title: "", summary: "", metadata_json: "{}" });
      await load();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="space-y-6">
      <SectionHeader title="AI Reports Center" subtitle="Generate PDF or DOCX reports from healthcare insights and operational data." />
      <Card>
        <div className="grid gap-4 md:grid-cols-2">
          <Select value={form.report_type} onChange={(e) => setForm({ ...form, report_type: e.target.value })}>
            <option>Executive Summary</option>
            <option>Patient Health Report</option>
            <option>Doctor Performance Report</option>
            <option>Resource Utilization Report</option>
            <option>Disease Analytics Report</option>
          </Select>
          <Select value={form.format} onChange={(e) => setForm({ ...form, format: e.target.value })}>
            <option>PDF</option>
            <option>DOCX</option>
          </Select>
          <Input placeholder="Report title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <Textarea placeholder="Summary" rows="3" value={form.summary} onChange={(e) => setForm({ ...form, summary: e.target.value })} />
          <Textarea placeholder='Metadata JSON, for example {"narrative":"..."}' rows="3" value={form.metadata_json} onChange={(e) => setForm({ ...form, metadata_json: e.target.value })} />
          <div className="md:col-span-2">
            <Button type="button" onClick={submit}>Generate Report</Button>
          </div>
        </div>
      </Card>
      <Card>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">Generated Reports</h3>
        <DataTable
          columns={[
            { key: "title", label: "Title" },
            { key: "report_type", label: "Type" },
            { key: "format", label: "Format" },
            { key: "file_name", label: "File" },
            { key: "output_path", label: "Path" },
          ]}
          rows={reports}
          emptyText="No generated reports found."
        />
      </Card>
    </div>
  );
}
