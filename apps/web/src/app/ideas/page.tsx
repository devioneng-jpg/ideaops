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
    return <p className="text-gray-400">Loading...</p>;
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-800 bg-red-950 p-4 text-sm text-red-300">
        {error}
      </div>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold">Idea History</h1>
      {ideas.length === 0 ? (
        <p className="text-gray-400">No ideas submitted yet.</p>
      ) : (
        <div className="space-y-3">
          {ideas.map((idea) => (
            <a
              key={idea.id}
              href={`/?id=${idea.id}`}
              className="block rounded-lg border border-gray-800 bg-gray-900 p-4 transition hover:border-gray-700"
            >
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  {new Date(idea.created_at).toLocaleDateString()} via{" "}
                  {idea.source}
                </span>
                <StatusBadge status={idea.status} />
              </div>
              <p className="text-sm text-gray-300 line-clamp-2">
                {idea.raw_text}
              </p>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    completed: "bg-green-900 text-green-300",
    partial_success: "bg-yellow-900 text-yellow-300",
    failed: "bg-red-900 text-red-300",
    processing: "bg-blue-900 text-blue-300",
    pending: "bg-gray-700 text-gray-300",
  };
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[status] || "bg-gray-700 text-gray-300"}`}
    >
      {status}
    </span>
  );
}
