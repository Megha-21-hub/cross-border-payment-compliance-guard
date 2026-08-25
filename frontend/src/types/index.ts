export interface User {
  id: string;
  email: string;
  full_name: string;
  merchant_id: string | null;
}

export interface Merchant {
  id: string;
  business_name: string;
  business_type: string;
  country: string;
  default_iec_code: string | null;
  demo_persona: string | null;
}

export interface PaymentConfiguration {
  id: string;
  merchant_id: string;
  currency: string;
  amount: number;
  customer_country: string | null;
  payment_method: string | null;
  is_international: boolean;
  purpose_code: string | null;
  iec_code: string | null;
  hs_code: string | null;
  documentation_status: string | null;
  invoice_reference: string | null;
  razorpay_order_id: string | null;
  razorpay_payment_id: string | null;
  transaction_data_source: string;
  compliance_data_source: string;
  created_at: string;
  updated_at: string;
}

export interface AIExplanation {
  summary: string;
  why_it_matters: string;
  recommended_action: string;
  confidence: "high" | "medium" | "low";
  mode: "live_llm" | "demo_template";
}

export type Severity = "low" | "medium" | "high";
export type RiskLevel = "low" | "medium" | "high";
export type CheckStatus = "open" | "resolved";

export interface ComplianceFinding {
  id: string;
  rule_code: string;
  severity: Severity;
  reason: string;
  suggested_action: string;
  field_name: string | null;
  ai_explanation: AIExplanation | null;
  created_at: string;
}

export interface ComplianceCheck {
  id: string;
  payment_configuration_id: string;
  merchant_id: string;
  risk_level: RiskLevel;
  risk_score: number;
  status: CheckStatus;
  created_at: string;
  resolved_at: string | null;
  findings: ComplianceFinding[];
}

export interface DashboardSummary {
  total_configurations: number;
  safe_configurations: number;
  needs_review_configurations: number;
  high_risk_configurations: number;
  overall_compliance_score: number;
  recent_checks: ComplianceCheck[];
  demo_mode: {
    razorpay_demo_mode: boolean;
    ai_demo_mode: boolean;
  };
}

export interface AuditLog {
  id: string;
  merchant_id: string;
  user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string;
  risk_level: string | null;
  details: Record<string, unknown> | null;
  created_at: string;
}

export interface PaymentConfigurationCreatePayload {
  currency: string;
  amount: number;
  customer_country?: string;
  payment_method?: string;
  purpose_code?: string;
  iec_code?: string;
  hs_code?: string;
  documentation_status?: string;
  invoice_reference?: string;
  use_razorpay_test_api?: boolean;
}

export interface PaymentConfigurationUpdatePayload {
  purpose_code?: string;
  iec_code?: string;
  hs_code?: string;
  documentation_status?: string;
  invoice_reference?: string;
}
