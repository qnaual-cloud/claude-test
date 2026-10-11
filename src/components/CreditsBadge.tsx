/**
 * The prominent "Available Credits" box. Always reflects the real
 * account balance passed in by the caller — never a hardcoded number —
 * and shows a distinct loading/error state instead of a misleading
 * zero or dash when the balance can't be read.
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
        Credits unavailable
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-success-border bg-success-bg px-3 py-1.5 text-sm font-semibold text-success-foreground">
      Available Credits: {balance}
    </span>
  );
}
