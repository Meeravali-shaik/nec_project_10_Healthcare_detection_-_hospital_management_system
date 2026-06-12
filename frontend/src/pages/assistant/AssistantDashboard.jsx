import { Link } from "react-router-dom";
import { MessageSquareMore, BrainCircuit, FileText, ShieldCheck, Sparkles, BookOpen } from "lucide-react";
import { SectionHeader } from "../../components/shared/SectionHeader";
import { Card } from "../../components/ui/Card";
import { Disclaimer } from "../../components/ai/Disclaimer";

const links = [
  { to: "/assistant/chat", label: "AI Chat Assistant", icon: MessageSquareMore },
  { to: "/assistant/patient", label: "Patient Assistant", icon: Sparkles },
  { to: "/assistant/doctor", label: "Doctor Copilot", icon: BrainCircuit },
  { to: "/assistant/knowledge", label: "Knowledge Base", icon: BookOpen },
  { to: "/assistant/insights", label: "Executive Insights", icon: ShieldCheck },
  { to: "/assistant/reports", label: "AI Reports Center", icon: FileText },
];

export function AssistantDashboard() {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="Generative AI assistant"
        subtitle="Chat, retrieval, copilots, reports, and executive intelligence assembled into a polished healthcare AI workspace."
      />
      <Disclaimer />
      <Card>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {links.map((link) => {
            const Icon = link.icon;
            return (
              <Link
                key={link.to}
                className="flex items-center gap-3 rounded-[1.5rem] border border-slate-200 bg-slate-50/80 px-4 py-4 font-medium text-slate-800 transition hover:border-brand-200 hover:bg-brand-50/60"
                to={link.to}
              >
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white text-brand-700 shadow-sm">
                  <Icon className="h-5 w-5" />
                </span>
                <span>{link.label}</span>
              </Link>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
