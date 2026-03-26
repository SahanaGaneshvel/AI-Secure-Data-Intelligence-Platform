import React from "react";
import { AuditLog } from "@/lib/types";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { StatusBadge } from "@/components/shared/StatusBadge";

interface AuditLogsTableProps {
  logs: AuditLog[];
}

const actionColors: Record<string, string> = {
  Allow: "bg-green-500/10 text-green-400 border-green-500/20",
  Mask: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  Block: "bg-red-500/10 text-red-400 border-red-500/20",
  "Masked & Flagged": "bg-orange-500/10 text-orange-400 border-orange-500/20",
};

const inputTypeColors: Record<string, string> = {
  text: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  file: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  log: "bg-green-500/10 text-green-400 border-green-500/20",
  sql: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  chat: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
};

export const AuditLogsTable: React.FC<AuditLogsTableProps> = ({ logs }) => {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const timeStr = date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
    const dateStr = date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    return { time: timeStr, date: dateStr };
  };

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Timestamp</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">
                Analysis ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Input Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Risk</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Action</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">
                Policies Triggered
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {logs.map((log) => {
              const { time, date } = formatTimestamp(log.timestamp);
              return (
                <tr key={log.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-white">{time}</div>
                      <div className="text-xs text-slate-500">{date}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono text-xs text-blue-400">{log.analysisId}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center rounded border px-2 py-1 text-xs font-medium uppercase ${inputTypeColors[log.inputType]}`}
                    >
                      {log.inputType}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <RiskBadge level={log.riskLevel} size="sm" />
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center rounded border px-2 py-1 text-xs font-medium ${actionColors[log.action]}`}
                    >
                      {log.action}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={log.status} />
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      {log.triggeredPolicies.length > 0 ? (
                        log.triggeredPolicies.slice(0, 2).map((policy, idx) => (
                          <span key={idx} className="text-xs text-slate-400">
                            {policy}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs text-slate-600">None</span>
                      )}
                      {log.triggeredPolicies.length > 2 && (
                        <span className="text-xs text-slate-600">
                          +{log.triggeredPolicies.length - 2} more
                        </span>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
