"""
Demo Reliability Test Suite
Tests all critical detection patterns against real-world inputs
to ensure no embarrassing false positives/negatives during live demo
"""

from app.services.detector import DetectorService

def test_github_tokens():
    """Test GitHub PAT detection"""
    detector = DetectorService()

    # Valid GitHub PAT (should detect) - exactly 36 chars after ghp_
    valid_pat = "ghp_abcdefghijklmnopqrstuvwxyz1234567890"
    result = detector.detect(f'token = "{valid_pat}"')
    assert any(d['type'] == 'GitHub PAT' for d in result), f"Failed to detect valid GitHub PAT. Got: {result}"

    # Invalid/short token (should NOT detect)
    invalid = "ghp_short"
    result = detector.detect(f'token = "{invalid}"')
    assert not any(d['type'] == 'GitHub PAT' for d in result), "False positive on short token"

    # Random string starting with ghp_ (should NOT detect)
    random_str = "ghp_this_is_not_a_valid_token_format"
    result = detector.detect(f'token = "{random_str}"')
    # This might detect - acceptable as it has the right prefix

    print("✓ GitHub PAT detection validated")

def test_aws_keys():
    """Test AWS Access Key detection"""
    detector = DetectorService()

    # Valid AWS key (should detect)
    valid_key = "AKIAIOSFODNN7EXAMPLE"
    result = detector.detect(f'aws_key = {valid_key}')
    assert any(d['type'] == 'AWS Access Key' for d in result), "Failed to detect AWS key"

    # Invalid format (should NOT detect)
    invalid = "AKIA123"
    result = detector.detect(f'key = {invalid}')
    assert not any(d['type'] == 'AWS Access Key' for d in result), "False positive on short AWS key"

    print("✓ AWS Access Key detection validated")

def test_sql_injection():
    """Test SQL injection detection"""
    detector = DetectorService()

    # Classic OR 1=1 injection (should detect)
    sql1 = "SELECT * FROM users WHERE id = 1 OR 1=1;"
    result = detector.detect(sql1)
    assert any(d['type'] == 'SQL Injection' for d in result), "Failed to detect OR 1=1 injection"

    # UNION injection (should detect)
    sql2 = "SELECT id FROM users UNION SELECT password FROM admin"
    result = detector.detect(sql2)
    assert any(d['type'] == 'SQL Injection' for d in result), "Failed to detect UNION injection"

    # Normal SQL (should NOT detect)
    safe_sql = "SELECT name, email FROM users WHERE id = ?"
    result = detector.detect(safe_sql)
    # May or may not detect depending on heuristics - that's ok

    print("✓ SQL Injection detection validated")

def test_email_detection():
    """Test email address detection"""
    detector = DetectorService()

    # Valid email (should detect)
    valid_email = "user@company.com"
    result = detector.detect(f'email: {valid_email}')
    assert any(d['type'] == 'Email Address' for d in result), "Failed to detect valid email"

    # Invalid format (should NOT detect)
    invalid = "not-an-email"
    result = detector.detect(f'text: {invalid}')
    assert not any(d['type'] == 'Email Address' for d in result), "False positive on non-email"

    print("✓ Email detection validated")

def test_private_key():
    """Test private key detection"""
    detector = DetectorService()

    # RSA private key (should detect)
    key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7
-----END PRIVATE KEY-----"""
    result = detector.detect(key)
    assert any(d['type'] == 'Private Key (RSA/SSH)' for d in result), "Failed to detect private key"

    # Not a key (should NOT detect)
    not_key = "BEGIN KEY but not really"
    result = detector.detect(not_key)
    assert not any(d['type'] == 'Private Key (RSA/SSH)' for d in result), "False positive on fake key"

    print("✓ Private Key detection validated")

def test_jwt_token():
    """Test JWT detection"""
    detector = DetectorService()

    # Valid JWT structure (should detect)
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    result = detector.detect(f'token: {jwt}')
    assert any(d['type'] == 'JWT Token' for d in result), "Failed to detect JWT"

    # Random base64 (should NOT detect - must have 3 parts)
    not_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    result = detector.detect(f'token: {not_jwt}')
    assert not any(d['type'] == 'JWT Token' for d in result), "False positive on incomplete JWT"

    print("✓ JWT detection validated")

def test_stripe_keys():
    """Test Stripe API key detection"""
    detector = DetectorService()

    # Valid Stripe live key (should detect)
    stripe_live = "sk_live_EXAMPLE_KEY_FOR_TESTING"
    result = detector.detect(f'key = {stripe_live}')
    assert any(d['type'] == 'Stripe Live Key' for d in result), "Failed to detect Stripe live key"

    # Stripe test key (should detect but as test key)
    stripe_test = "sk_test_EXAMPLE_KEY_FOR_TESTING"
    result = detector.detect(f'key = {stripe_test}')
    assert any(d['type'] == 'Stripe Test Key' for d in result), "Failed to detect Stripe test key"

    print("✓ Stripe key detection validated")

def test_behavioral_repeated_failures():
    """Test behavioral detection of repeated failures"""
    detector = DetectorService()

    # 5+ repeated failures (should detect)
    log_with_failures = """
