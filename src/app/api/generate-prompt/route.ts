import { NextResponse } from "next/server";
import { generatePrompt, PromptValidationError, type EntityItem } from "@/server/promptEngine";
import { logAnalyticsEvent } from "@/lib/supabaseServer";

interface RequestBody {
  categoryId: string;
  entity: string | EntityItem[];
  roleId?: string;
  chipIds: string[];
  outputFormatId: string;
  sessionId: string;
  usedVoice?: boolean;
}

export async function POST(request: Request) {
  let body: RequestBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  if (!body.sessionId || typeof body.sessionId !== "string") {
    return NextResponse.json({ error: "Missing session id." }, { status: 400 });
  }

  try {
    const result = generatePrompt({
      categoryId: body.categoryId,
      entity: body.entity,
      roleId: body.roleId,
      chipIds: Array.isArray(body.chipIds) ? body.chipIds : [],
      outputFormatId: body.outputFormatId,
    });

    // Fire-and-forget analytics — never blocks or fails the response.
    logAnalyticsEvent({
      sessionId: body.sessionId,
      categoryId: body.categoryId,
      event: "prompt_generated",
      metadata: {
        roleId: body.roleId ?? null,
        chipIds: body.chipIds,
        outputFormatId: body.outputFormatId,
        usedVoice: Boolean(body.usedVoice),
      },
    }).catch(() => {});

    return NextResponse.json(result);
  } catch (err) {
    if (err instanceof PromptValidationError) {
      return NextResponse.json({ error: err.message }, { status: 400 });
    }
    console.error("[generate-prompt] unexpected error:", err);
    return NextResponse.json({ error: "Something went wrong. Please try again." }, { status: 500 });
  }
}
