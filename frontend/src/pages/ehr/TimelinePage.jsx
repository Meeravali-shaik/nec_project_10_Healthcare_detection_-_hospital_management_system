import { useState } from "react";
import { ehrApi } from "../../api/ehr";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Badge } from "../../components/ui/Badge";

export function TimelinePage() {
  const { user } = useAuth();
  const [patientId, setPatientId] = useState("");
  const [events, setEvents] = useState([]);

  const load = async () => {
    const { data } = await ehrApi.timeline(patientId);
    setEvents(Array.isArray(data) ? data : []);
  };

  const fetchMyTimeline = async () => {
    if (user?.role === "Patient") {
      const { data } = await ehrApi.meTimeline();
      setEvents(data);
    } else {
      await load();
    }
  };

  return (
    <div className="space-y-6">
      <SectionHeader title="Patient Medical Timeline" subtitle="Appointments, diagnoses, prescriptions, reports, treatments, and vaccinations." />
      {user?.role !== "Patient" ? (
        <Card>
          <div className="flex gap-3">
            <Input placeholder="Patient ID" type="number" value={patientId} onChange={(e) => setPatientId(e.target.value)} />
            <Button type="button" onClick={load}>
              Load Timeline
            </Button>
          </div>
        </Card>
      ) : (
        <Card>
          <Button type="button" onClick={fetchMyTimeline}>
            Load My Timeline
          </Button>
        </Card>
      )}
      <div className="space-y-3">
        {events.map((event, index) => (
          <Card key={`${event.source_id || index}-${event.event_type}`}>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-700">{event.event_type}</p>
                <h3 className="mt-1 text-lg font-semibold text-slate-900">{event.title}</h3>
                <p className="mt-1 text-sm text-slate-500">{event.description || "No additional notes"}</p>
              </div>
              <Badge tone="info">{event.event_date}</Badge>
            </div>
          </Card>
        ))}
        {!events.length ? <Card><p className="text-sm text-slate-500">No timeline events loaded yet.</p></Card> : null}
      </div>
    </div>
  );
}
