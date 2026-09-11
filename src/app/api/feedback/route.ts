import { NextResponse } from "next/server";
import { insertFeedback } from "@/lib/supabaseServer";

interface RequestBody {
  sessionId?: string;
  categoryId?: string;
  rating?: "up" | "down";
  comment?: string;
}

const MAX_COMMENT_LENGTH = 500;

export async function POST(request: Request) {
  let body: RequestBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  if (!body.sessionId || !body.categoryId || (body.rating !== "up" && body.rating !== "down")) {
    return NextResponse.json({ error: "Missing required fields." }, { status: 400 });
  }

  const comment = body.comment?.trim().slice(0, MAX_COMMENT_LENGTH) || undefined;

  try {
    await insertFeedback({
      sessionId: body.sessionId,
      categoryId: body.categoryId,
      rating: body.rating,
      comment,
    });
    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error("[feedback] unexpected error:", err);
    return NextResponse.json({ error: "Something went wrong. Please try again." }, { status: 500 });
  }
}
