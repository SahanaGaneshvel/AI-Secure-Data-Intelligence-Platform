"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { TopNavbar } from "@/components/layout/TopNavbar";
import { Footer } from "@/components/layout/Footer";
import { RiskSummaryCards } from "@/components/analysis/RiskSummaryCards";
import { FindingsTable } from "@/components/analysis/FindingsTable";
import { MaskedOutputViewer } from "@/components/analysis/MaskedOutputViewer";
import { AISecurityPanel } from "@/components/insights/AISecurityPanel";
import { RiskDistributionChart } from "@/components/charts/RiskDistributionChart";
import { AnalysisMetadataCard } from "@/components/analysis/AnalysisMetadataCard";
import { AnalysisResponse, Finding } from "@/lib/types";
import { getAnalysisById, APIError } from "@/lib/api";
import { ArrowLeft, Clock, Calendar } from "lucide-react";

type AnalysisWithTimestamp = AnalysisResponse & { timestamp?: string };

export default function AnalysisDetailPage() {
  const params = useParams();
  const router = useRouter();
  const analysisId = params.id as string;

  const [analysis, setAnalysis] = useState<AnalysisWithTimestamp | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [highlightedLine, setHighlightedLine] = useState<number | undefined>();

  useEffect(() => {
    fetchAnalysis();
  }, [analysisId]);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAnalysisById(analysisId);
      setAnalysis(data);
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError("Failed to load analysis");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFindingClick = (finding: Finding) => {
    if (finding.line) {
      setHighlightedLine(finding.line);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col bg-slate-950">
        <TopNavbar />
        <main className="flex flex-1 items-center justify-center">
          <div className="flex items-center gap-3 text-slate-400">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-700 border-t-blue-500"></div>
            <span>Loading analysis...</span>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="flex min-h-screen flex-col bg-slate-950">
        <TopNavbar />
        <main className="flex flex-1 items-center justify-center">
          <div className="text-center">
            <h2 className="mb-2 text-xl font-semibold text-red-400">Analysis Not Found</h2>
            <p className="mb-4 text-sm text-slate-500">{error || "The requested analysis could not be found."}</p>
            <button
              onClick={() => router.push("/audit-logs")}
              className="rounded border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300 hover:bg-slate-700"
            >
              Back to Audit Logs
            </button>
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
          {/* Header with Back Button */}
          <div className="mb-6 flex items-center justify-between">
            <div>
              <button
                onClick={() => router.push("/audit-logs")}
                className="mb-2 flex items-center gap-2 text-sm text-slate-400 hover:text-slate-300"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Audit Logs
              </button>
              <h1 className="text-2xl font-bold text-white">Analysis Detail</h1>
              <div className="mt-1 flex flex-wrap items-center gap-4 text-sm text-slate-400">
                <span className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  ID: {analysisId}
                </span>
                {analysis.timestamp && (
                  <span className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    {new Date(analysis.timestamp).toLocaleString()}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Summary Cards */}
          <div className="mb-6">
            <RiskSummaryCards
              overallRiskScore={analysis.overallRiskScore}
              overallRiskLevel={analysis.overallRiskLevel}
              primaryAction={analysis.primaryAction}
              totalFindings={analysis.totalFindings}
            />
          </div>

          {/* Metadata Card */}
          {analysis.metadata && (
            <div className="mb-6">
              <AnalysisMetadataCard metadata={analysis.metadata} />
            </div>
          )}

          {/* Main Content Grid */}
          <div className="grid grid-cols-12 gap-6">
            {/* Left Column: Findings + Output */}
            <div className="col-span-8 space-y-6">
              <FindingsTable
                findings={analysis.findings}
                onFindingClick={handleFindingClick}
                selectedFindingId={
                  analysis.findings.find((f) => f.line === highlightedLine)?.id
                }
              />
              <MaskedOutputViewer
                output={analysis.maskedOutput}
                highlightedLine={highlightedLine}
              />
            </div>

            {/* Right Column: AI Insights + Chart */}
            <div className="col-span-4 space-y-6">
              <AISecurityPanel
                contextSummary={analysis.aiSummary}
                criticalVulnerabilities={analysis.criticalVulnerabilities}
                behavioralAnomalies={analysis.behavioralAnomalies}
                recommendedActions={analysis.recommendedActions}
                riskScoreBreakdown={analysis.riskScoreBreakdown}
              />
              <RiskDistributionChart distribution={analysis.riskDistribution} />
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
