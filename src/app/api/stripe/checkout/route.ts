import { NextResponse } from "next/server";
import { getStripeClient } from "@/lib/stripeServer";
import { getAuthenticatedUser } from "@/lib/supabaseServerAuth";
import { membershipTiers, creditPack, type Currency } from "@/content/membership.config";

interface RequestBody {
  type?: "credit_pack" | "membership";
  tierId?: "member" | "professional";
  currency?: Currency;
}

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
    const priceId = creditPack.stripePriceId[currency];
    if (!priceId) {
      return NextResponse.json(
        { error: "Buying credits isn't available yet — pricing hasn't been connected." },
        { status: 400 }
      );
    }

    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      line_items: [{ price: priceId, quantity: 1 }],
      client_reference_id: user.id,
      customer_email: user.email,
      metadata: { type: "credit_pack", userId: user.id, credits: String(creditPack.credits) },
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
