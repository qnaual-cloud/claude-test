/**
 * SERVER-ONLY. The structured-output schema for the "Research Dashboard"
 * format. Used only by /src/server/anthropicClient.ts to constrain the
 * Claude API response — never imported by client components. Only the
 * inferred `DashboardData` type (erased at build time via `import type`)
 * is safe to import from the client, for typing the JSON it receives
 * back from the API route.
 *
 * Deliberately generic: no field here names a specific company, sector,
 * or industry. The model fills every field based on the user's actual
 * inputs for whichever category/entity was selected — the same schema
 * works for a single company, a comparison, or a portfolio.
 */

import { z } from "zod";

export const DashboardSchema = z.object({
  headline: z.string(),
  outlook: z.enum(["positive", "neutral", "negative", "mixed"]),
  keyMetrics: z
    .array(
      z.object({
        label: z.string(),
        value: z.string(),
        detail: z.string().optional(),
      })
    )
    .min(2)
    .max(6),
  sections: z
    .array(
      z.object({
        heading: z.string(),
        body: z.string(),
      })
    )
    .min(2)
    .max(6),
  strengths: z.array(z.string()).min(1).max(6),
  risks: z.array(z.string()).min(1).max(6),
  assumptions: z.array(z.string()).min(1).max(5),
});

export type DashboardData = z.infer<typeof DashboardSchema>;
