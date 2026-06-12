import { useEffect, useState } from "react";
import { operationsApi } from "../../api/operations";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Button } from "../../components/ui/Button";
import { Textarea } from "../../components/ui/Textarea";
import { Select } from "../../components/ui/Select";

export function EmergencyPage() {
  const [alerts, setAlerts] = useState([]);
  const [form, setForm] = useState({ alert_type: "", severity: "High", recipient: "", message: "" });
  const [signalForm, setSignalForm] = useState({ oxygen_level: "", icu_occupancy: "", bed_availability: "", emergency_patient_arrival: false, equipment_failure: false });

  const load = async () => {
    const { data } = await operationsApi.alerts();
    setAlerts(data);
  };

  useEffect(() => {
    load();
  }, []);

  const createAlert = async () => {
    await operationsApi.createAlert(form);
    setForm({ alert_type: "", severity: "High", recipient: "", message: "" });
    await load();
  };

  const detect = async () => {
    const { data } = await operationsApi.detectAlerts({
      oxygen_level: signalForm.oxygen_level ? Number(signalForm.oxygen_level) : undefined,
      icu_occupancy: signalForm.icu_occupancy ? Number(signalForm.icu_occupancy) : undefined,
      bed_availability: signalForm.bed_availability ? Number(signalForm.bed_availability) : undefined,
      emergency_patient_arrival: signalForm.emergency_patient_arrival,
      equipment_failure: signalForm.equipment_failure,
    });
    if (data?.length) {
      await load();
    }
  };

  const columns = [
    { key: "alert_id", label: "ID" },
    { key: "alert_type", label: "Type" },
    { key: "severity", label: "Severity" },
    { key: "recipient", label: "Recipient" },
    { key: "timestamp", label: "Timestamp" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Emergency Dashboard" subtitle="Critical events and alert review." />
      <Card>
        <div className="grid gap-4 md:grid-cols-2">
          <Input placeholder="Alert type" value={form.alert_type} onChange={(e) => setForm({ ...form, alert_type: e.target.value })} />
          <Select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Critical</option>
          </Select>
          <Input placeholder="Recipient" value={form.recipient} onChange={(e) => setForm({ ...form, recipient: e.target.value })} />
          <Textarea placeholder="Message" rows="2" value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
          <div className="md:col-span-2">
            <Button type="button" onClick={createAlert}>Create Alert</Button>
          </div>
        </div>
      </Card>

      <Card>
        <div className="grid gap-4 md:grid-cols-2">
          <Input placeholder="Oxygen level" type="number" value={signalForm.oxygen_level} onChange={(e) => setSignalForm({ ...signalForm, oxygen_level: e.target.value })} />
          <Input placeholder="ICU occupancy %" type="number" value={signalForm.icu_occupancy} onChange={(e) => setSignalForm({ ...signalForm, icu_occupancy: e.target.value })} />
          <Input placeholder="Bed availability %" type="number" value={signalForm.bed_availability} onChange={(e) => setSignalForm({ ...signalForm, bed_availability: e.target.value })} />
          <div className="flex flex-wrap items-center gap-3">
            <label className="flex items-center gap-2 text-sm text-slate-600">
              <input type="checkbox" checked={signalForm.emergency_patient_arrival} onChange={(e) => setSignalForm({ ...signalForm, emergency_patient_arrival: e.target.checked })} />
              Emergency arrival
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-600">
              <input type="checkbox" checked={signalForm.equipment_failure} onChange={(e) => setSignalForm({ ...signalForm, equipment_failure: e.target.checked })} />
              Equipment failure
            </label>
          </div>
          <div className="md:col-span-2">
            <Button type="button" onClick={detect}>Run Detection</Button>
          </div>
        </div>
      </Card>
      <DataTable columns={columns} rows={alerts} emptyText="No emergency alerts found." />
    </div>
  );
}
