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
  the home page (Free / Member / Professional) and the "Buy Credits"
  pack: names, descriptions, features, prices, currency, and Stripe
  Price ids. **This is the one place to edit pricing** — prices and
  Stripe price ids are intentionally blank right now; fill them in and
  the Subscribe / Buy Credits buttons work immediately, no other code
  changes needed.
- **`src/server/dashboardSchema.ts`** and **`src/server/anthropicClient.ts`**
  — the "Run Analysis" integration (now with web search — see below).
  Server-only.
- **`src/lib/credits.ts`** — the credits ledger (balance, spend, refund,
  grant). Server-only; always call with a user id you've already
  verified via `getAuthenticatedUser()`.
- **`sql/schema.sql`** — includes `profiles` and `credit_transactions`
  plus the Postgres functions that change balances atomically. Run the
  whole file (it's additive/idempotent) even if you already ran an
  earlier version.

Editing content in `src/content/*.ts` or `src/server/promptTemplates.ts`
and pushing is enough to change categories, questions, or prompt wording
— no other code needs to change.

## Local setup

```bash
npm install
cp .env.example .env.local   # optional — see below
npm run dev
```

### Accounts, login, and credits (Supabase)

1. Create a Supabase project (or reuse your existing one).
2. Run `sql/schema.sql` against it (SQL editor, or `supabase db push`).
   This creates everything: early-access/feedback/analytics tables, and
   the accounts/credits tables and functions.
3. Set `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, and
   `SUPABASE_SERVICE_ROLE_KEY` in `.env.local` (or your hosting
   provider's env vars). The anon key is safe to expose to the browser
   (it's used only for login/register); the service-role key must never
   be exposed and is only read server-side.

Without these three set, login/register show a "not configured" message
and Run Analysis can't be used (it requires being signed in). Early
access, feedback, and analytics still degrade gracefully as before.

New accounts get **5 free credits once they confirm their email** — not
immediately at signup (see "Protecting the free credits" below). To
manually add or adjust credits for a specific user, use the admin area
(see below) rather than SQL directly.

### Admin area

Visit `/admin` (not linked anywhere in the UI — go there directly).
Set `ADMIN_EMAILS` to your own account's email (comma-separated for more
than one) — there's no roles system, just this allowlist, checked
server-side on every admin request, not just when the page renders.
From there you can search users by email and add or subtract credits
with a note. Membership tier prices/credit-allowances are shown
read-only, sourced from `src/content/membership.config.ts` — edit that
file to change them.

### Protecting the free credits

Two things work together here:

1. **Email confirmation is required before the 5 credits are granted.**
   This only takes effect once you turn on **Confirm email** in your
   Supabase project (Authentication → Providers → Email → toggle "Confirm
   email"). Until you do, Supabase confirms new accounts immediately and
   the bonus is granted right away, same as before this change.
2. **Disposable email domains are blocked from getting the bonus** — see
   the `blocked_email_domains` table in `sql/schema.sql` (seeded with a
   short list of common ones). Add more any time:
   ```sql
   insert into blocked_email_domains (domain) values ('example.com');
   ```
   A blocked-domain account still works (0 starting credits, can still
   buy credits) — it's just not silently trusted with the free bonus.

**What this doesn't cover:** someone willing to use several different
real email addresses can still get multiple bonuses — there's no
IP/device-based signup throttling. Adding that would mean routing
registration through our own server (using Supabase's Admin API) instead
of the standard client-side sign-up flow this app uses, which is a
larger, separate change.

### Run Analysis (Claude API + web search)

Set `ANTHROPIC_API_KEY` to enable it; without it, the button shows a
friendly "not configured" message. Every successful analysis spends 1
credit and is a real, billed Claude API call — see
`src/server/anthropicClient.ts` for the model default and cost notes.
**Web search is on by default** so research reflects current
information, not just training data — this adds metered search cost on
top of normal token cost; set `ANTHROPIC_ENABLE_WEB_SEARCH=false` to
disable it. There is still no per-account rate limit beyond the credit
balance itself.

### Payments (Stripe)

1. Create a Stripe account (or use your existing one) and, in test mode
   first, create the Prices you want (one-time for each credit pack in
   `creditPacks`, recurring for each membership tier you're ready to
   sell) — remember Stripe prices are currency-specific, so create one
   per currency you support. Packages and prices aren't decided yet —
   `creditPacks` in `membership.config.ts` already supports adding more
   than the one pack there today, whenever you're ready.
2. Paste each Price id into `src/content/membership.config.ts`.
3. Set `STRIPE_SECRET_KEY` in your env vars.
4. Create a webhook endpoint in Stripe pointing at
   `<your-domain>/api/stripe/webhook`, subscribed to
   `checkout.session.completed`, and set `STRIPE_WEBHOOK_SECRET` to its
   signing secret.

Until these are set, Subscribe and Buy Credits show "not available yet"
instead of erroring. The webhook verifies Stripe's signature before
trusting anything in the payload — never skip `STRIPE_WEBHOOK_SECRET`.

**Payment methods:** Checkout is configured for cards (`payment_method_types:
["card"]` in `src/app/api/stripe/checkout/route.ts`). Apple Pay and
Google Pay aren't separate entries — Stripe Checkout shows them
automatically as wallet buttons on top of "card" for buyers whose
browser/device supports them, with no extra setup needed since Checkout
is hosted on Stripe's own domain. Add other method types to that one
array later (e.g. `"klarna"`) once you decide to support them.

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
- **Login / Register** (Supabase Auth, email + password) and a sitewide
  greeting ("Hello, {name}. What can I help you with today?") once
  signed in
- **Run Analysis** — spends 1 credit, runs the generated prompt against
  the Claude API (with web search) and shows the formatted result
  in-app (prose for Summary/Full Report/Memo, a visual dashboard for
  Research Dashboard) while keeping the prompt itself visible for
  learning. A failed analysis refunds the credit; credit spending is
  atomic and safe under concurrent requests.
- **Buy Credits** (any number of packages — see `creditPacks`) and
  **membership Subscribe buttons**, wired to real Stripe Checkout
  sessions supporting cards plus Apple Pay/Google Pay (env-gated — see
  above)
- **Admin area** (`/admin`, email-allowlisted) to search users and
  manually add or adjust credit balances
- A membership section (Free / Member / Professional) with a GBP/USD
  toggle, prices blank until you set them
- Early-access email capture and a lightweight thumbs up/down + comment
  feedback widget
- Lightweight, privacy-conscious usage analytics (category, chips,
  output format, voice vs. typed, Run Analysis token usage — no prompt
  or result content stored by default)

## What's deliberately not built yet

Advanced mode, saved/reusable prompts, prompt quality scoring, multi-step
workflows, a second vertical, recurring credit top-ups on subscription
renewal beyond the initial grant, IP/device-based signup throttling (see
"Protecting the free credits" above for why), and per-account rate
limiting beyond the credit balance are out of scope. Don't add them
without approval — see `src/lib/subscriptions.ts` and
`src/content/membership.config.ts` for what's already scaffolded.
