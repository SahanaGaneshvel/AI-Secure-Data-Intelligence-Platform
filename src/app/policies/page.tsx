"use client";

import React, { useState, useEffect } from "react";
import { TopNavbar } from "@/components/layout/TopNavbar";
import { Footer } from "@/components/layout/Footer";
import { PageHeader } from "@/components/shared/PageHeader";
import { Button } from "@/components/shared/Button";
import { getPolicy, updatePolicy as updatePolicyApi, resetPolicy, PolicyConfig, APIError } from "@/lib/api";
import { RefreshCw, AlertCircle, CheckCircle2, Shield } from "lucide-react";

export default function PoliciesPage() {
  const [policy, setPolicy] = useState<PolicyConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [resetting, setResetting] = useState(false);

  useEffect(() => {
    fetchPolicy();
  }, []);

  const fetchPolicy = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getPolicy();
      setPolicy(data);
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError("Backend unavailable");
      }
      console.error("Failed to fetch policy:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!policy) return;

    setSaving(true);
    setSaveSuccess(false);
    setError(null);

    try {
      const updatedPolicy = await updatePolicyApi(policy);
      setPolicy(updatedPolicy);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError("Failed to save policy");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Reset to default policy configuration?")) return;

    setResetting(true);
    setError(null);

    try {
      const defaultPolicy = await resetPolicy();
      setPolicy(defaultPolicy);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError("Failed to reset policy");
      }
    } finally {
      setResetting(false);
    }
  };

  const updatePolicy = (updates: Partial<PolicyConfig>) => {
    if (!policy) return;
    setPolicy({ ...policy, ...updates });
  };

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col bg-slate-950">
        <TopNavbar />
        <main className="flex flex-1 items-center justify-center">
          <div className="flex items-center gap-3 text-slate-400">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-700 border-t-blue-500"></div>
            <span>Loading policy configuration...</span>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error && !policy) {
    return (
      <div className="flex min-h-screen flex-col bg-slate-950">
        <TopNavbar />
        <main className="flex flex-1 items-center justify-center">
          <div className="text-center">
            <AlertCircle className="mx-auto mb-4 h-12 w-12 text-red-400" />
            <h2 className="mb-2 text-xl font-semibold text-red-400">Backend Unavailable</h2>
            <p className="mb-4 text-sm text-slate-500">{error}</p>
            <Button variant="primary" onClick={fetchPolicy}>
              Retry
            </Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!policy) {
    return null;
  }

  const enabledDetectorCount =
    policy.enabled_detectors === "all"
      ? 36
      : Array.isArray(policy.enabled_detectors)
      ? policy.enabled_detectors.length
      : 0;

  return (
    <div className="flex min-h-screen flex-col bg-slate-950">
      <TopNavbar />

      <main className="flex-1 p-6">
        <div className="mx-auto max-w-[1200px]">
          <PageHeader
            title="Policy Configuration"
            description="Configure analysis behavior, risk thresholds, and detection rules"
            action={
              <div className="flex gap-3">
                <Button
                  variant="secondary"
                  onClick={handleReset}
                  disabled={resetting || saving}
                >
                  <RefreshCw className={`h-4 w-4 ${resetting ? "animate-spin" : ""}`} />
                  Reset to Default
                </Button>
                <Button
                  variant="primary"
                  onClick={handleSave}
                  disabled={saving || resetting}
                >
                  {saving ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            }
          />

          {/* Success Message */}
          {saveSuccess && (
            <div className="mb-6 flex items-center gap-2 rounded-lg border border-green-900/50 bg-green-950/30 p-4 text-green-400">
              <CheckCircle2 className="h-5 w-5" />
              <span className="text-sm font-medium">Policy saved successfully</span>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 flex items-center gap-2 rounded-lg border border-red-900/50 bg-red-950/30 p-4 text-red-400">
              <AlertCircle className="h-5 w-5" />
              <span className="text-sm font-medium">{error}</span>
            </div>
          )}

          {/* Summary Cards */}
          <div className="mb-6 grid grid-cols-4 gap-4">
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <div className="mb-1 flex items-center gap-2">
                <Shield className="h-4 w-4 text-blue-400" />
                <p className="text-xs text-slate-400">Policy Name</p>
              </div>
              <p className="text-lg font-bold text-white capitalize">{policy.name}</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <p className="text-xs text-slate-400">Enabled Detectors</p>
              <p className="text-2xl font-bold text-blue-400">{enabledDetectorCount}</p>
              <p className="text-xs text-slate-500">
                {policy.enabled_detectors === "all" ? "All patterns" : "Selected patterns"}
              </p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <p className="text-xs text-slate-400">Critical Threshold</p>
              <p className="text-2xl font-bold text-red-400">{policy.critical_threshold}</p>
              <p className="text-xs text-slate-500">Risk score threshold</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
              <p className="text-xs text-slate-400">High Risk Threshold</p>
              <p className="text-2xl font-bold text-orange-400">{policy.high_threshold}</p>
              <p className="text-xs text-slate-500">Risk score threshold</p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Analysis Behavior */}
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-4 text-lg font-semibold text-white">Analysis Behavior</h3>
              <div className="space-y-4">
                <label className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={policy.block_high_risk}
                    onChange={(e) => updatePolicy({ block_high_risk: e.target.checked })}
                    className="mt-1 h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <div>
                    <span className="text-sm font-medium text-slate-300">
                      Block High-Risk Content
                    </span>
                    <p className="text-xs text-slate-500">
                      Automatically block content with high or critical risk scores
                    </p>
                  </div>
                </label>
                <label className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={policy.mask_all_secrets}
                    onChange={(e) => updatePolicy({ mask_all_secrets: e.target.checked })}
                    className="mt-1 h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <div>
                    <span className="text-sm font-medium text-slate-300">
                      Mask All Secrets
                    </span>
                    <p className="text-xs text-slate-500">
                      Automatically mask detected secrets, credentials, and tokens in output
                    </p>
                  </div>
                </label>
                <label className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={policy.auto_rotate_keys}
                    onChange={(e) => updatePolicy({ auto_rotate_keys: e.target.checked })}
                    className="mt-1 h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <div>
                    <span className="text-sm font-medium text-slate-300">
                      Auto-Rotate Keys (Future)
                    </span>
                    <p className="text-xs text-slate-500">
                      Automatically trigger key rotation for exposed credentials (not yet implemented)
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Alert Configuration */}
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-4 text-lg font-semibold text-white">Alert Configuration</h3>
              <div className="space-y-4">
                <label className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={policy.alert_on_critical}
                    onChange={(e) => updatePolicy({ alert_on_critical: e.target.checked })}
                    className="mt-1 h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <div>
                    <span className="text-sm font-medium text-slate-300">
                      Alert on Critical Findings
                    </span>
                    <p className="text-xs text-slate-500">
                      Generate alerts when critical security issues are detected
                    </p>
                  </div>
                </label>
              </div>
            </div>

            {/* Risk Thresholds */}
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-4 text-lg font-semibold text-white">Risk Thresholds</h3>
              <div className="space-y-4">
                <div>
                  <label className="mb-2 flex items-center justify-between text-sm font-medium text-slate-300">
                    <span>Critical Risk Threshold</span>
                    <span className="text-red-400">{policy.critical_threshold}</span>
                  </label>
                  <input
                    type="range"
                    min="70"
                    max="100"
                    value={policy.critical_threshold}
                    onChange={(e) =>
                      updatePolicy({ critical_threshold: parseInt(e.target.value) })
                    }
                    className="w-full"
                  />
                  <p className="mt-1 text-xs text-slate-500">
                    Risk scores above this value are classified as Critical
                  </p>
                </div>
                <div>
                  <label className="mb-2 flex items-center justify-between text-sm font-medium text-slate-300">
                    <span>High Risk Threshold</span>
                    <span className="text-orange-400">{policy.high_threshold}</span>
                  </label>
                  <input
                    type="range"
                    min="40"
                    max="85"
                    value={policy.high_threshold}
                    onChange={(e) => updatePolicy({ high_threshold: parseInt(e.target.value) })}
                    className="w-full"
                  />
                  <p className="mt-1 text-xs text-slate-500">
                    Risk scores above this value are classified as High
                  </p>
                </div>
              </div>
            </div>

            {/* Detector Configuration */}
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-4 text-lg font-semibold text-white">
                Detector Configuration
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-300">
                    Enabled Detectors
                  </label>
                  <div className="rounded border border-slate-800 bg-slate-950 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-white">
                          {policy.enabled_detectors === "all"
                            ? "All Detectors Enabled"
                            : `${enabledDetectorCount} Detectors Enabled`}
                        </p>
                        <p className="text-xs text-slate-500">
                          {policy.enabled_detectors === "all"
                            ? "All 36 detection patterns are active"
                            : "Custom detector selection"}
                        </p>
                      </div>
                      <span className="rounded bg-blue-900/30 px-2 py-1 text-xs font-medium text-blue-400">
                        {policy.enabled_detectors === "all" ? "ALL" : "CUSTOM"}
                      </span>
                    </div>
                  </div>
                  <p className="mt-2 text-xs text-slate-500">
                    Individual detector selection is managed through the backend policy API
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
