import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { patientsApi } from "../../api/patients";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Card } from "../../components/ui/Card";

export function PatientProfilePage() {
  const { patientId } = useParams();
  const [patient, setPatient] = useState(null);

  useEffect(() => {
    patientsApi.get(patientId).then((res) => setPatient(res.data));
  }, [patientId]);

  return (
    <div className="space-y-6">
      <SectionHeader title="Patient Profile" subtitle="Clinical and administrative summary." />
      <Card>
        {patient ? (
          <dl className="grid gap-4 sm:grid-cols-2">
            <ProfileItem label="Full name" value={patient.full_name} />
            <ProfileItem label="Age" value={patient.age} />
            <ProfileItem label="Gender" value={patient.gender} />
            <ProfileItem label="Blood group" value={patient.blood_group} />
            <ProfileItem label="Emergency contact" value={patient.emergency_contact} />
            <ProfileItem label="Insurance provider" value={patient.insurance_provider} />
          </dl>
        ) : (
          <p className="text-sm text-slate-500">Loading patient profile...</p>
        )}
      </Card>
    </div>
  );
}

function ProfileItem({ label, value }) {
  return (
    <div className="rounded-2xl bg-slate-50 p-4">
      <dt className="text-xs font-semibold uppercase tracking-[0.15em] text-slate-500">{label}</dt>
      <dd className="mt-1 text-sm font-medium text-slate-900">{value || "Not provided"}</dd>
    </div>
  );
}

