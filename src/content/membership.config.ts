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
 */

export type Currency = "GBP" | "USD";

export const currencySymbols: Record<Currency, string> = {
  GBP: "£",
  USD: "$",
};

export const defaultCurrency: Currency = "GBP";

export interface MembershipTier {
  id: string;
  name: string;
  description: string;
  features: string[];
  /** null = not yet priced; shown as a blank amount next to the currency symbol. */
  price: Record<Currency, number | null>;
  priceSuffix: string;
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
  },
];
