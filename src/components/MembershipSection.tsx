"use client";

import { useState } from "react";
import { membershipTiers } from "@/content/membership.config";
import { startCheckout } from "@/lib/startCheckout";
import { useCurrency } from "@/lib/currencyContext";
import { ProficereProfessionalCard } from "@/components/ProficereProfessionalCard";

export function MembershipSection() {
  const { currency, setCurrency } = useCurrency();
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [errorByTier, setErrorByTier] = useState<Record<string, string>>({});

  async function handleSubscribe(tierId: "member" | "professional") {
    setPendingId(tierId);
    setErrorByTier((prev) => ({ ...prev, [tierId]: "" }));
    const result = await startCheckout({ type: "membership", tierId, currency });
    if (!result.ok) {
      setErrorByTier((prev) => ({ ...prev, [tierId]: result.error }));
      setPendingId(null);
    }
  }

  const symbol = currency === "GBP" ? "£" : "$";
  const regionLabel = currency === "GBP" ? "UK" : "US";

  return (
    <section className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold text-foreground">Membership</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Proposed beta pricing — sign-up isn&apos;t open yet during testing.
        </p>
      </div>

      <div className="inline-flex w-fit rounded-full border border-border bg-muted p-1" role="group" aria-label="Currency">
        <button
          type="button"
          onClick={() => setCurrency("GBP")}
          aria-pressed={currency === "GBP"}
          className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
            currency === "GBP"
              ? "bg-accent text-accent-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          GBP (£)
        </button>
        <button
          type="button"
          onClick={() => setCurrency("USD")}
          aria-pressed={currency === "USD"}
          className={`rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
            currency === "USD"
              ? "bg-accent text-accent-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          USD ($)
        </button>
      </div>

      <div className="flex flex-col gap-4">
        {membershipTiers.map((tier) => {
          const canSubscribe = tier.id !== "free";
          const price = tier.price[currency];
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

              {price !== null ? (
                <p className="text-xl font-semibold text-foreground">
                  {symbol}
                  {price}
                  <span className="text-sm font-normal text-muted-foreground">
                    {" "}
                    {regionLabel}
                    {tier.priceSuffix}
                  </span>
                </p>
              ) : (
                <p className="text-2xl font-semibold text-muted-foreground">Free</p>
              )}

              {tier.creditAllowance > 0 && (
                <p className="text-sm font-medium text-accent">
                  {tier.creditAllowance} credits / month
                  {tier.annualTotalCredits && ` (${tier.annualTotalCredits} credits over 12 months)`}
                </p>
              )}
              <ul className="flex flex-col gap-1.5 text-sm text-foreground">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex gap-2">
                    <span className="text-accent">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              {canSubscribe && (
                <div className="mt-auto pt-2">
                  <button
                    type="button"
                    onClick={() => handleSubscribe(tier.id as "member" | "professional")}
                    disabled={pendingId === tier.id}
                    className="min-h-9 w-full rounded-lg bg-accent px-3 py-2 text-sm font-medium text-accent-foreground hover:bg-accent-hover disabled:opacity-50"
                  >
                    {pendingId === tier.id ? "Redirecting…" : "Subscribe"}
                  </button>
                  {errorByTier[tier.id] && (
                    <p className="mt-1.5 text-xs text-red-600">{errorByTier[tier.id]}</p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div id="professional">
        <ProficereProfessionalCard />
      </div>
    </section>
  );
}
