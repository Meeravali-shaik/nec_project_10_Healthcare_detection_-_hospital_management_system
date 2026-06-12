import { useEffect, useState } from "react";
import { operationsApi } from "../../api/operations";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { DataTable } from "../../components/shared/DataTable";
import { StatCard } from "../../components/shared/StatCard";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Button } from "../../components/ui/Button";

export function BedsPage() {
  const [beds, setBeds] = useState([]);
  const [wards, setWards] = useState([]);
  const [analytics, setAnalytics] = useState({ total_beds: 0, occupancy_rate: 0, by_status: {}, by_type: {} });
  const [form, setForm] = useState({ ward_id: "", bed_number: "", bed_type: "General Ward Bed", status: "Available" });
  const [actionForm, setActionForm] = useState({ bed_id: "", patient_id: "", admission_date: "", discharge_date: "", transfer_date: "", target_bed_id: "" });

  const load = async () => {
    const [bedsRes, wardsRes, analyticsRes] = await Promise.all([operationsApi.beds(), operationsApi.wards(), operationsApi.bedAnalytics()]);
    setBeds(bedsRes.data);
    setWards(wardsRes.data);
    setAnalytics(analyticsRes.data);
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    await operationsApi.createBed({
      ward_id: Number(form.ward_id),
      bed_number: form.bed_number,
      bed_type: form.bed_type,
      status: form.status,
    });
    await load();
  };

  const selectedBedId = Number(actionForm.bed_id);

  const handleAllocate = async () => {
    if (!selectedBedId || !actionForm.patient_id || !actionForm.admission_date) return;
    await operationsApi.allocateBed(selectedBedId, {
      patient_id: Number(actionForm.patient_id),
      admission_date: actionForm.admission_date,
    });
    await load();
  };

  const handleReserve = async () => {
    if (!selectedBedId) return;
    await operationsApi.reserveBed(selectedBedId, {
      patient_id: actionForm.patient_id ? Number(actionForm.patient_id) : undefined,
      reservation_date: actionForm.admission_date || undefined,
    });
    await load();
  };

  const handleDischarge = async () => {
    if (!selectedBedId || !actionForm.discharge_date) return;
    await operationsApi.dischargeBed(selectedBedId, {
      discharge_date: actionForm.discharge_date,
    });
    await load();
  };

  const handleTransfer = async () => {
    if (!selectedBedId || !actionForm.target_bed_id || !actionForm.transfer_date) return;
    await operationsApi.transferBed(selectedBedId, {
      target_bed_id: Number(actionForm.target_bed_id),
      patient_id: actionForm.patient_id ? Number(actionForm.patient_id) : undefined,
      transfer_date: actionForm.transfer_date,
    });
    await load();
  };

  const columns = [
    { key: "bed_id", label: "ID" },
    { key: "ward_id", label: "Ward" },
    { key: "bed_number", label: "Bed No" },
    { key: "bed_type", label: "Type" },
    { key: "status", label: "Status" },
    { key: "patient_id", label: "Patient" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader title="Bed Management" subtitle="Track bed availability and allocation." />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Beds" value={analytics.total_beds} />
        <StatCard label="Occupancy" value={`${analytics.occupancy_rate}%`} />
        <StatCard label="Occupied" value={analytics.by_status?.Occupied ?? 0} />
        <StatCard label="Reserved" value={analytics.by_status?.Reserved ?? 0} />
      </div>
      <Card>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
          <Select value={form.ward_id} onChange={(e) => setForm({ ...form, ward_id: e.target.value })}>
            <option value="">Select ward</option>
            {wards.map((ward) => (
              <option key={ward.ward_id} value={ward.ward_id}>{ward.ward_name}</option>
            ))}
          </Select>
          <Input placeholder="Bed number" value={form.bed_number} onChange={(e) => setForm({ ...form, bed_number: e.target.value })} />
          <Select value={form.bed_type} onChange={(e) => setForm({ ...form, bed_type: e.target.value })}>
            <option>General Ward Bed</option>
            <option>ICU Bed</option>
            <option>Emergency Bed</option>
            <option>Isolation Bed</option>
            <option>Pediatric Bed</option>
          </Select>
          <Select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
            <option>Available</option>
            <option>Occupied</option>
            <option>Reserved</option>
            <option>Maintenance</option>
          </Select>
          <div className="md:col-span-2">
            <Button type="submit">Create Bed</Button>
          </div>
        </form>
      </Card>

      <Card>
        <h3 className="mb-4 text-lg font-semibold text-slate-900">Bed Actions</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <Select value={actionForm.bed_id} onChange={(e) => setActionForm({ ...actionForm, bed_id: e.target.value })}>
            <option value="">Select bed</option>
            {beds.map((bed) => (
              <option key={bed.bed_id} value={bed.bed_id}>
                {bed.bed_number} - {bed.status}
              </option>
            ))}
          </Select>
          <Input placeholder="Patient ID" value={actionForm.patient_id} onChange={(e) => setActionForm({ ...actionForm, patient_id: e.target.value })} />
          <Input type="date" placeholder="Admission / Reservation date" value={actionForm.admission_date} onChange={(e) => setActionForm({ ...actionForm, admission_date: e.target.value })} />
          <Input type="date" placeholder="Discharge date" value={actionForm.discharge_date} onChange={(e) => setActionForm({ ...actionForm, discharge_date: e.target.value })} />
          <Select value={actionForm.target_bed_id} onChange={(e) => setActionForm({ ...actionForm, target_bed_id: e.target.value })}>
            <option value="">Select transfer target</option>
            {beds.filter((bed) => String(bed.bed_id) !== actionForm.bed_id).map((bed) => (
              <option key={bed.bed_id} value={bed.bed_id}>
                {bed.bed_number} - {bed.status}
              </option>
            ))}
          </Select>
          <Input type="date" placeholder="Transfer date" value={actionForm.transfer_date} onChange={(e) => setActionForm({ ...actionForm, transfer_date: e.target.value })} />
          <div className="flex flex-wrap gap-3 md:col-span-2">
            <Button type="button" onClick={handleAllocate}>Allocate</Button>
            <Button type="button" onClick={handleReserve}>Reserve</Button>
            <Button type="button" onClick={handleDischarge}>Discharge</Button>
            <Button type="button" onClick={handleTransfer}>Transfer</Button>
          </div>
        </div>
      </Card>

      <DataTable columns={columns} rows={beds} emptyText="No beds found." />
    </div>
  );
}
