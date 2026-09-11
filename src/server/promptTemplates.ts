/**
 * SERVER-ONLY. Do not import this file from any "use client" component or
 * from /src/content/*. Only /src/server/promptEngine.ts and API routes
 * under /src/app/api/** may import it.
 *
 * This is the actual prompt-engineering library: the wording, structure,
 * and analytical framing that make a generated prompt good. It is the
 * product's protected IP, so it must never reach the browser bundle.
 *
 * To change how a category's prompts read, edit the strings below and
 * redeploy — no other code needs to change.
 */

export interface CategoryTemplate {
  role: string;
  objective: (subject: string) => string;
  roleContext?: Record<string, string>;
  chipInstructions: Record<string, string>;
  outputFormatInstructions: Record<string, string>;
  whyItWorksBase: string[];
}

const SHARED_CONSTRAINTS = [
  "Use the most recent publicly available information you have access to.",
  "If you are not certain of a figure or fact, say so explicitly rather than guessing.",
  "State the key assumptions your analysis relies on.",
  "This analysis is for research and educational purposes only and is not financial advice.",
];

const SHARED_FOLLOW_UP =
  "If you need clarifying information to complete this analysis well, ask for it before proceeding.";

export const categoryTemplates: Record<string, CategoryTemplate> = {
  "company-research": {
    role:
      "You are an experienced equity research analyst producing objective, well-sourced company research.",
    objective: (subject) => `Produce investment research on ${subject}.`,
    roleContext: {
      "long-term-investor":
        "The reader is a long-term investor evaluating this as a multi-year holding — weigh durability and long-term trajectory over short-term noise.",
      "quick-due-diligence":
        "The reader needs a fast, high-signal due-diligence pass — prioritize the points that would most change an investment decision.",
      learning:
        "The reader is learning how to evaluate companies — briefly explain why each point matters, not just what the data says.",
    },
    chipInstructions: {
      "business-overview":
        "Explain what the company does, how it makes money, and its position in its industry.",
      financials:
        "Assess revenue growth, margins, cash flow, and balance-sheet health over the recent reporting periods.",
      growth: "Evaluate the company's growth drivers and their sustainability.",
      "competitive-position":
        "Assess the company's competitive position, moat, and key competitors.",
      risks:
        "Identify the most material risks to the business and the investment thesis.",
      "recent-news":
        "Summarize recent news, catalysts, or events likely to affect the company going forward.",
    },
    outputFormatInstructions: {
      summary: "Present the findings as a concise summary (roughly 200-300 words).",
      "full-report":
        "Present the findings as a full structured report with clear section headings.",
      memo: "Present the findings as an investment memo suitable for sharing with another investor.",
    },
    whyItWorksBase: [
      "Clear analyst role and objective",
      "Reader perspective shapes tone and depth",
      "Structured, specific research checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
    ],
  },

  "valuation-dcf": {
    role:
      "You are a valuation analyst experienced in discounted cash flow and comparable-company analysis.",
    objective: (subject) =>
      `Estimate the intrinsic value of ${subject} and assess whether the current price offers a margin of safety.`,
    chipInstructions: {
      "dcf-intrinsic-value":
        "Build a discounted cash flow estimate, stating the discount rate, growth rate, and terminal value assumptions used.",
      "comparable-companies":
        "Compare valuation multiples (e.g. P/E, EV/EBITDA) against relevant peers.",
      "growth-assumptions":
        "State and justify the revenue and margin growth assumptions driving the valuation.",
      "margin-of-safety":
        "Compare the estimated intrinsic value to the current market price and state the resulting margin of safety.",
      "sensitivity-scenarios":
        "Show how the valuation changes under bull, base, and bear scenarios or key-assumption sensitivity.",
    },
    outputFormatInstructions: {
      summary: "Present the findings as a concise summary (roughly 200-300 words).",
      "full-report":
        "Present the findings as a full structured report with clear section headings.",
      "step-by-step":
        "Walk through the valuation step by step, showing the calculation logic at each stage, not just the final numbers.",
    },
    whyItWorksBase: [
      "Clear valuation-analyst role and objective",
      "Explicit assumption and methodology requirements",
      "Structured, specific analysis checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
    ],
  },

  "compare-investments": {
    role:
      "You are an investment analyst experienced in comparative equity analysis.",
    objective: (subject) =>
      `Compare the following investments and identify how they differ in ways relevant to an investment decision: ${subject}.`,
    chipInstructions: {
      valuation: "Compare valuation levels and whether each looks expensive or cheap relative to the others.",
      growth: "Compare growth rates and growth durability across the investments.",
      risk: "Compare the key risks facing each investment.",
      "financial-health":
        "Compare balance-sheet strength, profitability, and cash flow across the investments.",
      "competitive-moat":
        "Compare competitive positioning and moat strength across the investments.",
    },
    outputFormatInstructions: {
      "comparison-table":
        "Present the comparison as a table, with the investments as columns and the comparison points as rows, followed by a brief written takeaway.",
      "full-report":
        "Present the findings as a full structured report with clear section headings.",
      memo: "Present the findings as an investment memo suitable for sharing with another investor.",
    },
    whyItWorksBase: [
      "Clear comparative-analyst role and objective",
      "Same criteria applied evenly across all investments",
      "Structured, specific comparison checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
    ],
  },

  "earnings-market-analysis": {
    role:
      "You are a markets analyst experienced in earnings interpretation and sector/macro context.",
    objective: (subject) => `Analyze recent earnings and market context for ${subject}.`,
    chipInstructions: {
      "latest-earnings":
        "Summarize the most recent earnings results against expectations, including key metrics that moved.",
      guidance: "Assess management's forward guidance and how it compares to prior guidance.",
      "analyst-reaction":
        "Summarize how analysts and the market reacted, including notable estimate or rating changes.",
      "sector-trends":
        "Place the results in the context of broader sector trends.",
      "macro-factors":
        "Identify macro factors (rates, currency, demand environment, etc.) relevant to the results.",
    },
    outputFormatInstructions: {
      summary: "Present the findings as a concise summary (roughly 200-300 words).",
      "full-report":
        "Present the findings as a full structured report with clear section headings.",
    },
    whyItWorksBase: [
      "Clear markets-analyst role and objective",
      "Structured, specific analysis checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
    ],
  },

  "portfolio-research": {
    role:
      "You are a portfolio analyst experienced in risk, diversification, and allocation review.",
    objective: (subject) => `Review the following portfolio holdings: ${subject}.`,
    roleContext: {
      "risk-review":
        "The primary goal is a risk review — focus on what could go wrong and how concentrated that risk is.",
      "rebalancing-check":
        "The primary goal is a rebalancing check — focus on drift from target allocation and what trades would restore it.",
      "diversification-check":
        "The primary goal is a diversification check — focus on overlap, correlation, and concentration across holdings.",
    },
    chipInstructions: {
      diversification:
        "Assess how diversified the portfolio is across sectors, geographies, and asset types.",
      "risk-concentration":
        "Identify concentration risk — any single holding, sector, or theme that dominates the portfolio.",
      "sector-allocation":
        "Break down the portfolio's allocation by sector and compare it to a reasonable benchmark.",
      rebalancing:
        "Suggest what rebalancing, if any, would bring the portfolio closer to a well-balanced allocation.",
      correlation:
        "Assess how correlated the holdings are likely to be, particularly during a market downturn.",
    },
    outputFormatInstructions: {
      summary: "Present the findings as a concise summary (roughly 200-300 words).",
      "full-report":
        "Present the findings as a full structured report with clear section headings.",
      "action-checklist":
        "Present the findings as a short, prioritized checklist of concrete actions to consider.",
    },
    whyItWorksBase: [
      "Clear portfolio-analyst role and objective",
      "Review goal shapes what's prioritized",
      "Structured, specific review checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
    ],
  },
};

export { SHARED_CONSTRAINTS, SHARED_FOLLOW_UP };
