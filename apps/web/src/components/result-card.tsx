"use client";

import type { IdeaSubmissionResponse } from "@/lib/api";

interface ResultCardProps {
  result: IdeaSubmissionResponse;
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    completed:
      "border-emerald-500/20 bg-emerald-500/[0.08] text-emerald-400",
    partial_success:
      "border-yellow-500/20 bg-yellow-500/[0.08] text-yellow-400",
    failed: "border-red-500/20 bg-red-500/[0.08] text-red-400",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${styles[status] || "border-white/10 bg-white/5 text-gray-400"}`}
    >
      {status === "completed" && (
        <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-emerald-400" />
      )}
      {status === "partial_success" && (
        <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-yellow-400" />
      )}
      {status === "failed" && (
        <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-red-400" />
      )}
      {status.replace("_", " ")}
    </span>
  );
}

export function ResultCard({ result }: ResultCardProps) {
  return (
    <div className="card gradient-border rounded-xl p-6">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-lg font-semibold tracking-tight">Result</h2>
        <StatusBadge status={result.status} />
      </div>

      {result.summary && (
        <p className="mb-5 leading-relaxed text-gray-300">{result.summary}</p>
      )}

      <div className="grid grid-cols-2 gap-4">
        {result.category && (
          <div className="rounded-lg border border-white/[0.06] bg-surface-raised px-4 py-3">
            <span className="text-xs font-medium uppercase tracking-wider text-gray-500">
              Category
            </span>
            <p className="mt-1 font-medium text-gray-200">
              {result.category.replace("_", " ")}
            </p>
          </div>
        )}
        {result.total_score !== null && (
          <div className="rounded-lg border border-white/[0.06] bg-surface-raised px-4 py-3">
            <span className="text-xs font-medium uppercase tracking-wider text-gray-500">
              Score
            </span>
            <p className="mt-1 font-medium text-gray-200">
              <span className="gradient-text text-xl font-bold">
                {result.total_score}
              </span>
              <span className="text-sm text-gray-500"> / 10</span>
            </p>
          </div>
        )}
      </div>

      {result.notion_url && (
        <a
          href={result.notion_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-5 inline-flex items-center gap-2 rounded-lg border border-white/[0.08] bg-surface-raised px-4 py-2 text-sm font-medium text-gray-300 transition-all hover:border-white/[0.15] hover:text-white hover:shadow-glow"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
          </svg>
          View full brief in Notion
        </a>
      )}
    </div>
  );
}
