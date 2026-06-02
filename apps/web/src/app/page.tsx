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
      const ack = await submitIdea(ideaText);
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
    <div className="space-y-10">
      {/* Hero */}
      <div className="space-y-3">
        <h1 className="gradient-text text-4xl font-bold tracking-tight sm:text-5xl">
          Submit an Idea
        </h1>
        <p className="max-w-2xl text-base leading-relaxed text-gray-400">
          Describe your idea and IdeaOps will classify it, score it, generate an
          MVP plan, and break it into tasks.
        </p>
      </div>

      <IdeaForm
        onSubmit={handleSubmit}
        isLoading={isLoading}
        currentStep={currentStep}
      />

      {isLoading && (
        <ProgressSteps currentStep={currentStep} completedSteps={completedSteps} />
      )}

      {error && (
        <div className="card rounded-lg border-red-500/20 bg-red-500/[0.06] px-4 py-3 text-sm text-red-300">
          <div className="flex items-center gap-2">
            <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            {error}
          </div>
        </div>
      )}

      {warning && (
        <div className="card rounded-lg border-yellow-500/20 bg-yellow-500/[0.06] px-4 py-3 text-sm text-yellow-300">
          <div className="flex items-center gap-2">
            <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {warning}
          </div>
        </div>
      )}

      {result && <ResultCard result={result} />}

      {details?.task_output?.tasks && (
        <TaskTable tasks={details.task_output.tasks} />
      )}
    </div>
  );
}
