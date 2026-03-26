import React from "react";
import { RiskLevel, ActionType } from "@/lib/types";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { TrendingUp, AlertTriangle, Target } from "lucide-react";

interface RiskSummaryCardsProps {
  overallRiskScore: number;
  overallRiskLevel: RiskLevel;
  primaryAction: ActionType;
  totalFindings: number;
  scoreDelta?: number;
}

export const RiskSummaryCards: React.FC<RiskSummaryCardsProps> = ({
  overallRiskScore,
  overallRiskLevel,
  primaryAction,
  totalFindings,
  scoreDelta = 12,
}) => {
  return (
    <div className="grid grid-cols-3 gap-4">
      {/* Overall Risk Score */}
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm text-slate-400">Overall Risk Score</span>
          <RiskBadge level={overallRiskLevel} size="sm" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold text-white">{overallRiskScore}</span>
          <span className="text-2xl text-slate-500">/ 100</span>
        </div>
        <div className="mt-3 flex items-center gap-1 text-xs text-red-400">
          <TrendingUp className="h-3 w-3" />
          <span>+{scoreDelta} from previous scan</span>
        </div>
      </div>

      {/* Primary Action */}
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm text-slate-400">Primary Action</span>
          <AlertTriangle className="h-5 w-5 text-orange-500" />
        </div>
        <div className="mb-3">
          <span className="text-xl font-semibold text-white">{primaryAction}</span>
        </div>
        <p className="text-xs text-slate-500">
          Content modified before logging. Alert sent to SecOps.
        </p>
      </div>

      {/* Total Findings */}
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm text-slate-400">Total Findings</span>
          <Target className="h-5 w-5 text-blue-500" />
        </div>
        <div className="mb-3 flex items-baseline gap-2">
          <span className="text-4xl font-bold text-white">{totalFindings}</span>
          <span className="text-base text-slate-500">findings</span>
        </div>
        <div className="flex gap-2">
          <span className="h-2 w-2 rounded-full bg-red-500"></span>
          <span className="h-2 w-2 rounded-full bg-orange-500"></span>
          <span className="h-2 w-2 rounded-full bg-blue-500"></span>
        </div>
      </div>
    </div>
  );
};
