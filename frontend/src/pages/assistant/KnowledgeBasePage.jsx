import { useEffect, useState } from "react";
import { assistantApi } from "../../api/assistant";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { Select } from "../../components/ui/Select";
import { Button } from "../../components/ui/Button";

export function KnowledgeBasePage() {
  const [documents, setDocuments] = useState([]);
  const [results, setResults] = useState([]);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState({
    title: "",
    source_type: "Hospital Policy",
    source_ref: "",
    language: "English",
    content: "",
    summary: "",
    tags: "{}",
  });

  const load = async () => {
    const { data } = await assistantApi.knowledge();
    setDocuments(data);
  };

  useEffect(() => {
    load();
  }, []);

  const ingest = async () => {
    try {
      const payload = {
        ...form,
        tags: JSON.parse(form.tags || "{}"),
      };
      await assistantApi.ingestKnowledge(payload);
      setForm({ title: "", source_type: "Hospital Policy", source_ref: "", language: "English", content: "", summary: "", tags: "{}" });
      await load();
    } catch (error) {
      console.error(error);
    }
  };

  const runSearch = async () => {
    const { data } = await assistantApi.searchKnowledge({ query: search, top_k: 5 });
    setResults(data);
  };

  return (
    <div className="space-y-6">
      <SectionHeader title="Knowledge Base" subtitle="Ingest policies, guidelines, and hospital documents for RAG retrieval." />
      <Card>
        <div className="grid gap-4 md:grid-cols-2">
          <Input placeholder="Search knowledge base" value={search} onChange={(e) => setSearch(e.target.value)} />
          <Button type="button" onClick={runSearch}>Search</Button>
        </div>
      </Card>
      <Card>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">Ingest Document</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <Input placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <Select value={form.source_type} onChange={(e) => setForm({ ...form, source_type: e.target.value })}>
            <option>Hospital Policy</option>
            <option>Medical Guideline</option>
            <option>EHR Record</option>
            <option>Lab Report</option>
            <option>Uploaded Document</option>
          </Select>
          <Input placeholder="Source reference" value={form.source_ref} onChange={(e) => setForm({ ...form, source_ref: e.target.value })} />
          <Select value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })}>
            <option>English</option>
            <option>Hindi</option>
            <option>Telugu</option>
          </Select>
          <Textarea placeholder="Document content" rows="4" value={form.content} onChange={(e) => setForm({ ...form, content: e.target.value })} />
          <Textarea placeholder="Summary" rows="4" value={form.summary} onChange={(e) => setForm({ ...form, summary: e.target.value })} />
          <Textarea placeholder='Tags JSON, for example {"department":"ICU"}' rows="3" value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} />
          <div className="md:col-span-2">
            <Button type="button" onClick={ingest}>Ingest Knowledge</Button>
          </div>
        </div>
      </Card>
      <Card>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">Knowledge Documents</h3>
        <DataTable
          columns={[
            { key: "title", label: "Title" },
            { key: "source_type", label: "Type" },
            { key: "source_ref", label: "Reference" },
            { key: "language", label: "Language" },
            { key: "summary", label: "Summary" },
          ]}
          rows={documents}
          emptyText="No knowledge documents found."
        />
      </Card>
      <Card>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">Search Results</h3>
        {results.length ? (
          <div className="space-y-3">
            {results.map((result) => (
              <div key={`${result.document_title}-${result.chunk_index}`} className="rounded-2xl bg-slate-50 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-medium text-slate-900">{result.document_title}</p>
                  <p className="text-xs text-slate-500">Score {result.score}</p>
                </div>
                <p className="mt-2 text-sm text-slate-600">{result.excerpt}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No search results yet.</p>
        )}
      </Card>
    </div>
  );
}
