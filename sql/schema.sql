-- AI Investment Research Assistant — Supabase schema
--
-- Run this once against a new Supabase project (SQL editor, or `supabase
-- db push`). These tables are written to only from server-side code using
-- the service-role key — Row Level Security is enabled with no public
-- policies, so anon/client keys cannot read or write them directly.
--
-- Safe to re-run against a project that already has this exact schema —
-- every statement below is idempotent (if not exists / or replace / on
-- conflict do nothing). Wrapped in a transaction so a project with
-- *pre-existing* data that conflicts with a new constraint (see the
-- signup_bonus unique index below) fails and rolls back atomically
-- instead of leaving the schema half-upgraded.
--
-- This file does NOT backfill profiles or signup bonuses for users who
-- already existed before this script ran — that's intentionally a
-- separate, one-time script, since it touches existing user data rather
-- than just defining schema.

begin;

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

-- Added after the initial version of this table — safe to re-run.
alter table profiles add column if not exists email text;

-- One-time backfill for any profiles created before the email column
-- existed. Safe to re-run (no-ops once every row has an email).
update profiles
set email = auth.users.email
from auth.users
where profiles.id = auth.users.id and profiles.email is null;

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

-- Enforces "exactly once" for the signup bonus at the database level,
-- not just in application logic — a second attempt to grant it for the
-- same user (e.g. a retried request, or a race between two concurrent
-- triggers) fails this constraint rather than double-crediting.
--
-- IMPORTANT if running against a project with existing data: this will
-- fail to create if any user already has more than one 'signup_bonus'
-- transaction recorded. Check first with:
--   select user_id, count(*) from credit_transactions
--   where reason = 'signup_bonus' group by user_id having count(*) > 1;
-- If that returns rows, resolve them before re-running this script —
-- the whole transaction rolls back cleanly otherwise, so nothing else
-- here is at risk, but this specific statement won't succeed until
-- the duplicates are gone.
create unique index if not exists credit_transactions_one_signup_bonus_per_user_idx
  on credit_transactions (user_id)
  where reason = 'signup_bonus';

alter table profiles enable row level security;
alter table credit_transactions enable row level security;

-- Editable blocklist of disposable/temporary email domains, checked
-- before granting the signup bonus (see grant_signup_bonus below). Add
-- or remove domains any time:
--   insert into blocked_email_domains (domain) values ('example.com');
--   delete from blocked_email_domains where domain = 'example.com';
-- This is a "basic safeguard", not a complete one — it stops the common
-- disposable-inbox pattern, not someone willing to use many real
-- personal addresses. There is no IP/device-based signup throttling in
-- this app yet (see README for why).
create table if not exists blocked_email_domains (
  domain text primary key
);

insert into blocked_email_domains (domain) values
  ('mailinator.com'), ('10minutemail.com'), ('guerrillamail.com'),
  ('tempmail.com'), ('temp-mail.org'), ('yopmail.com'), ('trashmail.com'),
  ('throwawaymail.com'), ('getnada.com'), ('fakeinbox.com'), ('sharklasers.com'),
  ('mailnesia.com'), ('dispostable.com'), ('mintemail.com')
on conflict (domain) do nothing;

-- Grants the 5 starter credits exactly once for a given user, if
-- eligible. Shared by both triggers below so the bonus is correctly
-- granted whether "Confirm email" is enabled or disabled in this
-- project's Auth settings:
--   - disabled: email_confirmed_at is already set the instant the user
--     row is first inserted, so handle_new_user grants it immediately.
--   - enabled: email_confirmed_at starts null and is set later, on the
--     confirmation click, so handle_user_email_confirmed grants it then.
-- Those are mutually exclusive events for a given user (confirmed at
-- insert time, or confirmed later via update — never both), so this is
-- never invoked twice for the same signup under normal operation.
--
-- The balance update runs first and its actual row_count is checked
-- before logging anything — this is what guarantees a transaction row
-- is never written without a matching balance change (e.g. if this is
-- ever called for a user_id with no profiles row yet). The unique
-- index on (user_id) where reason = 'signup_bonus' is the backstop
-- against a genuine concurrent double-call ever recording two bonus
-- rows for the same user.
create or replace function grant_signup_bonus(p_user_id uuid, p_email text)
returns void
language plpgsql
security definer set search_path = public
as $$
declare
  v_domain text;
  v_updated integer;
begin
  if exists (
    select 1 from credit_transactions where user_id = p_user_id and reason = 'signup_bonus'
  ) then
    return;
  end if;

  v_domain := lower(split_part(p_email, '@', 2));
  if exists (select 1 from blocked_email_domains where domain = v_domain) then
    return;
  end if;

  update profiles
  set credits_balance = credits_balance + 5,
      updated_at = now()
  where id = p_user_id;

  get diagnostics v_updated = row_count;
  if v_updated = 0 then
    return; -- no profile row for this user — nothing to credit, nothing to log
  end if;

  insert into credit_transactions (user_id, amount, reason)
  values (p_user_id, 5, 'signup_bonus')
  on conflict do nothing;
