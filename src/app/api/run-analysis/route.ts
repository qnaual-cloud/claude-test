import { NextResponse } from "next/server";
import {
  runResearchAnalysis,
  AnalysisNotConfiguredError,
  AnalysisFailedError,
} from "@/server/anthropicClient";
import { logAnalyticsEvent } from "@/lib/supabaseServer";
import { getAuthenticatedUser } from "@/lib/supabaseServerAuth";
import { consumeCredit, refundCredit, CreditsNotConfiguredError } from "@/lib/credits";

interface RequestBody {
  prompt?: string;
  categoryId?: string;
  outputFormatId?: string;
  sessionId?: string;
}

const MAX_PROMPT_LENGTH = 6000;

export async function POST(request: Request) {
  const user = await getAuthenticatedUser();
  if (!user) {
    return NextResponse.json(
      { error: "Please log in to run analysis." },
      { status: 401 }
    );
  }

  let body: RequestBody;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const { prompt, categoryId, outputFormatId, sessionId } = body;

  if (!prompt || !categoryId || !outputFormatId || !sessionId) {
    return NextResponse.json({ error: "Missing required fields." }, { status: 400 });
  }
  if (typeof prompt !== "string" || prompt.length > MAX_PROMPT_LENGTH) {
    return NextResponse.json({ error: "Invalid prompt." }, { status: 400 });
  }

  // Reserve the credit atomically BEFORE calling Claude — this is what
  // makes concurrent requests safe (two simultaneous clicks can't both
  // spend the same last credit) and guarantees a failed analysis never
  // gets to the point of spending one in the first place.
  let creditsRemaining: number;
  try {
    const result = await consumeCredit(user.id, { categoryId, outputFormatId });
    if (result === null) {
      return NextResponse.json(
        { error: "You're out of credits. Buy more to continue." },
        { status: 402 }
      );
    }
    creditsRemaining = result;
  } catch (err) {
    if (err instanceof CreditsNotConfiguredError) {
      return NextResponse.json({ error: err.message }, { status: 503 });
    }
    console.error("[run-analysis] consumeCredit unexpected error:", err);
    return NextResponse.json({ error: "Something went wrong. Please try again." }, { status: 500 });
  }

  try {
    const result = await runResearchAnalysis({ prompt, outputFormatId });

    logAnalyticsEvent({
      sessionId,
      categoryId,
      event: "analysis_run",
      metadata: {
        outputFormatId,
        resultType: result.resultType,
        inputTokens: result.usage.inputTokens,
        outputTokens: result.usage.outputTokens,
      },
    }).catch(() => {});

    return NextResponse.json({ ...result, creditsRemaining });
  } catch (err) {
    // The credit was reserved above but the analysis didn't succeed —
    // give it back. "A failed analysis does not use a credit."
    await refundCredit(user.id, { categoryId, outputFormatId });

    if (err instanceof AnalysisNotConfiguredError) {
      return NextResponse.json({ error: err.message }, { status: 503 });
    }
    if (err instanceof AnalysisFailedError) {
      return NextResponse.json({ error: err.message }, { status: 502 });
    }
    console.error("[run-analysis] unexpected error:", err);
    return NextResponse.json({ error: "Something went wrong. Please try again." }, { status: 500 });
  }
}
