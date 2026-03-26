"use client";

import React, { useState } from "react";
import { TopNavbar } from "@/components/layout/TopNavbar";
import { Footer } from "@/components/layout/Footer";
import { AnalysisInputCard } from "@/components/analysis/AnalysisInputCard";
import { RiskSummaryCards } from "@/components/analysis/RiskSummaryCards";
import { FindingsTable } from "@/components/analysis/FindingsTable";
import { MaskedOutputViewer } from "@/components/analysis/MaskedOutputViewer";
import { AISecurityPanel } from "@/components/insights/AISecurityPanel";
import { RiskDistributionChart } from "@/components/charts/RiskDistributionChart";
import { AnalysisLoadingState } from "@/components/analysis/AnalysisLoadingState";
import { AnalysisMetadataCard } from "@/components/analysis/AnalysisMetadataCard";
import { ExportReportButton } from "@/components/analysis/ExportReportButton";
import { EmptyState } from "@/components/shared/EmptyState";
import { ErrorState } from "@/components/shared/ErrorState";
import { InputType, AnalysisOptions, AnalysisResponse, AnalysisState, Finding } from "@/lib/types";
import { mockInputSample } from "@/lib/mockData";
import { analyzeContent, uploadFile, APIError } from "@/lib/api";
import { Shield } from "lucide-react";

