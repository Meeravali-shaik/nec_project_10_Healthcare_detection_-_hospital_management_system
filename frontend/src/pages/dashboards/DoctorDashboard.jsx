import { useEffect, useState } from "react";
import { appointmentsApi } from "../../api/appointments";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { StatCard } from "../../components/shared/StatCard";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { Activity, CalendarClock, CheckCircle2, Clock3 } from "lucide-react";

export function DoctorDashboard() {
  const [appointments, setAppointments] = useState([]);

  useEffect(() => {
    appointmentsApi.list().then((res) => setAppointments(res.data));
  }, []);

  const pending = appointments.filter((item) => item.appointment_status === "Pending").length;
  const approved = appointments.filter((item) => item.appointment_status === "Approved").length;
  const completed = appointments.filter((item) => item.appointment_status === "Completed").length;

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Doctor workspace"
        subtitle="A fast, focused dashboard for reviewing appointments, approvals, and the daily patient queue."
      />

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Pending" value={pending} note="Appointments awaiting approval" accent="violet" icon={Clock3} trend="Needs attention" />
        <StatCard label="Approved" value={approved} note="Confirmed schedule entries" accent="medical" icon={CheckCircle2} trend="Ready for consult" />
        <StatCard label="Completed" value={completed} note="Finished visits" accent="emerald" icon={Activity} trend="Closing the loop" />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Queue</p>
              <h3 className="mt-2 text-xl font-semibold text-slate-950">Recent appointments</h3>
            </div>
            <Badge tone="info">Live</Badge>
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
            {!appointments.length ? <p className="text-sm text-slate-500">No appointments queued.</p> : null}
          </div>
        </Card>

        <Card>
          <div className="mb-4 flex items-center gap-3">
            <div className="rounded-2xl bg-brand-50 p-3 text-brand-700">
              <CalendarClock className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Clinical rhythm</p>
              <h3 className="mt-2 text-xl font-semibold text-slate-950">Daily focus</h3>
            </div>
          </div>
          <div className="space-y-3">
            {[
              "Review high-priority follow-ups before the morning clinic.",
              "Approve or decline appointment requests in one pass.",
              "Use EHR summaries to reduce clicks during rounds.",
            ].map((item) => (
              <div key={item} className="rounded-[1.25rem] border border-slate-200/70 bg-white/80 p-4 text-sm leading-6 text-slate-600">
                {item}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
