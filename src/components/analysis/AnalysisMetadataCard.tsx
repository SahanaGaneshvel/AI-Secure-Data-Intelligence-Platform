import React from "react";
import { AnalysisMetadata } from "@/lib/types";
import { Clock, FileText, Zap, HardDrive } from "lucide-react";

interface AnalysisMetadataCardProps {
  metadata: AnalysisMetadata;
}

export const AnalysisMetadataCard: React.FC<AnalysisMetadataCardProps> = ({ metadata }) => {
  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
        Analysis Metadata
      </h3>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-blue-500" />
          <div>
            <p className="text-xs text-slate-500">Processing Time</p>
            <p className="text-sm font-semibold text-white">{metadata.processingTimeMs}ms</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-green-500" />
          <div>
            <p className="text-xs text-slate-500">Lines Scanned</p>
            <p className="text-sm font-semibold text-white">{metadata.linesScanned}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Zap className="h-4 w-4 text-yellow-500" />
          <div>
            <p className="text-xs text-slate-500">Detectors Used</p>
            <p className="text-sm font-semibold text-white">{metadata.detectorsTriggered}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <HardDrive className="h-4 w-4 text-purple-500" />
          <div>
            <p className="text-xs text-slate-500">Input Size</p>
            <p className="text-sm font-semibold text-white">{formatBytes(metadata.inputSizeBytes)}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
