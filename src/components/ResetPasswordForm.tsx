"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getSupabaseBrowserClient } from "@/lib/supabaseBrowser";

type SessionCheck = "checking" | "ready" | "no-session";

export function ResetPasswordForm({ returnTo }: { returnTo?: string }) {
  const router = useRouter();
  const supabase = getSupabaseBrowserClient();
  const destination = returnTo || "/";

  const [sessionCheck, setSessionCheck] = useState<SessionCheck>("checking");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting">("idle");
  const [error, setError] = useState("");

  // Supabase's reset-password email links to this page carrying a
  // recovery token in the URL; the browser client picks it up
  // automatically and either fires a PASSWORD_RECOVERY auth event or has
  // already established the session by the time getSession() resolves —
  // check both, since which one fires first isn't guaranteed.
  useEffect(() => {
    if (!supabase) return;
    let settled = false;
    function markReady() {
      if (settled) return;
      settled = true;
      setSessionCheck("ready");
    }

    supabase.auth.getSession().then(({ data }) => {
      if (data.session) markReady();
      else if (!settled) setSessionCheck("no-session");
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY") markReady();
    });
    return () => subscription.unsubscribe();
  }, [supabase]);

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
    setError("");
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setStatus("submitting");
    const { error: updateError } = await supabase!.auth.updateUser({ password });
    if (updateError) {
      setError(updateError.message);
      setStatus("idle");
      return;
    }
    router.push(destination);
  }

  if (sessionCheck === "checking") {
    return null;
  }

  if (sessionCheck === "no-session") {
    return (
      <div className="flex flex-col gap-3">
        <p className="text-sm text-red-600">
          This password reset link is invalid or has expired.
        </p>
        <Link href="/forgot-password" className="text-sm font-medium text-accent hover:underline">
          Request a new link
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <label htmlFor="password" className="text-sm font-medium text-foreground">
          New password
        </label>
        <input
          id="password"
          type="password"
          required
          minLength={6}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="min-h-11 rounded-lg border border-border bg-card px-3 py-2 text-base text-foreground outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
      </div>
      <div className="flex flex-col gap-2">
        <label htmlFor="confirmPassword" className="text-sm font-medium text-foreground">
          Confirm new password
        </label>
        <input
          id="confirmPassword"
          type="password"
          required
          minLength={6}
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="min-h-11 rounded-lg border border-border bg-card px-3 py-2 text-base text-foreground outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={status === "submitting"}
        className="min-h-11 rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground hover:bg-accent-hover disabled:opacity-50"
      >
        {status === "submitting" ? "Updating…" : "Update password"}
      </button>
    </form>
  );
}
