const STEPS = [
  { key: "classify", label: "Classifying idea..." },
  { key: "score", label: "Scoring idea..." },
  { key: "plan", label: "Planning MVP..." },
  { key: "break_down_tasks", label: "Breaking down tasks..." },
  { key: "publish_notion", label: "Publishing to Notion..." },
] as const;

interface ProgressStepsProps {
  currentStep: string | null;
  completedSteps: string[];
}

export function ProgressSteps({ currentStep, completedSteps }: ProgressStepsProps) {
  return (
    <div className="space-y-2">
      {STEPS.map((step, i) => {
        const isCompleted = completedSteps.includes(step.key);
        const isActive = step.key === currentStep;

        return (
          <div
            key={step.key}
            className={`flex items-center gap-2 text-sm ${
              isCompleted
                ? "text-green-400"
                : isActive
                  ? "text-blue-400"
                  : "text-gray-600"
            }`}
          >
            {isCompleted ? (
              <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-green-900 text-xs text-green-400">
                &#10003;
              </span>
            ) : isActive ? (
              <span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-blue-400 border-t-transparent" />
            ) : (
              <span className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-gray-700 text-xs text-gray-600">
                {i + 1}
              </span>
            )}
            <span className={isCompleted ? "line-through" : ""}>{step.label}</span>
          </div>
        );
      })}
    </div>
  );
}
