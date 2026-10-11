/**
 * ============================================================
 *  EDIT PRICING AND TIERS HERE — nowhere else.
 * ============================================================
 *
 * This is the single place to change tier names, descriptions, features,
 * prices, or the default currency. Safe to import from client components
 * (marketing copy only — no proprietary logic). Edit and redeploy; no
 * other file needs to change.
 *
 * A price left `null` for a currency shows as a blank amount next to
 * the symbol ("£ —") rather than a fake or zero price — used for the
 * Free tier, where there's genuinely no number to show. Priced tiers
 * show only the currently-selected currency (GBP/USD toggle at the top
 * of the Membership section, shared with Add Credits via
 * src/lib/currencyContext.tsx) — change the `price` values below for
 * either currency any time; nothing else needs to change for that to
 * appear.
 *
 * `stripePriceId` is also blank everywhere. Once you've created the
 * corresponding Price in your Stripe dashboard (one Price per currency —
 * Stripe prices are currency-specific), paste its id in here and the
 * Subscribe / Add Credits buttons start working automatically. Until
 * then they show "not available yet" instead of erroring.
 *
 * PAYMENTS_ENABLED below is the actual safety switch, separate from
 * stripePriceId — see its own comment.
 */

/**
 * ============================================================
 *  THE testing-period safety switch — read before touching prices.
 * ============================================================
 * While this is false, /api/stripe/checkout refuses every checkout
 * request (both Add Credits and Subscribe) before it ever looks at a
 * Stripe price id, and tells the tester sign-up isn't open yet. This is
 * what lets preview pricing be visible below WITHOUT risking a real
 * charge — it does not depend on remembering to leave stripePriceId
 * blank. Flip to true only when you are ready to accept real payments
 * AND have filled in real Stripe price ids above.
 */
export const PAYMENTS_ENABLED = false;

export type Currency = "GBP" | "USD";

export const currencySymbols: Record<Currency, string> = {
  GBP: "£",
  USD: "$",
};

export const defaultCurrency: Currency = "GBP";

export interface MembershipTier {
  id: "free" | "member" | "professional";
  name: string;
  description: string;
  features: string[];
  /** null = not yet priced; shown as a blank amount next to the currency symbol. */
  price: Record<Currency, number | null>;
  priceSuffix: string;
  /** Stripe Price id for this tier's subscription, per currency. null = not connected yet. */
  stripePriceId: Record<Currency, string | null>;
  /**
   * Credits granted when a subscription to this tier is first activated,
   * and the intended monthly refresh amount once recurring top-ups are
   * built (see the note on the "member" tier below — not automated yet).
   */
  creditAllowance: number;
  /** Only set for annual plans: the total credits over the full 12 months (creditAllowance × 12), shown alongside the monthly figure for clarity. */
  annualTotalCredits?: number;
  highlighted?: boolean;
}

export const membershipTiers: MembershipTier[] = [
  {
    // id stays "free" internally (matches the DB's membership_tier check
    // constraint) — only the displayed name changed to "Free / Starter".
    id: "free",
    name: "Free / Starter",
    description: "For new users and testers — explore every workflow before you commit.",
    features: [
      "All research categories",
      "Guided, step-by-step prompt building",
      "5 free credits to try Run Analysis",
    ],
    price: { GBP: null, USD: null },
    priceSuffix: "/month",
    stripePriceId: { GBP: null, USD: null },
    creditAllowance: 0,
  },
  {
    // id stays "member" internally — displayed as "Monthly Member".
    id: "member",
    name: "Monthly Member",
    description: "Pay monthly, cancel any time.",
    features: [
      "Everything in Free / Starter",
      "Run Analysis — see results inside the app",
      "Research Dashboard format",
    ],
    price: { GBP: 49, USD: 49 },
    priceSuffix: "/month",
    stripePriceId: { GBP: null, USD: null },
    // 50 credits/month shown in the UI. Note: this app does not yet
    // automatically re-grant this allowance every billing cycle — only
    // once, when a subscription first activates (see README). That's
    // moot while PAYMENTS_ENABLED is false, since no real subscription
    // can start yet, but worth building (a recurring monthly top-up on
    // each Stripe invoice.paid event) before going live.
    creditAllowance: 50,
    highlighted: true,
  },
  {
    // id stays "professional" internally — displayed as "Annual Member".
    id: "professional",
    name: "Annual Member",
    description: "Pay yearly — more credits per month and a discounted annual price.",
    features: [
      "Everything in Monthly Member",
      "Priority analysis depth",
      "Early access to new research modules",
    ],
    price: { GBP: 500, USD: 500 },
    priceSuffix: "/year",
    stripePriceId: { GBP: null, USD: null },
    // Same automatic-monthly-refresh caveat as the "member" tier above.
    creditAllowance: 60,
    annualTotalCredits: 720,
  },
];

export interface CreditPack {
  id: string;
  name: string;
  credits: number;
  /** Price for visitors and non-members (no active paid subscription). */
  price: Record<Currency, number | null>;
  /** Stripe Price id for the public price above, per currency. null = not connected yet. */
  stripePriceId: Record<Currency, string | null>;
  /**
   * Discounted price — only ever applied for a user whose *server-verified*
   * membership_tier is not "free" (see creditPackPriceFor() below). Never
   * decided by anything the client sends.
   */
  memberPrice: Record<Currency, number | null>;
  /** Stripe Price id for the member price above, per currency. null = not connected yet. */
  memberStripePriceId: Record<Currency, string | null>;
}

/**
 * "Add Credits" packages. One pack today — packages and prices aren't
 * finalized yet, so add more entries here later (e.g. a larger pack) once
 * they are; the checkout route and Add Credits UI both already support
 * any number of packs.
 */
export const creditPacks: CreditPack[] = [
  {
    id: "standard",
    name: "Credit pack",
    credits: 20,
    price: { GBP: 25, USD: 25 },
    stripePriceId: { GBP: null, USD: null },
    memberPrice: { GBP: 9, USD: 9 },
    memberStripePriceId: { GBP: null, USD: null },
  },
];

/** True for any paid membership tier — the only thing that unlocks the member credit-pack price. */
export function isActiveMembership(membershipTier: MembershipTier["id"] | null | undefined): boolean {
  return membershipTier === "member" || membershipTier === "professional";
}

/**
 * The one place that decides which credit-pack price applies. Used by both
 * the Add Credits UI (for display) and the checkout route (to pick the
 * Stripe price id) — the route always calls this with a membership tier it
 * looked up itself from the database, never one supplied by the client, so
 * a non-member can never be charged the member price.
 */
export function creditPackPriceFor(
  pack: CreditPack,
  membershipTier: MembershipTier["id"] | null | undefined,
  currency: Currency
): number | null {
  return isActiveMembership(membershipTier) ? pack.memberPrice[currency] : pack.price[currency];
}
