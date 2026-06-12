import { useEffect, useState } from "react";
import { appointmentsApi } from "../../api/appointments";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { StatCard } from "../../components/shared/StatCard";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { HeartPulse, CalendarClock, ClipboardList } from "lucide-react";

export function PatientDashboard() {
  const [appointments, setAppointments] = useState([]);

  useEffect(() => {
    appointmentsApi.list().then((res) => setAppointments(res.data));
  }, []);

  const pending = appointments.filter((item) => item.appointment_status === "Pending").length;
  const completed = appointments.filter((item) => item.appointment_status === "Completed").length;

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Patient health dashboard"
        subtitle="A calmer view of upcoming appointments, past visits, and your clinical timeline."
      />

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Pending" value={pending} note="Awaiting doctor approval" accent="brand" icon={CalendarClock} trend="Next visit pending" />
        <StatCard label="Completed" value={completed} note="Finished visits" accent="emerald" icon={HeartPulse} trend="Historical care" />
        <StatCard label="Care timeline" value="Live" note="Recent reports and health history" accent="medical" icon={ClipboardList} trend="Available now" />
      </div>

      <Card>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Timeline</p>
            <h3 className="mt-2 text-xl font-semibold text-slate-950">Appointment history</h3>
          </div>
          <Badge tone="info">Synced</Badge>
        </div>
        <div className="space-y-3">
          {appointments.slice(0, 5).map((item) => (
            <div key={item.appointment_id} className="flex items-center justify-between rounded-[1.5rem] border border-slate-200/70 bg-slate-50/70 px-4 py-3">
              <div>
                <p className="font-semibold text-slate-950">{item.appointment_date}</p>
                <p className="text-sm text-slate-500">{item.appointment_time}</p>
              </div>
              <Badge>{item.appointment_status}</Badge>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
