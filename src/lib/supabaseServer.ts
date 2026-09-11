/**
 * SERVER-ONLY Supabase client, used for writing early-access emails,
 * feedback, and lightweight usage analytics.
 *
 * Deliberately env-gated: if NEXT_PUBLIC_SUPABASE_URL or
 * SUPABASE_SERVICE_ROLE_KEY are not set, every write function below
 * logs a warning and no-ops instead of throwing. This lets the app run
 * end-to-end in testing before a Supabase project is provisioned — see
 * /sql/schema.sql for the tables to create, and README.md for setup.
 *
 * The service-role key must only ever be read here, in server-only code.
 * Never expose it via NEXT_PUBLIC_*, an API response, or client code.
 */

import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

let client: SupabaseClient | null = null;

function getClient(): SupabaseClient | null {
  if (!supabaseUrl || !serviceRoleKey) return null;
  if (!client) {
    client = createClient(supabaseUrl, serviceRoleKey, {
      auth: { persistSession: false },
    });
  }
  return client;
}

function warnNotConfigured(action: string) {
  console.warn(
    `[supabase] Skipped "${action}" — NEXT_PUBLIC_SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set.`
  );
}

export async function insertEarlyAccessEmail(email: string): Promise<void> {
  const db = getClient();
  if (!db) return warnNotConfigured("insertEarlyAccessEmail");
  const { error } = await db.from("early_access_emails").insert({ email });
  if (error) console.error("[supabase] insertEarlyAccessEmail failed:", error.message);
}

export interface FeedbackInput {
  sessionId: string;
  categoryId: string;
  rating: "up" | "down";
  comment?: string;
}

export async function insertFeedback(input: FeedbackInput): Promise<void> {
  const db = getClient();
  if (!db) return warnNotConfigured("insertFeedback");
  const { error } = await db.from("feedback").insert({
    session_id: input.sessionId,
    category_id: input.categoryId,
    rating: input.rating,
    comment: input.comment ?? null,
  });
  if (error) console.error("[supabase] insertFeedback failed:", error.message);
}

export interface AnalyticsEventInput {
  sessionId: string;
  categoryId: string;
  event: string;
  metadata?: Record<string, unknown>;
}

export async function logAnalyticsEvent(input: AnalyticsEventInput): Promise<void> {
  const db = getClient();
  if (!db) return warnNotConfigured("logAnalyticsEvent");
  const { error } = await db.from("analytics_events").insert({
    session_id: input.sessionId,
    category_id: input.categoryId,
    event: input.event,
    metadata: input.metadata ?? {},
  });
  if (error) console.error("[supabase] logAnalyticsEvent failed:", error.message);
}
