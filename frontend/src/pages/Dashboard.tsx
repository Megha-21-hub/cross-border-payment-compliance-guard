import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { CheckCircle2, FileWarning, Gauge, ShieldAlert } from "lucide-react";
import Layout from "../components/Layout";
import StatCard from "../components/StatCard";
import RiskBadge from "../components/RiskBadge";
import DemoModeBanner from "../components/DemoModeBanner";
import { fetchDashboard } from "../api/endpoints";
import type { DashboardSummary } from "../types";

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Layout>
        <p className="text-sm text-ink-500">Loading dashboard…</p>
      </Layout>
    );
  }

  if (!data) {
    return (
      <Layout>
        <p className="text-sm text-red-600">Could not load dashboard data.</p>
      </Layout>
    );
  }

  const chartData = [
    { name: "Safe", value: data.safe_configurations, fill: "#0f9d58" },
    { name: "Needs review", value: data.needs_review_configurations, fill: "#e0912b" },
    { name: "High risk", value: data.high_risk_configurations, fill: "#d64545" },
  ];

  return (
    <Layout>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900">Dashboard</h1>
          <p className="mt-1 text-sm text-ink-500">
            Overview of your international payment configurations and compliance risk.
          </p>
        </div>
        <Link
          to="/scanner"
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          Open Payment Scanner
        </Link>
      </div>

      <DemoModeBanner
        razorpayDemoMode={data.demo_mode.razorpay_demo_mode}
        aiDemoMode={data.demo_mode.ai_demo_mode}
      />

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total configurations" value={data.total_configurations} icon={Gauge} />
        <StatCard
          label="Safe configurations"
          value={data.safe_configurations}
          icon={CheckCircle2}
          tone="safe"
        />
        <StatCard
          label="Requiring review"
          value={data.needs_review_configurations}
          icon={FileWarning}
          tone="review"
        />
        <StatCard
          label="High risk"
          value={data.high_risk_configurations}
          icon={ShieldAlert}
          tone="high"
        />
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="rounded-xl border border-ink-200 bg-white p-5 shadow-card lg:col-span-2">
          <h2 className="mb-4 text-sm font-semibold text-ink-700">Configuration risk breakdown</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#64748b" }} axisLine={false} tickLine={false} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "#64748b" }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: "#f1f5f9" }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-xl border border-ink-200 bg-white p-5 shadow-card">
          <h2 className="mb-1 text-sm font-semibold text-ink-700">Overall compliance score</h2>
          <p className="mb-4 text-xs text-ink-500">Based on latest scans across all configurations</p>
          <div className="flex items-end gap-2">
            <span className="text-5xl font-semibold tracking-tight text-ink-900">
              {data.overall_compliance_score}
            </span>
            <span className="mb-1.5 text-lg text-ink-400">/ 100</span>
          </div>
          <div className="mt-4 h-2 w-full overflow-hidden rounded-full bg-ink-100">
            <div
              className="h-full rounded-full bg-brand-600"
              style={{ width: `${data.overall_compliance_score}%` }}
            />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-ink-200 bg-white shadow-card">
        <div className="flex items-center justify-between border-b border-ink-100 px-5 py-4">
          <h2 className="text-sm font-semibold text-ink-700">Recent alerts</h2>
          <Link to="/history" className="text-xs font-medium text-brand-600 hover:underline">
            View full history →
          </Link>
        </div>
        <div className="divide-y divide-ink-100">
          {data.recent_checks.length === 0 && (
            <p className="px-5 py-6 text-sm text-ink-500">No scans yet. Run your first scan from the Payment Scanner.</p>
          )}
          {data.recent_checks.map((check) => (
            <div key={check.id} className="flex items-center justify-between px-5 py-4">
              <div>
                <div className="mb-1 flex items-center gap-2">
                  <RiskBadge level={check.risk_level} size="sm" />
                  <span className="text-xs text-ink-400">
                    {new Date(check.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="text-sm text-ink-700">
                  {check.findings.length === 0
                    ? "No issues detected"
                    : `${check.findings.length} finding${check.findings.length > 1 ? "s" : ""}: ${check.findings[0].reason}`}
                </p>
              </div>
              <span
                className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                  check.status === "resolved"
                    ? "bg-ink-100 text-ink-600"
                    : "bg-amber-50 text-amber-700"
                }`}
              >
                {check.status === "resolved" ? "Resolved" : "Open"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
