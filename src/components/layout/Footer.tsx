import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800 bg-slate-950 px-6 py-4">
      <div className="flex items-center justify-between">
        <p className="text-xs text-slate-500">
          © 2026 SecureData AI Platform. All rights reserved.
        </p>
        <div className="flex items-center gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-green-500"></span>
            System Operational
          </span>
          <a href="#" className="hover:text-slate-400">
            Documentation
          </a>
          <a href="#" className="hover:text-slate-400">
            API Support
          </a>
        </div>
      </div>
    </footer>
  );
};
