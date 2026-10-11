/**
 * The prominent credit-balance box. Always reflects the real account
 * balance passed in by the caller — never a hardcoded number. A real
 * zero shows plainly as "0 credits"; an unknown balance shows a clear,
 * distinct loading/error message instead — never a misleading zero.
 */
export function CreditsBadge({
  status,
  balance,
}: {
  status: "loading" | "ready" | "error";
  balance?: number | null;
}) {
  if (status === "loading") {
    return (
      <span className="inline-flex items-center rounded-full border border-border bg-muted px-3 py-1.5 text-sm font-medium text-muted-foreground">
        Loading credits…
      </span>
    );
  }

  if (status === "error" || balance === null || balance === undefined) {
    return (
      <span className="inline-flex items-center rounded-full border border-border bg-muted px-3 py-1.5 text-sm font-medium text-muted-foreground">
        Unable to load credit balance
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-success-border bg-success-bg px-3 py-1.5 text-sm font-semibold text-success-foreground">
      {balance === 0 ? "0 credits" : `${balance} credits remaining`}
    </span>
  );
}
