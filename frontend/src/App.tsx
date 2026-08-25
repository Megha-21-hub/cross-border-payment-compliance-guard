import { ReactNode, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { ClipboardList, History as HistoryIcon } from "lucide-react";

import { useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import RiskBadge from "./components/RiskBadge";
import FindingCard from "./components/FindingCard";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Scanner from "./pages/Scanner";
import Findings from "./pages/Findings";

import { fetchAuditLogs, fetchHistory } from "./api/endpoints";
import type { AuditLog, ComplianceCheck } from "./types";

// ---------------------------------------------------------------------------
// Route guard: redirects to /login when not authenticated.
// Kept inline here (rather than a new file) per the instruction to touch
// only main.tsx and App.tsx.
// ---------------------------------------------------------------------------
function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

// ---------------------------------------------------------------------------
// Compliance History page ("scan -> finding -> action -> re-scan" trail).
// Uses the existing GET /compliance/history endpoint and existing
// RiskBadge/FindingCard components. Reachable from the sidebar's
// "Compliance History" link, which already points to /history.
// ---------------------------------------------------------------------------
function ComplianceHistoryPage() {
  const [checks, setChecks] = useState<ComplianceCheck[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory()
      .then(setChecks)
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink-900">Compliance History</h1>
        <p className="mt-1 text-sm text-ink-500">
          Every scan that has been run, in order, with its findings and resolution status.
        </p>
      </div>

      {loading && <p className="text-sm text-ink-500">Loading history…</p>}

      {!loading && checks.length === 0 && (
        <div className="rounded-xl border border-dashed border-ink-300 bg-white p-10 text-center">
          <HistoryIcon size={28} className="mx-auto mb-3 text-ink-400" />
          <p className="text-sm text-ink-500">
            No scans have been run yet. Run a scan from the Payment Scanner to see it here.
          </p>
        </div>
      )}

      <div className="space-y-4">
        {checks.map((check) => (
          <div key={check.id} className="rounded-xl border border-ink-200 bg-white shadow-card">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-ink-100 px-5 py-3">
              <div className="flex items-center gap-2">
                <RiskBadge level={check.risk_level} size="sm" />
                <span
                  className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
                    check.status === "resolved"
                      ? "bg-ink-100 text-ink-600"
                      : "bg-amber-50 text-amber-700"
                  }`}
                >
                  {check.status === "resolved" ? "Resolved" : "Open"}
                </span>
                <span className="text-xs text-ink-400">
                  Scanned {new Date(check.created_at).toLocaleString()}
                </span>
              </div>
              {check.resolved_at && (
                <span className="text-xs text-ink-400">
                  Resolved {new Date(check.resolved_at).toLocaleString()}
                </span>
              )}
            </div>
            <div className="px-5 py-4">
              {check.findings.length === 0 ? (
                <p className="text-sm font-medium text-emerald-700">
                  ✅ No configuration issues detected on this scan.
                </p>
              ) : (
                <div className="space-y-2.5">
                  {check.findings.map((f) => (
                    <FindingCard key={f.id} finding={f} />
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}

// ---------------------------------------------------------------------------
// Audit Trail page. Uses the existing GET /audit-logs endpoint. Reachable
// from the sidebar's "Audit Trail" link, which already points to
// /audit-trail.
// ---------------------------------------------------------------------------
function AuditTrailPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditLogs()
      .then(setLogs)
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-ink-900">Audit Trail</h1>
        <p className="mt-1 text-sm text-ink-500">
          A timestamped log of every scan, finding, and configuration change for this merchant.
        </p>
      </div>

      {loading && <p className="text-sm text-ink-500">Loading audit log…</p>}

      {!loading && logs.length === 0 && (
        <div className="rounded-xl border border-dashed border-ink-300 bg-white p-10 text-center">
          <ClipboardList size={28} className="mx-auto mb-3 text-ink-400" />
          <p className="text-sm text-ink-500">No audit events recorded yet.</p>
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-ink-200 bg-white shadow-card">
        <table className="w-full text-left text-sm">
          <thead className="bg-ink-50 text-xs font-semibold uppercase tracking-wide text-ink-500">
            <tr>
              <th className="px-4 py-3">Timestamp</th>
              <th className="px-4 py-3">Action</th>
              <th className="px-4 py-3">Entity</th>
              <th className="px-4 py-3">Risk level</th>
              <th className="px-4 py-3">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-100">
            {logs.map((log) => (
              <tr key={log.id}>
                <td className="whitespace-nowrap px-4 py-3 text-ink-500">
                  {new Date(log.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-3 font-medium text-ink-800">{log.action}</td>
                <td className="px-4 py-3 text-ink-600">
                  {log.entity_type}
                  <span className="ml-1 font-mono text-xs text-ink-400">#{log.entity_id.slice(0, 8)}</span>
                </td>
                <td className="px-4 py-3">{log.risk_level ? <RiskBadge level={log.risk_level as "low" | "medium" | "high"} size="sm" /> : "—"}</td>
                <td className="max-w-xs truncate px-4 py-3 text-xs text-ink-400">
                  {log.details ? JSON.stringify(log.details) : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}

// ---------------------------------------------------------------------------
// Root app: route table.
// ---------------------------------------------------------------------------
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/scanner"
        element={
          <ProtectedRoute>
            <Scanner />
          </ProtectedRoute>
        }
      />
      <Route
        path="/findings"
        element={
          <ProtectedRoute>
            <Findings />
          </ProtectedRoute>
        }
      />
      <Route
        path="/history"
        element={
          <ProtectedRoute>
            <ComplianceHistoryPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/audit-trail"
        element={
          <ProtectedRoute>
            <AuditTrailPage />
          </ProtectedRoute>
        }
      />

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
