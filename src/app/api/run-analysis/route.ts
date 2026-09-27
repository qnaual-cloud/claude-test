import { NextResponse } from "next/server";
import {
  runResearchAnalysis,
  AnalysisNotConfiguredError,
  AnalysisFailedError,
} from "@/server/anthropicClient";
import { logAnalyticsEvent } from "@/lib/supabaseServer";

interface RequestBody {
  prompt?: string;
  categoryId?: string;
  outputFormatId?: string;
  sessionId?: string;
}

const MAX_PROMPT_LENGTH = 6000;

export async function POST(request: Request) {
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

    return NextResponse.json(result);
  } catch (err) {
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
