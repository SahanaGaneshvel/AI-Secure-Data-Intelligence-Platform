import React from "react";
import { RiskLevel, InputType, ActionType } from "@/lib/types";
import { Search } from "lucide-react";

interface AuditFiltersProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  riskFilter: RiskLevel | "All";
  setRiskFilter: (risk: RiskLevel | "All") => void;
  actionFilter: ActionType | "All";
  setActionFilter: (action: ActionType | "All") => void;
  inputTypeFilter: InputType | "All";
  setInputTypeFilter: (type: InputType | "All") => void;
}

export const AuditFilters: React.FC<AuditFiltersProps> = ({
  searchQuery,
  setSearchQuery,
  riskFilter,
  setRiskFilter,
  actionFilter,
  setActionFilter,
  inputTypeFilter,
  setInputTypeFilter,
}) => {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <div className="grid grid-cols-4 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search analysis ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-10 w-full rounded border border-slate-800 bg-slate-950 pl-9 pr-3 text-sm text-slate-300 placeholder-slate-500 focus:border-blue-600 focus:outline-none"
          />
        </div>

        <select
          value={riskFilter}
          onChange={(e) => setRiskFilter(e.target.value as RiskLevel | "All")}
          className="h-10 rounded border border-slate-800 bg-slate-950 px-3 text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
        >
          <option value="All">All Risk Levels</option>
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>

        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value as ActionType | "All")}
          className="h-10 rounded border border-slate-800 bg-slate-950 px-3 text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
        >
          <option value="All">All Actions</option>
          <option value="Allow">Allow</option>
          <option value="Mask">Mask</option>
          <option value="Block">Block</option>
          <option value="Masked & Flagged">Masked & Flagged</option>
        </select>

        <select
          value={inputTypeFilter}
          onChange={(e) => setInputTypeFilter(e.target.value as InputType | "All")}
          className="h-10 rounded border border-slate-800 bg-slate-950 px-3 text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
        >
          <option value="All">All Input Types</option>
          <option value="text">Text</option>
          <option value="file">File</option>
          <option value="log">Log</option>
          <option value="sql">SQL</option>
          <option value="chat">Chat</option>
        </select>
      </div>
    </div>
  );
};