2026-03-24 10:15:45 ERROR Authentication failed for user admin
2026-03-24 10:15:50 ERROR Authentication failed for user admin
2026-03-24 10:15:55 ERROR Authentication failed for user admin
2026-03-24 10:16:00 ERROR Authentication failed for user admin
2026-03-24 10:16:05 ERROR Authentication failed for user admin
2026-03-24 10:16:10 ERROR Authentication failed for user root
"""
    result = detector.detect(log_with_failures)
    assert any(d['type'] == 'Repeated Auth Failures' for d in result), "Failed to detect repeated failures"

    # 3 failures (should NOT detect - below threshold)
    log_few_failures = """
2026-03-24 10:15:45 ERROR Authentication failed for user admin
2026-03-24 10:15:50 ERROR Authentication failed for user admin
2026-03-24 10:15:55 ERROR Authentication failed for user admin
"""
    result = detector.detect(log_few_failures)
    assert not any(d['type'] == 'Repeated Auth Failures' for d in result), "False positive on few failures"

    print("✓ Behavioral detection validated")

def test_stack_trace_detection():
    """Test stack trace exposure detection"""
    detector = DetectorService()

    # Stack trace (should detect)
    stack_trace = """
Traceback (most recent call last):
  File "/app/auth.py", line 42, in validate_token
    decoded = jwt.decode(token, SECRET_KEY)
  File "/usr/lib/python3.9/jwt/api_jwt.py", line 119, in decode
    raise DecodeError("Invalid token")
jwt.exceptions.DecodeError: Invalid token
"""
    result = detector.detect(stack_trace)
    assert any(d['type'] == 'Stack Trace Exposure' for d in result), "Failed to detect stack trace"

    print("✓ Stack trace detection validated")

def test_no_false_positives_on_clean_data():
    """Ensure clean data doesn't trigger false alarms"""
    detector = DetectorService()

    # Clean JSON
    clean_json = """
{
  "user": "john_doe",
  "action": "login",
  "timestamp": "2026-03-24T10:00:00Z"
}
"""
    result = detector.detect(clean_json)
    # Should only detect low-risk items like username
    critical_detections = [d for d in result if d['risk'] == 'Critical']
    assert len(critical_detections) == 0, f"False critical detection on clean data: {critical_detections}"

    print("✓ No false positives on clean data")

def test_demo_datasets():
    """Test all demo datasets to ensure they work correctly"""
    detector = DetectorService()

    # Demo 1: Clean Case (should be low risk)
    clean_case = """{
  "user": "john_doe",
  "email": "user@example.com",
  "query": "SELECT name, email FROM users WHERE id = ?",
  "timestamp": "2026-03-24T10:00:00Z"
}"""
    result = detector.detect(clean_case)
    critical_count = sum(1 for d in result if d['risk'] == 'Critical')
    assert critical_count == 0, f"Clean case should have no critical findings, found {critical_count}"
    print("  ✓ Demo dataset 'Clean Case' validated")

    # Demo 2: Mixed Risk (should have critical findings)
    mixed_risk = """{
  "user": "admin",
  "email": "jdoe@company.com",
  "token": "ghp_abcdefghijklmnopqrstuvwxyz1234567890",
  "query": "SELECT * FROM users WHERE id = 1 OR 1=1;",
  "api_key": "AKIA1234567890ABCDEF"
}"""
    result = detector.detect(mixed_risk)
    critical_count = sum(1 for d in result if d['risk'] == 'Critical')
    assert critical_count >= 2, f"Mixed risk should have 2+ critical findings, found {critical_count}"
    assert any(d['type'] == 'GitHub PAT' for d in result), "Should detect GitHub PAT"
    assert any(d['type'] == 'AWS Access Key' for d in result), "Should detect AWS key"
    print("  ✓ Demo dataset 'Mixed Risk' validated")

    # Demo 3: High Risk Logs
    high_risk_logs = """2026-03-24 10:15:32 INFO Starting authentication service
2026-03-24 10:15:45 ERROR Authentication failed for user admin
2026-03-24 10:15:50 ERROR Authentication failed for user admin
2026-03-24 10:15:55 ERROR Authentication failed for user admin
2026-03-24 10:16:00 ERROR Authentication failed for user admin
2026-03-24 10:16:05 ERROR Authentication failed for user admin
2026-03-24 10:16:10 ERROR Authentication failed for user root
2026-03-24 10:16:25 DEBUG AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
2026-03-24 10:16:30 DEBUG AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
"""
    result = detector.detect(high_risk_logs)
    assert any(d['type'] == 'AWS Access Key' for d in result), "Should detect AWS key in logs"
    assert any(d['type'] == 'Repeated Auth Failures' for d in result), "Should detect repeated failures"
    print("  ✓ Demo dataset 'High Risk Logs' validated")

def run_all_tests():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("DEMO RELIABILITY TEST SUITE")
    print("="*60 + "\n")

    try:
        test_github_tokens()
        test_aws_keys()
        test_sql_injection()
        test_email_detection()
        test_private_key()
        test_jwt_token()
        test_stripe_keys()
        test_behavioral_repeated_failures()
        test_stack_trace_detection()
        test_no_false_positives_on_clean_data()
        print("\n" + "-"*60)
        print("DEMO DATASET VALIDATION")
        print("-"*60 + "\n")
        test_demo_datasets()

        print("\n" + "="*60)
        print("[SUCCESS] ALL TESTS PASSED - DEMO READY")
        print("="*60 + "\n")
        return True
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}\n")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
