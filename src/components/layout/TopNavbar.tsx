"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Search, Bell } from "lucide-react";

export const TopNavbar: React.FC = () => {
  const pathname = usePathname();

  return (
    <nav className="border-b border-slate-800 bg-slate-950">
      <div className="flex h-14 items-center justify-between px-6">
        {/* Left: Brand + Navigation */}
        <div className="flex items-center gap-8">
          {/* Brand */}
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded bg-blue-600">
              <svg
                className="h-5 w-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
            </div>
            <span className="text-sm font-semibold text-white">SecureData AI</span>
          </Link>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-1">
            <NavTab href="/" label="Analysis Studio" active={pathname === "/"} />
            <NavTab href="/policies" label="Policies" active={pathname === "/policies"} />
            <NavTab href="/audit-logs" label="Audit Logs" active={pathname === "/audit-logs"} />
          </div>
        </div>

        {/* Right: Search + Notifications + User */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search resources..."
              className="h-9 w-64 rounded border border-slate-800 bg-slate-900 pl-9 pr-3 text-sm text-slate-300 placeholder-slate-500 focus:border-blue-600 focus:outline-none"
            />
          </div>

          {/* Notifications */}
          <button className="relative rounded p-2 hover:bg-slate-800">
            <Bell className="h-5 w-5 text-slate-400" />
            <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-red-500"></span>
          </button>

          {/* User Avatar */}
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-medium text-white">
            JD
          </div>
        </div>
      </div>
    </nav>
  );
};

interface NavTabProps {
  href: string;
  label: string;
  active?: boolean;
}

const NavTab: React.FC<NavTabProps> = ({ href, label, active }) => {
  return (
    <Link
      href={href}
      className={`relative px-3 py-2 text-sm font-medium transition-colors ${
        active
          ? "text-white after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-blue-600"
          : "text-slate-400 hover:text-slate-300"
      }`}
    >
      {label}
    </Link>
  );
};
