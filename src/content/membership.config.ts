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
 * show the actual number for both GBP and USD at once (no currency
 * toggle) — change the `price` values below for either currency any
 * time; nothing else needs to change for that to appear.
 *
 * `stripePriceId` is also blank everywhere. Once you've created the
 * corresponding Price in your Stripe dashboard (one Price per currency —
 * Stripe prices are currency-specific), paste its id in here and the
 * Subscribe / Buy Credits buttons start working automatically. Until
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
 * request (both Buy Credits and Subscribe) before it ever looks at a
 * Stripe price id, and tells the tester sign-up isn't open yet. This is
 * what lets beta pricing be visible below WITHOUT risking a real charge
 * — it does not depend on remembering to leave stripePriceId blank.
 * Flip to true only when you are ready to accept real payments AND have
 * filled in real Stripe price ids above.
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
  /** Credits granted when a subscription to this tier is first activated. */
  creditAllowance: number;
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
    // "Analyses per month" shown in the UI. Note: this app does not yet
    // automatically re-grant this allowance every billing cycle — only
    // once, when a subscription first activates (see README). That's
    // moot while PAYMENTS_ENABLED is false, since no real subscription
    // can start yet, but worth building before going live.
    creditAllowance: 20,
    highlighted: true,
  },
  {
    // id stays "professional" internally — displayed as "Annual Member".
    id: "professional",
    name: "Annual Member",
    description: "Pay yearly and save.",
    features: [
      "Everything in Monthly Member",
      "Priority analysis depth",
      "Early access to new research modules",
    ],
    price: { GBP: 500, USD: 500 },
    priceSuffix: "/year",
    stripePriceId: { GBP: null, USD: null },
    creditAllowance: 60,
  },
];

export interface CreditPack {
  id: string;
  name: string;
  credits: number;
  price: Record<Currency, number | null>;
  /** Stripe Price id for this one-time credit pack, per currency. null = not connected yet. */
  stripePriceId: Record<Currency, string | null>;
}

/**
 * "Buy Credits" packages. One pack today — packages and prices aren't
 * decided yet, so add more entries here later (e.g. a larger pack) once
 * they are; the checkout route and Buy Credits UI both already support
 * any number of packs.
 */
export const creditPacks: CreditPack[] = [
  {
    id: "standard",
    name: "Credit pack",
    credits: 20,
    price: { GBP: 9, USD: 9 },
    stripePriceId: { GBP: null, USD: null },
  },
];
