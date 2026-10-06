"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { CategoryConfig, EntityItem, OptionConfig } from "@/content/categories";
import { siteConfig } from "@/content/site.config";
import { VoiceTextField } from "@/components/VoiceTextField";
import { RepeatableEntityList } from "@/components/RepeatableEntityList";
import { ChipSelect } from "@/components/ChipSelect";
import { ProgressSteps } from "@/components/ProgressSteps";
import { FeedbackWidget } from "@/components/FeedbackWidget";
import { MarkdownLite } from "@/components/MarkdownLite";
import { ResearchDashboard } from "@/components/ResearchDashboard";
import { OutOfCreditsNotice } from "@/components/OutOfCreditsNotice";
import { AuthRequiredNotice } from "@/components/AuthRequiredNotice";
import type { DashboardData } from "@/server/dashboardSchema";
import { notifyCreditsChanged, onCreditsChanged } from "@/lib/creditsEvents";
import { getSupabaseBrowserClient } from "@/lib/supabaseBrowser";
import {
  savePendingResearch,
  loadPendingResearch,
  clearPendingResearch,
  type PendingResearchAnswers,
} from "@/lib/pendingResearch";

type StepKind = "entity" | "role" | "chips" | "format";
type Phase = "form" | "loading" | "review" | "error" | "auth-required";
type AnalysisPhase = "idle" | "running" | "done" | "error";
type AuthState =
  | { status: "loading" }
  | { status: "signed-out" }
  | { status: "signed-in"; creditsBalance: number | null };

interface GenerateResult {
  prompt: string;
  whyItWorks: string[];
}

type AnalysisResult =
  | { resultType: "dashboard"; dashboard: DashboardData }
  | { resultType: "text"; text: string };

function createSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function SingleSelect({
  options,
  value,
  onChange,
}: {
  options: OptionConfig[];
  value: string | undefined;
  onChange: (id: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => {
        const isSelected = value === option.id;
        return (
          <button
            key={option.id}
            type="button"
            onClick={() => onChange(option.id)}
            aria-pressed={isSelected}
            className={`min-h-11 rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
              isSelected
                ? "border-accent bg-accent text-accent-foreground"
                : "border-border bg-card text-foreground hover:border-accent hover:text-accent"
            }`}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}

export function ResearchWizard({ category }: { category: CategoryConfig }) {
  const steps = useMemo<StepKind[]>(() => {
    const s: StepKind[] = ["entity"];
    if (category.roleStep) s.push("role");
    s.push("chips", "format");
    return s;
  }, [category]);

  const returnTo = `/research/${category.id}`;

  const [sessionId] = useState(createSessionId);
  const [stepIndex, setStepIndex] = useState(0);
  const [phase, setPhase] = useState<Phase>("form");
  const [errorMessage, setErrorMessage] = useState("");
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [showWhyItWorks, setShowWhyItWorks] = useState(false);
  const [usedVoice, setUsedVoice] = useState(false);
  const [analysisPhase, setAnalysisPhase] = useState<AnalysisPhase>("idle");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [analysisError, setAnalysisError] = useState("");
  const [analysisErrorStatus, setAnalysisErrorStatus] = useState<number | null>(null);
  const [auth, setAuth] = useState<AuthState>({ status: "loading" });

  const [entitySingle, setEntitySingle] = useState("");
  const [entityItems, setEntityItems] = useState<EntityItem[]>(() => {
    if (category.entity.kind !== "repeatable") return [];
    return Array.from({ length: category.entity.minItems }, () => ({ name: "", weight: "" }));
  });
  const [roleId, setRoleId] = useState<string | undefined>(undefined);
  const [chipIds, setChipIds] = useState<string[]>([]);
  const [outputFormatId, setOutputFormatId] = useState<string | undefined>(undefined);

  const currentStep = steps[stepIndex];

  // Track signed-in state + live credit balance — needed both to gate
  // Run Analysis and to decide, once known, whether a saved pending
  // request (see below) should auto-continue.
  useEffect(() => {
    function refresh() {
      fetch("/api/account/me")
        .then((res) => res.json())
        .then((data) => {
          if (!data.signedIn) setAuth({ status: "signed-out" });
          else setAuth({ status: "signed-in", creditsBalance: data.profile?.creditsBalance ?? null });
        })
        .catch(() => setAuth({ status: "signed-out" }));
    }
    refresh();
    const unsubscribeCredits = onCreditsChanged(refresh);
    const supabase = getSupabaseBrowserClient();
    if (!supabase) return unsubscribeCredits;
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => refresh());
    return () => {
      unsubscribeCredits();
      subscription.unsubscribe();
    };
  }, []);

  // Restores selections saved before a login/register redirect (see
  // submitAnswers' 401 handling below). Only once auth state is known:
  // if now signed in, pick up exactly where the user left off and
  // regenerate automatically — "return to the exact same place" means
  // completing the action they already asked for, not making them
  // press Generate again. If still signed out (e.g. they navigated back
  // without finishing login), restore the selections but leave the
  // saved entry in place for next time.
  useEffect(() => {
    if (auth.status === "loading") return;
    const pending = loadPendingResearch(category.id);
    if (!pending) return;

    // Reading saved state from sessionStorage after mount — this can't
    // happen during render (no window on the server) and isn't a lazy
    // useState initializer candidate since it also depends on auth.status.
    /* eslint-disable react-hooks/set-state-in-effect */
    if (category.entity.kind === "single") {
      setEntitySingle(pending.entitySingle);
    } else if (pending.entityItems.length > 0) {
      setEntityItems(pending.entityItems);
    }
    setRoleId(pending.roleId);
    setChipIds(pending.chipIds);
    setOutputFormatId(pending.outputFormatId);
    setStepIndex(steps.length - 1);
    /* eslint-enable react-hooks/set-state-in-effect */

    if (auth.status === "signed-in") {
      clearPendingResearch(category.id);
      submitAnswers(pending);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auth.status, category.id]);

  const canAdvance = (() => {
    if (currentStep === "entity") {
      if (category.entity.kind === "single") return entitySingle.trim().length > 0;
      return (
        entityItems.length >= category.entity.minItems &&
        entityItems.every((item) => item.name.trim().length > 0)
      );
    }
    if (currentStep === "role") return Boolean(roleId);
    if (currentStep === "chips") {
      return (
        chipIds.length >= category.focusChips.minSelect &&
        chipIds.length <= category.focusChips.maxSelect
      );
    }
    if (currentStep === "format") return Boolean(outputFormatId);
    return false;
  })();

  function goBack() {
    if (stepIndex === 0) return;
    setStepIndex(stepIndex - 1);
  }

  // Deliberately not `async` — called directly from an effect above,
  // and an async function invoked there trips the same "setState in
  // effect" lint concern as a bare setState call. Kept as a plain
  // function that kicks off a promise chain instead.
  function submitAnswers(answers: PendingResearchAnswers) {
    setPhase("loading");
    setErrorMessage("");
    fetch("/api/generate-prompt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        categoryId: category.id,
        entity: category.entity.kind === "single" ? answers.entitySingle : answers.entityItems,
        roleId: answers.roleId,
        chipIds: answers.chipIds,
        outputFormatId: answers.outputFormatId,
        sessionId,
        usedVoice,
      }),
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          if (res.status === 401) {
            savePendingResearch(category.id, answers);
            setPhase("auth-required");
            return;
          }
          throw new Error(data.error || "Something went wrong.");
        }
        setResult(data);
        setPhase("review");
      })
      .catch((err) => {
        setErrorMessage(err instanceof Error ? err.message : "Something went wrong.");
        setPhase("error");
      });
  }

  function handleSubmit() {
    submitAnswers({ entitySingle, entityItems, roleId, chipIds, outputFormatId });
  }

  function goNext() {
    if (stepIndex < steps.length - 1) {
      setStepIndex(stepIndex + 1);
      return;
    }
    handleSubmit();
  }

  async function handleRunAnalysis() {
    if (!result || !outputFormatId) return;
    setAnalysisPhase("running");
    setAnalysisError("");
    setAnalysisErrorStatus(null);
    try {
      const res = await fetch("/api/run-analysis", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: result.prompt,
          categoryId: category.id,
          outputFormatId,
          sessionId,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setAnalysisError(data.error || "Something went wrong.");
        setAnalysisErrorStatus(res.status);
        setAnalysisPhase("error");
        return;
      }
      setAnalysisResult(data);
      setAnalysisPhase("done");
      // Update the balance immediately from the response rather than
      // waiting on the refetch notifyCreditsChanged() below triggers.
      setAuth((prev) =>
        prev.status === "signed-in" ? { ...prev, creditsBalance: data.creditsRemaining } : prev
      );
      notifyCreditsChanged();
    } catch {
      setAnalysisError("Something went wrong.");
      setAnalysisPhase("error");
    }
  }

  function handleStartOver() {
    clearPendingResearch(category.id);
    setPhase("form");
    setStepIndex(0);
    setResult(null);
    setShowWhyItWorks(false);
    setEntitySingle("");
    setEntityItems(
      category.entity.kind === "repeatable"
        ? Array.from({ length: category.entity.minItems }, () => ({ name: "", weight: "" }))
        : []
    );
    setRoleId(undefined);
    setChipIds([]);
    setOutputFormatId(undefined);
    setUsedVoice(false);
    setAnalysisPhase("idle");
    setAnalysisResult(null);
    setAnalysisError("");
  }

  const atZeroCredits = auth.status === "signed-in" && auth.creditsBalance === 0;

  if (phase === "review" && result) {
    return (
      <div className="flex flex-col gap-6">
        <Link href="/" className="text-sm text-muted-foreground hover:text-accent">
          ← Back to categories
        </Link>
        <h1 className="text-2xl font-semibold text-foreground">{category.label}</h1>

        <div className="rounded-xl border border-border bg-card p-4">
          <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-foreground">
            {result.prompt}
          </pre>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-4">
            {auth.status === "signed-in" && (
              <span className="text-sm font-medium text-foreground">
                Credits: {auth.creditsBalance ?? "—"}
              </span>
            )}
            <button
              type="button"
              onClick={handleRunAnalysis}
              disabled={analysisPhase === "running" || atZeroCredits}
              className="min-h-11 rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground hover:bg-accent-hover disabled:opacity-50"
            >
              {analysisPhase === "running" ? "Analyzing…" : "Run Analysis — 1 Credit"}
            </button>
          </div>
          <div className="flex flex-wrap gap-4 text-sm">
            <Link href="/#buy-credits" className="font-medium text-accent hover:underline">
              Buy Credits
            </Link>
            <Link href="/#membership" className="font-medium text-accent hover:underline">
              Become a Member
            </Link>
          </div>
        </div>

        {atZeroCredits && analysisPhase !== "error" && <OutOfCreditsNotice />}

        {analysisPhase === "error" && analysisErrorStatus === 402 ? (
          <OutOfCreditsNotice />
        ) : (
          analysisPhase === "error" && (
            <p className="text-sm text-red-600">
              {analysisError}
              {analysisErrorStatus === 401 && (
                <>
                  {" "}
                  <Link href={`/login?returnTo=${encodeURIComponent(returnTo)}`} className="font-medium underline">
                    Log in
                  </Link>
                </>
              )}
            </p>
          )
        )}

        {analysisPhase === "done" && analysisResult && (
          <div className="rounded-xl border border-border bg-card p-5">
            <p className="mb-4 text-xs font-medium tracking-wide text-muted-foreground uppercase">
              Research Result
            </p>
            {analysisResult.resultType === "dashboard" ? (
              <ResearchDashboard data={analysisResult.dashboard} />
            ) : (
              <MarkdownLite text={analysisResult.text} />
            )}
          </div>
        )}

        <div>
          <button
            type="button"
            onClick={() => setShowWhyItWorks(!showWhyItWorks)}
            className="text-sm font-medium text-accent"
          >
            {showWhyItWorks ? "Hide" : siteConfig.whyItWorksLabel}
          </button>
          {showWhyItWorks && (
            <ul className="mt-2 flex flex-col gap-1 text-sm text-muted-foreground">
              {result.whyItWorks.map((line) => (
                <li key={line}>✓ {line}</li>
              ))}
            </ul>
          )}
        </div>

        <FeedbackWidget sessionId={sessionId} categoryId={category.id} />

        <button
          type="button"
          onClick={handleStartOver}
          className="self-start text-sm text-muted-foreground hover:text-accent"
        >
          Start a new request
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <Link href="/" className="text-sm text-muted-foreground hover:text-accent">
        ← Back to categories
      </Link>
      <div>
        <h1 className="text-2xl font-semibold text-foreground">{category.label}</h1>
        <p className="mt-1 text-sm text-muted-foreground">{category.description}</p>
      </div>

      <ProgressSteps current={stepIndex + 1} total={steps.length} />

      <div className="flex flex-col gap-4">
        {currentStep === "entity" && category.entity.kind === "single" && (
          <VoiceTextField
            id="entity"
            label={category.entity.label}
            value={entitySingle}
            placeholder={category.entity.placeholder}
            onChange={setEntitySingle}
            onVoiceUsed={() => setUsedVoice(true)}
          />
        )}

        {currentStep === "entity" && category.entity.kind === "repeatable" && (
          <div>
            <p className="mb-3 text-sm font-medium text-foreground">{category.entity.label}</p>
            <RepeatableEntityList
              itemLabel={category.entity.itemLabel}
              itemPlaceholder={category.entity.itemPlaceholder}
              hasWeight={category.entity.hasWeight}
              minItems={category.entity.minItems}
              maxItems={category.entity.maxItems}
              items={entityItems}
              onChange={setEntityItems}
              onVoiceUsed={() => setUsedVoice(true)}
            />
          </div>
        )}

        {currentStep === "role" && category.roleStep && (
          <div>
            <p className="mb-3 text-sm font-medium text-foreground">
              {category.roleStep.question}
            </p>
            <SingleSelect options={category.roleStep.options} value={roleId} onChange={setRoleId} />
          </div>
        )}

        {currentStep === "chips" && (
          <div>
            <p className="mb-3 text-sm font-medium text-foreground">
              {category.focusChips.question}
            </p>
            <ChipSelect
              options={category.focusChips.options}
              selected={chipIds}
              maxSelect={category.focusChips.maxSelect}
              onChange={setChipIds}
            />
          </div>
        )}

        {currentStep === "format" && (
          <div>
            <p className="mb-3 text-sm font-medium text-foreground">
              {category.outputFormats.question}
            </p>
            <SingleSelect
              options={category.outputFormats.options}
              value={outputFormatId}
              onChange={setOutputFormatId}
            />
          </div>
        )}
      </div>

      {phase === "error" && <p className="text-sm text-red-600">{errorMessage}</p>}
      {phase === "auth-required" && <AuthRequiredNotice returnTo={returnTo} />}

      <div className="flex items-center gap-3">
        {stepIndex > 0 && (
          <button
            type="button"
            onClick={goBack}
            className="min-h-11 rounded-lg border border-border px-5 py-2.5 text-sm font-medium text-foreground hover:border-accent"
          >
            Back
          </button>
        )}
        <button
          type="button"
          onClick={goNext}
          disabled={!canAdvance || phase === "loading"}
          className="min-h-11 rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground hover:bg-accent-hover disabled:opacity-50"
        >
          {phase === "loading"
            ? "Generating…"
            : stepIndex < steps.length - 1
              ? "Next"
              : "Generate Prompt"}
        </button>
      </div>
    </div>
  );
}
