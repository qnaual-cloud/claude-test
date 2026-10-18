import { NextResponse } from "next/server";
import { getAuthenticatedUser } from "@/lib/supabaseServerAuth";
import { getProfile, reconcileStaleAnalysisRuns, CreditsNotConfiguredError } from "@/lib/credits";

export async function GET() {
  const user = await getAuthenticatedUser();
  if (!user) {
    return NextResponse.json({ signedIn: false });
  }

  try {
    // Opportunistic safety net: if a past analysis was interrupted
    // (e.g. a platform timeout) before it could refund its own
    // reserved credit, restore it here so the balance self-heals the
    // next time the user looks at it — never blocks or fails this
    // request if it errors.
    await reconcileStaleAnalysisRuns(user.id);

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
