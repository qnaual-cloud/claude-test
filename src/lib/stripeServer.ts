/**
 * SERVER-ONLY, env-gated Stripe client. Mirrors the same graceful
 * fallback pattern as supabaseServer.ts and anthropicClient.ts: if
 * STRIPE_SECRET_KEY isn't set, getStripeClient() returns null and
 * callers show "not available yet" instead of failing.
 */

import Stripe from "stripe";

let client: Stripe | null | undefined;

export function getStripeClient(): Stripe | null {
  if (client !== undefined) return client;

  const secretKey = process.env.STRIPE_SECRET_KEY;
  if (!secretKey) {
    client = null;
    return null;
  }

  client = new Stripe(secretKey);
  return client;
}
