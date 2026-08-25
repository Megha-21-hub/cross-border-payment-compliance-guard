import { useEffect, useState } from "react";
import { CheckCircle2, Loader2 } from "lucide-react";
import Layout from "../components/Layout";
import FindingCard from "../components/FindingCard";
import { fetchFindings, resolveCheck } from "../api/endpoints";
import type { ComplianceFinding } from "../types";

export default function Findings() {
  const [findings, setFindings] = useState<ComplianceFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolvingCheckId, setResolvingCheckId] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "open" | "resolved">("open");

  async function reload(currentFilter: "all" | "open" | "resolved") {
    setLoading(true);
    const data = await fetchFindings(currentFilter === "all" ? undefined : currentFilter);
    setFindings(data);
    setLoading(false);
  }

  useEffect(() => {
    reload(filter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  async function handleResolve(checkId: string) {
    setResolvingCheckId(checkId);
    try {
      await resolveCheck(checkId);
      await reload(filter);
    } finally {
      setResolvingCheckId(null);
    }
  }

  return (
    <Layout>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900">Findings</h1>
          <p className="mt-1 text-sm text-ink-500">
            Every potential risk raised by the compliance rule engine, with a plain-language explanation.
          </p>
        </div>
        <div className="flex gap-1 rounded-lg border border-ink-200 bg-white p-1">
          {(["open", "resolved", "all"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium capitalize ${
                filter === f ? "bg-brand-600 text-white" : "text-ink-500 hover:bg-ink-50"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {loading && <p className="text-sm text-ink-500">Loading findings…</p>}

      {!loading && findings.length === 0 && (
        <div className="rounded-xl border border-dashed border-ink-300 bg-white p-10 text-center">
          <CheckCircle2 size={28} className="mx-auto mb-3 text-emerald-500" />
          <p className="text-sm text-ink-500">No {filter !== "all" ? filter : ""} findings right now.</p>
        </div>
      )}

      <div className="space-y-3">
        {findings.map((finding) => (
          <div key={finding.id}>
            <FindingCard finding={finding} />
            {filter !== "resolved" && (
              <div className="flex justify-end pt-1.5">
                <button
                  onClick={() => handleResolve(finding.compliance_check_id)}
                  disabled={resolvingCheckId === finding.compliance_check_id}
                  className="flex items-center gap-1.5 rounded-md border border-ink-200 bg-white px-2.5 py-1 text-xs font-medium text-ink-600 hover:bg-ink-50 disabled:opacity-60"
                >
                  {resolvingCheckId === finding.compliance_check_id && (
                    <Loader2 size={12} className="animate-spin" />
                  )}
                  Mark as Resolved
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </Layout>
  );
}
