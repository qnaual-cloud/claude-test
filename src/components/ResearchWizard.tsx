"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { CategoryConfig, EntityItem, OptionConfig } from "@/content/categories";
import { siteConfig } from "@/content/site.config";
import { VoiceTextField } from "@/components/VoiceTextField";
import { RepeatableEntityList } from "@/components/RepeatableEntityList";
import { ChipSelect } from "@/components/ChipSelect";
import { ProgressSteps } from "@/components/ProgressSteps";
import { FeedbackWidget } from "@/components/FeedbackWidget";

type StepKind = "entity" | "role" | "chips" | "format";
type Phase = "form" | "loading" | "review" | "error";

interface GenerateResult {
  prompt: string;
  whyItWorks: string[];
}

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

  const [sessionId] = useState(createSessionId);
  const [stepIndex, setStepIndex] = useState(0);
  const [phase, setPhase] = useState<Phase>("form");
  const [errorMessage, setErrorMessage] = useState("");
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [showWhyItWorks, setShowWhyItWorks] = useState(false);
  const [copied, setCopied] = useState(false);
  const [usedVoice, setUsedVoice] = useState(false);

  const [entitySingle, setEntitySingle] = useState("");
  const [entityItems, setEntityItems] = useState<EntityItem[]>(() => {
    if (category.entity.kind !== "repeatable") return [];
    return Array.from({ length: category.entity.minItems }, () => ({ name: "", weight: "" }));
  });
  const [roleId, setRoleId] = useState<string | undefined>(undefined);
  const [chipIds, setChipIds] = useState<string[]>([]);
  const [outputFormatId, setOutputFormatId] = useState<string | undefined>(undefined);

  const currentStep = steps[stepIndex];

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

  async function handleSubmit() {
    setPhase("loading");
    setErrorMessage("");
    try {
      const res = await fetch("/api/generate-prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          categoryId: category.id,
          entity: category.entity.kind === "single" ? entitySingle : entityItems,
          roleId,
          chipIds,
          outputFormatId,
          sessionId,
          usedVoice,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong.");
      setResult(data);
      setPhase("review");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Something went wrong.");
      setPhase("error");
    }
  }

  function goNext() {
    if (stepIndex < steps.length - 1) {
      setStepIndex(stepIndex + 1);
      return;
    }
    handleSubmit();
  }

  async function handleCopy() {
    if (!result) return;
    await navigator.clipboard.writeText(result.prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleStartOver() {
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
  }

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

        <button
          type="button"
          onClick={handleCopy}
          className="min-h-11 self-start rounded-lg bg-accent px-5 py-2.5 text-sm font-medium text-accent-foreground hover:bg-accent-hover"
        >
          {copied ? "Copied!" : "Copy Prompt"}
        </button>

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
