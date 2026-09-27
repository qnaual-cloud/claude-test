/**
 * SERVER-ONLY. There's no roles/permissions system in this app — admin
 * access is a plain allowlist of email addresses from an env var. Simple
 * and adequate for a single-owner admin area, but it means:
 *   - ADMIN_EMAILS must be set to YOUR account's email (comma-separated
 *     for more than one).
 *   - Every admin route must call requireAdminUser() itself — never rely
 *     on the /admin page's own check alone, since API routes are
 *     reachable directly regardless of what the page renders.
 */

import { getAuthenticatedUser, type AuthenticatedUser } from "./supabaseServerAuth";

function getAdminEmails(): string[] {
  return (process.env.ADMIN_EMAILS ?? "")
    .split(",")
    .map((e) => e.trim().toLowerCase())
    .filter(Boolean);
}

export function isAdminEmail(email: string | undefined | null): boolean {
  if (!email) return false;
  return getAdminEmails().includes(email.toLowerCase());
}

/** Returns the authenticated user if they're an admin, otherwise null. */
export async function requireAdminUser(): Promise<AuthenticatedUser | null> {
  const user = await getAuthenticatedUser();
  if (!user || !isAdminEmail(user.email)) return null;
  return user;
}
