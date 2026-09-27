"use client";

import { useState } from "react";

interface UserRow {
  id: string;
  email: string | null;
  fullName: string;
  creditsBalance: number;
  membershipTier: "free" | "member" | "professional";
}

export function AdminPanel() {
  const [query, setQuery] = useState("");
  const [users, setUsers] = useState<UserRow[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [amountByUser, setAmountByUser] = useState<Record<string, string>>({});
  const [noteByUser, setNoteByUser] = useState<Record<string, string>>({});
  const [pendingUserId, setPendingUserId] = useState<string | null>(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`/api/admin/users?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong.");
      setUsers(data.users);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  async function handleAdjust(userId: string) {
    const amount = parseInt(amountByUser[userId] ?? "", 10);
    if (!amount || Number.isNaN(amount)) return;

    setPendingUserId(userId);
    setError("");
    try {
      const res = await fetch("/api/admin/credits", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId, amount, note: noteByUser[userId] || undefined }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong.");

      setUsers((prev) =>
        prev
          ? prev.map((u) => (u.id === userId ? { ...u, creditsBalance: data.creditsBalance } : u))
          : prev
      );
      setAmountByUser((prev) => ({ ...prev, [userId]: "" }));
      setNoteByUser((prev) => ({ ...prev, [userId]: "" }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setPendingUserId(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by email (leave blank for most recent)"
          className="min-h-11 flex-1 rounded-lg border border-border bg-card px-3 py-2 text-sm text-foreground outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
        <button
          type="submit"
          disabled={loading}
          className="min-h-11 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-accent-foreground hover:bg-accent-hover disabled:opacity-50"
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {users && (
        <div className="flex flex-col gap-3">
          {users.length === 0 && <p className="text-sm text-muted-foreground">No users found.</p>}
          {users.map((u) => (
            <div key={u.id} className="flex flex-col gap-3 rounded-lg border border-border bg-card p-4">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <div>
                  <p className="text-sm font-medium text-foreground">{u.email || "(no email)"}</p>
                  <p className="text-xs text-muted-foreground">
                    {u.fullName || "(no name)"} · {u.membershipTier}
                  </p>
                </div>
                <p className="text-sm font-semibold text-foreground">{u.creditsBalance} credits</p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <input
                  type="number"
                  value={amountByUser[u.id] ?? ""}
                  onChange={(e) => setAmountByUser((prev) => ({ ...prev, [u.id]: e.target.value }))}
                  placeholder="+10 or -5"
                  className="min-h-9 w-28 rounded-lg border border-border bg-background px-2 py-1 text-sm text-foreground outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
                />
                <input
                  type="text"
                  value={noteByUser[u.id] ?? ""}
                  onChange={(e) => setNoteByUser((prev) => ({ ...prev, [u.id]: e.target.value }))}
                  placeholder="Note (optional)"
                  className="min-h-9 flex-1 rounded-lg border border-border bg-background px-2 py-1 text-sm text-foreground outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
                />
                <button
                  type="button"
                  onClick={() => handleAdjust(u.id)}
                  disabled={pendingUserId === u.id || !amountByUser[u.id]}
                  className="min-h-9 rounded-lg border border-accent px-3 py-1.5 text-sm font-medium text-accent hover:bg-accent/10 disabled:opacity-50"
                >
                  {pendingUserId === u.id ? "Applying…" : "Apply"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
