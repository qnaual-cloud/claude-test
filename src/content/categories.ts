/**
 * Public form schema for the 5 research categories.
 *
 * IMPORTANT: This file is safe to import from client components. It only
 * describes what questions to render (labels, chip options, formats) —
 * it does NOT contain the actual prompt template wording or assembly
 * logic. That lives server-side only, in /src/server/promptTemplates.ts,
 * and is never shipped to the browser.
 *
 * To add/rename a category or change its questions, edit this file and
 * redeploy — no other code needs to change. Keep `id` values stable once
 * shipped, since the server-side templates are keyed by the same id.
 */

export type EntityFieldConfig =
  | {
      kind: "single";
      label: string;
      placeholder: string;
    }
  | {
      kind: "repeatable";
      label: string;
      itemLabel: string;
      itemPlaceholder: string;
      hasWeight?: boolean;
      minItems: number;
      maxItems: number;
    };

export interface OptionConfig {
  id: string;
  label: string;
}

/** A single entity in a repeatable field (e.g. one ticker in a comparison or one portfolio holding). */
export interface EntityItem {
  name: string;
  weight?: string;
}

export interface RoleStepConfig {
  question: string;
  options: OptionConfig[];
}

export interface ChipStepConfig {
  question: string;
  options: OptionConfig[];
  minSelect: number;
  maxSelect: number;
}

export interface OutputFormatStepConfig {
  question: string;
  options: OptionConfig[];
}

export interface CategoryConfig {
  id: string;
  label: string;
  description: string;
  entity: EntityFieldConfig;
  /** Optional — only shown for categories where it changes the output. */
  roleStep?: RoleStepConfig;
  focusChips: ChipStepConfig;
  outputFormats: OutputFormatStepConfig;
}

export const categories: CategoryConfig[] = [
  {
    id: "company-research",
    label: "Company Research",
    description: "Understand a company's business, financials, and risks.",
    entity: {
      kind: "single",
      label: "Company or ticker",
      placeholder: "e.g. NVIDIA or NVDA",
    },
    roleStep: {
      question: "What's your perspective?",
      options: [
        { id: "long-term-investor", label: "Long-term investor" },
        { id: "quick-due-diligence", label: "Quick due diligence" },
        { id: "learning", label: "Learning" },
      ],
    },
    focusChips: {
      question: "What should the research focus on?",
      minSelect: 1,
      maxSelect: 4,
      options: [
        { id: "business-overview", label: "Business overview" },
        { id: "financials", label: "Financials" },
        { id: "growth", label: "Growth" },
        { id: "competitive-position", label: "Competitive position" },
        { id: "risks", label: "Risks" },
        { id: "recent-news", label: "Recent news & catalysts" },
      ],
    },
    outputFormats: {
      question: "How should the result be formatted?",
      options: [
        { id: "summary", label: "Summary" },
        { id: "full-report", label: "Full report" },
        { id: "memo", label: "Memo" },
      ],
    },
  },
  {
    id: "valuation-dcf",
    label: "Valuation & DCF",
    description: "Estimate intrinsic value and stress-test assumptions.",
    entity: {
      kind: "single",
      label: "Company or ticker",
      placeholder: "e.g. Microsoft or MSFT",
    },
    focusChips: {
      question: "What should the valuation focus on?",
      minSelect: 1,
      maxSelect: 4,
      options: [
        { id: "dcf-intrinsic-value", label: "Intrinsic value / DCF" },
        { id: "comparable-companies", label: "Comparable companies" },
        { id: "growth-assumptions", label: "Growth assumptions" },
        { id: "margin-of-safety", label: "Margin of safety" },
        { id: "sensitivity-scenarios", label: "Sensitivity / scenarios" },
      ],
    },
    outputFormats: {
      question: "How should the result be formatted?",
      options: [
        { id: "summary", label: "Summary" },
        { id: "full-report", label: "Full report" },
        { id: "step-by-step", label: "Step-by-step walkthrough" },
      ],
    },
  },
  {
    id: "compare-investments",
    label: "Compare Investments",
    description: "Put two or more investments side by side.",
    entity: {
      kind: "repeatable",
      label: "Investments to compare",
      itemLabel: "Ticker",
      itemPlaceholder: "e.g. AAPL",
      minItems: 2,
      maxItems: 4,
    },
    focusChips: {
      question: "What should the comparison focus on?",
      minSelect: 1,
      maxSelect: 4,
      options: [
        { id: "valuation", label: "Valuation" },
        { id: "growth", label: "Growth" },
        { id: "risk", label: "Risk" },
        { id: "financial-health", label: "Financial health" },
        { id: "competitive-moat", label: "Competitive moat" },
      ],
    },
    outputFormats: {
      question: "How should the result be formatted?",
      options: [
        { id: "comparison-table", label: "Comparison table" },
        { id: "full-report", label: "Full report" },
        { id: "memo", label: "Memo" },
      ],
    },
  },
  {
    id: "earnings-market-analysis",
    label: "Earnings & Market Analysis",
    description: "Break down earnings results or broader market moves.",
    entity: {
      kind: "single",
      label: "Company, ticker, or sector/market",
      placeholder: "e.g. Tesla, TSLA, or semiconductor sector",
    },
    focusChips: {
      question: "What should the analysis focus on?",
      minSelect: 1,
      maxSelect: 4,
      options: [
        { id: "latest-earnings", label: "Latest earnings" },
        { id: "guidance", label: "Guidance" },
        { id: "analyst-reaction", label: "Analyst reaction" },
        { id: "sector-trends", label: "Sector trends" },
        { id: "macro-factors", label: "Macro factors" },
      ],
    },
    outputFormats: {
      question: "How should the result be formatted?",
      options: [
        { id: "summary", label: "Summary" },
        { id: "full-report", label: "Full report" },
      ],
    },
  },
  {
    id: "portfolio-research",
    label: "Portfolio Research",
    description: "Review your holdings for risk, balance, and fit.",
    entity: {
      kind: "repeatable",
      label: "Your holdings",
      itemLabel: "Holding",
      itemPlaceholder: "e.g. VTI",
      hasWeight: true,
      minItems: 1,
      maxItems: 15,
    },
    roleStep: {
      question: "What are you checking for?",
      options: [
        { id: "risk-review", label: "Risk review" },
        { id: "rebalancing-check", label: "Rebalancing check" },
        { id: "diversification-check", label: "Diversification check" },
      ],
    },
    focusChips: {
      question: "What should the review focus on?",
      minSelect: 1,
      maxSelect: 4,
      options: [
        { id: "diversification", label: "Diversification" },
        { id: "risk-concentration", label: "Risk concentration" },
        { id: "sector-allocation", label: "Sector allocation" },
        { id: "rebalancing", label: "Rebalancing" },
        { id: "correlation", label: "Correlation" },
      ],
    },
    outputFormats: {
      question: "How should the result be formatted?",
      options: [
        { id: "summary", label: "Summary" },
        { id: "full-report", label: "Full report" },
        { id: "action-checklist", label: "Action checklist" },
      ],
    },
  },
];

export function getCategoryById(id: string): CategoryConfig | undefined {
  return categories.find((c) => c.id === id);
}
