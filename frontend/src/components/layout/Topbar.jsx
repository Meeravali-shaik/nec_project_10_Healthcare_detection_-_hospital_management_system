import { Bell, Menu, Search, Sparkles, UserCircle2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export function Topbar({ onMenuClick }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="sticky top-0 z-20 border-b border-emerald-100 bg-white/82 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-[1480px] items-center gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <button
          type="button"
          onClick={onMenuClick}
          className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-emerald-100 bg-white/90 text-slate-700 shadow-sm transition hover:bg-emerald-50 lg:hidden"
          aria-label="Toggle navigation"
        >
          <Menu className="h-4 w-4" />
        </button>

        <div className="hidden min-w-0 flex-1 items-center gap-3 rounded-[1.75rem] border border-emerald-100 bg-white/96 px-4 py-3 shadow-sm lg:flex">
          <Search className="h-4 w-4 text-slate-400" />
          <input
            aria-label="Search"
            placeholder="Search patients, appointments, records..."
            className="w-full border-0 bg-transparent text-sm text-slate-700 outline-none placeholder:text-slate-400"
          />
          <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">Cmd K</span>
        </div>

        <div className="ml-auto flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-emerald-100 bg-white/92 px-3 py-2 text-sm text-slate-600 md:flex">
            <Sparkles className="h-4 w-4 text-brand-600" />
            <span>Clinical dashboard online</span>
          </div>
          <button type="button" className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-emerald-100 bg-white/96 text-slate-600 transition hover:bg-emerald-50" aria-label="Notifications">
            <Bell className="h-4 w-4" />
          </button>
          <div className="hidden items-center gap-2 rounded-full border border-emerald-100 bg-white/92 px-3 py-2 text-sm text-slate-700 sm:flex">
            <UserCircle2 className="h-4 w-4" />
            {user?.role}
          </div>
          <button
            onClick={handleLogout}
            className="rounded-2xl bg-slate-950 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-800"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
