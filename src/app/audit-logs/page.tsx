"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { TopNavbar } from "@/components/layout/TopNavbar";
import { Footer } from "@/components/layout/Footer";
import { RiskBadge } from "@/components/shared/RiskBadge";
import { Button } from "@/components/shared/Button";
import { RiskLevel } from "@/lib/types";
import { getAnalyses, AnalysisRecord, APIError } from "@/lib/api";
import { Clock, Filter, Search, AlertCircle } from "lucide-react";

export default function AuditLogsPage() {
  const router = useRouter();
  const [analyses, setAnalyses] = useState<AnalysisRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterRisk, setFilterRisk] = useState<RiskLevel | "All">("All");

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAnalyses();
      setAnalyses(data.analyses || []);
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError("Failed to load analyses. Backend may be unavailable.");
      }
      console.error("Failed to fetch analyses:", err);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  const filteredAnalyses = analyses.filter((analysis) => {
    const matchesSearch =
      analysis.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      analysis.inputType.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRisk =
      filterRisk === "All" || analysis.overallRiskLevel === filterRisk;
    return matchesSearch && matchesRisk;
  });

  if (error && analyses.length === 0) {
    return (
      <div className="flex min-h-screen flex-col bg-slate-950">
        <TopNavbar />
        <main className="flex flex-1 items-center justify-center">
          <div className="text-center">
            <AlertCircle className="mx-auto mb-4 h-12 w-12 text-red-400" />
            <h2 className="mb-2 text-xl font-semibold text-red-400">Backend Unavailable</h2>
            <p className="mb-4 text-sm text-slate-500">{error}</p>
            <Button variant="primary" onClick={fetchAnalyses}>
              Retry
            </Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-950">
      <TopNavbar />

      <main className="flex-1 p-6">
        <div className="mx-auto max-w-[1800px]">
          {/* Page Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-white">Audit Logs</h1>
            <p className="text-sm text-slate-400">
              Historical record of all security analyses
            </p>
          </div>

          {/* Stats Cards */}
          <div className="mb-6 grid grid-cols-4 gap-4">
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <p className="text-xs text-slate-400">Total Analyses</p>
              <p className="text-2xl font-bold text-white">{analyses.length}</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <p className="text-xs text-slate-400">Critical Risks</p>
              <p className="text-2xl font-bold text-red-400">
                {analyses.filter((a) => a.overallRiskLevel === "Critical").length}
              </p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <p className="text-xs text-slate-400">High Risks</p>
              <p className="text-2xl font-bold text-orange-400">
                {analyses.filter((a) => a.overallRiskLevel === "High").length}
              </p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <p className="text-xs text-slate-400">Total Findings</p>
              <p className="text-2xl font-bold text-white">
                {analyses.reduce((sum, a) => sum + a.totalFindings, 0)}
              </p>
            </div>
          </div>

          {/* Filters */}
          <div className="mb-6 rounded-lg border border-slate-800 bg-slate-900 p-4">
            <div className="flex gap-4">
              {/* Search */}
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search by ID or type..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="h-10 w-full rounded border border-slate-700 bg-slate-800 pl-10 pr-4 text-sm text-slate-300 placeholder-slate-500 focus:border-blue-600 focus:outline-none"
                />
              </div>

              {/* Risk Filter */}
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <select
                  value={filterRisk}
                  onChange={(e) => setFilterRisk(e.target.value as RiskLevel | "All")}
                  className="h-10 appearance-none rounded border border-slate-700 bg-slate-800 pl-10 pr-8 text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
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
          <div className="rounded-lg border border-slate-800 bg-slate-900">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-400">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-400">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-400">
                    Risk Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-400">
                    Risk Level
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-400">
                    Action
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-slate-400">
                    Findings
                  </th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-700 border-t-blue-500"></div>
                        <span>Loading analyses...</span>
                      </div>
                    </td>
                  </tr>
                ) : filteredAnalyses.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <p className="text-sm text-slate-500">No analyses found</p>
                    </td>
                  </tr>
                ) : (
                  filteredAnalyses.map((analysis) => (
                    <tr
                      key={analysis.id}
                      className="cursor-pointer border-b border-slate-800 transition-colors hover:bg-slate-800"
                      onClick={() => router.push(`/audit-logs/${analysis.id}`)}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2 text-sm text-slate-300">
                          <Clock className="h-4 w-4 text-slate-500" />
                          <span>{formatTimestamp(analysis.timestamp)}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="rounded border border-slate-700 bg-slate-800 px-2 py-1 text-xs font-medium text-slate-300">
                          {analysis.inputType.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm font-semibold text-white">
                          {analysis.overallRiskScore}
                        </span>
                        <span className="text-xs text-slate-500">/100</span>
                      </td>
                      <td className="px-6 py-4">
                        <RiskBadge level={analysis.overallRiskLevel as RiskLevel} />
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-300">
                        {analysis.primaryAction}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-400">
                        {analysis.totalFindings} finding{analysis.totalFindings !== 1 ? "s" : ""}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
