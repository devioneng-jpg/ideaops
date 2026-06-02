"use client";

import { useState } from "react";

const STEP_LABELS: Record<string, string> = {
  classify: "Classifying idea...",
  score: "Scoring idea...",
  plan: "Planning MVP...",
  break_down_tasks: "Breaking down tasks...",
  publish_notion: "Publishing to Notion...",
};

interface IdeaFormProps {
  onSubmit: (ideaText: string) => void;
  isLoading: boolean;
  currentStep: string | null;
}

export function IdeaForm({ onSubmit, isLoading, currentStep }: IdeaFormProps) {
  const [text, setText] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (text.trim().length >= 10) {
      onSubmit(text.trim());
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="idea" className="mb-2 block text-sm font-medium text-gray-300">
          Describe your idea
        </label>
        <textarea
          id="idea"
          rows={5}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="e.g. A CLI tool that turns natural language into SQL queries against your local database..."
          className="w-full rounded-lg border border-gray-700 bg-gray-900 px-4 py-3 text-gray-100 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          disabled={isLoading}
        />
        <p className="mt-1 text-xs text-gray-500">
          Minimum 10 characters. Be as descriptive as you like.
        </p>
      </div>
      <button
        type="submit"
        disabled={isLoading || text.trim().length < 10}
        className="rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            {currentStep ? STEP_LABELS[currentStep] ?? "Processing..." : "Processing..."}
          </span>
        ) : (
          "Analyze Idea"
        )}
      </button>
    </form>
  );
}
