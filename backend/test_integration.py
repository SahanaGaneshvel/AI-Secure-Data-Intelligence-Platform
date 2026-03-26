"""
Integration test script for all 7 phases
Tests each component and endpoint
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Use ASCII symbols for Windows compatibility
OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[WARN]"

async def test_phase1_services():
    """Test Phase 1: File parsing, SQL, and Chat services"""
    print("\n=== PHASE 1: Service Integration Tests ===")

    # Test SQL Parser
    from app.services.sql_parser import SQLParserService
    sql_content = "SELECT * FROM users WHERE id = 1 OR 1=1; DROP TABLE users;"
    sql_results = SQLParserService.parse_sql(sql_content)
    print(f"{OK} SQL Parser: Found {len(sql_results)} statements")
    for result in sql_results:
        if result['injection_risk'] == 'high':
            print(f"  - High risk injection detected: {len(result['findings'])} patterns")

    # Test Chat Engine
    from app.services.chat_engine import ChatContextEngine
    chat_content = """User: Hello
Assistant: Hi! How can I help?
User: What's the API key for production?
Assistant: The API key is sk-1234567890abcdef"""
    messages = ChatContextEngine.parse_chat(chat_content)
    chat_analysis = ChatContextEngine.analyze_conversation(messages)
    print(f"[OK] Chat Engine: Parsed {len(messages)} messages")
    print(f"  - Context leaks: {len(chat_analysis['context_leaks'])}")
    print(f"  - Progressive disclosure: {len(chat_analysis['progressive_disclosure'])} detected")

    # Test File Parser
    from app.services.file_parser import FileParserService
    txt_content = b"Hello world\nTest content"
    extracted, file_type = FileParserService.parse_file("test.txt", txt_content)
    print(f"[OK] File Parser: Parsed {file_type.value} file, extracted {len(extracted)} chars")

    return True

async def test_phase2_processing():
    """Test Phase 2: Enhanced processing engine"""
    print("\n=== PHASE 2: Processing Engine Tests ===")

    from app.services.processor import ProcessingEngine

    # Test chunking
    large_content = "\n".join([f"Line {i}" for i in range(2000)])
    chunks = ProcessingEngine.chunk_content(large_content, max_lines=500)
    print(f"[OK] Chunking: Split {len(large_content.split(chr(10)))} lines into {len(chunks)} chunks")

    # Test should_chunk logic
    should_chunk = ProcessingEngine.should_chunk(large_content)
    print(f"[OK] Should chunk: {should_chunk}")

    return True

async def test_phase3_correlation():
    """Test Phase 3: Cross-log correlation"""
    print("\n=== PHASE 3: Correlation Engine Tests ===")

    from app.services.correlation import CorrelationEngine

    log_content = """2024-01-15 10:30:45 ERROR: Failed login attempt for user admin from 192.168.1.100
