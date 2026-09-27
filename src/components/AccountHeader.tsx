"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getSupabaseBrowserClient } from "@/lib/supabaseBrowser";
import { onCreditsChanged } from "@/lib/creditsEvents";

interface Profile {
  fullName: string;
  creditsBalance: number;
  membershipTier: "free" | "member" | "professional";
}

interface MeResponse {
  signedIn: boolean;
  profile?: Profile | null;
}

type HeaderState = { status: "loading" } | { status: "loaded"; data: MeResponse };

export function AccountHeader() {
  const [state, setState] = useState<HeaderState>({ status: "loading" });

  useEffect(() => {
    function refresh() {
      fetch("/api/account/me")
        .then((res) => res.json())
        .then((data: MeResponse) => setState({ status: "loaded", data }))
        .catch(() => setState({ status: "loaded", data: { signedIn: false } }));
    }

    refresh();

    const unsubscribeCredits = onCreditsChanged(refresh);

    const supabase = getSupabaseBrowserClient();
    if (!supabase) return unsubscribeCredits;
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      refresh();
    });
    return () => {
      unsubscribeCredits();
      subscription.unsubscribe();
    };
  }, []);

  async function handleLogout() {
    const supabase = getSupabaseBrowserClient();
    await supabase?.auth.signOut();
  }

  if (state.status === "loading") {
    return <div className="h-12" aria-hidden="true" />;
  }

  if (!state.data.signedIn) {
    return (
      <div className="flex items-center justify-end gap-4 border-b border-border px-4 py-3 text-sm">
        <Link href="/login" className="text-muted-foreground hover:text-accent">
          Log in
        </Link>
        <Link
          href="/register"
          className="rounded-lg bg-accent px-3 py-1.5 font-medium text-accent-foreground hover:bg-accent-hover"
        >
          Register
        </Link>
      </div>
    );
  }

  const name = state.data.profile?.fullName?.trim();

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-4 py-3 text-sm">
      <p className="text-foreground">
        Hello{name ? `, ${name}` : ""}. What can I help you with today?
      </p>
      <div className="flex items-center gap-4">
        {state.data.profile && (
          <span className="text-muted-foreground">{state.data.profile.creditsBalance} credits</span>
        )}
        <button
          type="button"
          onClick={handleLogout}
          className="text-muted-foreground hover:text-accent"
        >
          Log out
        </button>
      </div>
    </div>
  );
}
