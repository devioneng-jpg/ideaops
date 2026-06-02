"use client";

import { useState } from "react";
import { IdeaForm } from "@/components/idea-form";
import { ResultCard } from "@/components/result-card";
import { TaskTable } from "@/components/task-table";
import {
  submitIdea,
  getIdea,
  type IdeaSubmissionResponse,
  type WorkflowRunResponse,
} from "@/lib/api";

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<IdeaSubmissionResponse | null>(null);
  const [details, setDetails] = useState<WorkflowRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(ideaText: string) {
    setIsLoading(true);
    setResult(null);
    setDetails(null);
    setError(null);

    try {
      const res = await submitIdea(ideaText);
      setResult(res);

      // Fetch full details including tasks
      const full = await getIdea(res.idea_id);
      setDetails(full);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="mb-2 text-3xl font-bold">Submit an Idea</h1>
        <p className="text-gray-400">
          Describe your idea and IdeaOps will classify it, score it, generate an
          MVP plan, and break it into tasks.
        </p>
      </div>

      <IdeaForm onSubmit={handleSubmit} isLoading={isLoading} />

      {error && (
        <div className="rounded-lg border border-red-800 bg-red-950 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && <ResultCard result={result} />}

      {details?.task_output?.tasks && (
        <TaskTable tasks={details.task_output.tasks} />
      )}
    </div>
  );
}
