import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ClipboardList, Pill, FlaskConical, HeartPulse, Syringe, ShieldAlert } from "lucide-react";
import { ehrApi } from "../../api/ehr";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { StatCard } from "../../components/shared/StatCard";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";

export function EhrDashboard() {
  const [stats, setStats] = useState({
    records: 0,
    prescriptions: 0,
    reports: 0,
    treatments: 0,
    vaccinations: 0,
    allergies: 0,
  });

  useEffect(() => {
    Promise.all([
      ehrApi.medicalRecords({ page: 1, size: 1 }),
      ehrApi.prescriptions({ page: 1, size: 1 }),
      ehrApi.labReports({ page: 1, size: 1 }),
      ehrApi.treatments({ page: 1, size: 1 }),
      ehrApi.vaccinations({ page: 1, size: 1 }),
      ehrApi.allergies({ page: 1, size: 1 }),
    ]).then(([records, prescriptions, reports, treatments, vaccinations, allergies]) => {
      setStats({
        records: records.data.meta.total,
        prescriptions: prescriptions.data.meta.total,
        reports: reports.data.meta.total,
        treatments: treatments.data.meta.total,
        vaccinations: vaccinations.data.meta.total,
        allergies: allergies.data.meta.total,
      });
    });
  }, []);

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Electronic health records"
        subtitle="A clinical record center with quick access to encounters, prescriptions, lab reports, and patient history."
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard label="Medical Records" value={stats.records} accent="brand" icon={ClipboardList} />
        <StatCard label="Prescriptions" value={stats.prescriptions} accent="medical" icon={Pill} />
        <StatCard label="Lab Reports" value={stats.reports} accent="emerald" icon={FlaskConical} />
        <StatCard label="Treatments" value={stats.treatments} accent="violet" icon={HeartPulse} />
        <StatCard label="Vaccinations" value={stats.vaccinations} accent="brand" icon={Syringe} />
        <StatCard label="Allergies" value={stats.allergies} accent="medical" icon={ShieldAlert} />
      </div>
      <Card>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/ehr/medical-records">
            Medical Records
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/ehr/prescriptions">
            Prescriptions
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/ehr/lab-reports">
            Lab Reports
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/ehr/treatments">
            Treatments
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/ehr/vaccinations">
            Vaccinations
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-50 px-4 py-3 font-medium text-brand-800 transition hover:bg-brand-100" to="/ehr/allergies">
            Allergies
          </Link>
          <Link className="rounded-[1.5rem] bg-brand-600 px-4 py-3 font-medium text-white transition hover:bg-brand-700" to="/ehr/timeline">
            Patient Timeline
          </Link>
        </div>
      </Card>
      <Card>
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-brand-700">Clinical safety</p>
            <h3 className="mt-2 text-xl font-semibold text-slate-950">Record quality signals</h3>
          </div>
          <Badge tone="success">Normal</Badge>
        </div>
        <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-600">
          The EHR workspace centralizes longitudinal patient data so clinicians can move faster without losing context.
        </p>
      </Card>
    </div>
  );
}
