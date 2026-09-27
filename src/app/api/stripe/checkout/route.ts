import { NextResponse } from "next/server";
import { getStripeClient } from "@/lib/stripeServer";
import { getAuthenticatedUser } from "@/lib/supabaseServerAuth";
import { membershipTiers, creditPacks, type Currency } from "@/content/membership.config";

interface RequestBody {
  type?: "credit_pack" | "membership";
  packId?: string;
  tierId?: "member" | "professional";
  currency?: Currency;
}

// Explicit rather than omitted so the accepted methods are visible and
// intentional here, not just whatever the Stripe Dashboard defaults to.
// Apple Pay and Google Pay are NOT separate entries — Stripe Checkout
// automatically shows them as wallet buttons on top of "card" for
// buyers whose browser/device supports them, with no extra setup needed
// on our side (Checkout is hosted on Stripe's domain, so the Apple Pay
// domain-registration step that self-hosted card forms need doesn't
// apply here). Add more methods later (e.g. "klarna") once decided.
const PAYMENT_METHOD_TYPES: Array<"card"> = ["card"];

export async function POST(request: Request) {
  const user = await getAuthenticatedUser();
  if (!user) {
    return NextResponse.json({ error: "Please log in first." }, { status: 401 });
  }

  const stripe = getStripeClient();
  if (!stripe) {
    return NextResponse.json(
      { error: "Payments aren't set up yet — check back soon." },
      { status: 503 }
    );
  }

  let body: RequestBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const currency = body.currency === "USD" ? "USD" : "GBP";
  const origin = new URL(request.url).origin;

  if (body.type === "credit_pack") {
    const pack = creditPacks.find((p) => p.id === body.packId) ?? creditPacks[0];
    if (!pack) {
      return NextResponse.json({ error: "Unknown credit pack." }, { status: 400 });
    }
    const priceId = pack.stripePriceId[currency];
    if (!priceId) {
      return NextResponse.json(
        { error: "Buying credits isn't available yet — pricing hasn't been connected." },
        { status: 400 }
      );
    }

    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      payment_method_types: PAYMENT_METHOD_TYPES,
      line_items: [{ price: priceId, quantity: 1 }],
      client_reference_id: user.id,
      customer_email: user.email,
      metadata: { type: "credit_pack", userId: user.id, packId: pack.id },
      success_url: `${origin}/?checkout=success`,
      cancel_url: `${origin}/?checkout=cancelled`,
    });

    return NextResponse.json({ url: session.url });
  }

  if (body.type === "membership") {
    const tier = membershipTiers.find((t) => t.id === body.tierId);
    if (!tier) {
      return NextResponse.json({ error: "Unknown membership tier." }, { status: 400 });
    }
    const priceId = tier.stripePriceId[currency];
    if (!priceId) {
      return NextResponse.json(
        { error: "This membership isn't available yet — pricing hasn't been connected." },
        { status: 400 }
      );
    }

    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      payment_method_types: PAYMENT_METHOD_TYPES,
      line_items: [{ price: priceId, quantity: 1 }],
      client_reference_id: user.id,
      customer_email: user.email,
      metadata: { type: "membership", userId: user.id, tierId: tier.id },
      success_url: `${origin}/?checkout=success`,
      cancel_url: `${origin}/?checkout=cancelled`,
    });

    return NextResponse.json({ url: session.url });
  }

  return NextResponse.json({ error: "Invalid checkout type." }, { status: 400 });
}
