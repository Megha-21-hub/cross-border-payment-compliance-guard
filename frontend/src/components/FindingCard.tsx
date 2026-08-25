import { useState } from "react";
import { ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import RiskBadge from "./RiskBadge";
import type { ComplianceFinding } from "../types";

export default function FindingCard({ finding }: { finding: ComplianceFinding }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-lg border border-ink-200 bg-white">
      <div className="flex items-start justify-between gap-4 p-4">
        <div className="flex-1">
          <div className="mb-1.5 flex items-center gap-2">
            <RiskBadge level={finding.severity} size="sm" />
            <span className="text-xs font-mono text-ink-400">{finding.rule_code}</span>
          </div>
          <p className="text-sm font-medium text-ink-900">{finding.reason}</p>
          <p className="mt-1 text-sm text-ink-600">
            <span className="font-medium text-ink-700">Suggested action: </span>
            {finding.suggested_action}
          </p>
        </div>
        <button
          onClick={() => setOpen((v) => !v)}
          className="flex shrink-0 items-center gap-1 rounded-md border border-brand-200 bg-brand-50 px-2.5 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-100"
        >
          <Sparkles size={14} />
          Why was this flagged?
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {open && (
        <div className="border-t border-ink-100 bg-ink-50 p-4">
          {finding.ai_explanation ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase tracking-wide text-ink-500">
                  AI Explanation
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                    finding.ai_explanation.mode === "live_llm"
                      ? "bg-brand-100 text-brand-700"
                      : "bg-ink-200 text-ink-600"
                  }`}
                >
                  {finding.ai_explanation.mode === "live_llm" ? "Live AI" : "Demo AI"}
                </span>
                <span className="text-[10px] text-ink-400">
                  confidence: {finding.ai_explanation.confidence}
                </span>
              </div>
              <p className="text-sm text-ink-800">{finding.ai_explanation.summary}</p>
              <p className="text-sm text-ink-600">
                <span className="font-medium text-ink-700">Why it matters: </span>
                {finding.ai_explanation.why_it_matters}
              </p>
              <p className="text-sm text-ink-600">
                <span className="font-medium text-ink-700">Recommended next step: </span>
                {finding.ai_explanation.recommended_action}
              </p>
            </div>
          ) : (
            <p className="text-sm text-ink-500">No AI explanation available for this finding.</p>
          )}
        </div>
      )}
    </div>
  );
}
