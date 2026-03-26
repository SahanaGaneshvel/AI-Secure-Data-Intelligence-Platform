"use client";

import React, { useState } from "react";
import { Finding, RiskLevel } from "@/lib/types";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { DetectorBadge } from "@/components/shared/DetectorBadge";
import { Search, Filter, Download } from "lucide-react";

interface FindingsTableProps {
  findings: Finding[];
  onFindingClick?: (finding: Finding) => void;
  selectedFindingId?: string;
}

export const FindingsTable: React.FC<FindingsTableProps> = ({
  findings,
  onFindingClick,
  selectedFindingId,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState<RiskLevel | "All">("All");

  const filteredFindings = findings.filter((finding) => {
    const matchesSearch =
      finding.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      finding.preview.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRisk = riskFilter === "All" || finding.risk === riskFilter;
    return matchesSearch && matchesRisk;
  });

  const handleExportJSON = () => {
    const jsonString = JSON.stringify(findings, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `findings-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900">
      {/* Header */}
      <div className="border-b border-slate-800 px-6 py-4">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="flex items-center gap-2 text-base font-semibold text-white">
            <span>Detected Entities</span>
          </h3>
          <button
            onClick={handleExportJSON}
            className="flex items-center gap-2 rounded border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-700"
          >
            <Download className="h-3 w-3" />
            Export JSON
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search findings..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-9 w-full rounded border border-slate-700 bg-slate-800 pl-9 pr-3 text-sm text-slate-300 placeholder-slate-500 focus:border-blue-600 focus:outline-none"
            />
          </div>

          {/* Risk Filter */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value as RiskLevel | "All")}
              className="h-9 appearance-none rounded border border-slate-700 bg-slate-800 pl-9 pr-8 text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
            >
              <option value="All">All Risks</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
        <table className="w-full table-fixed">
          <thead className="sticky top-0 bg-slate-900">
            <tr className="border-b border-slate-800 text-left">
              <th className="w-16 px-4 py-2.5 text-xs font-medium uppercase tracking-wide text-slate-400">
                Line
              </th>
              <th className="w-32 px-4 py-2.5 text-xs font-medium uppercase tracking-wide text-slate-400">
                Type
              </th>
              <th className="w-24 px-4 py-2.5 text-xs font-medium uppercase tracking-wide text-slate-400">
                Risk
              </th>
              <th className="w-28 px-4 py-2.5 text-xs font-medium uppercase tracking-wide text-slate-400">
                Detector
              </th>
              <th className="px-4 py-2.5 text-xs font-medium uppercase tracking-wide text-slate-400">
                Preview
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredFindings.map((finding) => (
              <tr
                key={finding.id}
                onClick={() => onFindingClick?.(finding)}
                className={`cursor-pointer border-b border-slate-800/50 transition-colors hover:bg-slate-800/50 ${
                  selectedFindingId === finding.id ? "bg-slate-800" : ""
                }`}
              >
                <td className="px-4 py-2.5 text-sm text-slate-400">
                  {finding.line || "—"}
                </td>
                <td className="px-4 py-2.5 text-sm font-medium text-slate-200 truncate">
                  {finding.type}
                </td>
                <td className="px-4 py-2.5">
                  <RiskBadge level={finding.risk} size="sm" />
                </td>
                <td className="px-4 py-2.5">
                  <DetectorBadge type={finding.detector} />
                </td>
                <td className="px-4 py-2.5">
                  <code className="text-sm text-slate-400 truncate block max-w-[300px]">{finding.preview}</code>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Empty State */}
      {filteredFindings.length === 0 && (
        <div className="py-12 text-center">
          <p className="text-sm text-slate-500">
            {searchQuery || riskFilter !== "All"
              ? "No findings match your filters"
              : "No findings detected"}
          </p>
        </div>
      )}
    </div>
  );
};
