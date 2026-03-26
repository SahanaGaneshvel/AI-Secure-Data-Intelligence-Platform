import React from "react";
import { DetectorType } from "@/lib/types";

interface DetectorBadgeProps {
  type: DetectorType;
}

const detectorIcons: Record<DetectorType, string> = {
  Regex: "</> ",
  Heuristic: "🎯 ",
  NLP: "🧠 ",
  AI: "✨ ",
};

export const DetectorBadge: React.FC<DetectorBadgeProps> = ({ type }) => {
  return (
    <span className="inline-flex items-center gap-1 text-xs text-slate-400">
      <span>{detectorIcons[type]}</span>
      <span>{type}</span>
    </span>
  );
};
