"use client";

import { useState } from "react";
import { siteConfig } from "@/content/site.config";

export function EarlyAccessBanner() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("submitting");
    try {
      const res = await fetch("/api/early-access", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) throw new Error("failed");
      setStatus("success");
      setEmail("");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div className="rounded-xl border border-border bg-muted px-5 py-4">
      {status === "success" ? (
        <p className="text-sm text-foreground">{siteConfig.earlyAccess.successMessage}</p>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <p className="flex-1 text-sm text-foreground">{siteConfig.earlyAccess.heading}</p>
          <div className="flex gap-2">
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={siteConfig.earlyAccess.placeholder}
              className="min-h-11 w-full min-w-0 rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 sm:w-56"
            />
            <button
              type="submit"
              disabled={status === "submitting"}
              className="min-h-11 shrink-0 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:bg-accent-hover disabled:opacity-60"
            >
              {siteConfig.earlyAccess.submitLabel}
            </button>
          </div>
        </form>
      )}
      {status === "error" && (
        <p className="mt-2 text-xs text-red-600">{siteConfig.earlyAccess.errorMessage}</p>
      )}
    </div>
  );
}
