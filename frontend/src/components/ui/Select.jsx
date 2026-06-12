import { cn } from "../../lib/utils";

export function Select({ className, children, ...props }) {
  return (
    <select
      className={cn(
        "w-full rounded-2xl border border-emerald-100/80 bg-white/92 px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-brand-500 focus:ring-4 focus:ring-brand-100/60",
        className,
      )}
      {...props}
    >
      {children}
    </select>
  );
}
