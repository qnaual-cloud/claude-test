import { NextResponse } from "next/server";
import { requireAdminUser } from "@/lib/adminAuth";
import { adminAdjustCredits, CreditsNotConfiguredError } from "@/lib/credits";

interface RequestBody {
  userId?: string;
  amount?: number;
  note?: string;
}

export async function POST(request: Request) {
  const admin = await requireAdminUser();
  if (!admin) {
    return NextResponse.json({ error: "Not authorized." }, { status: 403 });
  }

  let body: RequestBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const { userId, amount, note } = body;
  if (!userId || typeof amount !== "number" || !Number.isInteger(amount) || amount === 0) {
    return NextResponse.json(
      { error: "userId and a non-zero integer amount are required." },
      { status: 400 }
    );
  }
  if (Math.abs(amount) > 100000) {
    return NextResponse.json({ error: "Amount is too large." }, { status: 400 });
  }

  try {
    const newBalance = await adminAdjustCredits(userId, amount, admin.email ?? "unknown", note);
    if (newBalance === null) {
      return NextResponse.json({ error: "User not found." }, { status: 404 });
    }
    return NextResponse.json({ creditsBalance: newBalance });
  } catch (err) {
    if (err instanceof CreditsNotConfiguredError) {
      return NextResponse.json({ error: err.message }, { status: 503 });
    }
    console.error("[admin/credits] unexpected error:", err);
    return NextResponse.json({ error: "Something went wrong." }, { status: 500 });
  }
}
