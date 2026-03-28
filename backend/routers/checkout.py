from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
import stripe
import os

from backend.db.connection import get_db
from backend.db.models import User

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRICE_MAP = {
    "tripwire": os.getenv("STRIPE_PRICE_TRIPWIRE"),
    "pro": os.getenv("STRIPE_PRICE_PRO"),
    "ultimate": os.getenv("STRIPE_PRICE_ULTIMATE"),
}


class CheckoutRequest(BaseModel):
    user_id: UUID


class CheckoutResponse(BaseModel):
    session_url: str


@router.post("/{product}", response_model=CheckoutResponse)
async def create_checkout(
    product: str,
    payload: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
):
    if product not in PRICE_MAP:
        raise HTTPException(status_code=404, detail=f"Unknown product: {product}")

    result = await db.execute(select(User).where(User.user_id == payload.user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    session = stripe.checkout.Session.create(
        customer_email=user.email,
        line_items=[{"price": PRICE_MAP[product], "quantity": 1}],
        mode="payment",
        success_url=f"{frontend_url}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{frontend_url}/thank-you-tripwire",
        metadata={"user_id": str(user.user_id), "product": product},
    )

    return CheckoutResponse(session_url=session.url)
