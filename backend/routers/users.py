from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from backend.db.connection import get_db
from backend.db.models import User
from backend.schemas.models import OptInPayload, OptInResponse, UserStateDB, FunnelState
from backend.services.email import send_welcome_email

router = APIRouter()


@router.post("/optin", response_model=OptInResponse, status_code=201)
async def optin(payload: OptInPayload, db: AsyncSession = Depends(get_db)):
    # Check for existing email to keep endpoint idempotent
    result = await db.execute(select(User).where(User.email == payload.email))
    existing = result.scalar_one_or_none()
    if existing:
        return OptInResponse(user_id=existing.user_id, funnel_state=existing.current_funnel_state)

    user = User(
        email=payload.email,
        first_name=payload.first_name,
        goal=payload.goal,
        baseline_weight_lbs=payload.current_weight_lbs,
        age=payload.age,
        current_funnel_state=FunnelState.LEAD,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await send_welcome_email(email=user.email, first_name=user.first_name)

    return OptInResponse(user_id=user.user_id, funnel_state=user.current_funnel_state)


@router.get("/{user_id}/state", response_model=UserStateDB)
async def get_user_state(user_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
