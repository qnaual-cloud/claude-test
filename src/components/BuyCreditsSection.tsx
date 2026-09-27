"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { creditPack, currencySymbols, defaultCurrency, type Currency } from "@/content/membership.config";
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
  const [pending, setPending] = useState(false);
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

  async function handleBuy() {
    setPending(true);
    setError("");
    const result = await startCheckout({ type: "credit_pack", currency });
    if (!result.ok) {
      setError(result.error);
      setPending(false);
    }
  }

  if (state.status === "loading") return null;

  return (
    <section className="flex flex-col gap-3 rounded-xl border border-border bg-card p-5">
      <div>
        <h2 className="text-base font-semibold text-foreground">Buy Credits</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Each Run Analysis uses 1 credit. New accounts start with 5 free.
        </p>
      </div>

      {state.status === "signed-out" ? (
        <p className="text-sm text-muted-foreground">
          <Link href="/login" className="font-medium text-accent hover:underline">
            Log in
          </Link>{" "}
          to buy credits.
        </p>
      ) : (
        <div className="flex flex-wrap items-center gap-3">
          {state.profile && (
            <span className="text-sm text-foreground">
              {state.profile.creditsBalance} credits remaining
            </span>
          )}
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
          <button
            type="button"
            onClick={handleBuy}
            disabled={pending}
            className="min-h-10 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:bg-accent-hover disabled:opacity-50"
          >
            {pending
              ? "Redirecting…"
              : `Buy ${creditPack.credits} credits`}
          </button>
        </div>
      )}
      {error && <p className="text-xs text-red-600">{error}</p>}
    </section>
  );
}
