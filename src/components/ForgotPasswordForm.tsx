"use client";

import { useState } from "react";
import { getSupabaseBrowserClient } from "@/lib/supabaseBrowser";

export function ForgotPasswordForm({ returnTo }: { returnTo?: string }) {
  const supabase = getSupabaseBrowserClient();

  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "sent">("idle");
  const [error, setError] = useState("");

  if (!supabase) {
    return (
      <p className="text-sm text-muted-foreground">
        Accounts aren&apos;t set up yet — add the Supabase environment variables to enable password
        reset.
      </p>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("submitting");
    setError("");

    const redirectTo = `${window.location.origin}/reset-password${
      returnTo ? `?returnTo=${encodeURIComponent(returnTo)}` : ""
    }`;

    const { error: resetError } = await supabase!.auth.resetPasswordForEmail(email, { redirectTo });

    // Supabase doesn't report whether the email actually has an account —
    // show the same "check your email" message either way, so this can't
    // be used to probe which addresses are registered.
    if (resetError) {
      setError(resetError.message);
      setStatus("idle");
      return;
    }
    setStatus("sent");
  }

  if (status === "sent") {
    return (
      <p className="text-sm text-foreground">
        If an account exists for that email, a password reset link is on its way. Check your inbox.
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <label htmlFor="email" className="text-sm font-medium text-foreground">
          Email
        </label>
        <input
          id="email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="min-h-11 rounded-lg border border-border bg-card px-3 py-2 text-base text-foreground outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={status === "submitting"}
        className="min-h-11 rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground hover:bg-accent-hover disabled:opacity-50"
      >
        {status === "submitting" ? "Sending…" : "Send reset link"}
      </button>
    </form>
  );
}
