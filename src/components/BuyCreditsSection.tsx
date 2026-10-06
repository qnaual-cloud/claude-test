"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { creditPacks, type Currency } from "@/content/membership.config";
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
  const [pendingKey, setPendingKey] = useState<string | null>(null);
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

  async function handleBuy(packId: string, currency: Currency) {
    const key = `${packId}-${currency}`;
    setPendingKey(key);
    setError("");
    const result = await startCheckout({ type: "credit_pack", packId, currency });
    if (!result.ok) {
      setError(result.error);
      setPendingKey(null);
    }
  }

  if (state.status === "loading") return null;

  return (
    <section className="flex flex-col gap-3 rounded-xl border border-border bg-card p-5">
      <div>
        <h2 className="text-base font-semibold text-foreground">Buy Credits</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Each Run Analysis uses 1 credit. New accounts get 5 free after confirming their email.
        </p>
      </div>

      {state.status === "signed-in" && state.profile && (
        <p className="text-sm text-foreground">{state.profile.creditsBalance} credits remaining</p>
      )}
      <div className="flex flex-col gap-2">
        {creditPacks.map((pack) => (
          <div
            key={pack.id}
            className="flex flex-col gap-2 rounded-lg border border-border p-3 sm:flex-row sm:items-center sm:justify-between"
          >
            <div className="text-sm text-foreground">
              <span className="font-medium">{pack.credits} Credits</span>
              {pack.price.GBP !== null && pack.price.USD !== null && (
                <span className="text-muted-foreground">
                  {" "}
                  — £{pack.price.GBP} UK / ${pack.price.USD} US
                </span>
              )}
            </div>
            {state.status === "signed-out" ? (
              <Link
                href="/login"
                className="min-h-10 rounded-lg bg-accent px-4 py-2 text-center text-sm font-medium text-accent-foreground hover:bg-accent-hover"
              >
                Log in to buy
              </Link>
            ) : (
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => handleBuy(pack.id, "GBP")}
                  disabled={pendingKey === `${pack.id}-GBP`}
                  className="min-h-10 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:bg-accent-hover disabled:opacity-50"
                >
                  {pendingKey === `${pack.id}-GBP`
                    ? "Redirecting…"
                    : `Buy — £${pack.price.GBP ?? "—"} UK`}
                </button>
                <button
                  type="button"
                  onClick={() => handleBuy(pack.id, "USD")}
                  disabled={pendingKey === `${pack.id}-USD`}
                  className="min-h-10 rounded-lg border border-accent px-4 py-2 text-sm font-medium text-accent hover:bg-accent/10 disabled:opacity-50"
                >
                  {pendingKey === `${pack.id}-USD`
                    ? "Redirecting…"
                    : `Buy — $${pack.price.USD ?? "—"} US`}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </section>
  );
}
