import { FlaskConical } from "lucide-react";

interface DemoModeBannerProps {
  razorpayDemoMode: boolean;
  aiDemoMode: boolean;
}

export default function DemoModeBanner({ razorpayDemoMode, aiDemoMode }: DemoModeBannerProps) {
  if (!razorpayDemoMode && !aiDemoMode) return null;

  const parts: string[] = [];
  if (razorpayDemoMode) parts.push("Razorpay Test API credentials not set -- using simulated transaction data");
  if (aiDemoMode) parts.push("LLM API key not set -- using template-based Demo AI explanations");

  return (
    <div className="mb-6 flex items-start gap-2.5 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
      <FlaskConical size={16} className="mt-0.5 shrink-0" />
      <div>
        <span className="font-medium">Demo Mode: </span>
        {parts.join(". ")}. The app is fully functional -- add real credentials in{" "}
        <code className="rounded bg-amber-100 px-1 py-0.5 text-xs">backend/.env</code> to switch to live data.
      </div>
    </div>
  );
}
