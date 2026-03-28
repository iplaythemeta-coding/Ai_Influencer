# AI Influencer — Build TODO

> Architecture: Distributed State Machine
> Frontend = dumb terminal. FastAPI = orchestrator. PostgreSQL = state ledger. AI = async worker.
> This file is for planning only and does not affect the app.

---

## Architectural Rules (Non-Negotiable)

- Next.js has zero business logic — it only renders state returned by the API
- All funnel decisions are made by FastAPI, not the frontend
- AI generation is never synchronous — always async with job IDs
- All webhook endpoints must be idempotent (check transaction ID before acting)
- All Claude calls must have exponential backoff and a routing agent in front of them

---

## Phase 0 — Bug Fixes (Frontend, Do First)

- [ ] Add `name="name"` to the First Name `<Input>` in `app/page.tsx`
- [ ] Remove unused `revalidatePath` import in `app/actions/optin.ts`
- [ ] Update `<title>` and `<description>` metadata in `app/layout.tsx`
- [ ] Remove `mockDb` logic from `app/actions/optin.ts` — frontend should call FastAPI, not mock DB

---

## Phase 1 — Python Backend (FastAPI)

### Project Setup

- [ ] Create `/backend` directory at repo root
- [ ] Initialize Python project: `pyproject.toml` or `requirements.txt`
- [ ] Install: `fastapi`, `uvicorn`, `pydantic`, `asyncpg`, `sqlalchemy`, `python-dotenv`, `anthropic`, `stripe`, `resend`
- [ ] Create `backend/main.py` — FastAPI app entry point
- [ ] Create `backend/.env` — never commit, add to `.gitignore`

### Database Layer (PostgreSQL)

- [ ] Provision a PostgreSQL database (Supabase recommended — free tier)
- [ ] Create `users` table: `id`, `name`, `email`, `created_at`
- [ ] Create `funnel_states` table with strict state machine nodes:
  - States: `lead → tripwire_offered → tripwire_active → pro_active → ultimate_active`
  - Columns: `user_id`, `current_state`, `updated_at`
- [ ] Create `purchases` table: `id`, `user_id`, `product`, `amount`, `stripe_payment_intent_id` (unique), `created_at`
- [ ] Create `ai_jobs` table: `id`, `user_id`, `prompt`, `status` (pending/running/complete/failed), `result`, `created_at`, `completed_at`
- [ ] Create `backend/db/models.py` — SQLAlchemy models
- [ ] Create `backend/db/connection.py` — async connection pool

### API Routes

- [ ] `POST /api/users/optin` — validate with Pydantic, insert user, set state to `lead`, trigger welcome email, return user ID
- [ ] `GET /api/users/{user_id}/state` — return current `funnel_state` node (frontend calls this on every page load)
- [ ] `POST /api/ai/generate` — validate payload, write `pending` job to `ai_jobs`, return `202 Accepted` + `job_id`
- [ ] `GET /api/ai/jobs/{job_id}` — return job status + result (frontend polls this)
- [ ] `POST /api/webhooks/stripe` — idempotent handler (see Stripe section)

### Pydantic Schemas

- [ ] Create `backend/schemas/models.py` — all models (see schemas file, already scaffolded)
- [ ] `OptInPayload`: `email`, `first_name`, `goal`, `current_weight_lbs`, `age`
- [ ] `AIGenerationRequest`: `user_id`, `query` (backend enforces tier access — UI never sends state)
- [ ] `UserStateDB`: source-of-truth model returned to Next.js
- [ ] `OrchestratorJobResponse`: standardized async response for polling

---

## Phase 2 — Async AI Worker

### Job Queue (V1: asyncio background tasks, V2: Celery/RQ)

- [ ] Create `backend/workers/ai_worker.py`
- [ ] Worker flow: pull `pending` job → set status `running` → format system prompt → call Claude → parse structured JSON output → write result → set status `complete`
- [ ] Wrap Claude call in `try/except` with exponential backoff (3 retries, 2^n seconds)
- [ ] On unrecoverable failure: set status `failed`, log error

### Defensive Prompt Router (runs before every generation)

- [ ] Create `backend/workers/prompt_router.py`
- [ ] Router makes a fast Claude call to classify prompt as `fitness_related` or `out_of_bounds`
- [ ] If `out_of_bounds`: immediately return canned RicchelWings persona refusal, do NOT enqueue job
- [ ] If `fitness_related`: pass to generation worker
- [ ] System prompt for router must be strict — no exceptions for "educational" or "hypothetical" framing

### Generation Agent

- [ ] Create `backend/workers/generation_agent.py`
- [ ] Define system prompt: RicchelWings persona, fitness context, structured JSON output schema
- [ ] Enforce JSON structured output — parse with Pydantic, reject malformed responses
- [ ] Output schema: `{ workout_plan: string, nutrition_guidelines: string, generated_at: ISO8601 }`

---

## Phase 3 — Stripe Integration

- [ ] Create Stripe account, get test + live API keys
- [ ] Create products: Tripwire $17, Pro $37, Ultimate $67
- [ ] Create `backend/routers/checkout.py`:
  - `POST /api/checkout/tripwire` — create Stripe Checkout session, return `session_url`
