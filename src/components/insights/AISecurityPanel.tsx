import React from "react";
import { Brain, AlertTriangle, Activity, CheckCircle } from "lucide-react";

interface AISecurityPanelProps {
  contextSummary: string;
  criticalVulnerabilities: string[];
  behavioralAnomalies: string[];
  recommendedActions: string[];
  riskScoreBreakdown?: { finding: string; contribution: number }[];
}

export const AISecurityPanel: React.FC<AISecurityPanelProps> = ({
  contextSummary,
  criticalVulnerabilities,
  behavioralAnomalies,
  recommendedActions,
  riskScoreBreakdown,
}) => {
  return (
    <div className="space-y-4">
      {/* Main Panel */}
      <div className="rounded-lg border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 px-6 py-4">
          <h3 className="flex items-center gap-2 text-base font-semibold text-white">
            <Brain className="h-5 w-5 text-blue-500" />
            <span>Security Analysis</span>
          </h3>
          <p className="mt-1 text-xs text-slate-400">
            Rule-based threat intelligence
          </p>
        </div>

        <div className="space-y-6 p-6">
          {/* Context Summary */}
          <div>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
              Context Summary
            </h4>
            <p className="text-sm leading-relaxed text-slate-300">{contextSummary}</p>
          </div>

          {/* Critical Vulnerabilities */}
          {criticalVulnerabilities.length > 0 && (
            <div>
              <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-red-400">
                <AlertTriangle className="h-4 w-4" />
                Critical Vulnerabilities
              </h4>
              <ul className="space-y-2">
                {criticalVulnerabilities.map((vuln, index) => (
                  <li key={index} className="text-sm leading-relaxed text-slate-300">
                    <span className="mr-2 text-red-400">•</span>
                    {vuln}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Behavioral Anomalies */}
          {behavioralAnomalies.length > 0 && (
            <div>
              <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-orange-400">
                <Activity className="h-4 w-4" />
                Behavioral Anomalies
              </h4>
              <ul className="space-y-2">
                {behavioralAnomalies.map((anomaly, index) => (
                  <li key={index} className="text-sm leading-relaxed text-slate-300">
                    <span className="mr-2 text-orange-400">•</span>
                    {anomaly}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommended Actions */}
          {recommendedActions.length > 0 && (
            <div>
              <h4 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-green-400">
                <CheckCircle className="h-4 w-4" />
                Recommended Actions
              </h4>
              <ul className="space-y-2">
                {recommendedActions.map((action, index) => (
                  <li key={index} className="text-sm leading-relaxed text-slate-300">
                    <span className="mr-2 text-green-400">✓</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Risk Score Breakdown */}
      {riskScoreBreakdown && riskScoreBreakdown.length > 0 && (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
          <h4 className="mb-4 text-sm font-semibold text-white">Risk Score Breakdown</h4>
          <div className="space-y-3">
            {riskScoreBreakdown.map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-slate-400">{item.finding}</span>
                <div className="flex items-center gap-3">
                  <div className="h-2 w-32 overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full bg-blue-600"
                      style={{ width: `${item.contribution}%` }}
                    ></div>
                  </div>
                  <span className="w-8 text-right text-sm font-medium text-slate-300">
                    +{item.contribution}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
