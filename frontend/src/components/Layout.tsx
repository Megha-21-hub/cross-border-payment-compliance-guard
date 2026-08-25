import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  ScanSearch,
  ShieldAlert,
  History,
  ClipboardList,
  LogOut,
  ShieldCheck,
} from "lucide-react";
import { ReactNode } from "react";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/scanner", label: "Payment Scanner", icon: ScanSearch },
  { to: "/findings", label: "Findings", icon: ShieldAlert },
  { to: "/history", label: "Compliance History", icon: History },
  { to: "/audit-trail", label: "Audit Trail", icon: ClipboardList },
];

export default function Layout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="flex min-h-screen bg-ink-50">
      <aside className="flex w-64 shrink-0 flex-col border-r border-ink-200 bg-ink-950">
        <div className="flex items-center gap-2 px-5 py-5">
          <div className="rounded-lg bg-brand-600 p-1.5">
            <ShieldCheck size={18} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white leading-tight">Compliance Guard</p>
            <p className="text-[11px] text-ink-400 leading-tight">Cross-Border Payments</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-2">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-brand-600 text-white"
                    : "text-ink-300 hover:bg-ink-800 hover:text-white"
                }`
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-ink-800 px-3 py-4">
          <div className="mb-3 px-2">
            <p className="text-sm font-medium text-white">{user?.full_name}</p>
            <p className="truncate text-xs text-ink-400">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-ink-300 hover:bg-ink-800 hover:text-white"
          >
            <LogOut size={16} />
            Log out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-6xl px-8 py-8">{children}</div>
      </main>
    </div>
  );
}
