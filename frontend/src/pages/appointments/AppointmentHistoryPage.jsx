import { Link } from "react-router-dom";
import { ArrowRight, Clock3 } from "lucide-react";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";

export function AppointmentHistoryPage() {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="Appointment history"
        subtitle="A focused historical view is coming from the appointments workspace, which now contains the live booking and approval flow."
      />
      <Card>
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-4">
            <div className="rounded-2xl bg-brand-50 p-3 text-brand-700">
              <Clock3 className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-slate-950">Use the appointments workspace</h3>
              <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-600">
                We preserved the workflow in the main appointments module so history, editing, and approval actions stay in one place.
              </p>
            </div>
          </div>
          <Button as={Link} to="/appointments" variant="primary">
            Open appointments
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </Card>
    </div>
  );
}
