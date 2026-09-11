"use client";

import { VoiceTextField } from "@/components/VoiceTextField";
import type { EntityItem } from "@/content/categories";

interface RepeatableEntityListProps {
  itemLabel: string;
  itemPlaceholder: string;
  hasWeight?: boolean;
  minItems: number;
  maxItems: number;
  items: EntityItem[];
  onChange: (items: EntityItem[]) => void;
  onVoiceUsed?: () => void;
}

export function RepeatableEntityList({
  itemLabel,
  itemPlaceholder,
  hasWeight,
  minItems,
  maxItems,
  items,
  onChange,
  onVoiceUsed,
}: RepeatableEntityListProps) {
  function updateItem(index: number, patch: Partial<EntityItem>) {
    onChange(items.map((item, i) => (i === index ? { ...item, ...patch } : item)));
  }

  function addItem() {
    if (items.length >= maxItems) return;
    onChange([...items, { name: "", weight: "" }]);
  }

  function removeItem(index: number) {
    if (items.length <= minItems) return;
    onChange(items.filter((_, i) => i !== index));
  }

  return (
    <div className="flex flex-col gap-4">
      {items.map((item, index) => (
        <div key={index} className="flex items-end gap-2">
          <div className="flex-1">
            <VoiceTextField
              id={`entity-${index}`}
              label={`${itemLabel} ${index + 1}`}
              value={item.name}
              placeholder={itemPlaceholder}
              onChange={(value) => updateItem(index, { name: value })}
              onVoiceUsed={onVoiceUsed}
            />
          </div>
          {hasWeight && (
            <div className="w-28">
              <label htmlFor={`weight-${index}`} className="text-sm font-medium text-foreground">
                Weight %
              </label>
              <input
                id={`weight-${index}`}
                type="text"
                value={item.weight ?? ""}
                placeholder="optional"
                onChange={(e) => updateItem(index, { weight: e.target.value })}
                className="mt-2 min-h-11 w-full rounded-lg border border-border bg-card px-3 py-2 text-base text-foreground outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
              />
            </div>
          )}
          {items.length > minItems && (
            <button
              type="button"
              onClick={() => removeItem(index)}
              aria-label={`Remove ${itemLabel.toLowerCase()} ${index + 1}`}
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border border-border bg-card text-muted-foreground hover:border-accent hover:text-accent"
            >
              ×
            </button>
          )}
        </div>
      ))}
      {items.length < maxItems && (
        <button
          type="button"
          onClick={addItem}
          className="self-start rounded-lg border border-dashed border-border px-4 py-2 text-sm font-medium text-accent hover:border-accent"
        >
          + Add {itemLabel.toLowerCase()}
        </button>
      )}
    </div>
  );
}
