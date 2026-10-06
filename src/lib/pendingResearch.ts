"use client";

import type { EntityItem } from "@/content/categories";

/**
 * Preserves a user's in-progress research selections across the
 * register/login redirect, so "Generate Prompt" while logged out can
 * require authentication without losing their work. sessionStorage
 * (not localStorage) — this is meant to survive one redirect-and-back
 * within the same tab, not persist indefinitely.
 */

export interface PendingResearchAnswers {
  entitySingle: string;
  entityItems: EntityItem[];
  roleId?: string;
  chipIds: string[];
  outputFormatId?: string;
}

function storageKey(categoryId: string): string {
  return `pendingResearch:${categoryId}`;
}

export function savePendingResearch(categoryId: string, answers: PendingResearchAnswers): void {
  try {
    sessionStorage.setItem(storageKey(categoryId), JSON.stringify(answers));
  } catch {
    // sessionStorage can throw (e.g. some private-browsing modes) —
    // losing the saved selections isn't critical, so just skip it.
  }
}

export function loadPendingResearch(categoryId: string): PendingResearchAnswers | null {
  try {
    const raw = sessionStorage.getItem(storageKey(categoryId));
    return raw ? (JSON.parse(raw) as PendingResearchAnswers) : null;
  } catch {
    return null;
  }
}

export function clearPendingResearch(categoryId: string): void {
  try {
    sessionStorage.removeItem(storageKey(categoryId));
  } catch {
    // ignore
  }
}
