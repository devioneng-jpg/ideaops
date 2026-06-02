"use client";

import { useState } from "react";
import { IdeaForm } from "@/components/idea-form";
import { ProgressSteps } from "@/components/progress-steps";
import { ResultCard } from "@/components/result-card";
import { TaskTable } from "@/components/task-table";
import {
  submitIdea,
  pollIdea,
  type IdeaSubmissionResponse,
  type WorkflowRunResponse,
} from "@/lib/api";

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState<string | null>(null);
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [result, setResult] = useState<IdeaSubmissionResponse | null>(null);
  const [details, setDetails] = useState<WorkflowRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);

  async function handleSubmit(ideaText: string) {
    setIsLoading(true);
    setCurrentStep(null);
    setCompletedSteps([]);
    setResult(null);
    setDetails(null);
    setError(null);
    setWarning(null);

    try {
      // Submit returns immediately; the pipeline runs in the background.
      const ack = await submitIdea(ideaText);
      // Poll until the run finishes, updating progress along the way.
      const full = await pollIdea(ack.idea_id, {
        onProgress: (step, done) => {
          setCurrentStep(step);
          setCompletedSteps(done);
        },
      });
      setDetails(full);
      setResult({
        idea_id: full.idea_id,
        run_id: full.run_id,
        status: full.status,
        summary: full.planning_output?.one_sentence_summary ?? null,
        category: full.classifier_output?.category ?? null,
        total_score: full.scoring_output?.total_score ?? null,
        notion_url: full.notion_url,
      });
      if (full.status === "failed") {
        setError(full.error_message || "The workflow failed. Please try again.");
      } else if (full.status === "partial_success" && full.error_message) {
        setWarning(full.error_message);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
      setCurrentStep(null);
      setCompletedSteps([]);
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

      <IdeaForm onSubmit={handleSubmit} isLoading={isLoading} currentStep={currentStep} />

      {isLoading && (
        <ProgressSteps currentStep={currentStep} completedSteps={completedSteps} />
      )}

      {error && (
        <div className="rounded-lg border border-red-800 bg-red-950 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {warning && (
        <div className="rounded-lg border border-yellow-700 bg-yellow-950 p-4 text-sm text-yellow-300">
          {warning}
        </div>
      )}

      {result && <ResultCard result={result} />}

      {details?.task_output?.tasks && (
        <TaskTable tasks={details.task_output.tasks} />
      )}
    </div>
  );
}
