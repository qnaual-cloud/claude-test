"use client";

import { useState } from "react";
import { siteConfig } from "@/content/site.config";

interface FeedbackWidgetProps {
  sessionId: string;
  categoryId: string;
}

export function FeedbackWidget({ sessionId, categoryId }: FeedbackWidgetProps) {
  const [rating, setRating] = useState<"up" | "down" | null>(null);
  const [comment, setComment] = useState("");
  const [submitted, setSubmitted] = useState(false);

  async function submit(nextRating: "up" | "down", nextComment?: string) {
    setRating(nextRating);
    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId, categoryId, rating: nextRating, comment: nextComment }),
      });
    } catch {
      // Feedback is best-effort; failing silently keeps this non-blocking.
    }
    setSubmitted(true);
  }

  if (submitted) {
    return <p className="text-sm text-muted-foreground">{siteConfig.feedback.thanks}</p>;
  }

  return (
    <div className="flex flex-col gap-2">
      <p className="text-sm text-foreground">{siteConfig.feedback.prompt}</p>
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => submit("up", comment || undefined)}
          aria-label="Yes, this was useful"
          className={`flex h-10 w-10 items-center justify-center rounded-lg border transition-colors ${
            rating === "up"
              ? "border-accent bg-accent text-accent-foreground"
              : "border-border bg-card text-muted-foreground hover:border-accent hover:text-accent"
          }`}
        >
          👍
        </button>
        <button
          type="button"
          onClick={() => submit("down", comment || undefined)}
          aria-label="No, this wasn't useful"
          className={`flex h-10 w-10 items-center justify-center rounded-lg border transition-colors ${
            rating === "down"
              ? "border-accent bg-accent text-accent-foreground"
              : "border-border bg-card text-muted-foreground hover:border-accent hover:text-accent"
          }`}
        >
          👎
        </button>
        <input
          type="text"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Optional comment"
          className="min-h-10 flex-1 rounded-lg border border-border bg-card px-3 py-1.5 text-sm text-foreground outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
      </div>
    </div>
  );
}
