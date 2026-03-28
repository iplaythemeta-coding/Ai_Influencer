# AI Influencer — Build TODO

> Tracking everything needed to go from prototype → live product.
> This file is for planning only and does not affect the app.

---

## Bug Fixes (Before Anything Else)

- [ ] Add `name="name"` attribute to the First Name `<Input>` in `app/page.tsx` — FormData can't read it without it
- [ ] Wire `mockDb.saveUser()` into `app/actions/optin.ts` (currently disconnected)
- [ ] Remove unused `revalidatePath` import in `app/actions/optin.ts`
- [ ] Update `<title>` and `<description>` metadata in `app/layout.tsx` (currently says "Create Next App")

---

## Database

- [ ] Choose a database provider (Supabase recommended — free tier, has auth, good Next.js support)
- [ ] Create `users` table: `id`, `name`, `email`, `created_at`
- [ ] Create `funnel_states` table: `user_id`, `opt_in_completed`, `tripwire_purchased`, `core_product_tier`
- [ ] Create `purchases` table: `user_id`, `product`, `amount`, `stripe_payment_id`, `created_at`
- [ ] Replace mock in `app/actions/optin.ts` with real DB insert
- [ ] Add `.env.local` with DB connection string (never commit this)

---

## Email

- [ ] Choose an email provider (Resend recommended — simple API, good free tier)
- [ ] Create a verified sending domain
- [ ] Build welcome email: delivers the free PDF download link
- [ ] Build tripwire purchase confirmation email
- [ ] (Optional) Build a 3–5 email nurture sequence after opt-in
- [ ] Wire email send into `app/actions/optin.ts` after DB insert
- [ ] Add email API key to `.env.local`

---

## Lead Magnet (The Free PDF)

- [ ] Write the "15 Science-Backed Fitness Tips" PDF content
- [ ] Design the PDF (Canva, Figma, or hire a designer)
- [ ] Host the PDF (Supabase Storage, S3, or Vercel Blob)
- [ ] Wire the Download button in `app/thank-you-tripwire/page.tsx` to the real file URL
- [ ] Optionally gate the download behind email confirmation

---

## Checkout (Stripe)

- [ ] Create a Stripe account and get API keys
- [ ] Create a product in Stripe: "AI Nutrition Blueprint" — $17
- [ ] Create `app/api/checkout/tripwire/route.ts` — creates a Stripe Checkout session
- [ ] Create `app/checkout/tripwire/page.tsx` — redirects to Stripe or hosts an embedded form
- [ ] Create `app/api/webhooks/stripe/route.ts` — listens for `payment_intent.succeeded`
- [ ] On successful webhook: update `funnel_states.tripwire_purchased = true`, trigger confirmation email
- [ ] Add Stripe public + secret keys to `.env.local`
- [ ] Test with Stripe test mode cards before going live

---

## The Tripwire Product (The $17 Blueprint)

- [ ] Write the "AI Nutrition Quick-Start Blueprint" content
- [ ] Design and export as a PDF
- [ ] Host the file and deliver it via the post-purchase confirmation email

---

## AI Integration

- [ ] Choose AI provider (Claude API recommended given this stack)
- [ ] Add API key to `.env.local`
- [ ] Replace stub in `app/api/ai/generate/route.ts` with a real API call
- [ ] Define the prompt template: takes user input, returns workout plan + nutrition guidelines
- [ ] Decide which tier of user gets AI access (free vs. paid)
- [ ] Add rate limiting or usage caps to prevent abuse

---

## Dashboard (Post-Purchase)

- [ ] Create `app/dashboard/page.tsx` — landing page after opt-in or purchase
- [ ] Show personalized content based on `funnel_states.core_product_tier`
- [ ] Add AI generator UI — form input → calls `/api/ai/generate` → displays result
- [ ] Gate premium features behind tripwire or core product purchase
- [ ] (Optional) Add auth (Supabase Auth or NextAuth) so users can log back in

---

## Higher-Tier Products (Future)

- [ ] Define what Starter / Pro / Ultimate tiers include
- [ ] Create product pages for each tier
- [ ] Add upsell flow from dashboard or post-tripwire thank-you page
- [ ] Create Stripe products for each tier
- [ ] Update `funnel_states.core_product_tier` logic on purchase

---

## The AI Influencer Persona (PulseAI)

- [ ] Generate character images using ComfyUI + trained LoRA
- [ ] Train LoRA in kohya_ss from curated dataset (`D:/AI/training/character_name/`)
- [ ] Add character avatar/photo to the opt-in page
- [ ] Add character avatar/photo to the thank-you page
- [ ] Write a short "about PulseAI" blurb for credibility
- [ ] (Optional) Generate short-form video content for social traffic

---

## SEO & Metadata

- [ ] Set real `title` and `description` in `app/layout.tsx`
- [ ] Add Open Graph tags (for link previews on social)
- [ ] Add favicon (replace the default Next.js one)
- [ ] (Optional) Add a sitemap and `robots.txt`

---

## Analytics & Tracking

- [ ] Add Vercel Analytics or Plausible for page view tracking
- [ ] Track opt-in conversion rate
- [ ] Track tripwire conversion rate
- [ ] (Optional) Add Facebook Pixel or Google Tag for paid ad retargeting

---

## Deployment

- [ ] Push repo to GitHub (private)
- [ ] Connect to Vercel for hosting
- [ ] Add all `.env.local` variables as Vercel environment variables
- [ ] Set up a custom domain
- [ ] Test the full funnel end-to-end in production before sending traffic
- [ ] Set up Stripe webhook endpoint with the live Vercel URL

---

## Nice to Have (Post-Launch)

- [ ] A/B test headline copy on the opt-in page
- [ ] Add a countdown timer on the tripwire page for urgency
- [ ] Add social proof (testimonials, user count)
- [ ] Add an affiliate/referral system
- [ ] Build a content blog for organic SEO traffic
