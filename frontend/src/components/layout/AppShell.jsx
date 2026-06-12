import { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#eefaf7]">
      <div className="absolute inset-0 app-grid opacity-20" aria-hidden="true" />
      <div className="absolute inset-0 bg-hero-radial opacity-80" aria-hidden="true" />
      <div className="absolute left-[-8rem] top-24 h-72 w-72 rounded-full bg-brand-200/24 blur-3xl" aria-hidden="true" />
      <div className="absolute right-[-8rem] top-40 h-80 w-80 rounded-full bg-medical-200/18 blur-3xl" aria-hidden="true" />
      <div className="relative min-h-screen lg:flex">
        <Sidebar open={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
        <div className="flex min-h-screen flex-1 flex-col">
          <Topbar onMenuClick={() => setMobileNavOpen((value) => !value)} />
          <main className="flex-1 px-4 py-5 sm:px-6 lg:px-8 lg:py-8">
            <div className="mx-auto flex w-full max-w-[1480px] flex-col gap-6">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
