import React from "react";

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = "No analysis results yet",
  description = "Run an analysis to see results",
  icon,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {icon && <div className="mb-4 text-6xl text-slate-700">{icon}</div>}
      <h3 className="mb-2 text-lg font-medium text-slate-400">{title}</h3>
      <p className="text-sm text-slate-500">{description}</p>
    </div>
  );
};
