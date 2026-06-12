export function StatCard({ label, value, note, accent = "brand", trend, icon: Icon }) {
  const accentStyles = {
    brand: "from-brand-50 via-white to-white text-brand-700 ring-brand-100",
    medical: "from-cyan-50 via-white to-white text-cyan-700 ring-cyan-100",
    emerald: "from-emerald-50 via-white to-white text-emerald-700 ring-emerald-100",
    violet: "from-teal-50 via-white to-white text-teal-700 ring-teal-100",
  };

  return (
    <div className={`theme-surface rounded-[2rem] bg-gradient-to-br p-5 ${accentStyles[accent] || accentStyles.brand}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-[-0.05em] text-slate-950">{value}</p>
        </div>
        {Icon ? (
          <div className="rounded-[1.15rem] bg-emerald-50 p-3 text-emerald-700">
            <Icon className="h-5 w-5" />
          </div>
        ) : null}
      </div>
      {(trend || note) ? (
        <div className="mt-4 space-y-1">
          {trend ? <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-600">{trend}</p> : null}
          {note ? <p className="text-xs leading-5 text-slate-500">{note}</p> : null}
        </div>
      ) : null}
    </div>
  );
}
