/**
 * Subscription architecture — SCAFFOLDING ONLY, NOT ACTIVE IN V1.
 *
 * V1 ships with no payments, no billing provider, and no gated features.
 * Every user currently gets full access. This file exists purely so a
 * future build can turn on billing by wiring the single function below,
 * instead of rearchitecting the app.
 *
 * Future plan structure (approved, not yet built):
 *   - Free    — active today, the only plan that does anything in v1.
 *   - Monthly — paid subscription, inactive. Do not build billing for
 *               this until explicitly asked.
 *   - Annual  — paid subscription, inactive. Do not build billing for
 *               this until explicitly asked.
 *
 * When subscriptions are turned on: wire a real payment provider (e.g.
 * Stripe) behind hasProAccess(), set monthly/annual `active: true` below,
 * and gate whichever features should require Pro. Until then, leave this
 * file exactly as scaffolding — do not add payment code speculatively.
 */

export type PlanId = "free" | "monthly" | "annual";

export interface PlanConfig {
  id: PlanId;
  label: string;
  active: boolean;
}

export const PLANS: PlanConfig[] = [
  { id: "free", label: "Free", active: true },
  { id: "monthly", label: "Monthly", active: false },
  { id: "annual", label: "Annual", active: false },
];

export interface CurrentUser {
  id: string;
  planId?: PlanId;
}

/**
 * Single gate for any future paid feature. Always true in v1 — every
 * user has full access and there is nothing to unlock. When billing is
 * added, this becomes the one place that checks a real subscription
 * status instead of returning true unconditionally.
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars -- kept to document the future signature
export function hasProAccess(user?: CurrentUser): boolean {
  return true;
}
