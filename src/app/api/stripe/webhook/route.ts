import { NextResponse } from "next/server";
import Stripe from "stripe";
import { getStripeClient } from "@/lib/stripeServer";
import { grantCredits, setMembershipTier } from "@/lib/credits";
import { membershipTiers, creditPacks } from "@/content/membership.config";

/**
 * Stripe calls this directly — there is no user session here. Trust
 * nothing in the request body until the signature is verified against
 * STRIPE_WEBHOOK_SECRET; that's what proves the event genuinely came
 * from Stripe and wasn't forged by a third party hitting this URL.
 */
export async function POST(request: Request) {
  const stripe = getStripeClient();
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!stripe || !webhookSecret) {
    return NextResponse.json({ error: "Stripe isn't configured." }, { status: 503 });
  }

  const signature = request.headers.get("stripe-signature");
  if (!signature) {
    return NextResponse.json({ error: "Missing signature." }, { status: 400 });
  }

  const rawBody = await request.text();

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(rawBody, signature, webhookSecret);
  } catch (err) {
    console.error("[stripe-webhook] signature verification failed:", err);
    return NextResponse.json({ error: "Invalid signature." }, { status: 400 });
  }

  if (event.type === "checkout.session.completed") {
    const session = event.data.object as Stripe.Checkout.Session;
    const userId = session.metadata?.userId;

    if (!userId) {
      console.error("[stripe-webhook] checkout.session.completed with no userId in metadata");
      return NextResponse.json({ received: true });
    }

    if (session.metadata?.type === "credit_pack") {
      // Re-derive the credit amount from our own config by packId rather
      // than trusting a number carried in metadata — a single source of
      // truth for "how many credits does this pack grant".
      const pack = creditPacks.find((p) => p.id === session.metadata?.packId);
      if (pack) {
        await grantCredits(userId, pack.credits, "purchase", event.id, {
          checkoutSessionId: session.id,
          packId: pack.id,
        });
      } else {
        console.error("[stripe-webhook] unknown packId in metadata:", session.metadata?.packId);
      }
    }

    if (session.metadata?.type === "membership") {
      const tierId = session.metadata.tierId as "member" | "professional" | undefined;
      const tier = membershipTiers.find((t) => t.id === tierId);
      if (tier) {
        await setMembershipTier(userId, tier.id);
        if (tier.creditAllowance > 0) {
          await grantCredits(userId, tier.creditAllowance, "purchase", event.id, {
            checkoutSessionId: session.id,
            tierId: tier.id,
          });
        }
      }
    }
  }

  return NextResponse.json({ received: true });
}
