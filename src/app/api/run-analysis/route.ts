import { NextResponse } from "next/server";
import {
  runResearchAnalysis,
  AnalysisNotConfiguredError,
  AnalysisFailedError,
} from "@/server/anthropicClient";
import { logAnalyticsEvent } from "@/lib/supabaseServer";
import { getAuthenticatedUser } from "@/lib/supabaseServerAuth";
import {
  consumeCredit,
  refundCredit,
  completeAnalysisRun,
  reconcileStaleAnalysisRuns,
  CreditsNotConfiguredError,
} from "@/lib/credits";

interface RequestBody {
  prompt?: string;
  categoryId?: string;
  outputFormatId?: string;
  sessionId?: string;
}

const MAX_PROMPT_LENGTH = 6000;

// Vercel Hobby + Fluid Compute ceiling. Set to the plan's maximum because
// a Research Dashboard call (web search + a long structured response) can
// legitimately take several minutes. See ANALYSIS_TIMEOUT_MS in
// anthropicClient.ts — our own in-code timeout fires comfortably before
// this, so our catch block (and refundCredit below) gets to run instead
// of the platform hard-killing the function with no chance to clean up.
export const maxDuration = 300;

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

  // Opportunistic safety net: restore any credit left stuck "pending"
  // by a past run that was interrupted before it could refund itself
  // (e.g. a platform timeout), before this request spends a new one.
  await reconcileStaleAnalysisRuns(user.id);

  // Reserve the credit atomically BEFORE calling Claude — this is what
  // makes concurrent requests safe (two simultaneous clicks can't both
  // spend the same last credit) and guarantees a failed analysis never
  // gets to the point of spending one in the first place.
  let creditsRemaining: number;
  try {
    const result = await consumeCredit(user.id, { categoryId, outputFormatId });
    if (result === null) {
      return NextResponse.json(
        { error: "You're out of credits. Add more to continue." },
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

    // Close out the reservation immediately on success — before
    // anything else — so reconcileStaleAnalysisRuns never mistakes this
    // legitimately spent credit for one stuck mid-request.
    await completeAnalysisRun(user.id);

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
