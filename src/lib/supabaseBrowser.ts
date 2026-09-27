"use client";

/**
 * Browser-side Supabase client, used ONLY for auth (sign up, sign in,
 * sign out, reading the current session). It uses the public anon key,
 * which is safe to expose — Supabase's anon key has no table access in
 * this app (RLS is enabled everywhere with no public policies; see
 * sql/schema.sql). Never use this client to query tables directly —
 * account/credit data is read via /api/account/me instead.
 */

import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | null | undefined;

export function getSupabaseBrowserClient(): SupabaseClient | null {
  if (client !== undefined) return client;

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !anonKey) {
    client = null;
    return null;
  }

  client = createBrowserClient(url, anonKey);
  return client;
}
