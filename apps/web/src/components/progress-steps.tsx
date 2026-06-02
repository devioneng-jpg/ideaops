const STEPS = [
  { key: "classify", label: "Classifying idea" },
  { key: "score", label: "Scoring idea" },
  { key: "plan", label: "Planning MVP" },
  { key: "break_down_tasks", label: "Breaking down tasks" },
  { key: "publish_notion", label: "Publishing to Notion" },
] as const;

interface ProgressStepsProps {
  currentStep: string | null;
  completedSteps: string[];
}

export function ProgressSteps({
  currentStep,
  completedSteps,
}: ProgressStepsProps) {
  return (
    <div className="card rounded-xl p-5">
      <div className="mb-4 flex items-center gap-2">
        <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent-blue" />
        <span className="text-xs font-medium uppercase tracking-wider text-gray-400">
          Pipeline Progress
        </span>
      </div>
      <div className="space-y-1">
        {STEPS.map((step, i) => {
          const isCompleted = completedSteps.includes(step.key);
          const isActive = step.key === currentStep;

          return (
            <div
              key={step.key}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                isActive
                  ? "bg-accent-blue/[0.08] text-accent-blue"
                  : isCompleted
                    ? "text-gray-400"
                    : "text-gray-600"
              }`}
            >
              {isCompleted ? (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                  <svg
                    className="h-3 w-3"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={3}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </span>
              ) : isActive ? (
                <span className="relative flex h-5 w-5 items-center justify-center">
                  <span className="absolute h-5 w-5 animate-ping rounded-full bg-accent-blue/20" />
                  <span className="relative h-2.5 w-2.5 rounded-full bg-accent-blue" />
                </span>
              ) : (
                <span className="flex h-5 w-5 items-center justify-center rounded-full border border-white/[0.08] text-[10px] text-gray-600">
                  {i + 1}
                </span>
              )}

              <span className={isCompleted ? "line-through decoration-gray-600" : ""}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
