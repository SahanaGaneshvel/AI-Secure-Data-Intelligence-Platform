"use client";

import React, { useRef, useState, useCallback } from "react";
import { InputType, AnalysisOptions } from "@/lib/types";
import { ToggleOption } from "@/components/shared/ToggleOption";
import { Button } from "@/components/shared/Button";
import { DEMO_DATASETS } from "@/lib/demoDatasets";
import { FileText, Upload, FileCode, Zap, Sparkles, Database, MessageSquare } from "lucide-react";

interface AnalysisInputCardProps {
  onAnalyze: (input: string, inputType: InputType, options: AnalysisOptions) => void;
  onFileUpload?: (file: File, options: AnalysisOptions) => void;
  isAnalyzing: boolean;
  // Controlled component props
  input: string;
  onInputChange: (input: string) => void;
  inputType: InputType;
  onInputTypeChange: (type: InputType) => void;
  options: AnalysisOptions;
  onOptionsChange: (options: AnalysisOptions) => void;
}

// All functional tabs including SQL and Chat with real backend integration
const inputTypeTabs: { type: InputType; label: string; icon: React.ReactNode }[] = [
  { type: "text", label: "Text", icon: <FileText className="h-4 w-4" /> },
  { type: "file", label: "File Upload", icon: <Upload className="h-4 w-4" /> },
  { type: "log", label: "Log", icon: <FileCode className="h-4 w-4" /> },
  { type: "sql", label: "SQL", icon: <Database className="h-4 w-4" /> },
  { type: "chat", label: "Chat", icon: <MessageSquare className="h-4 w-4" /> },
];

