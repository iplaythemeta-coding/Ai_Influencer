from enum import Enum
from datetime import datetime, UTC
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID, uuid4

# ==========================================
# 1. State Enums (The Core State Machine)
# ==========================================

class FunnelState(str, Enum):
    """Strict linear progression through the PulseAI funnel."""
    LEAD = "lead"                                # Received Day 0 Free PDF
    TRIPWIRE_OFFERED = "tripwire_offered"        # Reached Day 7
    TRIPWIRE_ACTIVE = "tripwire_active"          # Purchased $17 Tier
    PRO_ACTIVE = "pro_active"                    # Purchased $37 Tier
    ULTIMATE_ACTIVE = "ultimate_active"          # Purchased $67 Tier
    CHURNED = "churned"                          # Unsubscribed or blocked


class FitnessGoal(str, Enum):
    CUT = "cut"
    BULK = "bulk"
    RECOMP = "recomp"


# ==========================================
# 2. Ingestion Payloads (Next.js -> FastAPI)
# ==========================================

class OptInPayload(BaseModel):
    """Raw payload from the Next.js frontend opt-in form."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    goal: FitnessGoal
    current_weight_lbs: float = Field(..., gt=70.0, lt=500.0)
    age: int = Field(..., ge=18, le=90)  # Restrict minors for liability


class OptInResponse(BaseModel):
    user_id: UUID
    funnel_state: FunnelState


class AIGenerationRequest(BaseModel):
    """User prompt payload from the dashboard UI."""
    user_id: UUID
    query: str = Field(..., min_length=3, max_length=1000)
    # The UI never sends the user's state — backend enforces tier access
    # via DB lookup of user_id.


# ==========================================
# 3. Webhook Payloads (Stripe -> FastAPI)
# ==========================================

class StripeCheckoutEvent(BaseModel):
    """Validated payload extracted from a verified Stripe webhook."""
    stripe_session_id: str
    customer_email: EmailStr
    price_id: str
    amount_total: int  # in cents
    # price_id is mapped to a FunnelState transition in the webhook handler


# ==========================================
# 4. Database / Internal State Models
# ==========================================

class UserStateDB(BaseModel):
    """
    Source of truth returned to the Next.js UI layer.
    The frontend renders exclusively based on current_funnel_state.
    """
    model_config = ConfigDict(from_attributes=True)  # Enables SQLAlchemy ORM parsing

    user_id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    first_name: str
    goal: FitnessGoal
    baseline_weight_lbs: float
    age: int

    # State Tracking
    current_funnel_state: FunnelState = FunnelState.LEAD
    stripe_customer_id: Optional[str] = None
    days_in_funnel: int = 0

    # Telemetry
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_state_change: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ==========================================
# 5. Async Job Models
# ==========================================

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class OrchestratorJobResponse(BaseModel):
    """Standardized 202 response for frontend polling."""
    status: str = "accepted"
    job_id: UUID
    estimated_latency_sec: float


class AIJobResult(BaseModel):
    """Structured output enforced on every Claude generation response."""
    workout_plan: str
    nutrition_guidelines: str
    generated_at: datetime


class AIJobStatusResponse(BaseModel):
    """Returned by GET /api/ai/jobs/{job_id}"""
    job_id: UUID
    status: JobStatus
    result: Optional[AIJobResult] = None
    error: Optional[str] = None
