/**
 * SERVER-ONLY. Wraps the Postgres RPCs in sql/schema.sql for reading and
 * changing a user's credit balance. Always call with a user id you've
 * already verified via getAuthenticatedUser() — never a client-supplied
 * id — since this uses the service-role client and bypasses RLS.
 */

import { getServiceRoleClient } from "./supabaseServer";

export class CreditsNotConfiguredError extends Error {}

export interface Profile {
  fullName: string;
  creditsBalance: number;
  membershipTier: "free" | "member" | "professional";
}

export async function getProfile(userId: string): Promise<Profile | null> {
  const db = getServiceRoleClient();
  if (!db) throw new CreditsNotConfiguredError("Accounts aren't configured yet.");

  const { data, error } = await db
    .from("profiles")
    .select("full_name, credits_balance, membership_tier")
    .eq("id", userId)
    .maybeSingle();

  if (error) {
    console.error("[credits] getProfile failed:", error.message);
    return null;
  }
  if (!data) return null;

  return {
    fullName: data.full_name,
    creditsBalance: data.credits_balance,
    membershipTier: data.membership_tier,
  };
}

/**
 * Atomically spends 1 credit. Returns the new balance, or null if the
 * user had no credits left (caller must refuse the action in that case
 * — do not call the Claude API first and check this after).
 */
export async function consumeCredit(
  userId: string,
  metadata: Record<string, unknown> = {}
): Promise<number | null> {
  const db = getServiceRoleClient();
  if (!db) throw new CreditsNotConfiguredError("Accounts aren't configured yet.");

  const { data, error } = await db.rpc("consume_credit", {
    p_user_id: userId,
    p_reason: "analysis_run",
    p_metadata: metadata,
  });
  if (error) {
    console.error("[credits] consumeCredit failed:", error.message);
    return null;
  }
  return data as number | null;
}

/** Refunds 1 credit — call when a Run Analysis attempt fails after consumeCredit succeeded. */
export async function refundCredit(
  userId: string,
  metadata: Record<string, unknown> = {}
): Promise<void> {
  const db = getServiceRoleClient();
  if (!db) return;
  const { error } = await db.rpc("refund_credit", {
    p_user_id: userId,
    p_reason: "refund",
    p_metadata: metadata,
  });
  if (error) console.error("[credits] refundCredit failed:", error.message);
}

/**
 * Grants credits — used for Stripe purchase fulfillment (pass the Stripe
 * event id for idempotency) and for manually adding credits by hand.
 */
export async function grantCredits(
  userId: string,
  amount: number,
  reason: "purchase" | "manual_grant",
  stripeEventId?: string,
  metadata: Record<string, unknown> = {}
): Promise<number | null> {
  const db = getServiceRoleClient();
  if (!db) throw new CreditsNotConfiguredError("Accounts aren't configured yet.");

  const { data, error } = await db.rpc("grant_credits", {
    p_user_id: userId,
    p_amount: amount,
    p_reason: reason,
    p_stripe_event_id: stripeEventId ?? null,
    p_metadata: metadata,
  });
  if (error) {
    console.error("[credits] grantCredits failed:", error.message);
    return null;
  }
  return data as number | null;
}

export async function setMembershipTier(
  userId: string,
  tier: "free" | "member" | "professional"
): Promise<void> {
  const db = getServiceRoleClient();
  if (!db) return;
  const { error } = await db.rpc("set_membership_tier", { p_user_id: userId, p_tier: tier });
  if (error) console.error("[credits] setMembershipTier failed:", error.message);
}
