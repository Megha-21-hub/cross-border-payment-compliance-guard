import { createContext, useContext, useState, ReactNode } from "react";
import { login as loginRequest } from "../api/endpoints";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function loadStoredUser(): User | null {
  const raw = localStorage.getItem("cbcg_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(loadStoredUser());

  async function login(email: string, password: string) {
    const data = await loginRequest(email, password);
    localStorage.setItem("cbcg_token", data.access_token);
    localStorage.setItem("cbcg_user", JSON.stringify(data.user));
    setUser(data.user);
  }

  function logout() {
    localStorage.removeItem("cbcg_token");
    localStorage.removeItem("cbcg_user");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
