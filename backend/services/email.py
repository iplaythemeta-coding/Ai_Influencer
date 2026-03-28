import resend
import os
import logging

logger = logging.getLogger(__name__)

resend.api_key = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "pulseai@yourdomain.com")
PDF_URL = os.getenv("LEAD_MAGNET_PDF_URL", "#")  # Set once PDF is hosted


async def send_welcome_email(email: str, first_name: str) -> bool:
    """Fires immediately after opt-in. Delivers the free PDF. Returns True on success."""
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": email,
            "subject": "Your 15 Fitness Tips Are Here, {first_name}".format(first_name=first_name),
            "html": f"""
                <h1>Protocol Initialized, {first_name}.</h1>
                <p>Your <strong>15 Science-Backed Fitness Tips</strong> are ready.</p>
                <p><a href="{PDF_URL}" style="background:#00e5ff;color:#000;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;">
                    Download Your PDF Now
                </a></p>
                <p>— RicchelWings</p>
            """,
        })
        return True
    except Exception as e:
        # Email failure should never crash the opt-in flow
        logger.error("Failed to send welcome email to %s: %s", email, e)
        return False


async def send_purchase_confirmation(email: str, first_name: str, product: str):
    """Fires after a confirmed Stripe purchase."""
    product_names = {
        "tripwire": "AI Nutrition Blueprint",
        "pro": "RicchelWings Pro",
        "ultimate": "RicchelWings Ultimate",
    }
    product_label = product_names.get(product, product)

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": email,
            "subject": f"Access Granted: {product_label}",
            "html": f"""
                <h1>You're in the system, {first_name}.</h1>
                <p>Your <strong>{product_label}</strong> is now active.</p>
                <p><a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard"
                    style="background:#00e5ff;color:#000;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;">
                    Go to Dashboard
                </a></p>
                <p>— RicchelWings</p>
            """,
        })
    except Exception as e:
        logger.error("Failed to send purchase confirmation to %s: %s", email, e)
