"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { creditPacks, currencySymbols, defaultCurrency, type Currency } from "@/content/membership.config";
import { startCheckout } from "@/lib/startCheckout";
import { onCreditsChanged } from "@/lib/creditsEvents";

interface Profile {
  creditsBalance: number;
}

type LoadState =
  | { status: "loading" }
  | { status: "signed-out" }
  | { status: "signed-in"; profile: Profile | null };

export function BuyCreditsSection() {
  const [state, setState] = useState<LoadState>({ status: "loading" });
  const [currency, setCurrency] = useState<Currency>(defaultCurrency);
  const [pendingPackId, setPendingPackId] = useState<string | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    function refresh() {
      fetch("/api/account/me")
        .then((res) => res.json())
        .then((data) => {
          if (cancelled) return;
          if (!data.signedIn) setState({ status: "signed-out" });
          else setState({ status: "signed-in", profile: data.profile });
        })
        .catch(() => {
          if (!cancelled) setState({ status: "signed-out" });
        });
    }
    refresh();
    const unsubscribe = onCreditsChanged(refresh);
    return () => {
      cancelled = true;
      unsubscribe();
    };
  }, []);

  async function handleBuy(packId: string) {
    setPendingPackId(packId);
    setError("");
    const result = await startCheckout({ type: "credit_pack", packId, currency });
    if (!result.ok) {
      setError(result.error);
      setPendingPackId(null);
    }
  }

  if (state.status === "loading") return null;

  return (
    <section className="flex flex-col gap-3 rounded-xl border border-border bg-card p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-foreground">Buy Credits</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Each Run Analysis uses 1 credit. New accounts get 5 free after confirming their email.
          </p>
        </div>
        {state.status === "signed-in" && (
          <div className="inline-flex rounded-lg border border-border p-1">
            {(["GBP", "USD"] as Currency[]).map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => setCurrency(c)}
                aria-pressed={currency === c}
                className={`min-h-8 rounded-md px-2.5 text-xs font-medium transition-colors ${
                  currency === c
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {currencySymbols[c]} {c}
              </button>
            ))}
          </div>
        )}
      </div>

      {state.status === "signed-out" ? (
        <p className="text-sm text-muted-foreground">
          <Link href="/login" className="font-medium text-accent hover:underline">
            Log in
          </Link>{" "}
          to buy credits.
        </p>
      ) : (
        <>
          {state.profile && (
            <p className="text-sm text-foreground">{state.profile.creditsBalance} credits remaining</p>
          )}
          <div className="flex flex-col gap-2">
            {creditPacks.map((pack) => {
              const amount = pack.price[currency];
              return (
                <div
                  key={pack.id}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border p-3"
                >
                  <div className="text-sm text-foreground">
                    <span className="font-medium">{pack.name}</span> — {pack.credits} credits
                    {amount !== null && (
                      <span className="text-muted-foreground">
                        {" "}
                        ({currencySymbols[currency]}
                        {amount})
                      </span>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleBuy(pack.id)}
                    disabled={pendingPackId === pack.id}
                    className="min-h-10 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:bg-accent-hover disabled:opacity-50"
                  >
                    {pendingPackId === pack.id ? "Redirecting…" : "Buy"}
                  </button>
                </div>
              );
            })}
          </div>
        </>
      )}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </section>
  );
}
