import { cn } from "../../lib/utils";

export function Button({ className, variant = "primary", size = "md", as: Component = "button", ...props }) {
  const variants = {
    primary: "bg-gradient-to-r from-brand-600 to-medical-500 text-white shadow-soft hover:from-brand-700 hover:to-medical-600",
    secondary: "border border-emerald-100 bg-white/85 text-slate-900 hover:bg-emerald-50/70",
    outline: "border border-emerald-100 bg-transparent text-slate-900 hover:bg-emerald-50/70",
    ghost: "bg-transparent text-slate-700 hover:bg-emerald-50",
    danger: "bg-rose-600 text-white hover:bg-rose-700",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2.5 text-sm",
    lg: "px-5 py-3 text-sm",
  };

  return (
    <Component
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-2xl font-medium tracking-[-0.01em] transition duration-200 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  );
}
