from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import stripe
import os
import logging

from backend.db.connection import get_db
from backend.db.models import User, Purchase
from backend.schemas.models import FunnelState
from backend.services.email import send_purchase_confirmation

router = APIRouter()
logger = logging.getLogger(__name__)

WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Maps Stripe price IDs to funnel state transitions
PRICE_TO_STATE: dict[str, FunnelState] = {
    os.getenv("STRIPE_PRICE_TRIPWIRE", ""): FunnelState.TRIPWIRE_ACTIVE,
    os.getenv("STRIPE_PRICE_PRO", ""): FunnelState.PRO_ACTIVE,
    os.getenv("STRIPE_PRICE_ULTIMATE", ""): FunnelState.ULTIMATE_ACTIVE,
}


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Verify signature — reject anything that can't be verified
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await _handle_checkout_completed(session, db)

    # Always return 200 to acknowledge receipt, even for unhandled event types
    return {"received": True}


async def _handle_checkout_completed(session: dict, db: AsyncSession):
    payment_intent_id = session.get("payment_intent")
    user_id = session.get("metadata", {}).get("user_id")
    product = session.get("metadata", {}).get("product")
    price_id = session["line_items"]["data"][0]["price"]["id"] if session.get("line_items") else None

    if not all([payment_intent_id, user_id, product]):
        logger.error("Stripe webhook missing required metadata: %s", session)
        return

    # IDEMPOTENCY GUARD — discard duplicate webhook fires
    existing = await db.execute(
        select(Purchase).where(Purchase.stripe_payment_intent_id == payment_intent_id)
    )
    if existing.scalar_one_or_none():
        logger.info("Duplicate webhook for payment_intent %s — discarding", payment_intent_id)
        return

    # Resolve target funnel state from price ID
    new_state = PRICE_TO_STATE.get(price_id or "")
    if not new_state:
        logger.warning("Unknown price_id in webhook: %s", price_id)
        return

    # Load user and transition state
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        logger.error("Webhook references unknown user_id: %s", user_id)
        return

    user.current_funnel_state = new_state

    purchase = Purchase(
        user_id=user.user_id,
        product=product,
        amount_cents=session.get("amount_total", 0),
        stripe_payment_intent_id=payment_intent_id,
    )
    db.add(purchase)
    await db.commit()

    await send_purchase_confirmation(email=user.email, first_name=user.first_name, product=product)
    logger.info("State transition: user %s → %s", user_id, new_state)
