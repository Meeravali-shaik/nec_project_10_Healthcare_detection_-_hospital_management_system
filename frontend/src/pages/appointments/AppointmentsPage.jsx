import { useEffect, useState } from "react";
import { appointmentsApi } from "../../api/appointments";
import { doctorsApi } from "../../api/doctors";
import { patientsApi } from "../../api/patients";
import { useAuth } from "../../context/AuthContext";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Textarea } from "../../components/ui/Textarea";
import { Button } from "../../components/ui/Button";
import { DataTable } from "../../components/shared/DataTable";
import { Badge } from "../../components/ui/Badge";
import { CalendarClock, ClipboardList, Sparkles, Users } from "lucide-react";

const statusOptions = ["Pending", "Approved", "Rejected", "Completed", "Cancelled"];

export function AppointmentsPage() {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({
    patient_id: "",
    doctor_id: "",
    appointment_date: "",
    appointment_time: "",
    notes: "",
  });

  const load = async () => {
    const requests = [appointmentsApi.list(), doctorsApi.list()];
    if (user?.role !== "Patient") {
      requests.push(patientsApi.list());
    }
    const responses = await Promise.all(requests);
    const [appointmentsRes, doctorsRes, patientsRes] = responses;
    setAppointments(appointmentsRes.data);
    setDoctors(doctorsRes.data);
    setPatients(patientsRes?.data || []);
  };

  useEffect(() => {
    load();
  }, [user?.role]);

  const onCreate = async (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      patient_id: form.patient_id ? Number(form.patient_id) : undefined,
      doctor_id: Number(form.doctor_id),
    };
    if (editingId) {
      await appointmentsApi.update(editingId, payload);
    } else {
      await appointmentsApi.create(payload);
    }
    setEditingId(null);
    setForm({ patient_id: "", doctor_id: "", appointment_date: "", appointment_time: "", notes: "" });
    await load();
  };

  const columns = [
    { key: "appointment_id", label: "ID" },
    { key: "appointment_date", label: "Date" },
    { key: "appointment_time", label: "Time" },
    { key: "appointment_status", label: "Status", render: (row) => <Badge>{row.appointment_status}</Badge> },
    {
      key: "actions",
      label: "Actions",
      render: (row) => (
        <div className="flex gap-3">
          <button type="button" className="font-medium text-slate-700 hover:underline" onClick={() => startEdit(row)}>
            Edit
          </button>
          <button type="button" className="font-medium text-rose-600 hover:underline" onClick={() => appointmentsApi.remove(row.appointment_id).then(load)}>
            Cancel
          </button>
        </div>
      ),
    },
  ];

  const startEdit = (row) => {
    setEditingId(row.appointment_id);
    setForm({
      patient_id: row.patient_id ?? "",
      doctor_id: row.doctor_id ?? "",
      appointment_date: row.appointment_date ?? "",
      appointment_time: row.appointment_time ?? "",
      notes: row.notes ?? "",
    });
  };

  const statusAction = async (appointmentId, appointmentStatus) => {
    await appointmentsApi.changeStatus(appointmentId, { appointment_status: appointmentStatus });
    await load();
  };

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Appointment management"
        subtitle="Book, review, and manage hospital visits in a clean, high-contrast workspace."
      />

      <section className="grid gap-4 md:grid-cols-3">
        {[
          { label: "Scheduled visits", value: appointments.length, icon: CalendarClock, note: "All appointments loaded" },
          { label: "Doctors available", value: doctors.length, icon: Users, note: "Choose from current roster" },
          { label: "Quick actions", value: "Live", icon: Sparkles, note: "Book and update in one view" },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.label}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-slate-500">{item.label}</p>
                  <p className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-slate-950">{item.value}</p>
                </div>
                <div className="rounded-[1.15rem] bg-brand-50 p-3 text-brand-700">
                  <Icon className="h-5 w-5" />
                </div>
              </div>
              <p className="mt-4 text-sm leading-6 text-slate-500">{item.note}</p>
            </Card>
          );
        })}
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <div className="mb-6 flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Booking form</p>
              <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
                {editingId ? "Edit appointment" : "Create appointment"}
              </h3>
            </div>
            <Badge tone="info">{editingId ? "Editing" : "New"}</Badge>
          </div>

          <form className="grid gap-4 md:grid-cols-2" onSubmit={onCreate}>
            {user?.role !== "Patient" ? (
              <label className="space-y-1.5 md:col-span-2">
                <span className="text-sm font-medium text-slate-700">Patient</span>
                <Select value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })}>
                  <option value="">Select patient</option>
                  {patients.map((patient) => (
                    <option key={patient.patient_id} value={patient.patient_id}>
                      {patient.full_name}
                    </option>
                  ))}
                </Select>
              </label>
            ) : null}
            <label className="space-y-1.5">
              <span className="text-sm font-medium text-slate-700">Doctor</span>
              <Select value={form.doctor_id} onChange={(e) => setForm({ ...form, doctor_id: e.target.value })}>
                <option value="">Select doctor</option>
                {doctors.map((doctor) => (
                  <option key={doctor.doctor_id} value={doctor.doctor_id}>
                    {doctor.full_name}
                  </option>
                ))}
              </Select>
            </label>
            <label className="space-y-1.5">
              <span className="text-sm font-medium text-slate-700">Date</span>
              <Input type="date" value={form.appointment_date} onChange={(e) => setForm({ ...form, appointment_date: e.target.value })} />
            </label>
            <label className="space-y-1.5">
              <span className="text-sm font-medium text-slate-700">Time</span>
              <Input type="time" value={form.appointment_time} onChange={(e) => setForm({ ...form, appointment_time: e.target.value })} />
            </label>
            <label className="space-y-1.5 md:col-span-2">
              <span className="text-sm font-medium text-slate-700">Notes</span>
              <Textarea rows="4" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
            </label>
            <div className="md:col-span-2 flex flex-wrap gap-3 pt-2">
              <Button type="submit">{editingId ? "Update Appointment" : "Book Appointment"}</Button>
              {editingId ? (
                <Button type="button" variant="secondary" onClick={() => setEditingId(null)}>
                  Cancel Edit
                </Button>
              ) : null}
            </div>
          </form>
        </Card>

        <div className="space-y-6">
          {user?.role === "Doctor" || user?.role === "Admin" || user?.role === "Hospital Staff" ? (
            <Card>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Approval queue</p>
                  <h3 className="mt-2 text-xl font-semibold text-slate-950">Quick actions</h3>
                </div>
                <Badge tone="success">Ready</Badge>
              </div>
              <div className="space-y-3">
                {appointments.slice(0, 5).map((item) => (
                  <div key={item.appointment_id} className="rounded-[1.4rem] border border-emerald-100 bg-white/95 p-4">
                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                      <div>
                        <p className="font-semibold text-slate-950">Appointment #{item.appointment_id}</p>
                        <p className="text-sm text-slate-500">
                          {item.appointment_date} at {item.appointment_time}
                        </p>
                      </div>
                      <Badge>{item.appointment_status}</Badge>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {statusOptions.map((status) => (
                        <Button key={status} variant="outline" onClick={() => statusAction(item.appointment_id, status)} type="button" size="sm">
                          {status}
                        </Button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ) : null}

          <Card>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Overview</p>
                <h3 className="mt-2 text-xl font-semibold text-slate-950">Appointment notes</h3>
              </div>
              <ClipboardList className="h-5 w-5 text-slate-400" />
            </div>
            <p className="text-sm leading-6 text-slate-600">
              The refreshed theme keeps the workflow familiar while making the booking screen easier to read and scan.
            </p>
          </Card>
        </div>
      </div>

      <DataTable columns={columns} rows={appointments} emptyText="No appointments found." />
    </div>
  );
}
