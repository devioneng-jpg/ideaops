"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface IdeaSummary {
  id: string;
  created_at: string;
  source: string;
  raw_text: string;
  status: string;
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    completed:
      "border-emerald-500/20 bg-emerald-500/[0.08] text-emerald-400",
    partial_success:
      "border-yellow-500/20 bg-yellow-500/[0.08] text-yellow-400",
    failed: "border-red-500/20 bg-red-500/[0.08] text-red-400",
    processing: "border-accent-blue/20 bg-accent-blue/[0.08] text-accent-blue",
    pending: "border-white/10 bg-white/5 text-gray-400",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${styles[status] || "border-white/10 bg-white/5 text-gray-400"}`}
    >
      {status.replace("_", " ")}
    </span>
  );
}

export default function IdeasHistoryPage() {
  const [ideas, setIdeas] = useState<IdeaSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchIdeas() {
      try {
        const res = await fetch(`${API_BASE}/api/ideas`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setIdeas(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load ideas");
      } finally {
        setLoading(false);
      }
    }
    fetchIdeas();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-gray-400">
        <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-gray-600 border-t-gray-300" />
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <div className="card rounded-lg border-red-500/20 bg-red-500/[0.06] px-4 py-3 text-sm text-red-300">
        {error}
      </div>
    );
  }

  return (
    <div>
      <h1 className="gradient-text mb-8 text-4xl font-bold tracking-tight">
        Idea History
      </h1>
      {ideas.length === 0 ? (
        <p className="text-gray-500">No ideas submitted yet.</p>
      ) : (
        <div className="space-y-3">
          {ideas.map((idea) => (
            <a
              key={idea.id}
              href={`/?id=${idea.id}`}
              className="card card-hover block rounded-xl p-4"
            >
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {new Date(idea.created_at).toLocaleDateString()} via{" "}
                  {idea.source}
                </span>
                <StatusBadge status={idea.status} />
              </div>
              <p className="text-sm leading-relaxed text-gray-300 line-clamp-2">
                {idea.raw_text}
              </p>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
