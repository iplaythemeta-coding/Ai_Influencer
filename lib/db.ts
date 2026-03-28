// TypeScript mirrors of backend/schemas/models.py
// These types are the contract between Next.js and FastAPI.
// Never add business logic here — this file is types only.

export type FunnelState =
  | "lead"
  | "tripwire_offered"
  | "tripwire_active"
  | "pro_active"
  | "ultimate_active"
  | "churned";

export type FitnessGoal = "cut" | "bulk" | "recomp";

export type JobStatus = "pending" | "running" | "complete" | "failed";

// POST /api/users/optin
export interface OptInPayload {
  email: string;
  first_name: string;
  goal: FitnessGoal;
  current_weight_lbs: number;
  age: number;
}

export interface OptInResponse {
  user_id: string;
  funnel_state: FunnelState;
}

// GET /api/users/{user_id}/state
export interface UserState {
  user_id: string;
  email: string;
  first_name: string;
  goal: FitnessGoal;
  baseline_weight_lbs: number;
  age: number;
  current_funnel_state: FunnelState;
  stripe_customer_id: string | null;
  days_in_funnel: number;
  created_at: string;
  last_state_change: string;
}

// POST /api/ai/generate → 202
export interface OrchestratorJobResponse {
  status: string;
  job_id: string;
  estimated_latency_sec: number;
}

// GET /api/ai/jobs/{job_id}
export interface AIJobResult {
  workout_plan: string;
  nutrition_guidelines: string;
  generated_at: string;
}

export interface AIJobStatusResponse {
  job_id: string;
  status: JobStatus;
  result?: AIJobResult;
  error?: string;
}

// POST /api/checkout/{product}
export interface CheckoutResponse {
  session_url: string;
}
