import React from "react";
import { RiskLevel } from "@/lib/types";

interface RiskBadgeProps {
  level: RiskLevel;
  size?: "sm" | "md" | "lg";
}

const riskStyles: Record<RiskLevel, string> = {
  Low: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  Medium: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  High: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  Critical: "bg-red-500/10 text-red-400 border-red-500/20",
};

const sizeStyles = {
  sm: "text-[10px] px-1.5 py-0.5",
  md: "text-xs px-2 py-1",
  lg: "text-sm px-3 py-1.5",
};

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = "md" }) => {
  return (
    <span
      className={`inline-flex items-center rounded border font-medium uppercase ${riskStyles[level]} ${sizeStyles[size]}`}
    >
      {level}
    </span>
  );
};
