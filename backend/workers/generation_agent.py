import anthropic
import os
import json
import asyncio
import logging
from datetime import datetime, UTC

from backend.schemas.models import AIJobResult, FitnessGoal

logger = logging.getLogger(__name__)

client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

_GENERATION_SYSTEM_PROMPT = """
You are PulseAI — an elite AI fitness coach with deep expertise in exercise science,
sports nutrition, and body composition. Your persona is precise, data-driven, and motivating.

The user has already provided their goal ({goal}), current weight ({weight_lbs} lbs),
and age ({age}). All recommendations must be personalized to these parameters.

You MUST respond with valid JSON matching this exact schema — nothing else:
{{
  "workout_plan": "<detailed, actionable workout plan as a string>",
  "nutrition_guidelines": "<macro targets and meal timing as a string>",
  "generated_at": "<ISO 8601 UTC timestamp>"
}}

Rules:
- Stay strictly in the fitness domain
- Be specific: include sets, reps, weights, macros, timing
- Do not include any text outside the JSON object
- generated_at must be the current UTC time in ISO 8601 format
""".strip()

_MAX_RETRIES = 3


async def generate(query: str, goal: FitnessGoal, weight_lbs: float, age: int) -> AIJobResult:
    """
    Calls Claude with exponential backoff and enforces structured JSON output.
    Raises on unrecoverable failure after _MAX_RETRIES attempts.
    """
    system_prompt = _GENERATION_SYSTEM_PROMPT.format(
        goal=goal.value, weight_lbs=weight_lbs, age=age
    )

    last_error: Exception | None = None

    for attempt in range(_MAX_RETRIES):
        try:
            message = await client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": query}],
            )
            raw = message.content[0].text.strip()
            data = json.loads(raw)

            # Validate against Pydantic schema — raises ValidationError if malformed
            return AIJobResult(**data)

        except json.JSONDecodeError as e:
            last_error = e
            logger.warning("Attempt %d: malformed JSON from Claude: %s", attempt + 1, e)
        except Exception as e:
            last_error = e
            logger.warning("Attempt %d: Claude call failed: %s", attempt + 1, e)

        if attempt < _MAX_RETRIES - 1:
            backoff = 2 ** attempt
            logger.info("Retrying in %ds...", backoff)
            await asyncio.sleep(backoff)

    raise RuntimeError(f"Generation failed after {_MAX_RETRIES} attempts: {last_error}")
