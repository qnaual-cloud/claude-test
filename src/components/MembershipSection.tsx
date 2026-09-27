"use client";

import { useState } from "react";
import {
  membershipTiers,
  currencySymbols,
  defaultCurrency,
  type Currency,
} from "@/content/membership.config";
import { startCheckout } from "@/lib/startCheckout";

export function MembershipSection() {
  const [currency, setCurrency] = useState<Currency>(defaultCurrency);
  const [pendingTierId, setPendingTierId] = useState<string | null>(null);
  const [errorByTier, setErrorByTier] = useState<Record<string, string>>({});

  async function handleSubscribe(tierId: "member" | "professional") {
    setPendingTierId(tierId);
    setErrorByTier((prev) => ({ ...prev, [tierId]: "" }));
    const result = await startCheckout({ type: "membership", tierId, currency });
    if (!result.ok) {
      setErrorByTier((prev) => ({ ...prev, [tierId]: result.error }));
      setPendingTierId(null);
    }
  }

  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-col items-center gap-4 text-center sm:flex-row sm:justify-between sm:text-left">
        <div>
          <h2 className="text-xl font-semibold text-foreground">Membership</h2>
          <p className="mt-1 text-sm text-muted-foreground">Pricing coming soon.</p>
        </div>
        <div className="inline-flex rounded-lg border border-border bg-card p-1">
          {(["GBP", "USD"] as Currency[]).map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setCurrency(c)}
              aria-pressed={currency === c}
              className={`min-h-9 rounded-md px-3 text-sm font-medium transition-colors ${
                currency === c
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {currencySymbols[c]} {c}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {membershipTiers.map((tier) => {
          const amount = tier.price[currency];
          const canSubscribe = tier.id !== "free";
          return (
            <div
              key={tier.id}
              className={`flex flex-col gap-3 rounded-xl border bg-card p-5 ${
                tier.highlighted ? "border-accent" : "border-border"
              }`}
            >
              <div>
                <p className="text-sm font-semibold text-foreground">{tier.name}</p>
                <p className="mt-1 text-sm text-muted-foreground">{tier.description}</p>
              </div>
              <p className="text-2xl font-semibold text-foreground">
                {currencySymbols[currency]}
                {amount !== null ? amount : <span className="text-muted-foreground">—</span>}
                <span className="text-sm font-normal text-muted-foreground">
                  {tier.priceSuffix}
                </span>
              </p>
              <ul className="flex flex-col gap-1.5 text-sm text-foreground">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex gap-2">
                    <span className="text-accent">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              {canSubscribe && (
                <div className="mt-auto flex flex-col gap-1.5 pt-2">
                  <button
                    type="button"
                    onClick={() => handleSubscribe(tier.id as "member" | "professional")}
                    disabled={pendingTierId === tier.id}
                    className="min-h-10 rounded-lg border border-accent px-4 py-2 text-sm font-medium text-accent hover:bg-accent/10 disabled:opacity-50"
                  >
                    {pendingTierId === tier.id ? "Redirecting…" : "Subscribe"}
                  </button>
                  {errorByTier[tier.id] && (
                    <p className="text-xs text-red-600">{errorByTier[tier.id]}</p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
