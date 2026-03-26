"""
Quick Demo Validation - Ensures demo datasets work correctly
Run this before presenting to avoid embarrassment
"""

from app.services.detector import DetectorService

def validate():
    detector = DetectorService()
    passed = 0
    failed = 0

    print("\n" + "="*60)
    print("DEMO VALIDATION CHECK")
    print("="*60 + "\n")

    # Test 1: Clean case (should be low risk)
    print("[1/5] Testing Clean Case...")
    clean = '{"user": "john_doe", "email": "user@example.com"}'
    r = detector.detect(clean)
    critical = [x for x in r if x['risk'] == 'Critical']
    if len(critical) == 0:
        print("      PASS - No critical findings")
        passed += 1
    else:
        print(f"      FAIL - Found {len(critical)} critical (should be 0)")
        failed += 1

    # Test 2: GitHub PAT detection
    print("[2/5] Testing GitHub PAT...")
    pat = 'token = "ghp_abcdefghijklmnopqrstuvwxyz1234567890"'
    r = detector.detect(pat)
    if any(x['type'] == 'GitHub PAT' for x in r):
        print("      PASS - GitHub PAT detected")
        passed += 1
    else:
        print("      FAIL - GitHub PAT not detected")
        failed += 1

    # Test 3: AWS Key detection
    print("[3/5] Testing AWS Access Key...")
    aws = 'aws_key = AKIAIOSFODNN7EXAMPLE'
    r = detector.detect(aws)
    if any(x['type'] == 'AWS Access Key' for x in r):
        print("      PASS - AWS key detected")
        passed += 1
    else:
        print("      FAIL - AWS key not detected")
        failed += 1

    # Test 4: SQL Injection
    print("[4/5] Testing SQL Injection...")
    sql = "SELECT * FROM users WHERE id = 1 OR 1=1;"
    r = detector.detect(sql)
    if any(x['type'] == 'SQL Injection' for x in r):
        print("      PASS - SQL injection detected")
        passed += 1
    else:
        print("      FAIL - SQL injection not detected")
        failed += 1

    # Test 5: Repeated Failures
    print("[5/5] Testing Behavioral Detection...")
    logs = "\n".join([
        "ERROR Authentication failed for user admin",
        "ERROR Authentication failed for user admin",
        "ERROR Authentication failed for user admin",
        "ERROR Authentication failed for user admin",
        "ERROR Authentication failed for user admin",
    ])
    r = detector.detect(logs)
    if any('Repeated' in x['type'] for x in r):
        print("      PASS - Repeated failures detected")
        passed += 1
    else:
        print("      FAIL - Repeated failures not detected")
        print(f"        Got: {[x['type'] for x in r]}")
        failed += 1

    print("\n" + "="*60)
    if failed == 0:
        print(f"SUCCESS: All {passed} tests passed - Demo is ready!")
    else:
        print(f"FAILED: {passed} passed, {failed} failed - Fix before demo!")
    print("="*60 + "\n")

    return failed == 0

if __name__ == "__main__":
    success = validate()
    exit(0 if success else 1)
