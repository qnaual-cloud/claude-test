import Link from "next/link";
import { siteConfig } from "@/content/site.config";

/**
 * Shown instead of the generated prompt when "Generate Prompt" is
 * attempted while logged out. `returnTo` carries the current research
 * page so login/register can send the user straight back here, where
 * their saved selections (see src/lib/pendingResearch.ts) pick up
 * automatically.
 */
export function AuthRequiredNotice({ returnTo }: { returnTo: string }) {
  const copy = siteConfig.authRequired;
  const suffix = `?returnTo=${encodeURIComponent(returnTo)}`;

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h3 className="text-base font-semibold text-foreground">{copy.title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{copy.body}</p>
      <div className="mt-4 flex flex-wrap gap-3">
        <Link
          href={`/register${suffix}`}
          className="min-h-10 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:bg-accent-hover"
        >
          {copy.registerLabel}
        </Link>
        <Link
          href={`/login${suffix}`}
          className="min-h-10 rounded-lg border border-accent px-4 py-2 text-sm font-medium text-accent hover:bg-accent/10"
        >
          {copy.loginLabel}
        </Link>
      </div>
    </div>
  );
}
