-- ============================================================
-- RicchelWings — Supabase PostgreSQL Schema
-- Execute this in the Supabase SQL Editor (one-time setup).
-- FastAPI connects via service role key only.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. USERS
-- Canonical identity record. Created on opt-in.
-- ============================================================
CREATE TABLE public.users (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email               TEXT UNIQUE NOT NULL,
    first_name          TEXT NOT NULL,
    goal                TEXT NOT NULL CHECK (goal IN ('cut', 'bulk', 'recomp')),
    baseline_weight_lbs FLOAT NOT NULL,
    age                 INTEGER NOT NULL,
    stripe_customer_id  TEXT,

    -- State Machine (drives all routing decisions)
    current_funnel_state TEXT NOT NULL DEFAULT 'lead'
        CHECK (current_funnel_state IN (
            'lead', 'tripwire_offered', 'tripwire_active',
            'pro_active', 'ultimate_active', 'churned'
        )),

    days_in_funnel      INTEGER NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_state_change   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 2. FUNNEL STATE FLAGS
-- Granular delivery tracking. One row per user.
-- Enum drives routing; booleans track what was actually sent.
-- ============================================================
CREATE TABLE public.funnel_state (
    user_id                 UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,

    -- Email Delivery Flags
    welcome_email_sent      BOOLEAN NOT NULL DEFAULT FALSE,
    lead_magnet_downloaded  BOOLEAN NOT NULL DEFAULT FALSE,

    -- Tripwire
    tripwire_purchased      BOOLEAN NOT NULL DEFAULT FALSE,

    -- Skool Community (Ultimate/Pro tier)
    skool_membership_active BOOLEAN NOT NULL DEFAULT FALSE,
    skool_invite_sent       BOOLEAN NOT NULL DEFAULT FALSE,
    skool_invite_token      TEXT,                            -- single-use token
    skool_invite_sent_at    TIMESTAMPTZ,

    last_active_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 3. PURCHASES
-- Append-only. stripe_payment_intent_id is the idempotency key.
-- ============================================================
CREATE TABLE public.purchases (
    id                       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                  UUID NOT NULL REFERENCES public.users(id),
    product                  TEXT NOT NULL CHECK (product IN ('tripwire', 'pro', 'ultimate')),
    amount_cents             INTEGER NOT NULL,
    stripe_payment_intent_id TEXT UNIQUE NOT NULL,   -- prevents duplicate webhook processing
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 4. AI JOBS
-- Async generation pipeline. Frontend polls status.
-- ============================================================
CREATE TABLE public.ai_jobs (
    id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id      UUID NOT NULL REFERENCES public.users(id),
    query        TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'complete', 'failed')),
    result       JSONB,                              -- structured AIJobResult
    error        TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ============================================================
-- 5. ATTRIBUTION
-- UTM tracking for every opt-in.
-- Tells you which platform (TikTok/IG/X/LinkedIn) drives LTV.
-- ============================================================
CREATE TABLE public.attribution (
    user_id      UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
    utm_source   TEXT,    -- 'tiktok' | 'instagram' | 'x' | 'linkedin' | 'skool' | null
    utm_medium   TEXT,    -- 'social' | 'bio' | 'paid' | etc.
    utm_campaign TEXT,    -- campaign slug
    referrer     TEXT,    -- raw HTTP referrer header
    captured_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 6. INDEXES
-- ============================================================
CREATE INDEX idx_users_email              ON public.users(email);
CREATE INDEX idx_users_funnel_state       ON public.users(current_funnel_state);
CREATE INDEX idx_purchases_user_id        ON public.purchases(user_id);
CREATE INDEX idx_ai_jobs_user_id          ON public.ai_jobs(user_id);
CREATE INDEX idx_ai_jobs_status           ON public.ai_jobs(status);
CREATE INDEX idx_attribution_utm_source   ON public.attribution(utm_source);

-- ============================================================
-- 7. ROW LEVEL SECURITY
-- Only the FastAPI service role can read/write.
-- No client can query these tables directly.
-- ============================================================
ALTER TABLE public.users        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.funnel_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.purchases    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_jobs      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.attribution  ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role only" ON public.users
    USING (auth.role() = 'service_role');
CREATE POLICY "Service role only" ON public.funnel_state
    USING (auth.role() = 'service_role');
CREATE POLICY "Service role only" ON public.purchases
    USING (auth.role() = 'service_role');
CREATE POLICY "Service role only" ON public.ai_jobs
    USING (auth.role() = 'service_role');
CREATE POLICY "Service role only" ON public.attribution
    USING (auth.role() = 'service_role');
