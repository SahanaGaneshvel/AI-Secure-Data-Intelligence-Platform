"use client";

import React, { useState, useEffect } from "react";
import { TopNavbar } from "@/components/layout/TopNavbar";
import { Footer } from "@/components/layout/Footer";
import { PageHeader } from "@/components/shared/PageHeader";
import { Button } from "@/components/shared/Button";
import { getSettings, updateSettings, resetSettings, APIError } from "@/lib/api";
import { UserSettings, InputType } from "@/lib/types";
import { Eye, EyeOff, AlertCircle, CheckCircle2, RefreshCw } from "lucide-react";

export default function SettingsPage() {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getSettings();
      setSettings(data);
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError("Failed to load settings. Backend may be unavailable.");
      }
      console.error("Failed to fetch settings:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;

    setSaving(true);
    setSaveSuccess(false);
    setError(null);

    try {
      const updatedSettings = await updateSettings(settings);
      setSettings(updatedSettings);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError("Failed to save settings");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Reset all settings to default values?")) return;

    setResetting(true);
    setError(null);

    try {
      const defaultSettings = await resetSettings();
      setSettings(defaultSettings);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      if (err instanceof APIError) {
        setError(err.message);
      } else {
        setError("Failed to reset settings");
      }
    } finally {
      setResetting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col bg-slate-950">
        <TopNavbar />
        <main className="flex flex-1 items-center justify-center">
          <div className="flex items-center gap-3 text-slate-400">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-slate-700 border-t-blue-500"></div>
            <span>Loading settings...</span>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error && !settings) {
    return (
      <div className="flex min-h-screen flex-col bg-slate-950">
        <TopNavbar />
        <main className="flex flex-1 items-center justify-center">
          <div className="text-center">
            <AlertCircle className="mx-auto mb-4 h-12 w-12 text-red-400" />
            <h2 className="mb-2 text-xl font-semibold text-red-400">Backend Unavailable</h2>
            <p className="mb-4 text-sm text-slate-500">{error}</p>
            <Button variant="primary" onClick={fetchSettings}>
              Retry
            </Button>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!settings) {
    return null;
  }

  return (
    <div className="flex min-h-screen flex-col bg-slate-950">
      <TopNavbar />

      <main className="flex-1 p-6">
        <div className="mx-auto max-w-[1200px]">
          <PageHeader
            title="Settings"
            description="Configure your preferences, analysis defaults, and integrations"
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
              <span className="text-sm font-medium">Settings saved successfully</span>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 flex items-center gap-2 rounded-lg border border-red-900/50 bg-red-950/30 p-4 text-red-400">
              <AlertCircle className="h-5 w-5" />
              <span className="text-sm font-medium">{error}</span>
            </div>
          )}

          <div className="space-y-6">
            {/* Profile & Preferences */}
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-4 text-lg font-semibold text-white">Profile & Preferences</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">Theme</label>
                    <select
                      value={settings.theme}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          theme: e.target.value as "dark" | "light" | "system",
                        })
                      }
                      className="w-full rounded border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
                    >
                      <option value="dark">Dark</option>
                      <option value="light">Light</option>
                      <option value="system">System</option>
                    </select>
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">
                      Timezone
                    </label>
                    <input
                      type="text"
                      value={settings.timezone}
                      onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                      className="w-full rounded border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
                    />
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-300">Language</label>
                  <select
                    value={settings.language}
                    onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                    className="w-full rounded border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
                  >
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Notification Preferences */}
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-4 text-lg font-semibold text-white">Notification Preferences</h3>
              <div className="space-y-3">
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={settings.notifications.email}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, email: e.target.checked },
                      })
                    }
                    className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <div>
                    <span className="text-sm font-medium text-slate-300">Email Notifications</span>
                    <p className="text-xs text-slate-500">Receive email updates for analysis results</p>
                  </div>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={settings.notifications.highRiskAlerts}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        notifications: {
                          ...settings.notifications,
                          highRiskAlerts: e.target.checked,
                        },
                      })
                    }
                    className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <div>
                    <span className="text-sm font-medium text-slate-300">High-Risk Alerts</span>
                    <p className="text-xs text-slate-500">
                      Immediate alerts for critical security threats
                    </p>
                  </div>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={settings.notifications.dailyDigest}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, dailyDigest: e.target.checked },
                      })
                    }
                    className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <div>
                    <span className="text-sm font-medium text-slate-300">Daily Digest</span>
                    <p className="text-xs text-slate-500">Daily summary of security findings</p>
                  </div>
                </label>
              </div>
            </div>

            {/* Analysis Defaults */}
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-4 text-lg font-semibold text-white">Analysis Defaults</h3>
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-300">
                    Default Input Type
                  </label>
                  <select
                    value={settings.analysisDefaults.defaultInputType}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        analysisDefaults: {
                          ...settings.analysisDefaults,
                          defaultInputType: e.target.value as InputType,
                        },
                      })
                    }
                    className="w-full rounded border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
                  >
                    <option value="text">Text</option>
                    <option value="file">File</option>
                    <option value="log">Log</option>
                    <option value="sql">SQL</option>
                    <option value="chat">Chat</option>
                  </select>
                </div>
                <div className="space-y-3">
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={settings.analysisDefaults.maskSensitiveData}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          analysisDefaults: {
                            ...settings.analysisDefaults,
                            maskSensitiveData: e.target.checked,
                          },
                        })
                      }
                      className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                    />
                    <span className="text-sm text-slate-300">Auto-mask sensitive data</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={settings.analysisDefaults.blockHighRiskContent}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          analysisDefaults: {
                            ...settings.analysisDefaults,
                            blockHighRiskContent: e.target.checked,
                          },
                        })
                      }
                      className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                    />
                    <span className="text-sm text-slate-300">Auto-block high-risk content</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={settings.analysisDefaults.advancedThreatDetection}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          analysisDefaults: {
                            ...settings.analysisDefaults,
                            advancedThreatDetection: e.target.checked,
                          },
                        })
                      }
                      className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                    />
                    <span className="text-sm text-slate-300">Advanced threat detection</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Detector Configuration */}
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-4 text-lg font-semibold text-white">Detector Configuration</h3>
              <div className="grid grid-cols-2 gap-3">
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={settings.detectorConfig.regex}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        detectorConfig: { ...settings.detectorConfig, regex: e.target.checked },
                      })
                    }
                    className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <span className="text-sm text-slate-300">Regex Detector</span>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={settings.detectorConfig.heuristic}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        detectorConfig: { ...settings.detectorConfig, heuristic: e.target.checked },
                      })
                    }
                    className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <span className="text-sm text-slate-300">Heuristic Detector</span>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={settings.detectorConfig.nlp}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        detectorConfig: { ...settings.detectorConfig, nlp: e.target.checked },
                      })
                    }
                    className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <span className="text-sm text-slate-300">NLP Detector</span>
                </label>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={settings.detectorConfig.ai}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        detectorConfig: { ...settings.detectorConfig, ai: e.target.checked },
                      })
                    }
                    className="h-4 w-4 rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-2 focus:ring-blue-600"
                  />
                  <span className="text-sm text-slate-300">AI Detector</span>
                </label>
              </div>
            </div>

            {/* API & Integrations */}
            <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
              <h3 className="mb-4 text-lg font-semibold text-white">API & Integrations</h3>
              <div className="space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-300">API Key</label>
                  <div className="relative">
                    <input
                      type={showApiKey ? "text" : "password"}
                      value={settings.apiIntegration.apiKey}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          apiIntegration: { ...settings.apiIntegration, apiKey: e.target.value },
                        })
                      }
                      className="w-full rounded border border-slate-800 bg-slate-950 px-3 py-2 pr-10 font-mono text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
                    />
                    <button
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300"
                    >
                      {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-300">
                    Webhook URL
                  </label>
                  <input
                    type="text"
                    value={settings.apiIntegration.webhookUrl}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        apiIntegration: { ...settings.apiIntegration, webhookUrl: e.target.value },
                      })
                    }
                    placeholder="https://your-webhook-url.com"
                    className="w-full rounded border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300 focus:border-blue-600 focus:outline-none"
                  />
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
