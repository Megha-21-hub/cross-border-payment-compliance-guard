import { FormEvent, useEffect, useState } from "react";
import { Loader2, Plus, ScanSearch, X } from "lucide-react";
import Layout from "../components/Layout";
import RiskBadge from "../components/RiskBadge";
import FindingCard from "../components/FindingCard";
import {
  createConfiguration,
  fetchConfigurations,
  runScan,
  updateConfiguration,
} from "../api/endpoints";
import type {
  ComplianceCheck,
  PaymentConfiguration,
  PaymentConfigurationCreatePayload,
} from "../types";

interface ScanState {
  before: ComplianceCheck | null;
  after: ComplianceCheck | null;
  loading: boolean;
}

export default function Scanner() {
  const [configs, setConfigs] = useState<PaymentConfiguration[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewForm, setShowNewForm] = useState(false);
  const [scanStates, setScanStates] = useState<Record<string, ScanState>>({});
  const [editingId, setEditingId] = useState<string | null>(null);

  async function reload() {
    const data = await fetchConfigurations();
    setConfigs(data);
  }

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, []);

  async function handleScan(configId: string) {
    setScanStates((prev) => ({
      ...prev,
      [configId]: { before: prev[configId]?.after ?? null, after: null, loading: true },
    }));
    const result = await runScan(configId);
    setScanStates((prev) => ({
      ...prev,
      [configId]: { before: prev[configId]?.before ?? null, after: result, loading: false },
    }));
  }

  return (
    <Layout>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900">International Payment Scanner</h1>
          <p className="mt-1 text-sm text-ink-500">
            Scan a payment configuration for potential compliance/configuration risks that require review.
          </p>
        </div>
        <button
          onClick={() => setShowNewForm((v) => !v)}
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          {showNewForm ? <X size={16} /> : <Plus size={16} />}
          {showNewForm ? "Close" : "New transaction"}
        </button>
      </div>

      {showNewForm && (
        <NewConfigForm
          onCreated={async () => {
            setShowNewForm(false);
            await reload();
          }}
        />
      )}

      {loading && <p className="text-sm text-ink-500">Loading configurations…</p>}

      {!loading && configs.length === 0 && !showNewForm && (
        <div className="rounded-xl border border-dashed border-ink-300 bg-white p-10 text-center">
          <ScanSearch size={28} className="mx-auto mb-3 text-ink-400" />
          <p className="text-sm text-ink-500">
            No payment configurations yet. Click "New transaction" to add one and run your first scan.
          </p>
        </div>
      )}

      <div className="space-y-4">
        {configs.map((config) => (
          <ConfigCard
            key={config.id}
            config={config}
            scanState={scanStates[config.id]}
            isEditing={editingId === config.id}
            onToggleEdit={() => setEditingId(editingId === config.id ? null : config.id)}
            onScan={() => handleScan(config.id)}
            onSaved={async (updated) => {
              setConfigs((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
              setEditingId(null);
              await handleScan(updated.id);
            }}
          />
        ))}
      </div>
    </Layout>
  );
}

// ---------------------------------------------------------------------------
function ConfigCard({
  config,
  scanState,
  isEditing,
  onToggleEdit,
  onScan,
  onSaved,
}: {
  config: PaymentConfiguration;
  scanState?: ScanState;
  isEditing: boolean;
  onToggleEdit: () => void;
  onScan: () => void;
  onSaved: (updated: PaymentConfiguration) => void;
}) {
  const after = scanState?.after;
  const before = scanState?.before;

  return (
    <div className="rounded-xl border border-ink-200 bg-white shadow-card">
      <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-4">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <span className="text-sm font-semibold text-ink-900">
              {config.currency} {config.amount.toLocaleString()}
            </span>
            {config.is_international && (
              <span className="rounded-full bg-brand-50 px-2 py-0.5 text-[11px] font-medium text-brand-700">
                International
              </span>
            )}
            <span
              className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
                config.transaction_data_source === "razorpay_test_api"
                  ? "bg-emerald-50 text-emerald-700"
                  : "bg-ink-100 text-ink-500"
              }`}
              title="Data provenance"
            >
              {config.transaction_data_source === "razorpay_test_api"
                ? "Live Razorpay Test data"
                : "Simulated transaction data"}
            </span>
          </div>
          <p className="text-xs text-ink-500">
            Customer country: {config.customer_country || "—"} · Method: {config.payment_method || "—"} ·
            Purpose code: {config.purpose_code || "missing"}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {after && <RiskBadge level={after.risk_level} />}
          <button
            onClick={onToggleEdit}
            className="rounded-lg border border-ink-200 px-3 py-1.5 text-xs font-medium text-ink-700 hover:bg-ink-50"
          >
            Review Configuration
          </button>
          <button
            onClick={onScan}
            disabled={scanState?.loading}
            className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700 disabled:opacity-60"
          >
            {scanState?.loading && <Loader2 size={13} className="animate-spin" />}
            Run Scan
          </button>
        </div>
      </div>

      {isEditing && (
        <div className="border-t border-ink-100 bg-ink-50 px-5 py-4">
          <ReviewForm config={config} onSaved={onSaved} />
        </div>
      )}

      {(before || after) && (
        <div className="border-t border-ink-100 px-5 py-4">
          {before && after && (
            <div className="mb-4 grid grid-cols-2 gap-3">
              <div className="rounded-lg border border-ink-200 bg-ink-50 p-3">
                <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-ink-400">
                  Before
                </p>
                <RiskBadge level={before.risk_level} size="sm" />
                <p className="mt-1 text-xs text-ink-500">{before.findings.length} finding(s)</p>
              </div>
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
                <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-emerald-600">
                  After
                </p>
                <RiskBadge level={after.risk_level} size="sm" />
                <p className="mt-1 text-xs text-ink-500">{after.findings.length} finding(s)</p>
              </div>
            </div>
          )}

          {after && after.findings.length === 0 && (
            <p className="rounded-lg bg-emerald-50 px-3 py-2.5 text-sm font-medium text-emerald-700">
              ✅ No current configuration issues detected.
            </p>
          )}

          {after && after.findings.length > 0 && (
            <div className="space-y-2.5">
              {after.findings.map((f) => (
                <FindingCard key={f.id} finding={f} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
function ReviewForm({
  config,
  onSaved,
}: {
  config: PaymentConfiguration;
  onSaved: (updated: PaymentConfiguration) => void;
}) {
  const [purposeCode, setPurposeCode] = useState(config.purpose_code || "");
  const [iecCode, setIecCode] = useState(config.iec_code || "");
  const [hsCode, setHsCode] = useState(config.hs_code || "");
  const [docStatus, setDocStatus] = useState(config.documentation_status || "unknown");
  const [invoiceRef, setInvoiceRef] = useState(config.invoice_reference || "");
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await updateConfiguration(config.id, {
        purpose_code: purposeCode || undefined,
        iec_code: iecCode || undefined,
        hs_code: hsCode || undefined,
        documentation_status: docStatus || undefined,
        invoice_reference: invoiceRef || undefined,
      });
      onSaved(updated);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      <Field label="Purpose code" value={purposeCode} onChange={setPurposeCode} placeholder="e.g. P0802" />
      <Field label="IEC code" value={iecCode} onChange={setIecCode} placeholder="e.g. AABCK1234L" />
      <Field label="HS code" value={hsCode} onChange={setHsCode} placeholder="e.g. 85238020" />
      <Field label="Invoice reference" value={invoiceRef} onChange={setInvoiceRef} placeholder="e.g. INV-1042" />
      <div>
        <label className="mb-1 block text-xs font-medium text-ink-600">Documentation status</label>
        <select
          value={docStatus}
          onChange={(e) => setDocStatus(e.target.value)}
          className="w-full rounded-lg border border-ink-200 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500"
        >
          <option value="unknown">Unknown</option>
          <option value="incomplete">Incomplete</option>
          <option value="complete">Complete</option>
        </select>
      </div>
      <div className="flex items-end">
        <button
          type="submit"
          disabled={saving}
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
        >
          {saving && <Loader2 size={14} className="animate-spin" />}
          Save & Re-scan
        </button>
      </div>
    </form>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}) {
  return (
    <div>
      <label className="mb-1 block text-xs font-medium text-ink-600">{label}</label>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg border border-ink-200 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500"
      />
    </div>
  );
}

// ---------------------------------------------------------------------------
function NewConfigForm({ onCreated }: { onCreated: () => void }) {
  const [currency, setCurrency] = useState("USD");
  const [amount, setAmount] = useState("1000");
  const [customerCountry, setCustomerCountry] = useState("United States");
  const [paymentMethod, setPaymentMethod] = useState("card");
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: PaymentConfigurationCreatePayload = {
        currency,
        amount: parseFloat(amount),
        customer_country: customerCountry,
        payment_method: paymentMethod,
        use_razorpay_test_api: true,
      };
      await createConfiguration(payload);
      onCreated();
    } finally {
      setSaving(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-6 grid grid-cols-1 gap-3 rounded-xl border border-ink-200 bg-white p-5 shadow-card sm:grid-cols-4"
    >
      <Field label="Currency (ISO)" value={currency} onChange={setCurrency} placeholder="USD" />
      <Field label="Amount" value={amount} onChange={setAmount} placeholder="1000" />
      <Field label="Customer country" value={customerCountry} onChange={setCustomerCountry} />
      <Field label="Payment method" value={paymentMethod} onChange={setPaymentMethod} placeholder="card" />
      <div className="sm:col-span-4">
        <button
          type="submit"
          disabled={saving}
          className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
        >
          {saving && <Loader2 size={14} className="animate-spin" />}
          Create transaction
        </button>
        <p className="mt-2 text-xs text-ink-500">
          Compliance fields (purpose code, IEC, HS code) are left blank initially so you can see the
          scanner flag them -- add them via "Review Configuration" afterward.
        </p>
      </div>
    </form>
  );
}
