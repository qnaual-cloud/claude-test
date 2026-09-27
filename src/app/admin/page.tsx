import { notFound } from "next/navigation";
import { requireAdminUser } from "@/lib/adminAuth";
import { AdminPanel } from "@/components/AdminPanel";
import { membershipTiers, currencySymbols } from "@/content/membership.config";

// Must never be statically prerendered — the admin check has to run on
// every request. Without this, whether the auth check is actually
// per-request depends on Next.js noticing a dynamic API call during the
// build, which in turn depends on env vars being set at build time. For
// a security-sensitive page, that's not a chance worth taking.
export const dynamic = "force-dynamic";

export default async function AdminPage() {
  const admin = await requireAdminUser();
  if (!admin) notFound();

  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-4 py-12 sm:py-16">
      <h1 className="mb-1 text-2xl font-semibold text-foreground">Admin</h1>
      <p className="mb-8 text-sm text-muted-foreground">Signed in as {admin.email}.</p>

      <section className="mb-10">
        <h2 className="mb-3 text-base font-semibold text-foreground">Users &amp; credits</h2>
        <AdminPanel />
      </section>

      <section>
        <h2 className="mb-1 text-base font-semibold text-foreground">Membership tiers</h2>
        <p className="mb-3 text-sm text-muted-foreground">
          Read-only summary of <code className="text-xs">src/content/membership.config.ts</code> —
          edit that file to change prices, Stripe price ids, or the credit allowance each tier
          grants on subscribe.
        </p>
        <div className="flex flex-col gap-2">
          {membershipTiers.map((tier) => (
            <div
              key={tier.id}
              className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border bg-card p-3 text-sm"
            >
              <span className="font-medium text-foreground">{tier.name}</span>
              <span className="text-muted-foreground">
                {tier.creditAllowance} credits on subscribe · GBP price:{" "}
                {tier.price.GBP !== null ? `${currencySymbols.GBP}${tier.price.GBP}` : "not set"} ·
                USD price: {tier.price.USD !== null ? `${currencySymbols.USD}${tier.price.USD}` : "not set"} ·
                Stripe: {tier.stripePriceId.GBP || tier.stripePriceId.USD ? "connected" : "not connected"}
              </span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
