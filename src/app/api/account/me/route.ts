import { NextResponse } from "next/server";
import { getAuthenticatedUser } from "@/lib/supabaseServerAuth";
import { getProfile, CreditsNotConfiguredError } from "@/lib/credits";

export async function GET() {
  const user = await getAuthenticatedUser();
  if (!user) {
    return NextResponse.json({ signedIn: false });
  }

  try {
    const profile = await getProfile(user.id);
    if (!profile) {
      return NextResponse.json({ signedIn: true, profile: null });
    }
    return NextResponse.json({ signedIn: true, profile });
  } catch (err) {
    if (err instanceof CreditsNotConfiguredError) {
      return NextResponse.json({ signedIn: true, profile: null });
    }
    console.error("[account/me] unexpected error:", err);
    return NextResponse.json({ error: "Something went wrong." }, { status: 500 });
  }
}