export default function AnalysisStudioPage() {
  const [analysisState, setAnalysisState] = useState<AnalysisState>("idle");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [highlightedLine, setHighlightedLine] = useState<number | undefined>();
  const [error, setError] = useState<string | null>(null);
  const [isBackendOffline, setIsBackendOffline] = useState(false);

  // Lift input state to parent to persist across layout changes
  const [userInput, setUserInput] = useState<string>(mockInputSample);
  const [inputType, setInputType] = useState<InputType>("text");
  const [analysisOptions, setAnalysisOptions] = useState<AnalysisOptions>({
    maskSensitiveData: true,
    blockHighRiskContent: false,
    advancedThreatDetection: true,
  });

  const handleAnalyze = async (
    input: string,
    inputType: InputType,
    options: AnalysisOptions
  ) => {
    try {
      setError(null);

      // Multi-stage analysis with real API
      setAnalysisState("validating");
      await new Promise((resolve) => setTimeout(resolve, 400));

      setAnalysisState("scanning");
      await new Promise((resolve) => setTimeout(resolve, 300));

      setAnalysisState("analyzing");

      // Call real backend API
      const result = await analyzeContent(input, inputType, options);

      setAnalysisState("generating");
      await new Promise((resolve) => setTimeout(resolve, 300));

      setAnalysisResult(result);
      setAnalysisState("complete");
    } catch (err) {
      setAnalysisState("error");
      if (err instanceof APIError) {
        setError(err.message);
        // Detect backend offline
        if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError") || err.message.includes("connect")) {
          setIsBackendOffline(true);
        }
      } else if (err instanceof TypeError && err.message.includes("fetch")) {
        setError("Cannot connect to backend server");
        setIsBackendOffline(true);
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
      console.error("Analysis failed:", err);
    }
  };

  const handleRetry = () => {
    setError(null);
    setIsBackendOffline(false);
    setAnalysisState("idle");
  };

  // Handle binary file uploads (PDF, DOCX) - sends to backend for real parsing
  const handleFileUpload = async (file: File, options: AnalysisOptions) => {
    try {
      setError(null);

      setAnalysisState("validating");
      await new Promise((resolve) => setTimeout(resolve, 300));

      setAnalysisState("scanning");
      await new Promise((resolve) => setTimeout(resolve, 200));

      setAnalysisState("analyzing");

      // Call real backend file upload API for PDF/DOCX parsing
      const result = await uploadFile(file, options);

      setAnalysisState("generating");
      await new Promise((resolve) => setTimeout(resolve, 200));

      setAnalysisResult(result);
      setAnalysisState("complete");
    } catch (err) {
      setAnalysisState("error");
      if (err instanceof APIError) {
        setError(err.message);
        if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError") || err.message.includes("connect")) {
          setIsBackendOffline(true);
        }
      } else if (err instanceof TypeError && err.message.includes("fetch")) {
        setError("Cannot connect to backend server");
        setIsBackendOffline(true);
      } else {
        setError("File upload failed. Please try again.");
      }
      console.error("File upload failed:", err);
    }
  };

  const handleFindingClick = (finding: Finding) => {
    if (finding.line) {
      setHighlightedLine(finding.line);
    }
  };

  const isAnalyzing =
    analysisState === "validating" ||
    analysisState === "scanning" ||
    analysisState === "analyzing" ||
    analysisState === "generating";

  const showResults = analysisState === "complete" && analysisResult;

  return (
    <div className="flex min-h-screen flex-col bg-slate-950">
      <TopNavbar />

      <main className="flex-1 p-6">
        <div className="mx-auto max-w-[1800px]">
          {/* Error State */}
          {error && (
            <div className="mb-6">
              <ErrorState
                title={isBackendOffline ? "Backend Server Offline" : "Analysis Failed"}
                message={error}
                type={isBackendOffline ? "offline" : "error"}
                onRetry={handleRetry}
                actionLabel="Dismiss"
              />
            </div>
          )}

          {/* Layout: Before Analysis (Input Dominant) */}
          {!showResults && !isAnalyzing && (
            <div className="grid grid-cols-12 gap-6">
              <div className="col-span-8">
                <AnalysisInputCard
                  onAnalyze={handleAnalyze}
                  onFileUpload={handleFileUpload}
                  isAnalyzing={isAnalyzing}
                  input={userInput}
                  onInputChange={setUserInput}
                  inputType={inputType}
                  onInputTypeChange={setInputType}
                  options={analysisOptions}
                  onOptionsChange={setAnalysisOptions}
                />
              </div>
              <div className="col-span-4">
                <EmptyState
                  title="No analysis results yet"
                  description="Submit your data using the input panel to start security analysis"
                  icon={<Shield />}
                />
              </div>
            </div>
          )}

          {/* Loading State */}
          {isAnalyzing && (
            <div className="grid grid-cols-12 gap-6">
              <div className="col-span-8">
                <AnalysisInputCard
                  onAnalyze={handleAnalyze}
                  onFileUpload={handleFileUpload}
                  isAnalyzing={isAnalyzing}
                  input={userInput}
                  onInputChange={setUserInput}
                  inputType={inputType}
                  onInputTypeChange={setInputType}
                  options={analysisOptions}
                  onOptionsChange={setAnalysisOptions}
                />
                <div className="mt-6">
                  <AnalysisLoadingState state={analysisState} />
                </div>
              </div>
              <div className="col-span-4">
                <EmptyState
                  title="Analysis in progress"
                  description="Please wait while we analyze your data for security threats"
                  icon={<Shield />}
                />
              </div>
            </div>
          )}

          {/* Layout: After Analysis (Full 3-Column) */}
          {showResults && (
            <>
              <div className="grid grid-cols-12 gap-6">
                {/* Left: Input Panel */}
                <div className="col-span-3">
                  <AnalysisInputCard
                    onAnalyze={handleAnalyze}
                    onFileUpload={handleFileUpload}
                    isAnalyzing={isAnalyzing}
                    input={userInput}
                    onInputChange={setUserInput}
                    inputType={inputType}
                    onInputTypeChange={setInputType}
                    options={analysisOptions}
                    onOptionsChange={setAnalysisOptions}
                  />
                </div>

                {/* Center + Right: Results */}
                <div className="col-span-9">
                  {/* Summary Cards */}
                  <div className="mb-6">
                    <RiskSummaryCards
                      overallRiskScore={analysisResult.overallRiskScore}
                      overallRiskLevel={analysisResult.overallRiskLevel}
                      primaryAction={analysisResult.primaryAction}
                      totalFindings={analysisResult.totalFindings}
                    />
                  </div>

                  {/* Metadata Card + Export */}
                  <div className="mb-6 flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <AnalysisMetadataCard metadata={analysisResult.metadata} />
                    </div>
                    <ExportReportButton analysis={analysisResult} />
                  </div>

                  <div className="grid grid-cols-12 gap-6">
                    {/* Center Column: Findings + Output */}
                    <div className="col-span-8 space-y-6">
                      <FindingsTable
                        findings={analysisResult.findings}
                        onFindingClick={handleFindingClick}
                        selectedFindingId={
                          analysisResult.findings.find((f) => f.line === highlightedLine)?.id
                        }
                      />
                      <MaskedOutputViewer
                        output={analysisResult.maskedOutput}
                        highlightedLine={highlightedLine}
                        findings={analysisResult.findings}
                      />
                    </div>

                    {/* Right Column: AI Insights + Chart */}
                    <div className="col-span-4 space-y-6">
                      <AISecurityPanel
                        contextSummary={analysisResult.aiSummary}
                        criticalVulnerabilities={analysisResult.criticalVulnerabilities}
                        behavioralAnomalies={analysisResult.behavioralAnomalies}
                        recommendedActions={analysisResult.recommendedActions}
                        riskScoreBreakdown={analysisResult.riskScoreBreakdown}
                      />
                      <RiskDistributionChart distribution={analysisResult.riskDistribution} />
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
