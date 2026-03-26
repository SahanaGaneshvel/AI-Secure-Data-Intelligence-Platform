"""
Analysis endpoint - orchestrates detection, masking, risk calculation
"""
import time
from fastapi import APIRouter, HTTPException
from app.models import AnalysisRequest, AnalysisResponse, Finding, ErrorResponse, AnalysisMetadata
from app.services.detector import DetectorService
from app.services.masker import MaskerService
from app.services.risk import RiskService
from app.services.ai import AIService
from app.services.policy import PolicyEngine
from app.services.sql_parser import SQLParserService
from app.services.chat_engine import ChatContextEngine
from app.services.processor import ProcessingEngine
from app.services.correlation import CorrelationEngine
from app.config import get_risk_level
from app.database import save_analysis, get_analysis_by_id, get_all_analyses

router = APIRouter()

detector = DetectorService()
masker = MaskerService()
risk_service = RiskService()
ai_service = AIService()
policy_engine = PolicyEngine()

async def analyze_impl(request: AnalysisRequest) -> AnalysisResponse:
    """
    Main analysis endpoint
    """
    try:
        # Start timing
        start_time = time.time()

        # Validate input
        if not request.content or len(request.content.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid input",
                    "message": "Content cannot be empty",
                    "code": "INVALID_INPUT"
                }
            )

        # Collect metadata
        input_size = len(request.content.encode('utf-8'))
        lines_scanned = len(request.content.split('\n'))

        # Handle SQL-specific analysis
        sql_analysis = None
        if request.inputType == "sql":
            sql_analysis = SQLParserService.parse_sql(request.content)
            # Add SQL injection findings to detections
            for result in sql_analysis:
                if result.get('injection_risk') == 'high':
                    for finding in result.get('findings', []):
                        detector.detect(finding['matched_text'])  # Trigger detection on malicious patterns

        # Handle Chat-specific analysis
        chat_analysis = None
        if request.inputType == "chat":
            messages = ChatContextEngine.parse_chat(request.content)
            chat_analysis = ChatContextEngine.analyze_conversation(messages)
            # Add chat security findings to detections
            for leak in chat_analysis.get('context_leaks', []):
                detector.detect(leak['excerpt'])  # Trigger detection on leaked content excerpt

        # Step 1: Detect threats and sensitive data (with chunking for large files)
        if ProcessingEngine.should_chunk(request.content):
            # Use enhanced processing for large files
            all_detections = await ProcessingEngine.process_large_file(
                request.content,
                detector.detect
            )
        else:
            # Direct processing for small files
            all_detections = detector.detect(request.content)

        # Filter detections based on policy's enabled detectors
        policy = policy_engine.get_policy()
        if policy.get("enabled_detectors") != "all":
            enabled = policy.get("enabled_detectors", [])
            detections = [d for d in all_detections if d['type'] in enabled]
        else:
            detections = all_detections

        # Step 2: Mask content if enabled (respecting policy)
        if request.options.mask:
            masked_lines = masker.mask_content(request.content, detections)
        else:
            masked_lines = request.content.split('\n')

        # Step 3: Calculate risk score and distribution
        overall_score, score_breakdown = risk_service.calculate_score(detections)
        distribution = risk_service.calculate_distribution(detections)

        # Step 4: Determine risk level and primary action (using policy engine)
        risk_level = get_risk_level(overall_score)
        primary_action = policy_engine.evaluate_action(
            overall_score,
            risk_level,
            {
                "mask": request.options.mask,
                "blockHighRisk": request.options.blockHighRisk
            }
        )

        # Step 5: Build findings with explanations (using LLM if available)
        findings = []
        for detection in detections:
            explanation = await ai_service.generate_explanation_async(
                detection['type'],
                detection['matched_text']
            )

            # Get score contribution for this finding type
            score_contrib = next(
                (item.contribution for item in score_breakdown if item.finding == detection['type']),
                0
            )

            finding = Finding(
                line=detection['line'],
                type=detection['type'],
                risk=detection['risk'],
                detector=detection['detector'],
                preview=masker.create_preview(detection['matched_text'], detection['type']),
                explanation=explanation,
                scoreContribution=score_contrib
            )
            findings.append(finding)

        # Step 6: Generate AI insights (with findings for enhanced log analysis, using LLM if available)
        ai_summary = await ai_service.generate_summary_async(
            request.inputType,
            request.content,
            len(findings),
            detections  # Pass raw detections for better context
        )

        vulnerabilities = risk_service.get_vulnerabilities(detections)
        anomalies = risk_service.get_anomalies(detections)
        recommendations = risk_service.get_recommendations(
            detections,
            {"mask": request.options.mask}
        )

        # Step 6b: Generate cross-log correlation insights (for log type)
        insights = None
        if request.inputType == "log":
            insights = CorrelationEngine.generate_insights(request.content, detections)

        # Step 7: Calculate metadata
        end_time = time.time()
        processing_time_ms = int((end_time - start_time) * 1000)

        # Count unique detector types triggered
        detectors_triggered = len(set(d['detector'] for d in detections))

        metadata = AnalysisMetadata(
            processingTimeMs=processing_time_ms,
            linesScanned=lines_scanned,
            detectorsTriggered=detectors_triggered,
            inputSizeBytes=input_size
        )

        # Step 8: Build response
        response = AnalysisResponse(
            inputType=request.inputType,
            overallRiskScore=overall_score,
            overallRiskLevel=risk_level,
            primaryAction=primary_action,
            totalFindings=len(findings),
            findings=findings,
            maskedOutput=masked_lines,
            aiSummary=ai_summary,
            criticalVulnerabilities=vulnerabilities,
            behavioralAnomalies=anomalies,
            recommendedActions=recommendations,
            riskDistribution=distribution,
            riskScoreBreakdown=score_breakdown,
            metadata=metadata,
            sqlAnalysis=sql_analysis,
            chatAnalysis=chat_analysis,
            insights=insights
        )

        # Step 8: Save to database
        save_analysis(response.model_dump())

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis failed",
                "message": str(e),
                "code": "ANALYSIS_FAILED"
            }
        )

# Support both /api/analyze (current) and /analyze (document spec)
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """Main analysis endpoint - /api/analyze"""
    return await analyze_impl(request)

@router.get("/analyses")
async def get_analyses(limit: int = 50, offset: int = 0):
    """
    Get list of past analyses for audit logs
    """
    try:
        analyses = get_all_analyses(limit=limit, offset=offset)
        return {
            "analyses": analyses,
            "total": len(analyses),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve analyses",
                "message": str(e),
                "code": "SERVER_ERROR"
            }
        )

@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Get detailed analysis by ID
    """
    try:
        analysis = get_analysis_by_id(analysis_id)
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Analysis not found",
                    "message": f"No analysis found with ID: {analysis_id}",
                    "code": "NOT_FOUND"
                }
            )
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve analysis",
                "message": str(e),
                "code": "SERVER_ERROR"
            }
        )
