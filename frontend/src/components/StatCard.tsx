import { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone?: "default" | "safe" | "review" | "high";
}

const TONE_CLASSES: Record<string, string> = {
  default: "bg-brand-50 text-brand-700",
  safe: "bg-emerald-50 text-emerald-700",
  review: "bg-amber-50 text-amber-700",
  high: "bg-red-50 text-red-700",
};

export default function StatCard({ label, value, icon: Icon, tone = "default" }: StatCardProps) {
  return (
    <div className="rounded-xl border border-ink-200 bg-white p-5 shadow-card">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-ink-500">{label}</span>
        <div className={`rounded-lg p-2 ${TONE_CLASSES[tone]}`}>
          <Icon size={18} strokeWidth={2.25} />
        </div>
      </div>
      <div className="mt-3 text-3xl font-semibold tracking-tight text-ink-900">{value}</div>
    </div>
  );
}
