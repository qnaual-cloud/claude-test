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
const DASHBOARD_MAX_TOKENS = 3072;

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
      const response = await anthropic.messages.parse({
        model: MODEL,
        max_tokens: DASHBOARD_MAX_TOKENS,
        output_config: {
          format: zodOutputFormat(DashboardSchema),
          effort: "medium",
        },
        tools: WEB_SEARCH_ENABLED ? WEB_SEARCH_TOOLS : undefined,
        messages: [{ role: "user", content: input.prompt }],
      });

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
    const response = await anthropic.messages.create({
      model: MODEL,
      max_tokens: PROSE_MAX_TOKENS,
      output_config: { effort: "medium" },
      tools: WEB_SEARCH_ENABLED ? WEB_SEARCH_TOOLS : undefined,
      messages: [{ role: "user", content: input.prompt }],
    });

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
