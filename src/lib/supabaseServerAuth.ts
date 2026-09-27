/**
 * Server-side helper for reading "who is logged in" — used in Route
 * Handlers (API routes) and Server Components. Reads the session from
 * cookies and validates it against Supabase (never trusts a
 * client-supplied user id). Returns null if Supabase auth isn't
 * configured or nobody is signed in — callers must handle that as
 * "not authenticated", not as an error.
 */

import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import type { SupabaseClient } from "@supabase/supabase-js";

async function getServerSupabaseClient(): Promise<SupabaseClient | null> {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !anonKey) return null;

  const cookieStore = await cookies();

  return createServerClient(url, anonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          );
        } catch {
          // Called from a Server Component render, where cookies are
          // read-only. Safe to ignore — middleware already refreshes
          // the session cookie on the request.
        }
      },
    },
  });
}

export interface AuthenticatedUser {
  id: string;
  email: string | undefined;
}

export async function getAuthenticatedUser(): Promise<AuthenticatedUser | null> {
  const supabase = await getServerSupabaseClient();
  if (!supabase) return null;

  const { data, error } = await supabase.auth.getUser();
  if (error || !data.user) return null;

  return { id: data.user.id, email: data.user.email };
}
