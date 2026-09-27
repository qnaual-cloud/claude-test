# AI Investment Research Assistant

A guided assistant that turns "what do I want to research?" into a
professional, structured prompt — and, optionally, runs it and shows the
result inside the app.

## How it's organized (what's safe to edit, and where)

- **`src/content/categories.ts`** — the 5 research categories and their
  guided questions (entity input, role/objective options, focus chips,
  output formats). Safe to edit and ship to the browser. Add a category
  by adding an entry here **and** a matching entry in
  `src/server/promptTemplates.ts` (same `id`).
- **`src/content/site.config.ts`** — branding and copy: product name,
  tagline, the footer credit line, early-access banner copy, feedback
  copy. Edit freely.
- **`src/server/promptTemplates.ts`** — the actual prompt wording,
  analysis instructions, and "why this works" explanations. This is the
  product's core IP. **Server-only** — never imported by client
  components, so it never reaches the browser bundle. Edit this to
  change how generated prompts read.
- **`src/server/promptEngine.ts`** — assembles a category + answers into
  a finished prompt. Deterministic template assembly, not an AI call —
  there is no LLM API cost to generate a prompt in v1.
- **`src/lib/subscriptions.ts`** — billing-cadence scaffolding (Free /
  Monthly / Annual), **not active**. Distinct from the membership tiers
  below — this one is about *how you'd pay*, not *what you get*. See the
  comment at the top of that file before adding billing.
- **`src/content/membership.config.ts`** — the membership tiers shown on
  the home page (Free / Member / Professional): names, descriptions,
  features, prices, and currency. **This is the one place to edit
  pricing** — prices are intentionally blank (`null`) right now; fill in
  a number and it appears, no other code changes needed.
- **`src/server/dashboardSchema.ts`** and **`src/server/anthropicClient.ts`**
  — the "Run Analysis" integration. Server-only.

Editing content in `src/content/*.ts` or `src/server/promptTemplates.ts`
and pushing is enough to change categories, questions, or prompt wording
— no other code needs to change.

## Local setup

```bash
npm install
cp .env.example .env.local   # optional — see below
npm run dev
```

The app works fully without Supabase configured: early-access emails,
feedback, and analytics writes are skipped (with a console warning)
instead of failing. To enable them:

1. Create a Supabase project.
2. Run `sql/schema.sql` against it (SQL editor, or `supabase db push`).
3. Set `NEXT_PUBLIC_SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in
   `.env.local` (or your hosting provider's env vars). The service-role
   key is read only in server-side code and must never be exposed to the
   client.

**Run Analysis** works the same way: without `ANTHROPIC_API_KEY` set, the
button shows a friendly "not configured" message instead of failing.
Every click that succeeds is a real, billed Claude API call — see
`src/server/anthropicClient.ts` for the model default and cost notes.
There is no per-user rate limit yet.

## What's in the app

- 5 guided research flows (Company Research, Valuation & DCF, Compare
  Investments, Earnings & Market Analysis, Portfolio Research), each with
  4 output formats: Summary, Full Report, Memo, and Research Dashboard
- Typed and voice input (browser-native Web Speech API — free, no
  backend cost; the mic button only appears where the browser supports
  it, and typing always works)
- Server-side prompt assembly — the prompt template library is never
  shipped to the browser
- Copy Prompt button, collapsed "why this works" explanation
- **Run Analysis** — runs the generated prompt against the Claude API and
  shows the formatted result in-app (prose for Summary/Full Report/Memo,
  a visual dashboard for Research Dashboard) while keeping the prompt
  itself visible for learning
- A membership section (Free / Member / Professional) with a GBP/USD
  toggle — display only, no prices yet, no real tier gating
- Early-access email capture and a lightweight thumbs up/down + comment
  feedback widget
- Lightweight, privacy-conscious usage analytics (category, chips,
  output format, voice vs. typed, Run Analysis token usage — no prompt
  or result content stored by default)
- No payments, no login wall, no real per-tier access control

## What's deliberately not built yet

Advanced mode, saved/reusable prompts, prompt quality scoring, multi-step
workflows, a second vertical, real subscription billing, and real
account-based tier gating (there's no login system at all) are out of
scope. Don't add them without approval — see `src/lib/subscriptions.ts`
and `src/content/membership.config.ts` for what's already scaffolded.