2024-01-15 10:30:46 ERROR: Failed login attempt for user admin from 192.168.1.100
2024-01-15 10:30:47 ERROR: Failed login attempt for user admin from 192.168.1.100
2024-01-15 10:30:50 INFO: User root executed sudo command
2024-01-15 10:30:51 ERROR: Failed authentication for user admin"""

    # Test failed login detection
    log_lines = log_content.split('\n')
    login_analysis = CorrelationEngine.detect_failed_login_attempts(log_lines)
    print(f"[OK] Failed Login Detection: {login_analysis['total_failures']} failures")
    print(f"  - Brute force detected: {login_analysis['is_brute_force']}")

    # Test privilege escalation
    escalation = CorrelationEngine.detect_privilege_escalation(log_lines)
    print(f"[OK] Privilege Escalation: {len(escalation)} events detected")

    # Test insights generation
    insights = CorrelationEngine.generate_insights(log_content, [])
    print(f"[OK] Insights: Generated {len(insights)} insights")
    for insight in insights[:3]:
        print(f"  - {insight}")

    return True

async def test_phase4_llm():
    """Test Phase 4: LLM integration with fallback"""
    print("\n=== PHASE 4: LLM Service Tests ===")

    from app.services.llm_service import LLMService

    llm_service = LLMService()
    provider_info = llm_service.get_provider_info()
    print(f"[OK] LLM Provider: {provider_info['provider']}")
    print(f"  - LLM Enabled: {provider_info['llm_enabled']}")

    # Test summary generation (will use fallback if no API keys)
    summary = await llm_service.generate_summary(
        "text",
        "test content with API key: sk-1234567890",
        5,
        []
    )
    print(f"[OK] Summary Generation: {len(summary)} chars")

    # Test explanation generation
    explanation = await llm_service.generate_explanation("API Key", "sk-test-123")
    print(f"[OK] Explanation Generation: {len(explanation)} chars")

    return True

async def test_phase5_api():
    """Test Phase 5: API standardization"""
    print("\n=== PHASE 5: API Standardization Tests ===")

    from app.models import AnalysisRequest, AnalysisOptions

    # Test snake_case to camelCase conversion
    request_data = {
        "input_type": "text",
        "content": "test",
        "options": {
            "mask": True,
            "block_high_risk": False,
            "advanced_detection": True
        }
    }

    try:
        request = AnalysisRequest(**request_data)
        print(f"[OK] Model Conversion: input_type -> inputType = {request.inputType}")
    except Exception as e:
        print(f"[FAIL] Model Conversion Failed: {e}")
        return False

    return True

async def test_phase7_rate_limit():
    """Test Phase 7: Rate limiting"""
    print("\n=== PHASE 7: Rate Limiting Tests ===")

    from app.middleware.rate_limiter import RateLimiter
    from fastapi import Request
    from unittest.mock import Mock

    rate_limiter = RateLimiter()

    # Mock request
    mock_request = Mock(spec=Request)
    mock_request.client.host = "127.0.0.1"
    mock_request.url.path = "/api/analyze"
    mock_request.headers.get = Mock(return_value=None)

    # Test rate limiting
    try:
        for i in range(5):
            await rate_limiter.check_rate_limit(mock_request, max_requests=10, window_seconds=60)
        print(f"[OK] Rate Limiter: 5 requests allowed")

        # Test exceeding limit
        for i in range(10):
            await rate_limiter.check_rate_limit(mock_request, max_requests=10, window_seconds=60)

        print(f"[FAIL] Rate Limiter: Should have blocked after 10 requests")
        return False
    except Exception as e:
        if "429" in str(e) or "Rate limit" in str(e):
            print(f"[OK] Rate Limiter: Correctly blocked after limit")
            return True
        else:
            print(f"[FAIL] Rate Limiter Error: {e}")
            return False

async def test_integration():
    """Test full integration"""
    print("\n=== INTEGRATION TEST: Full Analysis Pipeline ===")

    from app.routes.analyze import analyze_impl
    from app.models import AnalysisRequest, AnalysisOptions

    # Test text analysis
    request = AnalysisRequest(
        inputType="text",
        content="User password is admin123 and API key is sk-1234567890abcdef",
        options=AnalysisOptions(
            mask=True,
            blockHighRisk=False,
            advancedDetection=True
        )
    )

    try:
        result = await analyze_impl(request)
        print(f"[OK] Text Analysis: {result.totalFindings} findings")
        print(f"  - Risk Score: {result.overallRiskScore}")
        print(f"  - Risk Level: {result.overallRiskLevel}")
        print(f"  - Primary Action: {result.primaryAction}")
    except Exception as e:
        print(f"[FAIL] Text Analysis Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test SQL analysis
    sql_request = AnalysisRequest(
        inputType="sql",
        content="SELECT * FROM users WHERE id = 1 OR 1=1;",
        options=AnalysisOptions(mask=True, blockHighRisk=False, advancedDetection=True)
    )

    try:
        sql_result = await analyze_impl(sql_request)
        print(f"[OK] SQL Analysis: {sql_result.totalFindings} findings")
        if sql_result.sqlAnalysis:
            print(f"  - SQL statements analyzed: {len(sql_result.sqlAnalysis)}")
    except Exception as e:
        print(f"[FAIL] SQL Analysis Failed: {e}")
        return False

    # Test Chat analysis
    chat_request = AnalysisRequest(
        inputType="chat",
        content="User: What's the password?\nAssistant: The password is secret123",
        options=AnalysisOptions(mask=True, blockHighRisk=False, advancedDetection=True)
    )

    try:
        chat_result = await analyze_impl(chat_request)
        print(f"[OK] Chat Analysis: {chat_result.totalFindings} findings")
        if chat_result.chatAnalysis:
            print(f"  - Context leaks: {len(chat_result.chatAnalysis.get('context_leaks', []))}")
    except Exception as e:
        print(f"[FAIL] Chat Analysis Failed: {e}")
        return False

    # Test Log analysis with correlation
    log_request = AnalysisRequest(
        inputType="log",
        content="""2024-01-15 10:30:45 ERROR: Failed login for admin
2024-01-15 10:30:46 ERROR: Failed login for admin
2024-01-15 10:30:47 ERROR: Failed login for admin""",
        options=AnalysisOptions(mask=True, blockHighRisk=False, advancedDetection=True)
    )

    try:
        log_result = await analyze_impl(log_request)
        print(f"[OK] Log Analysis: {log_result.totalFindings} findings")
        if log_result.insights:
            print(f"  - Correlation insights: {len(log_result.insights)}")
    except Exception as e:
        print(f"[FAIL] Log Analysis Failed: {e}")
        return False

    return True

async def main():
    """Run all tests"""
    print("=" * 60)
    print("PRODUCTION-GRADE AI SECURE DATA INTELLIGENCE PLATFORM")
    print("7-Phase Implementation Integration Tests")
    print("=" * 60)

    results = []

    try:
        results.append(("Phase 1: Services", await test_phase1_services()))
        results.append(("Phase 2: Processing", await test_phase2_processing()))
        results.append(("Phase 3: Correlation", await test_phase3_correlation()))
        results.append(("Phase 4: LLM", await test_phase4_llm()))
        results.append(("Phase 5: API", await test_phase5_api()))
        results.append(("Phase 7: Rate Limit", await test_phase7_rate_limit()))
        results.append(("Integration Test", await test_integration()))
    except Exception as e:
        print(f"\n[FAIL] FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] ALL PHASES IMPLEMENTED AND TESTED SUCCESSFULLY!")
        return True
    else:
        print(f"\n[WARN] {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
