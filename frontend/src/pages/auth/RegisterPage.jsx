import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, ShieldPlus } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { FormField } from "../../components/shared/FormField";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
    phone_number: "",
    role: "Patient",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await register(form);
      navigate("/login", { replace: true });
    } catch (err) {
      const detail = err?.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((item) => `${item?.loc?.slice?.(-1)?.[0] || "field"}: ${item?.msg || "invalid"}`).join(" | "));
      } else {
        setError(detail || "Registration failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen overflow-hidden px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto grid min-h-[calc(100vh-3rem)] max-w-7xl gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <section className="order-2 flex items-center lg:order-1">
          <div className="w-full rounded-[2.25rem] border border-white/75 bg-white/86 p-6 shadow-soft ring-1 ring-emerald-900/5 backdrop-blur-xl sm:p-8">
            <div className="mb-8 flex items-center gap-3">
              <div className="rounded-2xl bg-emerald-50 p-3 text-emerald-700">
                <ShieldPlus className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-700">Create access</p>
                <p className="text-sm text-slate-500">Join the hospital management platform</p>
              </div>
            </div>

            <h2 className="text-3xl font-semibold tracking-[-0.04em] text-slate-950">Create your account.</h2>
            <p className="mt-3 max-w-md text-sm leading-6 text-slate-500">
              Set up a secure workspace for your role, whether you are a patient, clinician, or administrator.
            </p>

            <form className="mt-8 grid gap-5" onSubmit={onSubmit}>
              <FormField label="Full name">
                <Input required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
              </FormField>
              <FormField label="Email">
                <Input required type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </FormField>
              <FormField label="Phone number">
                <Input value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} />
              </FormField>
              <FormField label="Role">
                <Select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                  <option value="Patient">Patient</option>
                  <option value="Doctor">Doctor</option>
                  <option value="Hospital Staff">Hospital Staff</option>
                  <option value="Admin">Admin</option>
                </Select>
              </FormField>
              <FormField label="Password">
                <Input required minLength={8} type="password" autoComplete="new-password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
              </FormField>
              {error ? <p className="text-sm font-medium text-rose-600">{error}</p> : null}
              <Button type="submit" className="w-full" disabled={loading} size="lg">
                {loading ? "Creating account..." : "Create account"}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </form>

            <p className="mt-6 text-sm text-slate-500">
              Already have an account?{" "}
              <Link className="font-semibold text-brand-700 transition hover:text-brand-800 hover:underline" to="/login">
                Sign in
              </Link>
            </p>
          </div>
        </section>

        <section className="order-1 relative overflow-hidden rounded-[2.25rem] border border-white/75 bg-gradient-to-br from-brand-50 via-white to-medical-50 p-8 text-slate-900 shadow-2xl lg:order-2">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(44,162,142,0.14),_transparent_28%),radial-gradient(circle_at_bottom_right,_rgba(46,145,223,0.12),_transparent_30%)]" />
          <div className="relative flex h-full flex-col justify-between gap-10">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-700">Trusted access</p>
              <h1 className="mt-5 text-4xl font-semibold tracking-[-0.05em] text-balance md:text-6xl">
                Bring every care workflow into one premium operating system.
              </h1>
              <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600 md:text-lg">
                Purpose-built for healthcare teams that need clarity, speed, and confidence across operations, EHR, AI, and patient care.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {[
                ["Role-specific", "Tailored dashboards for every user type"],
                ["Clinical grade", "Built around safety, clarity, and auditability"],
                ["Investor ready", "A portfolio-grade, enterprise visual system"],
              ].map(([title, description]) => (
                <div key={title} className="rounded-[1.5rem] border border-emerald-100 bg-white/85 p-4 backdrop-blur">
                  <p className="text-sm font-semibold text-slate-950">{title}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
