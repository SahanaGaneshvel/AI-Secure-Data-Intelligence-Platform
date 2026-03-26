"use client";

import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from "recharts";

interface RiskDistributionChartProps {
  distribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
}

const COLORS = {
  low: "#3b82f6", // blue-500
  medium: "#eab308", // yellow-500
  high: "#f97316", // orange-500
  critical: "#ef4444", // red-500
};

export const RiskDistributionChart: React.FC<RiskDistributionChartProps> = ({
  distribution,
}) => {
  const data = [
    { name: "Low", value: distribution.low, color: COLORS.low },
    { name: "Medium", value: distribution.medium, color: COLORS.medium },
    { name: "High", value: distribution.high, color: COLORS.high },
    { name: "Critical", value: distribution.critical, color: COLORS.critical },
  ].filter((item) => item.value > 0);

  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
      <h3 className="mb-6 text-base font-semibold text-white">Risk Distribution</h3>

      <div className="flex items-center justify-center">
        <div className="relative h-64 w-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-bold text-white">{total}</span>
            <span className="text-sm text-slate-400">Total</span>
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-3">
        {data.map((item) => (
          <div key={item.name} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span
                className="h-3 w-3 rounded-full"
                style={{ backgroundColor: item.color }}
              ></span>
              <span className="text-sm text-slate-400">{item.name}</span>
            </div>
            <span className="text-sm font-medium text-slate-200">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
