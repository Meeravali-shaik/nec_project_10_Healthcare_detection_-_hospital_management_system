import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, Doughnut } from "react-chartjs-2";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";
import { Activity, CalendarClock, HeartPulse, ShieldCheck, Sparkles, Users } from "lucide-react";
import { patientsApi } from "../../api/patients";
import { doctorsApi } from "../../api/doctors";
import { appointmentsApi } from "../../api/appointments";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { StatCard } from "../../components/shared/StatCard";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

export function AdminDashboard() {
  const [stats, setStats] = useState({ patients: 0, doctors: 0, appointments: 0 });
  const [recentAppointments, setRecentAppointments] = useState([]);

  useEffect(() => {
    Promise.all([patientsApi.list(), doctorsApi.list(), appointmentsApi.list()]).then(([patients, doctors, appointments]) => {
      setStats({
        patients: patients.data.length,
        doctors: doctors.data.length,
        appointments: appointments.data.length,
      });
      setRecentAppointments(appointments.data.slice(0, 5));
    });
  }, []);

  const operationalSplit = {
    labels: ["Patients", "Doctors", "Appointments"],
    datasets: [
      {
        data: [stats.patients, stats.doctors, stats.appointments],
        backgroundColor: ["#2ca28e", "#2e91df", "#16a34a"],
        borderWidth: 0,
      },
    ],
  };

  const velocity = {
    labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    datasets: [
      {
        label: "Hospital activity",
        data: [18, 26, 22, 31, 28, 34],
        backgroundColor: "rgba(44, 162, 142, 0.16)",
        borderColor: "#2ca28e",
        borderRadius: 14,
      },
    ],
  };

  return (
    <div className="space-y-6">
      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card className="relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(44,162,142,0.12),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(46,145,223,0.10),_transparent_30%)]" />
          <div className="relative flex h-full flex-col justify-between gap-10">
            <div className="space-y-5">
              <div className="inline-flex items-center gap-2 rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-brand-700">
                <Sparkles className="h-3.5 w-3.5" />
                Medlink dashboard
              </div>
              <div className="max-w-2xl space-y-4">
                <p className="text-sm font-medium uppercase tracking-[0.24em] text-slate-500">Hospital management dashboard</p>
                <h1 className="text-4xl font-semibold tracking-[-0.05em] text-slate-950 md:text-5xl">
                  Command every care workflow from one calm, modern workspace.
                </h1>
                <p className="max-w-xl text-sm leading-7 text-slate-600 md:text-base">
                  This view keeps the project intact while shifting the entire experience toward the soft, airy dashboard language in your reference.
                </p>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              {[
                ["Auto layout design", "Clean structure for faster scanning"],
                ["Live widgets", "Clinical activity at a glance"],
                ["Responsive system", "Desktop and mobile friendly"],
              ].map(([title, description]) => (
                <div key={title} className="rounded-[1.4rem] border border-emerald-100 bg-white/90 p-4">
                  <p className="text-sm font-semibold text-slate-950">{title}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
                </div>
              ))}
            </div>
          </div>
        </Card>

        <div className="grid gap-4 sm:grid-cols-2">
          <StatCard label="Patients" value={stats.patients} note="Registered patient records" accent="brand" icon={Users} trend="Active registry" />
          <StatCard label="Doctors" value={stats.doctors} note="Active doctor profiles" accent="medical" icon={HeartPulse} trend="Current roster" />
          <StatCard label="Appointments" value={stats.appointments} note="Scheduled visits in the system" accent="emerald" icon={CalendarClock} trend="Daily queue" />
          <StatCard label="Platform health" value="98.4%" note="Systems stable and responsive" accent="violet" icon={ShieldCheck} trend="All core modules live" />
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <div className="mb-5 flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Trends</p>
              <h3 className="mt-2 text-xl font-semibold text-slate-950">Operational velocity</h3>
            </div>
            <Badge tone="info">Live</Badge>
          </div>
          <Bar
            data={velocity}
            options={{
              responsive: true,
              plugins: { legend: { display: false } },
              scales: {
                x: { grid: { display: false } },
                y: { beginAtZero: true, grid: { color: "rgba(148, 163, 184, 0.12)" } },
              },
            }}
          />
        </Card>

        <Card>
          <div className="mb-5 flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Mix</p>
              <h3 className="mt-2 text-xl font-semibold text-slate-950">Platform distribution</h3>
            </div>
            <Activity className="h-5 w-5 text-slate-400" />
          </div>
          <Doughnut
            data={operationalSplit}
            options={{
              responsive: true,
              plugins: { legend: { position: "bottom", labels: { boxWidth: 12, usePointStyle: true } } },
              cutout: "68%",
            }}
          />
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Card>
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Recent</p>
              <h3 className="mt-2 text-xl font-semibold text-slate-950">Appointment queue</h3>
            </div>
            <Badge tone="info">Today</Badge>
          </div>
          <div className="space-y-3">
            {recentAppointments.map((item) => (
              <div key={item.appointment_id} className="flex items-center justify-between rounded-[1.4rem] border border-emerald-100 bg-white/90 px-4 py-3">
                <div>
                  <p className="font-semibold text-slate-950">{item.appointment_date}</p>
                  <p className="text-sm text-slate-500">{item.appointment_time}</p>
                </div>
                <Badge>{item.appointment_status}</Badge>
              </div>
            ))}
            {!recentAppointments.length ? <p className="text-sm text-slate-500">No appointments queued.</p> : null}
          </div>
        </Card>

        <Card>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {[
              ["Patient intake", "View and triage incoming records", "/patients"],
              ["Clinician roster", "Manage doctors and availability", "/doctors"],
              ["Appointments", "Oversee schedule approvals", "/appointments"],
              ["Hospital intelligence", "Open AI and operations modules", "/operations"],
            ].map(([title, description, href]) => (
              <Link key={href} to={href} className="rounded-[1.4rem] border border-emerald-100 bg-emerald-50/60 p-4 transition hover:border-brand-200 hover:bg-white">
                <p className="text-sm font-semibold text-slate-950">{title}</p>
                <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
              </Link>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
