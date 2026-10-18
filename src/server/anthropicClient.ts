/**
 * SERVER-ONLY. Runs a generated research prompt against the Claude API
 * for the "Run Analysis" feature. Imported only by
 * /src/app/api/run-analysis/route.ts.
 *
 * Every call here costs real money against whatever ANTHROPIC_API_KEY is
 * configured. There is no per-user rate limit in this app yet — anyone
 * with the URL can trigger calls. Model defaults to claude-sonnet-5 (a
 * deliberate cost/quality tradeoff, not the top-tier model) and is
 * overridable via ANTHROPIC_MODEL. effort is fixed at "medium" as a
 * further cost control for what is a synthesis/writing task, not a hard
 * reasoning problem — raise it in the two calls below if quality matters
 * more than cost for your use case.
 */

import Anthropic from "@anthropic-ai/sdk";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";
import { DashboardSchema, type DashboardData } from "./dashboardSchema";

const MODEL = process.env.ANTHROPIC_MODEL || "claude-sonnet-5";
const PROSE_MAX_TOKENS = 4096;
const DASHBOARD_MAX_TOKENS = 6144;

// Keep comfortably under the /api/run-analysis route's own `maxDuration`
// (300s, see route.ts) so a call that's genuinely stuck gets stopped by
// *our* code — which throws a handled error and still lets the route's
// catch block run refundCredit() — rather than by Vercel hard-killing the
// function at the platform timeout, which runs none of our code at all
// (the original cause of a credit never being refunded; see the stale
// reservation safety net in sql/schema.sql / reconcileStaleAnalysisRuns).
const ANALYSIS_TIMEOUT_MS = 270_000;

// On by default so research reflects current information, not just the
// model's training data. Adds metered cost per search on top of normal
// token cost — set ANTHROPIC_ENABLE_WEB_SEARCH=false to disable.
const WEB_SEARCH_ENABLED = process.env.ANTHROPIC_ENABLE_WEB_SEARCH !== "false";
const WEB_SEARCH_TOOLS: Anthropic.ToolUnion[] = [
  { type: "web_search_20260209", name: "web_search" },
];

export class AnalysisNotConfiguredError extends Error {}
export class AnalysisFailedError extends Error {}

let client: Anthropic | null = null;

function getClient(): Anthropic | null {
  if (!process.env.ANTHROPIC_API_KEY) return null;
  if (!client) client = new Anthropic();
  return client;
}

export interface RunAnalysisInput {
  prompt: string;
  outputFormatId: string;
}

export type RunAnalysisResult =
  | { resultType: "dashboard"; dashboard: DashboardData; usage: TokenUsage }
  | { resultType: "text"; text: string; usage: TokenUsage };

interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
}

function mapKnownError(err: unknown): never {
  if (err instanceof Anthropic.AuthenticationError) {
    throw new AnalysisNotConfiguredError(
      "The configured Anthropic API key was rejected. Check ANTHROPIC_API_KEY."
    );
  }
  if (err instanceof Anthropic.RateLimitError) {
    throw new AnalysisFailedError("Rate limited by the Anthropic API — please try again shortly.");
  }
  // Most-specific-first: APIConnectionTimeoutError extends
  // APIConnectionError extends APIError, so these must be checked before
  // the generic APIError branch below.
  if (err instanceof Anthropic.APIConnectionTimeoutError) {
    throw new AnalysisFailedError(
      "The analysis took longer than expected and was stopped automatically. Your credit has been refunded — please try again, or select fewer focus areas for a faster result."
    );
  }
  if (err instanceof Anthropic.APIConnectionError) {
    throw new AnalysisFailedError(
      "Couldn't reach the analysis service. Your credit has been refunded — please try again."
    );
  }
  if (err instanceof Anthropic.APIError) {
    throw new AnalysisFailedError(`Analysis failed: ${err.message}`);
  }
  throw err;
}

export async function runResearchAnalysis(input: RunAnalysisInput): Promise<RunAnalysisResult> {
  const anthropic = getClient();
  if (!anthropic) {
    throw new AnalysisNotConfiguredError(
      "Run Analysis isn't configured yet — add ANTHROPIC_API_KEY to enable it."
    );
  }

  if (input.outputFormatId === "research-dashboard") {
    try {
      // Streaming (rather than messages.parse()) so a long-running
      // dashboard request — web search plus a large structured response —
      // doesn't sit as one unbroken wait that risks the platform's own
      // timeout. output_config.format still gets automatically parsed and
      // validated into parsed_output on the final message, exactly like
      // messages.parse() — see the SDK's own messages.stream() docstring.
      const response = await anthropic.messages
        .stream(
          {
            model: MODEL,
            max_tokens: DASHBOARD_MAX_TOKENS,
            output_config: {
              format: zodOutputFormat(DashboardSchema),
              effort: "medium",
            },
            tools: WEB_SEARCH_ENABLED ? WEB_SEARCH_TOOLS : undefined,
            messages: [{ role: "user", content: input.prompt }],
          },
          { timeout: ANALYSIS_TIMEOUT_MS }
        )
        .finalMessage();

      // Diagnostic only — stop_reason and token counts, never prompt text
      // or the parsed research content, so nothing user- or company-
      // specific reaches the logs.
      console.log(
        `[run-analysis] dashboard response stop_reason=${response.stop_reason} inputTokens=${response.usage.input_tokens} outputTokens=${response.usage.output_tokens}`
      );

      if (!response.parsed_output) {
        throw new AnalysisFailedError(
          "The analysis didn't come back in the expected format. Please try again."
        );
      }

      return {
        resultType: "dashboard",
        dashboard: response.parsed_output,
        usage: {
          inputTokens: response.usage.input_tokens,
          outputTokens: response.usage.output_tokens,
        },
      };
    } catch (err) {
      if (err instanceof AnalysisFailedError || err instanceof AnalysisNotConfiguredError) throw err;
      mapKnownError(err);
    }
  }

  try {
    // Streaming (rather than messages.create()) for the same reason as
    // the dashboard path above — avoid one unbroken multi-minute wait.
    const response = await anthropic.messages
      .stream(
        {
          model: MODEL,
          max_tokens: PROSE_MAX_TOKENS,
          output_config: { effort: "medium" },
          tools: WEB_SEARCH_ENABLED ? WEB_SEARCH_TOOLS : undefined,
          messages: [{ role: "user", content: input.prompt }],
        },
        { timeout: ANALYSIS_TIMEOUT_MS }
      )
      .finalMessage();

    // Diagnostic only — stop_reason and token counts, never prompt text or
    // the generated research content, so nothing user- or company-specific
    // reaches the logs.
    console.log(
      `[run-analysis] text response stop_reason=${response.stop_reason} inputTokens=${response.usage.input_tokens} outputTokens=${response.usage.output_tokens}`
    );

    // With web search enabled, content can include multiple text blocks
    // interleaved with search-tool blocks (e.g. text before a search,
    // more text after) — join all of them in order rather than taking
    // just one, so nothing the model wrote gets silently dropped.
    const text = response.content
      .filter((block) => block.type === "text")
      .map((block) => block.text)
      .join("\n\n")
      .trim();

    if (!text) {
      throw new AnalysisFailedError("The analysis came back empty. Please try again.");
    }

    return {
      resultType: "text",
      text,
      usage: {
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens,
      },
    };
  } catch (err) {
    if (err instanceof AnalysisFailedError || err instanceof AnalysisNotConfiguredError) throw err;
    mapKnownError(err);
  }
}
