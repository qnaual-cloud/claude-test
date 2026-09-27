import Link from "next/link";
import { siteConfig } from "@/content/site.config";

/** Shown instead of a plain error line when Run Analysis is attempted with 0 credits left. */
export function OutOfCreditsNotice() {
  const copy = siteConfig.outOfCredits;

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h3 className="text-base font-semibold text-foreground">{copy.title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{copy.body}</p>
      <div className="mt-4 flex flex-wrap gap-3">
        <Link
          href="/#buy-credits"
          className="min-h-10 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:bg-accent-hover"
        >
          {copy.buyCreditsLabel}
        </Link>
        <Link
          href="/#membership"
          className="min-h-10 rounded-lg border border-accent px-4 py-2 text-sm font-medium text-accent hover:bg-accent/10"
        >
          {copy.viewMembershipsLabel}
        </Link>
      </div>
    </div>
  );
}
