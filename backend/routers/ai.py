from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
import uuid

from backend.db.connection import get_db
from backend.db.models import User, AIJob
from backend.schemas.models import (
    AIGenerationRequest,
    OrchestratorJobResponse,
    AIJobStatusResponse,
    JobStatus,
    FunnelState,
)
from backend.workers.ai_worker import enqueue_job

router = APIRouter()

# Minimum state required to access AI generation
_AI_ACCESS_STATES = {
    FunnelState.TRIPWIRE_ACTIVE,
    FunnelState.PRO_ACTIVE,
    FunnelState.ULTIMATE_ACTIVE,
}

_ESTIMATED_LATENCY = 8.0  # seconds


@router.post("/generate", response_model=OrchestratorJobResponse, status_code=202)
async def generate(payload: AIGenerationRequest, db: AsyncSession = Depends(get_db)):
    # 1. Verify user exists and has access
    result = await db.execute(select(User).where(User.user_id == payload.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.current_funnel_state not in _AI_ACCESS_STATES:
        raise HTTPException(status_code=403, detail="AI access requires an active subscription")

    # 2. Write pending job to DB — worker picks it up asynchronously
    job = AIJob(
        user_id=user.user_id,
        query=payload.query,
        status=JobStatus.PENDING,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # 3. Dispatch to background worker
    await enqueue_job(job_id=job.id, user=user, query=payload.query)

    return OrchestratorJobResponse(job_id=job.id, estimated_latency_sec=_ESTIMATED_LATENCY)


@router.get("/jobs/{job_id}", response_model=AIJobStatusResponse)
async def get_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AIJob).where(AIJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = AIJobStatusResponse(job_id=job.id, status=job.status)

    if job.status == JobStatus.COMPLETE and job.result:
        import json
        from backend.schemas.models import AIJobResult
        response.result = AIJobResult(**json.loads(job.result))

    if job.status == JobStatus.FAILED:
        response.error = job.error

    return response
