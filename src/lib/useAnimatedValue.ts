"use client";

import { useEffect, useState } from "react";

const NUMERIC_PATTERN = /^([^\d-]*)(-?[\d,]*\.?\d+)([^\d]*)$/;

/**
 * Renders `value` as-is on first paint (server and client match — no
 * hydration mismatch), then, if it looks numeric (e.g. "$1,234.56",
 * "23%", "1.2x"), animates a brief count-up to it after mount. Values
 * that aren't numeric-looking are returned unchanged. Subtle by design —
 * short duration, skipped entirely under prefers-reduced-motion.
 */
export function useAnimatedValue(value: string, durationMs = 700): string {
  const [display, setDisplay] = useState(value);

  useEffect(() => {
    // `display` already starts equal to `value` (useState initializer), so
    // the non-animating branches below just leave it as-is rather than
    // calling setState synchronously in the effect body.
    const match = value.match(NUMERIC_PATTERN);
    if (!match) return;
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;

    const [, prefix, numStr, suffix] = match;
    const target = parseFloat(numStr.replace(/,/g, ""));
    if (Number.isNaN(target)) return;
    const decimals = numStr.includes(".") ? numStr.split(".")[1].length : 0;
    const hasCommas = numStr.includes(",");

    let start: number | null = null;
    let raf = 0;

    function step(ts: number) {
      if (start === null) start = ts;
      const progress = Math.min((ts - start) / durationMs, 1);
      const current = target * progress;
      const formatted = hasCommas
        ? current.toLocaleString(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
          })
        : current.toFixed(decimals);
      setDisplay(`${prefix}${formatted}${suffix}`);
      if (progress < 1) raf = requestAnimationFrame(step);
    }

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [value, durationMs]);

  return display;
}
