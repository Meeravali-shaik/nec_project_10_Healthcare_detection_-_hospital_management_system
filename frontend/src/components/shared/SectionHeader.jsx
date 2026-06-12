export function SectionHeader({ title, subtitle, action }) {
  return (
    <section className="theme-surface relative overflow-hidden rounded-[2.25rem] p-6">
      <div className="absolute inset-0 bg-hero-radial opacity-70" aria-hidden="true" />
      <div className="relative flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-3xl">
          <p className="mb-3 inline-flex rounded-full border border-brand-200 bg-brand-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-brand-700">
            Hospital management
          </p>
          <h2 className="text-3xl font-semibold tracking-[-0.05em] text-slate-950 md:text-4xl">{title}</h2>
          {subtitle ? <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 md:text-base">{subtitle}</p> : null}
        </div>
        {action ? <div className="relative">{action}</div> : null}
      </div>
    </section>
  );
}
