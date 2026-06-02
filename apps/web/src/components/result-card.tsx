"use client";

import type { IdeaSubmissionResponse } from "@/lib/api";

interface ResultCardProps {
  result: IdeaSubmissionResponse;
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    completed: "bg-green-900 text-green-300",
    partial_success: "bg-yellow-900 text-yellow-300",
    failed: "bg-red-900 text-red-300",
  };
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[status] || "bg-gray-700 text-gray-300"}`}
    >
      {status}
    </span>
  );
}

export function ResultCard({ result }: ResultCardProps) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-6">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Result</h2>
        <StatusBadge status={result.status} />
      </div>

      {result.summary && (
        <p className="mb-4 text-gray-300">{result.summary}</p>
      )}

      <div className="grid grid-cols-2 gap-4 text-sm">
        {result.category && (
          <div>
            <span className="text-gray-500">Category</span>
            <p className="font-medium">{result.category}</p>
          </div>
        )}
        {result.total_score !== null && (
          <div>
            <span className="text-gray-500">Score</span>
            <p className="font-medium">{result.total_score}/10</p>
          </div>
        )}
      </div>

      {result.notion_url && (
        <a
          href={result.notion_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 inline-block rounded-lg bg-gray-800 px-4 py-2 text-sm text-blue-400 hover:bg-gray-700"
        >
          View full brief in Notion
        </a>
      )}
    </div>
  );
}
