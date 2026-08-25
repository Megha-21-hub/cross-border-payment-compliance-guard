import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ShieldCheck, Loader2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const DEMO_ACCOUNTS = [
  { label: "TechNova Solutions (Software -> US)", email: "demo@technova.io" },
  { label: "Kavya Consulting (IT -> UK)", email: "demo@kavyaconsulting.in" },
  { label: "Bloom Digital Agency (Marketing -> Singapore)", email: "demo@bloomdigital.in" },
];
const DEMO_PASSWORD = "demo1234";

export default function Login() {
  const [email, setEmail] = useState("demo@technova.io");
  const [password, setPassword] = useState(DEMO_PASSWORD);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch {
      setError("Incorrect email or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-950 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-3 rounded-xl bg-brand-600 p-3">
            <ShieldCheck size={26} className="text-white" />
          </div>
          <h1 className="text-xl font-semibold text-white">Cross-Border Payment Compliance Guard</h1>
          <p className="mt-1 text-sm text-ink-400">
            Pre-transaction configuration checks for international payments
          </p>
        </div>

        <form onSubmit={handleSubmit} className="rounded-xl border border-ink-800 bg-ink-900 p-6 shadow-card">
          <label className="mb-1.5 block text-sm font-medium text-ink-200">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="mb-4 w-full rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm text-white placeholder-ink-500 outline-none focus:border-brand-500"
          />

          <label className="mb-1.5 block text-sm font-medium text-ink-200">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mb-4 w-full rounded-lg border border-ink-700 bg-ink-950 px-3 py-2 text-sm text-white placeholder-ink-500 outline-none focus:border-brand-500"
          />

          {error && <p className="mb-4 text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
          >
            {loading && <Loader2 size={16} className="animate-spin" />}
            Log in
          </button>
        </form>

        <div className="mt-5 rounded-xl border border-ink-800 bg-ink-900/60 p-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-400">
            Demo merchant accounts (password: {DEMO_PASSWORD})
          </p>
          <div className="space-y-1.5">
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.email}
                type="button"
                onClick={() => {
                  setEmail(acc.email);
                  setPassword(DEMO_PASSWORD);
                }}
                className="block w-full rounded-md px-2 py-1.5 text-left text-xs text-ink-300 hover:bg-ink-800"
              >
                <span className="font-medium text-ink-100">{acc.email}</span>
                <span className="ml-1.5 text-ink-500">{acc.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
