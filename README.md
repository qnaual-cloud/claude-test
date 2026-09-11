# AI Investment Research Assistant (V1)

A guided assistant that turns "what do I want to research?" into a
professional, structured prompt to paste into Claude, ChatGPT, or any
other AI model. V1 does not run AI inside the app — it only builds the
prompt and lets you copy it.

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
- **`src/lib/subscriptions.ts`** — subscription scaffolding, **not
  active**. Free/Monthly/Annual plans are defined but only Free does
  anything in v1. See the comment at the top of that file before adding
  billing.

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

## What's in v1

- 5 guided research flows (Company Research, Valuation & DCF, Compare
  Investments, Earnings & Market Analysis, Portfolio Research)
- Typed and voice input (browser-native Web Speech API — free, no
  backend cost; the mic button only appears where the browser supports
  it, and typing always works)
- Server-side prompt assembly — the prompt template library is never
  shipped to the browser
- Copy Prompt button, collapsed "why this works" explanation
- Early-access email capture and a lightweight thumbs up/down + comment
  feedback widget
- Lightweight, privacy-conscious usage analytics (category, chips,
  output format, voice vs. typed — no prompt content stored by default)
- No AI execution in-app, no payments, no login wall

## What's deliberately not built yet

Advanced mode, saved/reusable prompts, prompt quality scoring, multi-step
workflows, a second vertical, and subscriptions/billing are out of scope
for v1. Don't add them without approval — see `src/lib/subscriptions.ts`
for the documented (but inactive) future plan structure.
