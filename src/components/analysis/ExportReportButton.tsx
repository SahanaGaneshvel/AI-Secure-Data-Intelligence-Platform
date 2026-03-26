import React, { useState } from "react";
import { AnalysisResponse } from "@/lib/types";
import { Download, Copy, Check } from "lucide-react";

interface ExportReportButtonProps {
  analysis: AnalysisResponse;
}

export const ExportReportButton: React.FC<ExportReportButtonProps> = ({ analysis }) => {
  const [copied, setCopied] = useState(false);

  const handleCopyJSON = () => {
    const jsonString = JSON.stringify(analysis, null, 2);
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJSON = () => {
    const jsonString = JSON.stringify(analysis, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analysis-${analysis.id}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={handleCopyJSON}
        className="flex items-center gap-2 rounded border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-300 transition-colors hover:bg-slate-700"
      >
        {copied ? (
          <>
            <Check className="h-3 w-3 text-green-400" />
            <span className="text-green-400">Copied!</span>
          </>
        ) : (
          <>
            <Copy className="h-3 w-3" />
            <span>Copy JSON</span>
          </>
        )}
      </button>

      <button
        onClick={handleDownloadJSON}
        className="flex items-center gap-2 rounded border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-300 transition-colors hover:bg-slate-700"
      >
        <Download className="h-3 w-3" />
        <span>Download Report</span>
      </button>
    </div>
  );
};