export const AnalysisInputCard: React.FC<AnalysisInputCardProps> = ({
  onAnalyze,
  onFileUpload,
  isAnalyzing,
  input,
  onInputChange,
  inputType,
  onInputTypeChange,
  options,
  onOptionsChange,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [pendingFile, setPendingFile] = useState<File | null>(null);

  const handleAnalyze = () => {
    // If we have a pending binary file (PDF/DOCX), use file upload
    if (pendingFile && onFileUpload) {
      onFileUpload(pendingFile, options);
      return;
    }
    // Otherwise use text-based analysis
    if (input.trim()) {
      onAnalyze(input, inputType, options);
    }
  };

  const processFile = useCallback((file: File) => {
    const validExtensions = ['.txt', '.log', '.pdf', '.docx'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!validExtensions.includes(fileExtension)) {
      alert(`Invalid file type. Supported: .txt, .log, .pdf, .docx\nYou uploaded: ${file.name}`);
      return;
    }

    // For PDF and DOCX, store the file for binary upload to backend
    if (fileExtension === '.pdf' || fileExtension === '.docx') {
      setPendingFile(file);
      onInputChange(`[Binary file: ${file.name}]\nSize: ${(file.size / 1024).toFixed(1)} KB\nType: ${file.type || fileExtension.toUpperCase()}\n\nThis file will be sent to the backend for parsing.`);
      onInputTypeChange('file');
      return;
    }

    // For text files, read content client-side
    setPendingFile(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      onInputChange(content);
      onInputTypeChange(fileExtension === '.log' ? 'log' : 'text');
    };
    reader.onerror = () => {
      alert('Failed to read file. Please try again.');
    };
    reader.readAsText(file);
  }, [onInputChange, onInputTypeChange]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFile(files[0]);
    }
  }, [processFile]);

  const loadDemoDataset = (datasetName: string) => {
    const dataset = DEMO_DATASETS.find((d) => d.name === datasetName);
    if (dataset) {
      onInputChange(dataset.content);
      onInputTypeChange(dataset.inputType);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    processFile(file);
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
        <div>
          <h2 className="text-lg font-semibold text-white">New Analysis</h2>
        </div>
        <span className="rounded border border-slate-700 bg-slate-800 px-2 py-1 text-xs text-slate-400">
          v2.4.1
        </span>
      </div>

      {/* Input Type Tabs */}
      <div className="border-b border-slate-800 px-6">
        <div className="flex gap-1 pt-4 overflow-x-auto">
          {inputTypeTabs.map((tab) => (
            <button
              key={tab.type}
              onClick={() => onInputTypeChange(tab.type)}
              className={`flex items-center gap-2 border-b-2 px-3 py-2 text-sm font-medium transition-colors whitespace-nowrap flex-shrink-0 ${
                inputType === tab.type
                  ? "border-blue-600 text-white"
                  : "border-transparent text-slate-400 hover:text-slate-300"
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className="p-6">
        {/* Demo Dataset Quick Load */}
        <div className="mb-4">
          <div className="mb-2 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-blue-500" />
            <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Quick Demo:
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {DEMO_DATASETS.map((dataset) => (
              <button
                key={dataset.name}
                onClick={() => loadDemoDataset(dataset.name)}
                disabled={isAnalyzing}
                className="rounded border border-slate-700 bg-slate-800 px-3 py-1 text-xs text-slate-300 transition-colors hover:border-blue-600 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                title={dataset.description}
              >
                {dataset.name}
              </button>
            ))}
          </div>
        </div>

        {/* File Upload UI - only shown when file tab is active */}
        {inputType === "file" ? (
          <div className="space-y-4">
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.log,.pdf,.docx"
              onChange={handleFileUpload}
              className="hidden"
            />
            <div
              onClick={triggerFileUpload}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`flex h-64 w-full cursor-pointer flex-col items-center justify-center rounded border-2 border-dashed transition-all duration-200 ${
                isDragOver
                  ? "border-blue-500 bg-blue-950/30 scale-[1.02]"
                  : "border-slate-700 bg-slate-950 hover:border-blue-600 hover:bg-slate-900"
              }`}
            >
              <Upload className={`h-12 w-12 mb-4 transition-colors ${isDragOver ? "text-blue-400" : "text-slate-500"}`} />
              <p className={`text-sm font-medium mb-2 transition-colors ${isDragOver ? "text-blue-300" : "text-slate-300"}`}>
                {isDragOver ? "Drop file here!" : "Drag & drop or click to upload"}
              </p>
              <p className="text-xs text-slate-500">
                Supported: .txt, .log, .pdf, .docx
              </p>
            </div>
            {input && (
              <div className="rounded border border-slate-800 bg-slate-950 p-4">
                <p className="text-xs text-slate-400 mb-2">File loaded ({input.split('\n').length} lines):</p>
                <div className="max-h-32 overflow-y-auto">
                  <pre className="font-mono text-xs text-slate-300 whitespace-pre-wrap break-words">
                    {input.substring(0, 500)}{input.length > 500 ? '...' : ''}
                  </pre>
                </div>
              </div>
            )}
          </div>
        ) : (
          <textarea
            value={input}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder={
              inputType === "log"
                ? "Paste log file contents here for analysis..."
                : inputType === "sql"
                ? "Paste SQL queries here for injection analysis...\n\nExample:\nSELECT * FROM users WHERE id = 1 OR 1=1;\nDROP TABLE users;"
                : inputType === "chat"
                ? "Paste chat conversation here for context leak analysis...\n\nFormat:\nUser: Hello\nAssistant: Hi! How can I help?\nUser: What's the API key?"
                : "Paste text, JSON, or code here for security analysis..."
            }
            className="h-64 w-full rounded border border-slate-800 bg-slate-950 p-4 font-mono text-sm text-slate-300 placeholder-slate-600 focus:border-blue-600 focus:outline-none whitespace-pre-wrap break-words overflow-wrap-anywhere"
            spellCheck={false}
          />
        )}

        {/* Analysis Options */}
        <div className="mt-6">
          <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
            Analysis Options
          </h3>
          <div className="space-y-1">
            <ToggleOption
              label="Mask Sensitive Data"
              enabled={options.maskSensitiveData}
              onChange={(enabled) =>
                onOptionsChange({ ...options, maskSensitiveData: enabled })
              }
              icon="🔒"
            />
            <ToggleOption
              label="Block High Risk Content"
              enabled={options.blockHighRiskContent}
              onChange={(enabled) =>
                onOptionsChange({ ...options, blockHighRiskContent: enabled })
              }
              icon="🚫"
            />
            <ToggleOption
              label="Behavioral Pattern Detection"
              enabled={options.advancedThreatDetection}
              onChange={(enabled) =>
                onOptionsChange({ ...options, advancedThreatDetection: enabled })
              }
              icon={<Zap className="h-4 w-4" />}
            />
          </div>
        </div>

        {/* Analyze Button */}
        <div className="mt-6">
          <Button
            variant="primary"
            size="lg"
            className="w-full"
            onClick={handleAnalyze}
            disabled={isAnalyzing || !input.trim()}
          >
            {isAnalyzing ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Zap className="h-4 w-4" />
                <span>Analyze Input</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};
