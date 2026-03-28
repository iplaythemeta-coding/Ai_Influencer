import type {
  OptInPayload,
  OptInResponse,
  UserState,
  OrchestratorJobResponse,
  AIJobStatusResponse,
  CheckoutResponse,
} from "@/lib/db";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ==========================================
// Users
// ==========================================

export function optIn(payload: OptInPayload): Promise<OptInResponse> {
  return apiFetch("/api/users/optin", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getUserState(userId: string): Promise<UserState> {
  return apiFetch(`/api/users/${userId}/state`);
}

// ==========================================
// AI Generation
// ==========================================

export function generateAI(userId: string, query: string): Promise<OrchestratorJobResponse> {
  return apiFetch("/api/ai/generate", {
    method: "POST",
    body: JSON.stringify({ user_id: userId, query }),
  });
}

export function getJobStatus(jobId: string): Promise<AIJobStatusResponse> {
  return apiFetch(`/api/ai/jobs/${jobId}`);
}

// ==========================================
// Checkout
// ==========================================

export function createCheckout(
  userId: string,
  product: "tripwire" | "pro" | "ultimate"
): Promise<CheckoutResponse> {
  return apiFetch(`/api/checkout/${product}`, {
    method: "POST",
    body: JSON.stringify({ user_id: userId }),
  });
}
