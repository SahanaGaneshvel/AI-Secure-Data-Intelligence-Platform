"use client";

import React from "react";
import { AlertCircle, RefreshCw, Settings } from "lucide-react";

interface ErrorStateProps {
  title?: string;
  message: string;
  type?: "error" | "warning" | "offline";
  onRetry?: () => void;
  actionLabel?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Something went wrong",
  message,
  type = "error",
  onRetry,
  actionLabel = "Try Again",
}) => {
  const colors = {
    error: {
      bg: "bg-red-950/50",
      border: "border-red-800",
      icon: "text-red-400",
      title: "text-red-300",
      text: "text-red-400",
    },
    warning: {
      bg: "bg-yellow-950/50",
      border: "border-yellow-800",
      icon: "text-yellow-400",
      title: "text-yellow-300",
      text: "text-yellow-400",
    },
    offline: {
      bg: "bg-slate-900",
      border: "border-slate-700",
      icon: "text-slate-400",
      title: "text-slate-300",
      text: "text-slate-400",
    },
  };

  const colorScheme = colors[type];

  return (
    <div
      className={`rounded-lg border ${colorScheme.border} ${colorScheme.bg} p-6`}
    >
      <div className="flex items-start gap-4">
        <AlertCircle className={`h-6 w-6 flex-shrink-0 ${colorScheme.icon}`} />
        <div className="flex-1">
          <h3 className={`mb-1 text-base font-semibold ${colorScheme.title}`}>
            {title}
          </h3>
          <p className={`text-sm ${colorScheme.text}`}>{message}</p>

          {type === "offline" && (
            <div className="mt-3 space-y-2 text-xs text-slate-500">
              <p>Common issues:</p>
              <ul className="ml-4 list-disc space-y-1">
                <li>Backend server is not running (run: python run.py)</li>
                <li>Backend is running on a different port (check: http://localhost:8000)</li>
                <li>CORS configuration issue</li>
              </ul>
            </div>
          )}

          {onRetry && (
            <div className="mt-4 flex gap-3">
              <button
                onClick={onRetry}
                className="flex items-center gap-2 rounded border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300 transition-colors hover:bg-slate-700"
              >
                <RefreshCw className="h-4 w-4" />
                <span>{actionLabel}</span>
              </button>
              {type === "offline" && (
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 rounded border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300 transition-colors hover:bg-slate-700"
                >
                  <Settings className="h-4 w-4" />
                  <span>Check Backend</span>
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