end;
$$;

-- New account setup: creates the profile row with 0 credits, then
-- grants the signup bonus immediately if the email is already
-- confirmed at this point (the "Confirm email" disabled case — see
-- grant_signup_bonus above). Otherwise the bonus waits for
-- handle_user_email_confirmed below.
create or replace function handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, full_name, email, credits_balance, membership_tier)
  values (new.id, coalesce(new.raw_user_meta_data ->> 'full_name', ''), new.email, 0, 'free');

  if new.email_confirmed_at is not null then
    perform grant_signup_bonus(new.id, new.email);
  end if;

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();

-- Grants the signup bonus on the unconfirmed-to-confirmed transition —
-- the "Confirm email" enabled case (see grant_signup_bonus above for
-- the disabled case, handled in handle_new_user instead).
create or replace function handle_user_email_confirmed()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  if old.email_confirmed_at is null and new.email_confirmed_at is not null then
    perform grant_signup_bonus(new.id, new.email);
  end if;
  return new;
end;
$$;

drop trigger if exists on_auth_user_email_confirmed on auth.users;
create trigger on_auth_user_email_confirmed
  after update on auth.users
  for each row execute function handle_user_email_confirmed();

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

  -- No profile matched (e.g. a stale/bad id) — don't log a refund that
  -- never actually changed a balance.
  if v_new_balance is null then
    return null;
  end if;

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

  -- No profile matched — don't log a grant that never actually
  -- changed a balance.
  if v_new_balance is null then
    return null;
  end if;

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

-- Manual credit adjustment from the admin area. p_amount can be positive
-- (add) or negative (deduct); the balance is clamped at 0, never goes
-- negative. Always called server-side after verifying the caller is an
-- admin (see src/lib/adminAuth.ts) — this function itself does not
-- check that, so never expose it to a non-admin-gated route.
create or replace function admin_adjust_credits(
  p_user_id uuid,
  p_amount integer,
  p_admin_email text,
  p_note text default null
)
returns integer
language plpgsql
as $$
declare
  v_old_balance integer;
  v_new_balance integer;
  v_actual_delta integer;
begin
  select credits_balance into v_old_balance from profiles where id = p_user_id for update;
  if v_old_balance is null then
    return null; -- no such profile
  end if;

  v_new_balance := greatest(v_old_balance + p_amount, 0);
  v_actual_delta := v_new_balance - v_old_balance;

  update profiles
  set credits_balance = v_new_balance,
      updated_at = now()
  where id = p_user_id;

  -- Log the actual applied change, not the requested amount — if a
  -- deduction is clamped by the floor of 0, the audit trail should
  -- reflect what really happened to the balance.
  if v_actual_delta <> 0 then
    insert into credit_transactions (user_id, amount, reason, metadata)
    values (
      p_user_id,
      v_actual_delta,
      'manual_grant',
      jsonb_build_object('adminEmail', p_admin_email, 'note', coalesce(p_note, ''))
    );
  end if;

  return v_new_balance;
end;
$$;

-- ============================================================
-- Lock down the credit-changing functions
-- ============================================================
-- Postgres grants EXECUTE on a newly created function to PUBLIC by
-- default — meaning anon/authenticated could otherwise call any of
-- these directly via the PostgREST RPC endpoint (/rest/v1/rpc/...),
-- bypassing the app's own auth/ownership checks entirely.
--
-- grant_signup_bonus is the most important one to lock down here: it's
-- SECURITY DEFINER (runs with the function owner's privileges), so RLS
-- does not protect against calling it directly the way it does for
-- consume_credit/refund_credit/grant_credits/admin_adjust_credits
-- below (not SECURITY DEFINER — a direct call from anon/authenticated
-- would run as that role, and RLS with no policies would block it from
-- touching profiles/credit_transactions at all). handle_new_user and
-- handle_user_email_confirmed need no entry here: they `returns
-- trigger`, which Postgres only allows to run as an actual trigger
-- callback, never as a direct call — no grant can change that.
--
-- Only service_role (used exclusively by server-side code, after it
-- has already verified the caller's own session) keeps EXECUTE.
-- set_membership_tier is deliberately left as-is here — it doesn't
-- change credits, and tightening it is a separate decision.
revoke execute on function grant_signup_bonus(uuid, text) from public, anon, authenticated;
revoke execute on function consume_credit(uuid, text, jsonb) from public, anon, authenticated;
revoke execute on function refund_credit(uuid, text, jsonb) from public, anon, authenticated;
revoke execute on function grant_credits(uuid, integer, text, text, jsonb) from public, anon, authenticated;
revoke execute on function admin_adjust_credits(uuid, integer, text, text) from public, anon, authenticated;

grant execute on function grant_signup_bonus(uuid, text) to service_role;
grant execute on function consume_credit(uuid, text, jsonb) to service_role;
grant execute on function refund_credit(uuid, text, jsonb) to service_role;
grant execute on function grant_credits(uuid, integer, text, text, jsonb) to service_role;
grant execute on function admin_adjust_credits(uuid, integer, text, text) to service_role;

commit;
