export function FullPageLoader() {
  return (
    <div className="grid min-h-screen place-items-center bg-hero-radial px-6">
      <div className="glass-card animate-fadeUp max-w-sm rounded-[1.75rem] border border-white/70 px-6 py-5 shadow-soft">
        <p className="text-sm font-medium text-slate-600">Loading the healthcare platform...</p>
        <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
          <div className="h-full w-2/3 rounded-full bg-gradient-to-r from-brand-500 via-medical-500 to-emerald-500" />
        </div>
      </div>
    </div>
  );
}
