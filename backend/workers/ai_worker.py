import asyncio
import json
import logging
from datetime import datetime, UTC
from uuid import UUID

from backend.db.connection import AsyncSessionLocal
from backend.db.models import AIJob, User
from backend.schemas.models import JobStatus
from backend.workers.prompt_router import route_prompt
from backend.workers.generation_agent import generate

from sqlalchemy import select

logger = logging.getLogger(__name__)


async def enqueue_job(job_id: UUID, user: User, query: str):
    """
    Dispatches the AI job as a fire-and-forget asyncio background task.
    V2: replace with Celery/RQ for distributed processing.
    """
    asyncio.create_task(_process_job(job_id=job_id, user=user, query=query))


async def _process_job(job_id: UUID, user: User, query: str):
    """
    Full pipeline:
    1. Route the prompt (classify fitness_related vs out_of_bounds)
    2. Generate the response via Claude
    3. Write result back to DB
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AIJob).where(AIJob.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            logger.error("Worker: job %s not found", job_id)
            return

        try:
            # Step 1: Route
            is_valid, refusal = await route_prompt(query)
            if not is_valid:
                job.status = JobStatus.COMPLETE
                job.result = json.dumps({
                    "workout_plan": refusal,
                    "nutrition_guidelines": "",
                    "generated_at": datetime.now(UTC).isoformat(),
                })
                job.completed_at = datetime.now(UTC)
                await db.commit()
                return

            # Step 2: Mark running
            job.status = JobStatus.RUNNING
            await db.commit()

            # Step 3: Generate
            ai_result = await generate(
                query=query,
                goal=user.goal,
                weight_lbs=user.baseline_weight_lbs,
                age=user.age,
            )

            job.status = JobStatus.COMPLETE
            job.result = ai_result.model_dump_json()
            job.completed_at = datetime.now(UTC)

        except Exception as e:
            logger.error("Worker: job %s failed: %s", job_id, e)
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.now(UTC)

        await db.commit()
