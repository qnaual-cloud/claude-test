import { NextResponse } from "next/server";
import { requireAdminUser } from "@/lib/adminAuth";
import { searchProfiles, CreditsNotConfiguredError } from "@/lib/credits";

export async function GET(request: Request) {
  const admin = await requireAdminUser();
  if (!admin) {
    return NextResponse.json({ error: "Not authorized." }, { status: 403 });
  }

  const query = new URL(request.url).searchParams.get("q")?.trim() ?? "";

  try {
    const users = await searchProfiles(query);
    return NextResponse.json({ users });
  } catch (err) {
    if (err instanceof CreditsNotConfiguredError) {
      return NextResponse.json({ error: err.message }, { status: 503 });
    }
    console.error("[admin/users] unexpected error:", err);
    return NextResponse.json({ error: "Something went wrong." }, { status: 500 });
  }
}
