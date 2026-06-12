import { cn } from "../../lib/utils";

export function Badge({ children, tone = "default" }) {
  const tones = {
    default: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100",
    success: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100",
    warning: "bg-amber-50 text-amber-700 ring-1 ring-amber-100",
    danger: "bg-rose-50 text-rose-700 ring-1 ring-rose-100",
    info: "bg-teal-50 text-teal-700 ring-1 ring-teal-100",
  };
  return <span className={cn("inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold tracking-wide", tones[tone])}>{children}</span>;
}
