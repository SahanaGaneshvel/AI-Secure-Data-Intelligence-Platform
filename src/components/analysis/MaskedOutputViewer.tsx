"use client";

import React, { useEffect, useRef, useState } from "react";
import { Finding } from "@/lib/types";
import { Copy, Maximize2, AlertTriangle } from "lucide-react";

interface MaskedOutputViewerProps {
  output: string[];
  highlightedLine?: number;
  findings?: Finding[];
}

const MAX_LINES_DISPLAY = 1000; // Prevent UI freeze with large logs

export const MaskedOutputViewer: React.FC<MaskedOutputViewerProps> = ({
  output,
  highlightedLine,
  findings = [],
}) => {
  const lineRefs = useRef<{ [key: number]: HTMLDivElement | null }>({});
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [showTruncationWarning, setShowTruncationWarning] = useState(false);

  const displayedOutput = output.slice(0, MAX_LINES_DISPLAY);
  const isTruncated = output.length > MAX_LINES_DISPLAY;

  // Create a map of line numbers to findings for efficient lookup
  const lineToFindings = findings.reduce((acc, finding) => {
    if (finding.line) {
      if (!acc[finding.line]) {
        acc[finding.line] = [];
      }
      acc[finding.line].push(finding);
    }
    return acc;
  }, {} as Record<number, Finding[]>);

  // Get the highest risk level for a line
  const getLineRiskLevel = (lineNumber: number): string | null => {
    const lineFindings = lineToFindings[lineNumber];
    if (!lineFindings || lineFindings.length === 0) return null;

    const riskPriority = { Critical: 4, High: 3, Medium: 2, Low: 1 };
    const highestRisk = lineFindings.reduce((highest, finding) => {
      return (riskPriority[finding.risk] || 0) > (riskPriority[highest] || 0)
        ? finding.risk
        : highest;
    }, lineFindings[0].risk);

    return highestRisk;
  };

  // Get risk color for a line
  const getRiskColor = (risk: string): string => {
    switch (risk) {
      case "Critical": return "text-red-400";
      case "High": return "text-orange-400";
      case "Medium": return "text-yellow-400";
      case "Low": return "text-blue-400";
      default: return "text-slate-400";
    }
  };

  // Get risk background for a line
  const getRiskBackground = (risk: string): string => {
    switch (risk) {
      case "Critical": return "bg-red-500/5";
      case "High": return "bg-orange-500/5";
      case "Medium": return "bg-yellow-500/5";
      case "Low": return "bg-blue-500/5";
      default: return "";
    }
  };

  useEffect(() => {
    setShowTruncationWarning(isTruncated);
  }, [isTruncated]);

  useEffect(() => {
    if (highlightedLine && lineRefs.current[highlightedLine]) {
      // Ensure the highlighted line is within visible range
      if (highlightedLine <= MAX_LINES_DISPLAY) {
        lineRefs.current[highlightedLine]?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
      }
    }
  }, [highlightedLine]);

  const handleCopy = () => {
    const textToCopy = displayedOutput.join('\n');
    navigator.clipboard.writeText(textToCopy);
  };

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 px-6 py-3">
        <div className="flex items-center gap-4">
          <h3 className="text-sm font-semibold text-white">Masked Output View</h3>
          <div className="flex items-center gap-2 text-xs">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-red-500"></span>
              <span className="text-slate-400">Critical</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-orange-500"></span>
              <span className="text-slate-400">High</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-blue-500"></span>
              <span className="text-slate-400">Info</span>
            </span>
            {isTruncated && (
              <span className="flex items-center gap-1 ml-2">
                <AlertTriangle className="h-3 w-3 text-yellow-500" />
                <span className="text-slate-400">Showing first {MAX_LINES_DISPLAY} lines</span>
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="rounded p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-300"
            title="Copy to clipboard"
          >
            <Copy className="h-4 w-4" />
          </button>
          <button className="rounded p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-300">
            <Maximize2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Truncation Warning Banner */}
      {showTruncationWarning && (
        <div className="border-b border-yellow-800/50 bg-yellow-950/30 px-6 py-2">
          <div className="flex items-center gap-2 text-xs text-yellow-400">
            <AlertTriangle className="h-4 w-4" />
            <span>
              Large output detected. Displaying first {MAX_LINES_DISPLAY} of {output.length} lines to maintain performance.
              All findings are still detected.
            </span>
          </div>
        </div>
      )}

      {/* Code Viewer */}
      <div ref={containerRef} className="overflow-x-auto bg-slate-950 p-4 max-h-[600px] overflow-y-auto">
        <div className="font-mono text-sm">
          {displayedOutput.map((line, index) => {
            const lineNumber = index + 1;
            const isHighlighted = lineNumber === highlightedLine;
            const lineRisk = getLineRiskLevel(lineNumber);
            const lineFindings = lineToFindings[lineNumber] || [];
            const hasFindings = lineFindings.length > 0;

            return (
              <div
                key={lineNumber}
                ref={(el) => {
                  if (el) lineRefs.current[lineNumber] = el;
                }}
                className={`flex transition-colors ${
                  isHighlighted
                    ? "bg-blue-500/10"
                    : lineRisk
                    ? getRiskBackground(lineRisk)
                    : ""
                }`}
              >
                <span
                  className={`mr-6 inline-block w-8 select-none text-right text-slate-600 ${
                    isHighlighted ? "text-blue-400" : ""
                  }`}
                >
                  {lineNumber}
                </span>
                <span
                  className={`flex-1 ${
                    hasFindings ? "text-slate-300" : "text-slate-400"
                  }`}
                >
                  {line}
                </span>
                {hasFindings && lineFindings.length === 1 && (
                  <span className={`ml-4 text-xs ${getRiskColor(lineFindings[0].risk)}`}>
                    ← {lineFindings[0].risk}: {lineFindings[0].type}
                  </span>
                )}
                {hasFindings && lineFindings.length > 1 && (
                  <span className={`ml-4 text-xs ${getRiskColor(lineRisk!)}`}>
                    ← {lineFindings.length} findings ({lineRisk})
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
