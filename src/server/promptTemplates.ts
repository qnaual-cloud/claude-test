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
  /** Appended after SHARED_CONSTRAINTS for this category only — use for a stronger, category-specific requirement (e.g. "no invented figures") rather than editing the shared list. */
  extraConstraints?: string[];
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
      "research-dashboard":
        "Present the findings as a structured research dashboard: a one-line headline verdict, 3-6 key metrics with values, a short list of strengths, a short list of risks, the key sections of the analysis, and the key assumptions behind the analysis — organized for at-a-glance scanning rather than long-form prose.",
    },
    whyItWorksBase: [
      "Clear analyst role and objective",
      "Reader perspective shapes tone and depth",
      "Structured, specific research checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
      "Explicit sourcing, date, and verified-vs-estimate requirement for figures",
    ],
    extraConstraints: [
      "For key financial figures (e.g. revenue, margins, growth rates, valuation multiples), state the source and as-of date, and clearly label each one as a verified reported figure or an estimate — never invent a number.",
      "If current/live market data (e.g. a real-time price) is not available to you, say so explicitly rather than presenting a guess as current.",
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
      "research-dashboard":
        "Present the findings as a structured research dashboard: a one-line headline verdict on valuation, 3-6 key metrics with values (e.g. estimated intrinsic value, current price, margin of safety), a short list of strengths, a short list of risks, the key sections of the analysis, and the key assumptions behind the valuation — organized for at-a-glance scanning rather than long-form prose.",
    },
    whyItWorksBase: [
      "Clear valuation-analyst role and objective",
      "Explicit assumption and methodology requirements",
      "Structured, specific analysis checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
      "Explicit sourcing, date, and assumption-vs-fact distinction for valuation inputs",
    ],
    extraConstraints: [
      "For the current price and any financial inputs used in the valuation (revenue, margins, cash flow, etc.), state the source and as-of date — and clearly label the discount rate, growth rate, and terminal value as modeling assumptions, not verified facts.",
      "If the current market price is not available to you or may be outdated, say so explicitly rather than treating it as current.",
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
      "research-dashboard":
        "Present the findings as a structured research dashboard: a one-line headline verdict on which investment looks stronger and why, 3-6 key comparison metrics with values for each investment — prioritizing the metrics most relevant to the investment decision over even coverage of every investment — a short list of strengths, a short list of risks, the key sections of the comparison, and the key assumptions behind the comparison — organized for at-a-glance scanning rather than long-form prose.",
    },
    whyItWorksBase: [
      "Clear comparative-analyst role and objective",
      "Same criteria applied evenly across all investments",
      "Structured, specific comparison checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
      "Explicit sourcing, date, and verified-vs-estimate requirement across all compared investments",
    ],
    extraConstraints: [
      "For each investment's key figures, state the source and as-of date, and clearly label each figure as a verified reported number or an estimate — never invent a figure for any investment in the comparison.",
      "If data for one investment is unavailable, outdated, or not directly comparable (e.g. a different fiscal period), say so explicitly rather than filling the gap or treating the comparison as perfectly aligned.",
    ],
  },

  earnings: {
    role:
      "You are a markets analyst experienced in earnings interpretation and results analysis.",
    objective: (subject) => `Analyze recent earnings results for ${subject}.`,
    chipInstructions: {
      "latest-earnings":
        "Summarize the most recent earnings results against expectations, including key metrics that moved.",
      guidance: "Assess management's forward guidance and how it compares to prior guidance.",
      "analyst-reaction":
        "Summarize how analysts and the market reacted, including notable estimate or rating changes.",
      "earnings-quality":
        "Assess the quality of the reported earnings — one-off items, margin trends, and underlying run-rate performance.",
    },
    outputFormatInstructions: {
      summary: "Present the findings as a concise summary (roughly 200-300 words).",
      "full-report":
        "Present the findings as a full structured report with clear section headings.",
      "research-dashboard":
        "Present the findings as a structured research dashboard: a one-line headline verdict on the results, 3-6 key metrics with values, a short list of strengths, a short list of risks, the key sections of the analysis, and the key assumptions behind the analysis — organized for at-a-glance scanning rather than long-form prose.",
    },
    whyItWorksBase: [
      "Clear markets-analyst role and objective",
      "Structured, specific analysis checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
      "Explicit sourcing, date, and reported-vs-estimate distinction for results and guidance",
    ],
    extraConstraints: [
      "For reported results and guidance, state the source and as-of date (e.g. the specific quarter and release), and clearly distinguish GAAP from non-GAAP figures and actual results from analyst or consensus estimates.",
      "If a figure such as a consensus estimate or guidance detail isn't available or verifiable, say so explicitly rather than estimating it.",
    ],
  },

  "market-analysis": {
    role:
      "You are a markets analyst experienced in sector and macro market analysis.",
    objective: (subject) => `Analyze current market conditions and context for ${subject}.`,
    chipInstructions: {
      "sector-trends":
        "Place current conditions in the context of broader sector trends.",
      "macro-factors":
        "Identify macro factors (rates, currency, demand environment, etc.) relevant to this market.",
      "valuation-levels":
        "Assess current valuation levels relative to historical norms and relevant benchmarks.",
      "market-sentiment":
        "Assess investor sentiment and positioning, including any signs of excess optimism or pessimism.",
    },
    outputFormatInstructions: {
      summary: "Present the findings as a concise summary (roughly 200-300 words).",
      "full-report":
        "Present the findings as a full structured report with clear section headings.",
      "research-dashboard":
        "Present the findings as a structured research dashboard: a one-line headline verdict, 3-6 key metrics with values, a short list of strengths, a short list of risks, the key sections of the analysis, and the key assumptions behind the analysis — organized for at-a-glance scanning rather than long-form prose.",
    },
    whyItWorksBase: [
      "Clear markets-analyst role and objective",
      "Structured, specific analysis checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
      "Explicit sourcing, date, and data-vs-interpretation distinction",
    ],
    extraConstraints: [
      "For market, sector, and valuation data, state the source and as-of date, and explicitly flag when market conditions may have moved since that data was current.",
      "Distinguish objective data (e.g. valuation multiples, flows) from subjective judgment (e.g. sentiment, positioning), and label sentiment assessments as interpretation, not verified fact.",
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
      "research-dashboard":
        "Present the findings as a structured research dashboard: a one-line headline verdict on portfolio health, 3-6 key metrics with values — prioritizing the holdings and risks most relevant to the stated review goal over even coverage of every holding — a short list of strengths, a short list of risks, the key sections of the review, and the key assumptions behind the review — organized for at-a-glance scanning rather than long-form prose.",
    },
    whyItWorksBase: [
      "Clear portfolio-analyst role and objective",
      "Review goal shapes what's prioritized",
      "Structured, specific review checklist",
      "Explicit output format",
      "Verification and assumption-transparency instructions",
      "Explicit sourcing/date and estimate-labeling for portfolio figures",
    ],
    extraConstraints: [
      "Use the holdings and weights the user provided rather than assuming different ones, and state the as-of date for each holding's price or value, flagging explicitly if live pricing data isn't available.",
      "Label diversification, correlation, and rebalancing figures as estimates based on available data, not precise guarantees.",
    ],
  },

  "stock-screener": {
    role: "You are an equity research analyst building a stock screen from verifiable public data.",
    objective: (subject) => `Build a stock screen for: ${subject}.`,
    roleContext: {
      "value-investing":
        "Prioritize companies that appear undervalued relative to their fundamentals.",
      growth: "Prioritize companies with strong, sustainable growth.",
      "dividend-income": "Prioritize companies offering durable income through dividends.",
      quality:
        "Prioritize companies with high-quality fundamentals — strong margins, low debt, consistent returns.",
      momentum: "Prioritize companies showing strong recent price and earnings momentum.",
    },
    chipInstructions: {
      "valuation-metrics":
        "Screen on valuation metrics such as P/E, P/B, and EV/EBITDA relative to peers or historical norms.",
      "growth-metrics": "Screen on revenue and earnings growth metrics.",
      "dividend-metrics": "Screen on dividend yield and payout ratio.",
      "balance-sheet-strength":
        "Screen on balance-sheet strength — debt levels, interest coverage, and liquidity.",
      profitability: "Screen on profitability margins (gross, operating, net).",
      "market-cap-liquidity": "Screen on market capitalization and trading liquidity.",
    },
    outputFormatInstructions: {
      summary: "Present the findings as a concise summary (roughly 200-300 words).",
      "shortlist-table":
        "Present the result as a shortlist table of candidate companies with the key screening metrics as columns, followed by a brief written takeaway.",
      "full-report":
        "Present the findings as a full structured report with clear section headings.",
      "research-dashboard":
        "Present the findings as a structured research dashboard: a one-line headline verdict, 3-6 key metrics with values, a short list of strengths, a short list of risks, the key sections of the screen, and the key assumptions behind the screen — organized for at-a-glance scanning rather than long-form prose.",
    },
    whyItWorksBase: [
      "Clear analyst role and objective",
      "Screening approach shapes which companies surface",
      "Structured, specific screening criteria",
      "Explicit output format",
      "Explicit no-invented-figures, sourcing, and date requirement",
    ],
    extraConstraints: [
      "Only include companies, tickers, and figures that are genuinely verifiable — never invent a name, ticker, or financial figure. If a precise current figure isn't available, say so explicitly rather than estimating or guessing at a number.",
      "State the source, approximate as-of date, and basis for each company's inclusion in the shortlist (e.g. the metric and approximate value that qualified it), and label any approximate or estimated figure as such.",
    ],
  },

  "investment-briefing": {
    role: "You are an investment professional preparing a meeting-ready brief for an investment audience.",
    objective: (subject) => `Prepare an investment brief on: ${subject}.`,
    roleContext: {
      "client-meeting-brief":
        "This brief is for a client meeting — keep it clear, jargon-light, and focused on what matters to the client's decision.",
      "investment-committee-brief":
        "This brief is for an investment committee — be rigorous, cite evidence for each claim, and surface the key debate points the committee will need to weigh.",
      "executive-summary":
        "This is an executive summary — lead with the conclusion and recommendation, keeping supporting detail brief.",
    },
    chipInstructions: {
      "investment-thesis": "State the core investment thesis clearly.",
      "key-risks": "Identify the key risks to the thesis.",
      "valuation-snapshot": "Include a brief valuation snapshot.",
      "recent-developments": "Summarize recent developments relevant to the brief.",
      "competitive-context": "Provide brief competitive context.",
      recommendation: "Include a clear recommendation or talking points for discussion.",
    },
    outputFormatInstructions: {
      "one-pager":
        "Present the brief as a single page — tight and scannable, limited to the essential points.",
      "full-brief":
        "Present the brief as a full briefing document with clear section headings.",
      "talking-points":
        "Present the brief as 5-7 concise, meeting-ready talking points — each a short, speakable line, not a paragraph. Cover: what changed, why it matters, opportunities, risks, and questions for the committee to consider.",
      "research-dashboard":
        "Present the brief as a structured research dashboard: a one-line headline verdict, 3-6 key points with values, a short list of strengths, a short list of risks, the key sections of the brief, and the key assumptions behind the brief — organized for at-a-glance scanning rather than long-form prose.",
    },
    whyItWorksBase: [
      "Clear professional role and objective",
      "Brief type shapes tone and depth for the intended audience",
      "Structured, specific content checklist",
      "Explicit output format",
      "Explicit sourcing, date, and estimate-labeling requirement — no invented data",
    ],
    extraConstraints: [
      "Base every claim on verifiable, sourced information, cite the source and approximate as-of date for each key fact or figure, and clearly label any estimate or forward-looking judgment as such. Do not invent data, quotes, or figures.",
      "If information needed for a complete brief isn't available or verifiable, state that explicitly rather than filling the gap with an unlabeled assumption.",
    ],
  },
};

export { SHARED_CONSTRAINTS, SHARED_FOLLOW_UP };
