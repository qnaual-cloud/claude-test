"use client";

import type { Currency } from "@/content/membership.config";

type CheckoutRequest =
  | { type: "credit_pack"; packId: string; currency: Currency }
  | { type: "membership"; tierId: "member" | "professional"; currency: Currency };

/** POSTs to /api/stripe/checkout and redirects to Stripe on success. */
export async function startCheckout(
  body: CheckoutRequest
): Promise<{ ok: true } | { ok: false; error: string }> {
  try {
    const res = await fetch("/api/stripe/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) return { ok: false, error: data.error || "Something went wrong." };
    if (data.url) {
      window.location.href = data.url;
      return { ok: true };
    }
    return { ok: false, error: "Something went wrong." };
  } catch {
    return { ok: false, error: "Something went wrong." };
  }
}
