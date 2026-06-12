import { NavLink } from "react-router-dom";
import {
  Activity,
  CalendarClock,
  ChevronRight,
  ClipboardList,
  LayoutDashboard,
  MessageSquareMore,
  ShieldCheck,
  Stethoscope,
  Users,
  X,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { cn } from "../../lib/utils";

const navItemsByRole = {
  Admin: [
    { to: "/dashboard/admin", label: "Overview", icon: LayoutDashboard },
    { to: "/patients", label: "Patients", icon: Users },
    { to: "/doctors", label: "Doctors", icon: Stethoscope },
    { to: "/appointments", label: "Appointments", icon: CalendarClock },
    { to: "/ehr", label: "EHR", icon: ClipboardList },
    { to: "/ai", label: "AI Intelligence", icon: Activity },
    { to: "/assistant", label: "Assistant", icon: MessageSquareMore },
    { to: "/operations", label: "Operations", icon: ShieldCheck },
  ],
  "Hospital Staff": [
    { to: "/dashboard/admin", label: "Overview", icon: LayoutDashboard },
    { to: "/patients", label: "Patients", icon: Users },
    { to: "/doctors", label: "Doctors", icon: Stethoscope },
    { to: "/appointments", label: "Appointments", icon: CalendarClock },
    { to: "/ehr", label: "EHR", icon: ClipboardList },
    { to: "/ai", label: "AI Intelligence", icon: Activity },
    { to: "/assistant", label: "Assistant", icon: MessageSquareMore },
    { to: "/operations", label: "Operations", icon: ShieldCheck },
  ],
  Doctor: [
    { to: "/dashboard/doctor", label: "Overview", icon: LayoutDashboard },
    { to: "/appointments", label: "Appointments", icon: CalendarClock },
    { to: "/ehr", label: "EHR", icon: ClipboardList },
    { to: "/ai", label: "AI Intelligence", icon: Activity },
    { to: "/assistant", label: "Assistant", icon: MessageSquareMore },
    { to: "/operations", label: "Operations", icon: ShieldCheck },
  ],
  Patient: [
    { to: "/dashboard/patient", label: "Overview", icon: LayoutDashboard },
    { to: "/appointments", label: "Appointments", icon: CalendarClock },
    { to: "/ehr", label: "EHR", icon: ClipboardList },
    { to: "/ai", label: "AI Intelligence", icon: Activity },
    { to: "/assistant", label: "Assistant", icon: MessageSquareMore },
    { to: "/operations", label: "Operations", icon: ShieldCheck },
  ],
};

export function Sidebar({ open = false, onClose }) {
  const { user } = useAuth();
  const navItems = navItemsByRole[user?.role] || navItemsByRole.Patient;

  return (
    <>
      <div
        className={cn(
          "fixed inset-0 z-30 bg-slate-950/14 backdrop-blur-sm transition lg:hidden",
          open ? "opacity-100" : "pointer-events-none opacity-0",
        )}
        onClick={onClose}
        aria-hidden="true"
      />

      <aside
        className={cn(
          "fixed left-0 top-0 z-40 h-full w-[300px] border-r border-emerald-100 bg-white/92 shadow-2xl ring-1 ring-emerald-900/5 backdrop-blur-xl transition-transform duration-300 ease-out lg:sticky lg:top-0 lg:z-0 lg:h-screen lg:w-[320px] lg:translate-x-0 lg:self-start",
          open ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex h-full flex-col px-4 py-4">
          <div className="mb-6 flex items-center justify-between gap-3 rounded-[1.75rem] border border-emerald-100 bg-white/95 p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-600 to-medical-500 text-white shadow-soft">
                <Activity className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.22em] text-brand-700">Medlink</p>
                <p className="text-xs text-slate-500">Hospital management</p>
              </div>
            </div>
            <button
              type="button"
              className="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-600 transition hover:bg-slate-50 lg:hidden"
              onClick={onClose}
              aria-label="Close navigation"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="mb-6 rounded-[1.75rem] border border-brand-100 bg-gradient-to-br from-brand-50 via-white to-medical-50 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-brand-700">Signed in as</p>
            <p className="mt-2 text-sm font-semibold text-slate-950">{user?.full_name || "User"}</p>
            <p className="text-sm text-slate-500">{user?.role || "Patient"} access</p>
          </div>

          <nav className="flex-1 space-y-1 overflow-y-auto pr-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={onClose}
                  className={({ isActive }) =>
                    cn(
                      "group flex items-center justify-between rounded-2xl px-4 py-3 text-sm font-medium transition duration-200",
                      isActive
                        ? "bg-gradient-to-r from-brand-600 to-medical-500 text-white shadow-soft"
                        : "text-slate-700 hover:bg-emerald-50/90 hover:text-slate-950",
                    )
                  }
                >
                  <span className="flex items-center gap-3">
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </span>
                  <ChevronRight className="h-4 w-4 opacity-50 transition group-hover:translate-x-0.5" />
                </NavLink>
              );
            })}
          </nav>

          <div className="mt-4 rounded-[1.75rem] border border-emerald-100 bg-white/95 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Platform status</p>
            <div className="mt-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-slate-950">Care operations live</p>
                <p className="text-xs text-slate-500">All core modules connected</p>
              </div>
              <span className="h-3 w-3 rounded-full bg-emerald-500 shadow-[0_0_0_6px_rgba(16,185,129,0.15)]" />
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
