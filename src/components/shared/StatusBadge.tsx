import React from "react";
import { PolicyStatus, AuditLogStatus } from "@/lib/types";

interface StatusBadgeProps {
  status: PolicyStatus | AuditLogStatus;
  size?: "sm" | "md";
}

const statusStyles: Record<PolicyStatus | AuditLogStatus, string> = {
  active: "bg-green-500/10 text-green-400 border-green-500/20",
  inactive: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  success: "bg-green-500/10 text-green-400 border-green-500/20",
  failed: "bg-red-500/10 text-red-400 border-red-500/20",
  blocked: "bg-orange-500/10 text-orange-400 border-orange-500/20",
};

const sizeStyles = {
  sm: "text-[10px] px-1.5 py-0.5",
  md: "text-xs px-2 py-1",
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = "sm" }) => {
  return (
    <span
      className={`inline-flex items-center rounded border font-medium uppercase ${statusStyles[status]} ${sizeStyles[size]}`}
    >
      {status}
    </span>
  );
};
