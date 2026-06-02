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
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <label
          htmlFor="idea"
          className="mb-2 block text-sm font-medium text-gray-300"
        >
          Describe your idea
        </label>
        <div className="gradient-border rounded-xl">
          <textarea
            id="idea"
            rows={5}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="e.g. A CLI tool that turns natural language into SQL queries against your local database..."
            className="w-full rounded-xl border-0 bg-surface-raised px-4 py-3 text-gray-100 placeholder-gray-500 transition-shadow focus:shadow-glow focus:outline-none focus:ring-1 focus:ring-accent-blue/50"
            disabled={isLoading}
          />
        </div>
        <p className="mt-2 text-xs text-gray-500">
          Minimum 10 characters. Be as descriptive as you like.
        </p>
      </div>
      <button
        type="submit"
        disabled={isLoading || text.trim().length < 10}
        className="group relative overflow-hidden rounded-lg bg-gradient-accent px-6 py-2.5 text-sm font-medium text-white shadow-glow transition-all hover:shadow-glow-lg disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
      >
        <span className="relative z-10">
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              {currentStep
                ? (STEP_LABELS[currentStep] ?? "Processing...")
                : "Processing..."}
            </span>
          ) : (
            "Analyze Idea"
          )}
        </span>
      </button>
    </form>
  );
}
