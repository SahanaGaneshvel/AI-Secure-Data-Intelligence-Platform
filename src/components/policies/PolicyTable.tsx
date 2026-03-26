import React from "react";
import { Policy } from "@/lib/types";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { Edit2 } from "lucide-react";

interface PolicyTableProps {
  policies: Policy[];
  onPolicyClick: (policy: Policy) => void;
  onToggleStatus: (policyId: string, status: "active" | "inactive") => void;
}

const categoryColors: Record<string, string> = {
  "Data Security": "bg-blue-500/10 text-blue-400 border-blue-500/20",
  "Access Control": "bg-purple-500/10 text-purple-400 border-purple-500/20",
  "Threat Detection": "bg-orange-500/10 text-orange-400 border-orange-500/20",
};

export const PolicyTable: React.FC<PolicyTableProps> = ({
  policies,
  onPolicyClick,
  onToggleStatus,
}) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  };

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Policy Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Severity</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Last Updated</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {policies.map((policy) => (
              <tr key={policy.id} className="hover:bg-slate-800/50 transition-colors">
                <td className="px-6 py-4">
                  <div>
                    <div className="text-sm font-medium text-white">{policy.name}</div>
                    <div className="text-xs text-slate-500">{policy.description}</div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`inline-flex items-center rounded border px-2 py-1 text-xs font-medium ${categoryColors[policy.category]}`}
                  >
                    {policy.category}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <RiskBadge level={policy.severityThreshold} size="sm" />
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() =>
                      onToggleStatus(
                        policy.id,
                        policy.status === "active" ? "inactive" : "active"
                      )
                    }
                    className="cursor-pointer"
                  >
                    <StatusBadge status={policy.status} />
                  </button>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-slate-400">{formatDate(policy.lastUpdated)}</span>
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => onPolicyClick(policy)}
                    className="rounded p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
                  >
                    <Edit2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
