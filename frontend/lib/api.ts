import { Application } from "@/types/application";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type DashboardStats = {
  total: number;
  approved: number;
  rejected: number;
  hil_queue: number;
  avg_confidence: number;
  stp_rate: number;
  rejection_rate: number;
};

export type ChartData = {
  decision_distribution: Record<string, number>;
  risk_distribution: Record<string, number>;
  employer_split: Record<string, number>;
  rejection_reasons: Record<string, number>;
  daily_batch: {
    labels: string[];
    processed: number[];
    rejected: number[];
  };
};

export type HilQueue = {
  awaiting: Application[];
  review: Application[];
  approved: Application[];
  rejected: Application[];
};

async function fetchAPI<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`API Error: ${res.status} ${path}`);
  return res.json();
}

export const api = {
  getApplications: (params?: { decision?: string; risk_category?: string; search?: string }) => {
    const cleanParams = Object.fromEntries(
      Object.entries(params ?? {}).filter(([, value]) => value !== undefined && value !== "")
    );
    const query = new URLSearchParams(cleanParams as Record<string, string>).toString();
    return fetchAPI<Application[]>(`/api/applications${query ? `?${query}` : ""}`);
  },
  getApplication: (id: string) => fetchAPI<Application>(`/api/applications/${id}`),
  getStats: () => fetchAPI<DashboardStats>(`/api/applications/stats`),
  getCharts: () => fetchAPI<ChartData>(`/api/dashboard/charts`),
  getHilQueue: () => fetchAPI<HilQueue>(`/api/hil-review/queue`),
  hilAction: (applicationId: string, action: "approve" | "reject" | "modify_approve") =>
    fetch(`${BASE_URL}/api/hil-review/${applicationId}/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, officer_id: "CO-001", notes: "" }),
      cache: "no-store",
    }).then(async (r) => {
      if (!r.ok) {
        throw new Error(`API Error: ${r.status} /api/hil-review/${applicationId}/action`);
      }
      return r.json();
    }),
};
