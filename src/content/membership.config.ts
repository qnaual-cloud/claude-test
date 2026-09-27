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
 * Prices are deliberately blank (null) for both currencies right now —
 * the UI shows a currency symbol with no amount ("£ —") rather than a
 * fake or zero price. Fill in `amount` for a tier/currency when pricing
 * is decided; nothing else needs to change for that to appear.
 *
 * `stripePriceId` is also blank everywhere. Once you've created the
 * corresponding Price in your Stripe dashboard (one Price per currency —
 * Stripe prices are currency-specific), paste its id in here and the
 * Subscribe / Buy Credits buttons start working automatically. Until
 * then they show "not available yet" instead of erroring.
 */

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
    id: "free",
    name: "Free",
    description: "Get started with guided research prompts across every category.",
    features: [
      "All research categories",
      "Guided, step-by-step prompt building",
      "Copy Prompt to use anywhere",
    ],
    price: { GBP: null, USD: null },
    priceSuffix: "/month",
    stripePriceId: { GBP: null, USD: null },
    creditAllowance: 0,
  },
  {
    id: "member",
    name: "Member",
    description: "For individual investors who want deeper, formatted results.",
    features: [
      "Everything in Free",
      "Run Analysis — see results inside the app",
      "Research Dashboard format",
    ],
    price: { GBP: null, USD: null },
    priceSuffix: "/month",
    stripePriceId: { GBP: null, USD: null },
    creditAllowance: 0,
    highlighted: true,
  },
  {
    id: "professional",
    name: "Professional",
    description: "For analysts, asset managers, and family offices.",
    features: [
      "Everything in Member",
      "Priority analysis depth",
      "Early access to new research modules",
    ],
    price: { GBP: null, USD: null },
    priceSuffix: "/month",
    stripePriceId: { GBP: null, USD: null },
    creditAllowance: 0,
  },
];

export interface CreditPack {
  name: string;
  credits: number;
  price: Record<Currency, number | null>;
  /** Stripe Price id for this one-time credit pack, per currency. null = not connected yet. */
  stripePriceId: Record<Currency, string | null>;
}

/** The single "Buy Credits" pack offered today. Add more packs later if needed. */
export const creditPack: CreditPack = {
  name: "Credit pack",
  credits: 20,
  price: { GBP: null, USD: null },
  stripePriceId: { GBP: null, USD: null },
};
