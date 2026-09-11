"use client";

import { useVoiceInput } from "@/lib/useVoiceInput";

interface VoiceTextFieldProps {
  id: string;
  label: string;
  value: string;
  placeholder?: string;
  onChange: (value: string) => void;
  onVoiceUsed?: () => void;
}

export function VoiceTextField({
  id,
  label,
  value,
  placeholder,
  onChange,
  onVoiceUsed,
}: VoiceTextFieldProps) {
  const { supported, listening, start, stop } = useVoiceInput((transcript) => {
    onChange(value ? `${value} ${transcript}` : transcript);
    onVoiceUsed?.();
  });

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor={id} className="text-sm font-medium text-foreground">
        {label}
      </label>
      <div className="flex items-center gap-2">
        <input
          id={id}
          type="text"
          value={value}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          className="min-h-11 w-full rounded-lg border border-border bg-card px-3 py-2 text-base text-foreground outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
        {supported && (
          <button
            type="button"
            onClick={listening ? stop : start}
            aria-pressed={listening}
            aria-label={listening ? "Stop voice input" : "Start voice input"}
            className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border transition-colors ${
              listening
                ? "border-accent bg-accent text-accent-foreground"
                : "border-border bg-card text-muted-foreground hover:border-accent hover:text-accent"
            }`}
          >
            <MicIcon />
          </button>
        )}
      </div>
      {supported && listening && (
        <p className="text-xs text-muted-foreground">Listening…</p>
      )}
    </div>
  );
}

function MicIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M12 15a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <path
        d="M19 11a7 7 0 0 1-14 0M12 18v3"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}
