"use client";

import { useState } from "react";
import { membershipTiers, type Currency } from "@/content/membership.config";
import { startCheckout } from "@/lib/startCheckout";

export function MembershipSection() {
  const [pendingKey, setPendingKey] = useState<string | null>(null);
  const [errorByKey, setErrorByKey] = useState<Record<string, string>>({});

  async function handleSubscribe(tierId: "member" | "professional", currency: Currency) {
    const key = `${tierId}-${currency}`;
    setPendingKey(key);
    setErrorByKey((prev) => ({ ...prev, [key]: "" }));
    const result = await startCheckout({ type: "membership", tierId, currency });
    if (!result.ok) {
      setErrorByKey((prev) => ({ ...prev, [key]: result.error }));
      setPendingKey(null);
    }
  }

  return (
    <section className="flex flex-col gap-6">
      <div>
        <h2 className="text-xl font-semibold text-foreground">Membership</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Proposed beta pricing — sign-up isn&apos;t open yet during testing.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {membershipTiers.map((tier) => {
          const canSubscribe = tier.id !== "free";
          const hasPrice = tier.price.GBP !== null && tier.price.USD !== null;
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

              {hasPrice ? (
                <div className="text-foreground">
                  <p className="text-xl font-semibold">
                    £{tier.price.GBP}
                    <span className="text-sm font-normal text-muted-foreground">
                      {" "}
                      UK{tier.priceSuffix}
                    </span>
                  </p>
                  <p className="text-xl font-semibold">
                    ${tier.price.USD}
                    <span className="text-sm font-normal text-muted-foreground">
                      {" "}
                      US{tier.priceSuffix}
                    </span>
                  </p>
                </div>
              ) : (
                <p className="text-2xl font-semibold text-muted-foreground">Free</p>
              )}

              {tier.creditAllowance > 0 && (
                <p className="text-sm font-medium text-accent">
                  {tier.creditAllowance} analyses / month
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
                <div className="mt-auto flex flex-col gap-1.5 pt-2">
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => handleSubscribe(tier.id as "member" | "professional", "GBP")}
                      disabled={pendingKey === `${tier.id}-GBP`}
                      className="min-h-10 flex-1 rounded-lg border border-accent px-3 py-2 text-sm font-medium text-accent hover:bg-accent/10 disabled:opacity-50"
                    >
                      {pendingKey === `${tier.id}-GBP` ? "Redirecting…" : "Subscribe (UK)"}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleSubscribe(tier.id as "member" | "professional", "USD")}
                      disabled={pendingKey === `${tier.id}-USD`}
                      className="min-h-10 flex-1 rounded-lg border border-accent px-3 py-2 text-sm font-medium text-accent hover:bg-accent/10 disabled:opacity-50"
                    >
                      {pendingKey === `${tier.id}-USD` ? "Redirecting…" : "Subscribe (US)"}
                    </button>
                  </div>
                  {(errorByKey[`${tier.id}-GBP`] || errorByKey[`${tier.id}-USD`]) && (
                    <p className="text-xs text-red-600">
                      {errorByKey[`${tier.id}-GBP`] || errorByKey[`${tier.id}-USD`]}
                    </p>
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
