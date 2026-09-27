-- AI Investment Research Assistant — Supabase schema
--
-- Run this once against a new Supabase project (SQL editor, or `supabase
-- db push`). These tables are written to only from server-side code using
-- the service-role key — Row Level Security is enabled with no public
-- policies, so anon/client keys cannot read or write them directly.

create table if not exists early_access_emails (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  created_at timestamptz not null default now()
);

create table if not exists feedback (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  category_id text not null,
  rating text not null check (rating in ('up', 'down')),
  comment text,
  created_at timestamptz not null default now()
);

create table if not exists analytics_events (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  category_id text not null,
  event text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

alter table early_access_emails enable row level security;
alter table feedback enable row level security;
alter table analytics_events enable row level security;

-- No policies are created: these tables are intentionally unreachable
-- from the anon/public key. All writes go through server-side API routes
-- using the service-role key, which bypasses RLS.

-- ============================================================
-- Accounts and credits (login/register, Buy Credits, membership)
-- ============================================================
-- Same security model as above: RLS is enabled with no public policies.
-- The browser only ever talks to Supabase directly for auth (sign up /
-- sign in via the anon key) — it never reads or writes these tables
-- directly. Balance/name/tier are read via /api/account/me, and every
-- balance change goes through the functions below, called server-side
-- with the service-role key after verifying the caller's own session.

create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null default '',
  credits_balance integer not null default 0,
  membership_tier text not null default 'free'
    check (membership_tier in ('free', 'member', 'professional')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists credit_transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  amount integer not null, -- positive = credit granted, negative = credit spent
  reason text not null
    check (reason in ('signup_bonus', 'purchase', 'manual_grant', 'analysis_run', 'refund')),
  stripe_event_id text, -- set on Stripe-driven grants, for idempotency on webhook replay
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create unique index if not exists credit_transactions_stripe_event_id_idx
  on credit_transactions (stripe_event_id)
  where stripe_event_id is not null;

alter table profiles enable row level security;
alter table credit_transactions enable row level security;

-- New account setup: 5 starter credits, matching the "each tester gets
-- 5 free Run Analysis uses" testing policy. Change the literal `5`
-- below if that allowance changes.
create or replace function handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, full_name, credits_balance, membership_tier)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'full_name', ''), 5, 'free');

  insert into public.credit_transactions (user_id, amount, reason)
  values (new.id, 5, 'signup_bonus');

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();

-- Atomically spends 1 credit if the balance is positive; returns the new
-- balance, or NULL if there were no credits to spend (caller must check
-- for NULL and refuse the action — this is what makes concurrent
-- requests safe against double-spending the last credit).
create or replace function consume_credit(
  p_user_id uuid,
  p_reason text default 'analysis_run',
  p_metadata jsonb default '{}'::jsonb
)
returns integer
language plpgsql
as $$
declare
  v_new_balance integer;
begin
  update profiles
  set credits_balance = credits_balance - 1,
      updated_at = now()
  where id = p_user_id and credits_balance > 0
  returning credits_balance into v_new_balance;

  if v_new_balance is null then
    return null;
  end if;

  insert into credit_transactions (user_id, amount, reason, metadata)
  values (p_user_id, -1, p_reason, p_metadata);

  return v_new_balance;
end;
$$;

-- Refunds 1 credit (used when a Run Analysis call fails after a credit
-- was already reserved via consume_credit).
create or replace function refund_credit(
  p_user_id uuid,
  p_reason text default 'refund',
  p_metadata jsonb default '{}'::jsonb
)
returns integer
language plpgsql
as $$
declare
  v_new_balance integer;
begin
  update profiles
  set credits_balance = credits_balance + 1,
      updated_at = now()
  where id = p_user_id
  returning credits_balance into v_new_balance;

  insert into credit_transactions (user_id, amount, reason, metadata)
  values (p_user_id, 1, p_reason, p_metadata);

  return v_new_balance;
end;
$$;

-- Grants an arbitrary number of credits — used for Stripe purchase
-- fulfillment and for manually adding credits by hand (see README).
-- Idempotent on p_stripe_event_id: replays of the same Stripe webhook
-- event are safely ignored rather than double-granting.
create or replace function grant_credits(
  p_user_id uuid,
  p_amount integer,
  p_reason text,
  p_stripe_event_id text default null,
  p_metadata jsonb default '{}'::jsonb
)
returns integer
language plpgsql
as $$
declare
  v_new_balance integer;
begin
  if p_stripe_event_id is not null
     and exists (select 1 from credit_transactions where stripe_event_id = p_stripe_event_id) then
    select credits_balance into v_new_balance from profiles where id = p_user_id;
    return v_new_balance;
  end if;

  update profiles
  set credits_balance = credits_balance + p_amount,
      updated_at = now()
  where id = p_user_id
  returning credits_balance into v_new_balance;

  insert into credit_transactions (user_id, amount, reason, stripe_event_id, metadata)
  values (p_user_id, p_amount, p_reason, p_stripe_event_id, p_metadata);

  return v_new_balance;
end;
$$;

-- Sets membership tier (used on subscription checkout completion / Stripe
-- subscription webhooks). Separate from credits so a tier change never
-- silently loses a credit-transaction audit trail.
create or replace function set_membership_tier(p_user_id uuid, p_tier text)
returns void
language plpgsql
as $$
begin
  update profiles
  set membership_tier = p_tier,
      updated_at = now()
  where id = p_user_id;
end;
$$;
