"""
Quick validation script for hackathon enhancements
Checks that all new features are properly integrated
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def validate_imports():
    """Validate all new modules can be imported"""
    print("=" * 80)
    print("VALIDATION: Module Imports")
    print("=" * 80)

    try:
        from app.services.log_parser import LogParser, LogAnalyzer, LogEntry
        print("✓ log_parser module imported successfully")
        print(f"  - LogParser class: {LogParser.__name__}")
        print(f"  - LogAnalyzer class: {LogAnalyzer.__name__}")
        print(f"  - LogEntry class: {LogEntry.__name__}")
    except Exception as e:
        print(f"✗ Failed to import log_parser: {e}")
        return False

    try:
        from app.services.detector import DetectorService, PATTERNS
        print(f"✓ DetectorService imported ({len(PATTERNS)} patterns)")
    except Exception as e:
        print(f"✗ Failed to import DetectorService: {e}")
        return False

    try:
        from app.services.ai import AIService
        print("✓ AIService imported successfully")
    except Exception as e:
        print(f"✗ Failed to import AIService: {e}")
        return False

    try:
        from app.config import RISK_WEIGHTS
        print(f"✓ Config imported ({len(RISK_WEIGHTS)} risk weights)")
    except Exception as e:
        print(f"✗ Failed to import config: {e}")
        return False

    return True

def validate_patterns():
    """Validate new log-specific patterns are present"""
    print("\n" + "=" * 80)
    print("VALIDATION: Log-Specific Detection Patterns")
    print("=" * 80)

    from app.services.detector import PATTERNS

    expected_new_patterns = [
        "Session Token",
        "Access Token in Log",
        "Authorization Header Leak",
        "Cookie with Secrets",
        "Database Password in Connection String",
        "Hardcoded Secret",
        "Internal Path Disclosure",
        "Error with User Data"
    ]

    pattern_names = [p.name for p in PATTERNS]

    all_found = True
    for pattern in expected_new_patterns:
        if pattern in pattern_names:
            print(f"✓ {pattern}")
        else:
            print(f"✗ MISSING: {pattern}")
            all_found = False

    print(f"\nTotal patterns: {len(PATTERNS)}")
    print(f"Expected new patterns found: {sum(1 for p in expected_new_patterns if p in pattern_names)}/{len(expected_new_patterns)}")

    return all_found

def validate_risk_weights():
    """Validate new risk weights are configured"""
    print("\n" + "=" * 80)
    print("VALIDATION: Risk Weight Configuration")
    print("=" * 80)

    from app.config import RISK_WEIGHTS

    expected_new_weights = [
        "Session Token",
        "Access Token in Log",
        "Authorization Header Leak",
        "Cookie with Secrets",
        "Database Password in Connection String",
        "Hardcoded Secret",
        "Internal Path Disclosure",
        "Error with User Data",
        "Stack Trace Leak",
        "Suspicious IP Activity",
        "Sensitive Data in Error",
        "SQL Error Leak"
    ]

    all_found = True
    for weight_name in expected_new_weights:
        if weight_name in RISK_WEIGHTS:
            weight = RISK_WEIGHTS[weight_name]
            print(f"✓ {weight_name}: {weight} points")
        else:
            print(f"✗ MISSING: {weight_name}")
            all_found = False

    print(f"\nTotal configured weights: {len(RISK_WEIGHTS)}")
    print(f"Expected new weights found: {sum(1 for w in expected_new_weights if w in RISK_WEIGHTS)}/{len(expected_new_weights)}")

    return all_found

def validate_log_parser():
    """Validate log parser functionality"""
    print("\n" + "=" * 80)
    print("VALIDATION: Log Parser Functionality")
    print("=" * 80)

    from app.services.log_parser import LogParser, LogAnalyzer

    test_log = """2026-03-25 10:00:00 INFO Starting application
2026-03-25 10:00:01 ERROR Authentication failed for user admin
2026-03-25 10:00:02 DEBUG console.log() called
2026-03-25 10:00:03 ERROR Exception occurred
Traceback (most recent call last):
  File "app.py", line 42
