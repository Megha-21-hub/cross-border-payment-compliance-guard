import { api } from "./client";
import type {
  AuditLog,
  ComplianceCheck,
  DashboardSummary,
  PaymentConfiguration,
  PaymentConfigurationCreatePayload,
  PaymentConfigurationUpdatePayload,
  User,
} from "../types";

export async function login(email: string, password: string) {
  const { data } = await api.post<{ access_token: string; user: User }>("/auth/login", {
    email,
    password,
  });
  return data;
}

export async function fetchDashboard() {
  const { data } = await api.get<DashboardSummary>("/dashboard");
  return data;
}

export async function fetchConfigurations() {
  const { data } = await api.get<PaymentConfiguration[]>("/payment-configurations");
  return data;
}

export async function createConfiguration(payload: PaymentConfigurationCreatePayload) {
  const { data } = await api.post<PaymentConfiguration>("/payment-configurations", payload);
  return data;
}

export async function updateConfiguration(
  id: string,
  payload: PaymentConfigurationUpdatePayload
) {
  const { data } = await api.patch<PaymentConfiguration>(`/payment-configurations/${id}`, payload);
  return data;
}

export async function runScan(paymentConfigurationId: string) {
  const { data } = await api.post<ComplianceCheck>("/compliance/scan", {
    payment_configuration_id: paymentConfigurationId,
  });
  return data;
}

export async function fetchFindings(statusFilter?: string) {
  const { data } = await api.get("/compliance/findings", {
    params: statusFilter ? { status_filter: statusFilter } : {},
  });
  return data;
}

export async function fetchHistory() {
  const { data } = await api.get<ComplianceCheck[]>("/compliance/history");
  return data;
}

export async function resolveCheck(checkId: string, resolutionNote?: string) {
  const { data } = await api.post<ComplianceCheck>(`/compliance/${checkId}/resolve`, {
    resolution_note: resolutionNote,
  });
  return data;
}

export async function fetchAuditLogs() {
  const { data } = await api.get<AuditLog[]>("/audit-logs");
  return data;
}