- [ ] Update `app/thank-you-tripwire/page.tsx` — "ACTIVATE BLUEPRINT" button calls FastAPI checkout endpoint, redirects to Stripe URL
- [ ] Create `backend/routers/webhooks.py`:
  - `POST /api/webhooks/stripe`
  - Verify Stripe signature header before processing
  - On `payment_intent.succeeded`: check `purchases` table for `stripe_payment_intent_id` (idempotency guard) → if new, insert purchase, transition `funnel_state`, trigger confirmation email
  - On duplicate: log and return `200` silently
- [ ] Add Stripe keys to `backend/.env`
- [ ] Test full flow with Stripe test mode cards

---

## Phase 4 — Email (Resend)

- [ ] Create Resend account, verify sending domain
- [ ] Create `backend/services/email.py` — wrapper around Resend API
- [ ] Welcome email: fires after `lead` state — delivers PDF download link
- [ ] Purchase confirmation email: fires after each tier transition
- [ ] (Optional) 3-email nurture sequence: day 1, day 3, day 7 post opt-in
- [ ] Add Resend API key to `backend/.env`

---

## Phase 5 — Frontend Wired to FastAPI

### Opt-In Page (`app/page.tsx`)

- [ ] Replace server action call with `fetch` to `POST /api/users/optin`
- [ ] Form fields: `first_name`, `email`, `goal` (Cut/Bulk/Recomp), `current_weight_lbs`, `age`
- [ ] On success: store returned `user_id` in a cookie
- [ ] Redirect to `/thank-you-tripwire`

### Thank-You / Tripwire Page (`app/thank-you-tripwire/page.tsx`)

- [ ] On load: fetch `GET /api/users/{user_id}/state` to get current funnel node
- [ ] If state is already `tripwire_active` or higher: skip upsell, show dashboard CTA instead
- [ ] "ACTIVATE BLUEPRINT" → call `POST /api/checkout/tripwire` → redirect to Stripe URL
- [ ] Wire Download button to real hosted PDF URL

### Dashboard (`app/dashboard/page.tsx` — create this)

- [ ] On load: fetch `GET /api/users/{user_id}/state`
- [ ] Render content based on state node (gate premium features behind `tripwire_active`)
- [ ] AI Generator UI:
  - Input form → `POST /api/ai/generate` → receive `job_id`
  - Poll `GET /api/ai/jobs/{job_id}` every 2s until `complete`
  - Display result when ready, show loading state while polling

### Checkout Success Page (`app/checkout/success/page.tsx` — create this)

- [ ] Stripe redirects here after payment
- [ ] Fetch user state — if `tripwire_active` or higher, show confirmation + dashboard CTA

---

## Phase 6 — Lead Magnet (The Free PDF)

- [ ] Write "15 Science-Backed Fitness Tips" content
- [ ] Design PDF (Canva or Figma)
- [ ] Host on Supabase Storage or Vercel Blob
- [ ] Add signed/expiring URL generation to `backend/services/storage.py`
- [ ] Wire into welcome email and download button

---

## Phase 7 — The $17 Blueprint Product

- [ ] Write "AI Nutrition Quick-Start Blueprint" content
- [ ] Design and export as PDF
- [ ] Host file, deliver via purchase confirmation email

---

## Phase 8 — RicchelWings Persona

- [ ] Train LoRA in kohya_ss from curated dataset (`D:/AI/training/character_name/`)
- [ ] Generate character images in ComfyUI
- [ ] Add avatar to opt-in page, thank-you page, and dashboard
- [ ] Write "about RicchelWings" credibility blurb
- [ ] (Optional) Generate short-form video content for social traffic

---

## Phase 9 — SEO, Analytics & Deployment

### Metadata & SEO

- [ ] Set real `title` and `description` in `app/layout.tsx`
- [ ] Add Open Graph tags
- [ ] Replace default favicon
- [ ] (Optional) Add sitemap and `robots.txt`

### Analytics

- [ ] Add Vercel Analytics for page view tracking
- [ ] Track opt-in conversion rate
- [ ] Track tripwire conversion rate
- [ ] (Optional) Facebook Pixel / Google Tag for retargeting

### Deployment

- [ ] Connect repo to Vercel (frontend)
- [ ] Deploy FastAPI backend (Railway or Render recommended)
- [ ] Set all env vars in Vercel + Railway/Render dashboards
- [ ] Set Stripe webhook URL to live FastAPI endpoint
- [ ] Set up custom domain
- [ ] End-to-end test in production before sending traffic

---

## Phase 10 — Higher-Tier Products (Post-Launch)

- [ ] Define Pro ($37) and Ultimate ($67) tier feature sets
- [ ] Create Stripe products for each tier
- [ ] Build product pages and upsell flows
- [ ] Update `funnel_state` transitions for each tier
- [ ] Gate dashboard features by tier

---

## Nice to Have

- [ ] WebSocket support for AI job completion (replaces polling)
- [ ] Countdown timer on tripwire page
- [ ] Social proof / testimonials
- [ ] Affiliate/referral system
- [ ] A/B test opt-in headline copy
- [ ] Content blog for organic SEO
