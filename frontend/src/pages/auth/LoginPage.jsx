import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShieldCheck, Sparkles, Stethoscope, ArrowRight } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { FormField } from "../../components/shared/FormField";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(form);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen overflow-hidden px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto grid min-h-[calc(100vh-3rem)] max-w-7xl gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="relative overflow-hidden rounded-[2.25rem] border border-white/75 bg-gradient-to-br from-brand-50 via-white to-medical-50 p-8 text-slate-900 shadow-2xl">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(44,162,142,0.14),_transparent_28%),radial-gradient(circle_at_bottom_left,_rgba(46,145,223,0.12),_transparent_30%)]" />
          <div className="relative flex h-full flex-col justify-between gap-10">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/80 backdrop-blur">
                <ShieldCheck className="h-6 w-6 text-brand-700" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-700">Medlink</p>
                <p className="text-sm text-slate-500">Hospital management platform</p>
              </div>
            </div>

            <div className="max-w-xl space-y-6">
              <div className="inline-flex items-center gap-2 rounded-full border border-emerald-100 bg-white/80 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.2em] text-brand-700">
                <Sparkles className="h-3.5 w-3.5" />
                Premium care experience
              </div>
              <h1 className="text-4xl font-semibold tracking-[-0.05em] text-balance md:text-6xl">
                A calmer, faster way to run modern healthcare.
              </h1>
              <p className="max-w-2xl text-base leading-7 text-slate-600 md:text-lg">
                Secure access to dashboards, EHR workflows, predictive intelligence, and operational control in one polished workspace.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              {[
                ["Role-aware", "Doctor, patient, staff, and admin views"],
                ["AI-assisted", "Decision support with clear confidence signals"],
                ["Built for speed", "Fast navigation with a premium glass UI"],
              ].map(([title, description]) => (
                <div key={title} className="rounded-[1.5rem] border border-emerald-100 bg-white/85 p-4 backdrop-blur">
                  <p className="text-sm font-semibold text-slate-950">{title}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="flex items-center">
          <div className="w-full rounded-[2.25rem] border border-white/75 bg-white/86 p-6 shadow-soft ring-1 ring-emerald-900/5 backdrop-blur-xl sm:p-8">
            <div className="mb-8 flex items-center gap-3">
              <div className="rounded-2xl bg-brand-50 p-3 text-brand-700">
                <Stethoscope className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-brand-700">Secure sign in</p>
                <p className="text-sm text-slate-500">Access the healthcare operations platform</p>
              </div>
            </div>

            <h2 className="text-3xl font-semibold tracking-[-0.04em] text-slate-950">Welcome back.</h2>
            <p className="mt-3 max-w-md text-sm leading-6 text-slate-500">
              Sign in to continue monitoring patients, reviewing records, and coordinating care.
            </p>

            <form className="mt-8 space-y-5" onSubmit={onSubmit}>
              <FormField label="Email">
                <Input type="email" autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
              </FormField>
              <FormField label="Password">
                <Input
                  type="password"
                  autoComplete="current-password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                />
              </FormField>
              {error ? <p className="text-sm font-medium text-rose-600">{error}</p> : null}
              <Button type="submit" className="w-full" disabled={loading} size="lg">
                {loading ? "Signing in..." : "Continue to dashboard"}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </form>

            <p className="mt-6 text-sm text-slate-500">
              New here?{" "}
              <Link className="font-semibold text-brand-700 transition hover:text-brand-800 hover:underline" to="/register">
                Create an account
              </Link>
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
