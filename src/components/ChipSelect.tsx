"use client";

import type { OptionConfig } from "@/content/categories";

interface ChipSelectProps {
  options: OptionConfig[];
  selected: string[];
  maxSelect: number;
  onChange: (selected: string[]) => void;
}

export function ChipSelect({ options, selected, maxSelect, onChange }: ChipSelectProps) {
  function toggle(id: string) {
    if (selected.includes(id)) {
      onChange(selected.filter((s) => s !== id));
      return;
    }
    if (selected.length >= maxSelect) return;
    onChange([...selected, id]);
  }

  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => {
        const isSelected = selected.includes(option.id);
        const disabled = !isSelected && selected.length >= maxSelect;
        return (
          <button
            key={option.id}
            type="button"
            onClick={() => toggle(option.id)}
            disabled={disabled}
            aria-pressed={isSelected}
            className={`min-h-11 rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
              isSelected
                ? "border-accent bg-accent text-accent-foreground"
                : disabled
                  ? "border-border bg-muted text-muted-foreground opacity-50"
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
