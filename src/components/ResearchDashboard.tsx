"use client";

import type { DashboardData } from "@/server/dashboardSchema";
import { useAnimatedValue } from "@/lib/useAnimatedValue";

const OUTLOOK_LABEL: Record<DashboardData["outlook"], string> = {
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
  mixed: "Mixed",
};

const OUTLOOK_COLOR: Record<DashboardData["outlook"], string> = {
  positive: "border-status-positive/40 bg-status-positive/10 text-status-positive",
  neutral: "border-status-neutral/40 bg-status-neutral/10 text-status-neutral",
  negative: "border-status-negative/40 bg-status-negative/10 text-status-negative",
  mixed: "border-accent/40 bg-accent/10 text-accent",
};

function MetricTile({
  label,
  value,
  detail,
  delayMs,
}: {
  label: string;
  value: string;
  detail?: string;
  delayMs: number;
}) {
  const animatedValue = useAnimatedValue(value);
  return (
    <div
      className="dashboard-fade-up rounded-lg border border-border bg-card p-4"
      style={{ animationDelay: `${delayMs}ms` }}
    >
      <p className="text-xs font-medium tracking-wide text-muted-foreground uppercase">{label}</p>
      <p className="mt-1.5 text-xl font-semibold tabular-nums text-foreground">{animatedValue}</p>
      {detail && <p className="mt-1 text-xs text-muted-foreground">{detail}</p>}
    </div>
  );
}

export function ResearchDashboard({ data }: { data: DashboardData }) {
  return (
    <div className="flex flex-col gap-5">
      <div className="dashboard-fade-up flex flex-wrap items-center gap-3">
        <span
          className={`rounded-full border px-3 py-1 text-xs font-semibold tracking-wide uppercase ${OUTLOOK_COLOR[data.outlook]}`}
        >
          {OUTLOOK_LABEL[data.outlook]}
        </span>
        <p className="text-base font-medium text-foreground">{data.headline}</p>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {data.keyMetrics.map((metric, i) => (
          <MetricTile
            key={metric.label}
            label={metric.label}
            value={metric.value}
            detail={metric.detail}
            delayMs={i * 60}
          />
        ))}
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div
          className="dashboard-fade-up rounded-lg border border-status-positive/30 bg-status-positive/5 p-4"
          style={{ animationDelay: "180ms" }}
        >
          <p className="text-xs font-semibold tracking-wide text-status-positive uppercase">
            Strengths
          </p>
          <ul className="mt-2 flex flex-col gap-1.5 text-sm text-foreground">
            {data.strengths.map((item, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-status-positive">+</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
        <div
          className="dashboard-fade-up rounded-lg border border-status-negative/30 bg-status-negative/5 p-4"
          style={{ animationDelay: "220ms" }}
        >
          <p className="text-xs font-semibold tracking-wide text-status-negative uppercase">Risks</p>
          <ul className="mt-2 flex flex-col gap-1.5 text-sm text-foreground">
            {data.risks.map((item, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-status-negative">–</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="flex flex-col gap-4">
        {data.sections.map((section, i) => (
          <div
            key={section.heading}
            className="dashboard-fade-up border-t border-border pt-4"
            style={{ animationDelay: `${260 + i * 40}ms` }}
          >
            <h4 className="text-sm font-semibold text-foreground">{section.heading}</h4>
            <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{section.body}</p>
          </div>
        ))}
      </div>

      <div
        className="dashboard-fade-up rounded-lg border border-border bg-muted p-4"
        style={{ animationDelay: "420ms" }}
      >
        <p className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
          Key assumptions
        </p>
        <ul className="mt-2 flex flex-col gap-1 text-xs text-muted-foreground">
          {data.assumptions.map((item, i) => (
            <li key={i}>• {item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
