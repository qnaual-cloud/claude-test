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
