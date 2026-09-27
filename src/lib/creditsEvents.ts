"use client";

/**
 * Tiny event bus so components that show credit balance (AccountHeader,
 * BuyCreditsSection) refresh after Run Analysis spends one, without
 * introducing a state-management library for a single number.
 */
const CREDITS_REFRESH_EVENT = "credits:refresh";

export function notifyCreditsChanged() {
  window.dispatchEvent(new Event(CREDITS_REFRESH_EVENT));
}

export function onCreditsChanged(callback: () => void): () => void {
  window.addEventListener(CREDITS_REFRESH_EVENT, callback);
  return () => window.removeEventListener(CREDITS_REFRESH_EVENT, callback);
}
