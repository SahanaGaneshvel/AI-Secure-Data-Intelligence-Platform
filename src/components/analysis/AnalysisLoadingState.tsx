import React from "react";
import { AnalysisState } from "@/lib/types";

interface AnalysisLoadingStateProps {
  state: AnalysisState;
}

const stateMessages: Record<AnalysisState, { label: string; step: number }> = {
  idle: { label: "Ready to analyze", step: 0 },
  validating: { label: "Validating input...", step: 1 },
  scanning: { label: "Scanning for sensitive data...", step: 2 },
  analyzing: { label: "Analyzing logs...", step: 3 },
  generating: { label: "Generating AI insights...", step: 4 },
  complete: { label: "Analysis complete", step: 5 },
  error: { label: "Analysis failed", step: 0 },
};

export const AnalysisLoadingState: React.FC<AnalysisLoadingStateProps> = ({ state }) => {
  const { label, step } = stateMessages[state];
  const totalSteps = 4;
  const progress = (step / totalSteps) * 100;

  if (state === "idle" || state === "complete") return null;

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-700 border-t-blue-500"></div>
          <div>
            <p className="text-sm font-medium text-slate-200">{label}</p>
            <p className="text-xs text-slate-500">
              Step {step} of {totalSteps}
            </p>
          </div>
        </div>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full bg-blue-600 transition-all duration-500"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  );
};
