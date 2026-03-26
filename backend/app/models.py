from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
from uuid import uuid4

# Request Models
class AnalysisOptions(BaseModel):
    mask: bool = True
    blockHighRisk: bool = False
    advancedDetection: bool = True
    # Support both naming conventions
    block_high_risk: Optional[bool] = None
    advanced_detection: Optional[bool] = None

    def __init__(self, **data):
        # Handle snake_case to camelCase conversion
        if 'block_high_risk' in data and 'blockHighRisk' not in data:
            data['blockHighRisk'] = data['block_high_risk']
        if 'advanced_detection' in data and 'advancedDetection' not in data:
            data['advancedDetection'] = data['advanced_detection']
        super().__init__(**data)

class AnalysisRequest(BaseModel):
    inputType: Literal["text", "file", "log", "sql", "chat"]
    content: str
    options: AnalysisOptions
    # Support snake_case alternative
    input_type: Optional[Literal["text", "file", "log", "sql", "chat"]] = None
    # Optional: filename for file uploads
    filename: Optional[str] = None
    # Optional: content_type for API standardization
    content_type: Optional[str] = None

    def __init__(self, **data):
        # Handle snake_case to camelCase conversion
        if 'input_type' in data and 'inputType' not in data:
            data['inputType'] = data['input_type']
        if 'content_type' in data:
            data['content_type'] = data['content_type']
        super().__init__(**data)

# Response Models
class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    line: Optional[int] = None
    type: str
    risk: Literal["Low", "Medium", "High", "Critical"]
    detector: Literal["Regex", "Heuristic"]
    preview: str
    explanation: str
    scoreContribution: int

class RiskDistribution(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0

class RiskScoreBreakdownItem(BaseModel):
    finding: str
    contribution: int

class AnalysisMetadata(BaseModel):
    processingTimeMs: int
    linesScanned: int
    detectorsTriggered: int
    inputSizeBytes: int

class AnalysisResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    inputType: Literal["text", "file", "log", "sql", "chat"]
    overallRiskScore: int
    overallRiskLevel: Literal["Low", "Medium", "High", "Critical"]
    primaryAction: Literal["Allow", "Mask", "Block", "Masked & Flagged"]
    totalFindings: int
    findings: list[Finding]
    maskedOutput: list[str]
    aiSummary: str
    criticalVulnerabilities: list[str]
    behavioralAnomalies: list[str]
    recommendedActions: list[str]
    riskDistribution: RiskDistribution
    riskScoreBreakdown: list[RiskScoreBreakdownItem]
    metadata: AnalysisMetadata
    # Additional context-specific data
    sqlAnalysis: Optional[list] = None  # List of SQL statement analysis results
    chatAnalysis: Optional[dict] = None  # Chat conversation analysis summary
    # API standardization: unified insights array
    insights: Optional[list[str]] = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    code: Literal["INVALID_INPUT", "ANALYSIS_FAILED", "SERVER_ERROR"]
