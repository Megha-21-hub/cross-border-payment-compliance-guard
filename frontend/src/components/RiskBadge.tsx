interface RiskBadgeProps {
  level: "low" | "medium" | "high";
  size?: "sm" | "md";
}

const CONFIG: Record<string, { label: string; classes: string; dot: string }> = {
  low: {
    label: "Low risk",
    classes: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200",
    dot: "bg-emerald-500",
  },
  medium: {
    label: "Medium risk",
    classes: "bg-amber-50 text-amber-700 ring-1 ring-amber-200",
    dot: "bg-amber-500",
  },
  high: {
    label: "High risk",
    classes: "bg-red-50 text-red-700 ring-1 ring-red-200",
    dot: "bg-red-500",
  },
};

export default function RiskBadge({ level, size = "md" }: RiskBadgeProps) {
  const cfg = CONFIG[level] ?? CONFIG.low;
  const padding = size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ${padding} ${cfg.classes}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
}
