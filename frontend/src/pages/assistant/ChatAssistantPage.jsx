import { useEffect, useState } from "react";
import { assistantApi } from "../../api/assistant";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { Select } from "../../components/ui/Select";
import { Button } from "../../components/ui/Button";
import { Disclaimer } from "../../components/ai/Disclaimer";
import { Badge } from "../../components/ui/Badge";
import { MessageSquareMore } from "lucide-react";

function MessageBubble({ message }) {
  const isAssistant = message.sender_role === "assistant";
  return (
    <div className={`max-w-[85%] rounded-[1.75rem] px-4 py-3 shadow-sm ${isAssistant ? "ml-auto bg-brand-600 text-white" : "bg-slate-100 text-slate-800"}`}>
      <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>
      <p className={`mt-2 text-xs ${isAssistant ? "text-brand-100" : "text-slate-500"}`}>
        {message.language} · {message.sender_role}
      </p>
    </div>
  );
}

export function ChatAssistantPage() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [form, setForm] = useState({
    message: "",
    audience: "patient",
    language: "English",
    patient_id: "",
  });

  const selectedSessionId = selectedSession?.chat_session_id;

  const loadSessions = async () => {
    const { data } = await assistantApi.sessions();
    setSessions(data);
    if (!selectedSessionId && data.length) {
      await selectSession(data[0]);
    }
  };

  const selectSession = async (session) => {
    setSelectedSession(session);
    const { data } = await assistantApi.messages(session.chat_session_id);
    setMessages(data);
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const sendMessage = async () => {
    if (!form.message.trim()) return;
    const payload = {
      chat_session_id: selectedSessionId || undefined,
      audience: form.audience,
      language: form.language,
      patient_id: form.patient_id ? Number(form.patient_id) : undefined,
      message: form.message,
    };
    const { data } = await assistantApi.chat(payload);
    setSelectedSession(data.chat_session);
    setMessages((prev) => [...prev, data.user_message, data.assistant_message]);
    setForm((prev) => ({ ...prev, message: "" }));
    await loadSessions();
  };

  return (
    <div className="space-y-6">
      <SectionHeader
        title="AI chat assistant"
        subtitle="Multi-turn clinical conversations grounded in hospital knowledge and patient context."
      />
      <Disclaimer />

      <div className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-xl font-semibold text-slate-950">Conversations</h3>
            <Badge tone="info">{sessions.length} threads</Badge>
          </div>
          <div className="space-y-2">
            {sessions.map((session) => (
              <button
                key={session.chat_session_id}
                type="button"
                className={`w-full rounded-[1.5rem] border px-4 py-3 text-left transition ${
                  selectedSessionId === session.chat_session_id ? "border-brand-500 bg-brand-50" : "border-slate-200 bg-white hover:bg-slate-50"
                }`}
                onClick={() => selectSession(session)}
              >
                <p className="font-semibold text-slate-950">{session.title}</p>
                <p className="text-xs text-slate-500">
                  {session.audience} · {session.language}
                </p>
              </button>
            ))}
            {!sessions.length ? <p className="text-sm text-slate-500">No conversations yet.</p> : null}
          </div>
        </Card>

        <div className="space-y-6">
          <Card>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <Select value={form.audience} onChange={(e) => setForm({ ...form, audience: e.target.value })}>
                <option value="patient">Patient</option>
                <option value="doctor">Doctor</option>
                <option value="admin">Admin</option>
                <option value="staff">Hospital Staff</option>
              </Select>
              <Select value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })}>
                <option>English</option>
                <option>Hindi</option>
                <option>Telugu</option>
              </Select>
              <Input placeholder="Patient ID (optional)" value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} />
              <Button type="button" onClick={sendMessage}>
                <MessageSquareMore className="h-4 w-4" />
                Send
              </Button>
              <div className="xl:col-span-4">
                <Textarea
                  rows="4"
                  placeholder="Ask about symptoms, medications, reports, resources, or policies..."
                  value={form.message}
                  onChange={(e) => setForm({ ...form, message: e.target.value })}
                />
              </div>
            </div>
          </Card>

          <Card>
            <div className="space-y-3">
              {messages.map((message) => (
                <MessageBubble key={message.chat_message_id} message={message} />
              ))}
              {!messages.length ? <p className="text-sm text-slate-500">Start a conversation to see grounded responses.</p> : null}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
