import { AnalysisResponse, InputType, AnalysisOptions, UserSettings } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class APIError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number
  ) {
    super(message);
    this.name = "APIError";
  }
}

export async function analyzeContent(
  content: string,
  inputType: InputType,
  options: AnalysisOptions
): Promise<AnalysisResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        inputType,
        content,
        options: {
          mask: options.maskSensitiveData,
          blockHighRisk: options.blockHighRiskContent,
          advancedDetection: options.advancedThreatDetection,
        },
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: "Unknown error",
        message: "Failed to parse error response",
        code: "SERVER_ERROR",
      }));

      throw new APIError(
        errorData.message || "Analysis failed",
        errorData.code || "SERVER_ERROR",
        response.status
      );
    }

    const data = await response.json();
    return data as AnalysisResponse;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    // Network or parsing error
    throw new APIError(
      error instanceof Error ? error.message : "Network error occurred",
      "NETWORK_ERROR",
      0
    );
  }
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

// Settings API
export async function getSettings(): Promise<UserSettings> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/settings`);
    if (!response.ok) {
      throw new APIError("Failed to fetch settings", "FETCH_ERROR", response.status);
    }
    const data = await response.json();
    return data.settings as UserSettings;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : "Network error occurred",
      "NETWORK_ERROR",
      0
    );
  }
}

export async function updateSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/settings`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ updates: settings }),
    });
    if (!response.ok) {
      throw new APIError("Failed to update settings", "UPDATE_ERROR", response.status);
    }
    const data = await response.json();
    return data.settings as UserSettings;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : "Network error occurred",
      "NETWORK_ERROR",
      0
    );
  }
}

export async function resetSettings(): Promise<UserSettings> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/settings/reset`, {
      method: "POST",
    });
    if (!response.ok) {
      throw new APIError("Failed to reset settings", "RESET_ERROR", response.status);
    }
    const data = await response.json();
    return data.settings as UserSettings;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : "Network error occurred",
      "NETWORK_ERROR",
      0
    );
  }
}

// Audit Logs / Analysis History API
export interface AnalysisRecord {
  id: string;
  timestamp: string;
  inputType: string;
  overallRiskScore: number;
  overallRiskLevel: string;
  primaryAction: string;
  totalFindings: number;
}

export interface AnalysisListResponse {
  analyses: AnalysisRecord[];
  total: number;
  limit: number;
  offset: number;
}

export async function getAnalyses(limit = 50, offset = 0): Promise<AnalysisListResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyses?limit=${limit}&offset=${offset}`);
    if (!response.ok) {
      throw new APIError("Failed to fetch analyses", "FETCH_ERROR", response.status);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : "Network error occurred",
      "NETWORK_ERROR",
      0
    );
  }
}

export async function getAnalysisById(analysisId: string): Promise<AnalysisResponse & { timestamp?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}`);
    if (!response.ok) {
      if (response.status === 404) {
        throw new APIError("Analysis not found", "NOT_FOUND", 404);
      }
      throw new APIError("Failed to fetch analysis", "FETCH_ERROR", response.status);
    }
    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : "Network error occurred",
      "NETWORK_ERROR",
      0
    );
  }
}

// Policy API
export interface PolicyConfig {
  name: string;
  block_high_risk: boolean;
  mask_all_secrets: boolean;
  critical_threshold: number;
  high_threshold: number;
  auto_rotate_keys: boolean;
  alert_on_critical: boolean;
  enabled_detectors: string | string[];
}

export async function getPolicy(): Promise<PolicyConfig> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/policy`);
    if (!response.ok) {
      throw new APIError("Failed to fetch policy", "FETCH_ERROR", response.status);
    }
    const data = await response.json();
    return data.policy as PolicyConfig;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : "Network error occurred",
      "NETWORK_ERROR",
      0
    );
  }
}

export async function updatePolicy(updates: Partial<PolicyConfig>): Promise<PolicyConfig> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/policy`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ updates }),
    });
    if (!response.ok) {
      throw new APIError("Failed to update policy", "UPDATE_ERROR", response.status);
    }
    const data = await response.json();
    return data.policy as PolicyConfig;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : "Network error occurred",
      "NETWORK_ERROR",
      0
    );
  }
}

export async function resetPolicy(): Promise<PolicyConfig> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/policy/reset`, {
      method: "POST",
    });
    if (!response.ok) {
      throw new APIError("Failed to reset policy", "RESET_ERROR", response.status);
    }
    const data = await response.json();
    return data.policy as PolicyConfig;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : "Network error occurred",
      "NETWORK_ERROR",
      0
    );
  }
}

// File Upload API - sends binary file to backend for real PDF/DOCX parsing
export async function uploadFile(
  file: File,
  options: AnalysisOptions
): Promise<AnalysisResponse> {
  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("options", JSON.stringify({
      mask: options.maskSensitiveData,
      blockHighRisk: options.blockHighRiskContent,
      advancedDetection: options.advancedThreatDetection,
    }));

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: "Unknown error",
        message: "Failed to parse error response",
        code: "SERVER_ERROR",
      }));

      throw new APIError(
        errorData.detail?.message || errorData.message || "File upload failed",
        errorData.detail?.code || errorData.code || "UPLOAD_ERROR",
        response.status
      );
    }

    const data = await response.json();
    return data as AnalysisResponse;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : "Network error occurred",
      "NETWORK_ERROR",
      0
    );
  }
}
