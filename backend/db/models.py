from sqlalchemy import String, Float, Integer, DateTime, Boolean, Enum as SAEnum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime, UTC
import uuid

from backend.db.connection import Base
from backend.schemas.models import FunnelState, FitnessGoal, JobStatus


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    goal: Mapped[FitnessGoal] = mapped_column(SAEnum(FitnessGoal), nullable=False)
    baseline_weight_lbs: Mapped[float] = mapped_column(Float, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_funnel_state: Mapped[FunnelState] = mapped_column(SAEnum(FunnelState), nullable=False, default=FunnelState.LEAD)
    days_in_funnel: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    last_state_change: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    purchases: Mapped[list["Purchase"]] = relationship("Purchase", back_populates="user")
    ai_jobs: Mapped[list["AIJob"]] = relationship("AIJob", back_populates="user")
    funnel_state: Mapped["FunnelStateFlags"] = relationship("FunnelStateFlags", back_populates="user", uselist=False)
    attribution: Mapped["Attribution"] = relationship("Attribution", back_populates="user", uselist=False)


class FunnelStateFlags(Base):
    """Granular delivery tracking. Enum on User drives routing; these flags track what was actually sent."""
    __tablename__ = "funnel_state"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    welcome_email_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    lead_magnet_downloaded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tripwire_purchased: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    skool_membership_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    skool_invite_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    skool_invite_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    skool_invite_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship("User", back_populates="funnel_state")


class Attribution(Base):
    """UTM tracking. One row per user. Tells you which platform drives LTV."""
    __tablename__ = "attribution"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    utm_source: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    utm_medium: Mapped[str | None] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(255), nullable=True)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship("User", back_populates="attribution")


class Purchase(Base):
    __tablename__ = "purchases"
    __table_args__ = (UniqueConstraint("stripe_payment_intent_id", name="uq_stripe_payment_intent"),)

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    product: Mapped[str] = mapped_column(String(50), nullable=False)   # "tripwire" | "pro" | "ultimate"
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    stripe_payment_intent_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user: Mapped["User"] = relationship("User", back_populates="purchases")


class AIJob(Base):
    __tablename__ = "ai_jobs"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[JobStatus] = mapped_column(SAEnum(JobStatus), nullable=False, default=JobStatus.PENDING)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)   # JSON string of AIJobResult
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="ai_jobs")