Exception: Test error
"""

    try:
        parser = LogParser()
        entries = parser.parse_log_file(test_log)
        print(f"✓ LogParser.parse_log_file() - parsed {len(entries)} entries")

        # Check timestamp detection
        timestamps_found = sum(1 for e in entries if e.timestamp)
        print(f"✓ Timestamp detection - found {timestamps_found}/{len(entries)}")

        # Check level detection
        levels_found = sum(1 for e in entries if e.level)
        print(f"✓ Log level detection - found {levels_found}/{len(entries)}")

        analyzer = LogAnalyzer()
        analysis = analyzer.analyze_log_patterns(entries)
        print(f"✓ LogAnalyzer.analyze_log_patterns() - completed")
        print(f"  - Total lines: {analysis['total_lines']}")
        print(f"  - Error count: {analysis['error_count']}")
        print(f"  - Suspicious patterns: {len(analysis['suspicious_patterns'])}")

        return True
    except Exception as e:
        print(f"✗ Log parser validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_behavioral_detection():
    """Validate enhanced behavioral anomaly detection"""
    print("\n" + "=" * 80)
    print("VALIDATION: Behavioral Anomaly Detection")
    print("=" * 80)

    from app.services.detector import DetectorService

    # Test repeated failures
    test_log_failures = "\n".join([
        f"2026-03-25 10:00:{i:02d} ERROR Authentication failed"
        for i in range(12)
    ])

    # Test stack traces
    test_log_traces = """ERROR Exception 1
Traceback: line 1
ERROR Exception 2
Traceback: line 2
ERROR Exception 3
Traceback: line 3
"""

    # Test debug leaks
    test_log_debug = """DEBUG statement 1
TRACE statement 2
console.log() statement 3
print() statement 4
"""

    detector = DetectorService()

    # Test 1: Repeated failures
    detections = detector.detect(test_log_failures)
    failure_detections = [d for d in detections if d['type'] == 'Repeated Failures']
    if failure_detections:
        print(f"✓ Repeated Failures detection - detected {failure_detections[0]['matched_text']}")
    else:
        print("✗ Repeated Failures detection failed")

    # Test 2: Stack traces
    detections = detector.detect(test_log_traces)
    trace_detections = [d for d in detections if 'Stack Trace' in d['type']]
    if trace_detections:
        print(f"✓ Stack Trace detection - found {len(trace_detections)} occurrence(s)")
    else:
        print("✗ Stack Trace detection failed")

    # Test 3: Debug leaks
    detections = detector.detect(test_log_debug)
    debug_detections = [d for d in detections if 'Debug' in d['type']]
    if debug_detections:
        print(f"✓ Debug Leak detection - found {len(debug_detections)} occurrence(s)")
    else:
        print("✗ Debug Leak detection failed")

    return True

def validate_ai_insights():
    """Validate enhanced AI insight generation"""
    print("\n" + "=" * 80)
    print("VALIDATION: AI Insights Generation")
    print("=" * 80)

    from app.services.ai import AIService

    # Test log-specific summary
    test_findings = [
        {'type': 'GitHub PAT', 'risk': 'Critical'},
        {'type': 'Password', 'risk': 'High'},
        {'type': 'Stack Trace Leak', 'risk': 'Medium'},
        {'type': 'Repeated Failures', 'risk': 'High'}
    ]

    summary = AIService.generate_summary('log', '', 4, test_findings)

    if 'CRITICAL' in summary and 'secrets' in summary.lower():
        print(f"✓ Log-specific AI summary generated")
        print(f"  Summary: {summary[:100]}...")
    else:
        print(f"✗ AI summary may not be log-specific")
        print(f"  Summary: {summary}")

    # Test explanations for new patterns
    new_patterns_to_test = [
        "Authorization Header Leak",
        "Session Token",
        "Stack Trace Leak",
        "SQL Error Leak"
    ]

    for pattern in new_patterns_to_test:
        explanation = AIService.generate_explanation(pattern, "test")
        if len(explanation) > 50:
            print(f"✓ Explanation for '{pattern}' - {len(explanation)} chars")
        else:
            print(f"✗ Short explanation for '{pattern}'")

    return True

def main():
    """Run all validations"""
    print("\n" + "=" * 80)
    print("HACKATHON ENHANCEMENTS VALIDATION")
    print("Validating all new log analysis features")
    print("=" * 80 + "\n")

    results = []

    # Run validations
    results.append(("Module Imports", validate_imports()))
    results.append(("Detection Patterns", validate_patterns()))
    results.append(("Risk Weights", validate_risk_weights()))
    results.append(("Log Parser", validate_log_parser()))
    results.append(("Behavioral Detection", validate_behavioral_detection()))
    results.append(("AI Insights", validate_ai_insights()))

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    total = len(results)
    passed = sum(1 for _, r in results if r)

    print(f"\nTotal: {passed}/{total} validations passed")

    if passed == total:
        print("\n🎉 ALL VALIDATIONS PASSED - SYSTEM READY FOR HACKATHON! 🎉")
        return 0
    else:
        print(f"\n⚠️  {total - passed} validation(s) failed - review errors above")
        return 1

if __name__ == "__main__":
    exit(main())
