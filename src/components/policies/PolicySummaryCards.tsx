import React from "react";
import { Shield, Activity, Clock } from "lucide-react";

interface PolicySummaryCardsProps {
  totalPolicies: number;
  activePolicies: number;
  totalDetectors: number;
  lastUpdate: string;
}

export const PolicySummaryCards: React.FC<PolicySummaryCardsProps> = ({
  totalPolicies,
  activePolicies,
  totalDetectors,
  lastUpdate,
}) => {
  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm text-slate-400">Active Policies</span>
          <Shield className="h-5 w-5 text-green-500" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold text-white">{activePolicies}</span>
          <span className="text-base text-slate-500">/ {totalPolicies}</span>
        </div>
        <p className="mt-3 text-xs text-slate-500">
          {totalPolicies - activePolicies} inactive
        </p>
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm text-slate-400">Detectors Enabled</span>
          <Activity className="h-5 w-5 text-blue-500" />
        </div>
        <div className="mb-3">
          <span className="text-4xl font-bold text-white">{totalDetectors}</span>
        </div>
        <div className="flex gap-2">
          <span className="h-2 w-2 rounded-full bg-blue-500"></span>
          <span className="h-2 w-2 rounded-full bg-purple-500"></span>
          <span className="h-2 w-2 rounded-full bg-green-500"></span>
          <span className="h-2 w-2 rounded-full bg-orange-500"></span>
        </div>
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm text-slate-400">Last Updated</span>
          <Clock className="h-5 w-5 text-slate-500" />
        </div>
        <div className="mb-3">
          <span className="text-lg font-semibold text-white">{lastUpdate}</span>
        </div>
        <p className="text-xs text-slate-500">Most recent policy change</p>
      </div>
    </div>
  );
};
