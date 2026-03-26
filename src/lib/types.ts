export type RiskLevel = "Low" | "Medium" | "High" | "Critical";
export type DetectorType = "Regex" | "Heuristic" | "NLP" | "AI";
export type InputType = "text" | "file" | "log" | "sql" | "chat";
export type ActionType = "Allow" | "Mask" | "Block" | "Masked & Flagged";

export interface Finding {
  id: string;
  line?: number;
  type: string;
  risk: RiskLevel;
  detector: DetectorType;
  preview: string;
  explanation?: string;
  scoreContribution?: number;
}

export interface AnalysisMetadata {
  processingTimeMs: number;
  linesScanned: number;
  detectorsTriggered: number;
  inputSizeBytes: number;
}

export interface AnalysisResponse {
  id: string;
  inputType: InputType;
  overallRiskScore: number;
  overallRiskLevel: RiskLevel;
  primaryAction: ActionType;
  totalFindings: number;
  findings: Finding[];
  aiSummary: string;
  criticalVulnerabilities: string[];
  behavioralAnomalies: string[];
  recommendedActions: string[];
  maskedOutput: string[];
  riskDistribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  riskScoreBreakdown: {
    finding: string;
    contribution: number;
  }[];
  metadata: AnalysisMetadata;
}

export interface AnalysisOptions {
  maskSensitiveData: boolean;
  blockHighRiskContent: boolean;
  advancedThreatDetection: boolean;
}

export type AnalysisState = "idle" | "validating" | "scanning" | "analyzing" | "generating" | "complete" | "error";

// Policies
export type PolicyCategory = "Data Security" | "Access Control" | "Threat Detection";
export type PolicyStatus = "active" | "inactive";

export interface DetectorConfig {
  regex: boolean;
  heuristic: boolean;
  nlp: boolean;
  ai: boolean;
}

export interface Policy {
  id: string;
  name: string;
  description: string;
  category: PolicyCategory;
  severityThreshold: RiskLevel;
  status: PolicyStatus;
  lastUpdated: string;
  maskingEnabled: boolean;
  blockingEnabled: boolean;
  detectors: DetectorConfig;
}

// Audit Logs
export type AuditLogStatus = "success" | "failed" | "blocked";

export interface AuditLog {
  id: string;
  timestamp: string;
  analysisId: string;
  inputType: InputType;
  riskLevel: RiskLevel;
  action: ActionType;
  status: AuditLogStatus;
  triggeredPolicies: string[];
  userId?: string;
}

// Settings
export interface UserSettings {
  theme: "dark" | "light" | "system";
  timezone: string;
  language: string;
  notifications: {
    email: boolean;
    highRiskAlerts: boolean;
    dailyDigest: boolean;
  };
  analysisDefaults: AnalysisOptions & {
    defaultInputType: InputType;
  };
  detectorConfig: DetectorConfig;
  apiIntegration: {
    apiKey: string;
    webhookUrl: string;
  };
}
