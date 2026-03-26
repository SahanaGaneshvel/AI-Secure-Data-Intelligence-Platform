"""
Test script for enhanced log analysis features
Validates all new log-specific detection patterns and behavioral analysis
"""
import requests
import json
from typing import Dict, List

API_URL = "http://localhost:8000/api/analyze"

def test_log_analysis(name: str, log_content: str, expected_patterns: List[str]):
    """Test log analysis and print results"""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")

    payload = {
        "inputType": "log",
        "content": log_content,
        "options": {
            "mask": True,
            "blockHighRisk": False,
            "advancedDetection": True
        }
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        # Print summary
        print(f"\nRisk Level: {result['overallRiskLevel']}")
        print(f"Risk Score: {result['overallRiskScore']}/100")
        print(f"Total Findings: {result['totalFindings']}")
        print(f"Action: {result['primaryAction']}")

        # Print AI summary
        print(f"\nAI Summary:")
        print(f"  {result['aiSummary']}")

        # Print findings by type
        print(f"\nFindings by Type:")
        findings_by_type = {}
        for finding in result['findings']:
            ftype = finding['type']
            if ftype not in findings_by_type:
                findings_by_type[ftype] = []
            findings_by_type[ftype].append(finding)

        for ftype, findings_list in sorted(findings_by_type.items()):
            risk = findings_list[0]['risk']
            count = len(findings_list)
            print(f"  [{risk:8}] {ftype}: {count} occurrence(s)")

        # Print risk distribution
        print(f"\nRisk Distribution:")
        dist = result['riskDistribution']
        print(f"  Critical: {dist['critical']}")
        print(f"  High:     {dist['high']}")
        print(f"  Medium:   {dist['medium']}")
        print(f"  Low:      {dist['low']}")

        # Print critical vulnerabilities
        if result.get('criticalVulnerabilities'):
            print(f"\nCritical Vulnerabilities:")
            for vuln in result['criticalVulnerabilities']:
                print(f"  - {vuln}")

        # Print behavioral anomalies
        if result.get('behavioralAnomalies'):
            print(f"\nBehavioral Anomalies:")
            for anomaly in result['behavioralAnomalies']:
                print(f"  - {anomaly}")

        # Print recommendations
        if result.get('recommendedActions'):
            print(f"\nRecommended Actions:")
            for rec in result['recommendedActions'][:5]:  # Show first 5
                print(f"  - {rec}")

        # Validate expected patterns
        print(f"\nPattern Detection Validation:")
        detected_types = set(f['type'] for f in result['findings'])
        for pattern in expected_patterns:
            found = pattern in detected_types or any(pattern.lower() in dt.lower() for dt in detected_types)
            status = "✓" if found else "✗"
            print(f"  {status} {pattern}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        return None

# Test Case 1: Comprehensive Log with Multiple Issues
log_comprehensive = """2026-03-25 08:00:00 INFO [Server] Starting API server
2026-03-25 08:00:01 INFO [DB] Connected to postgresql://admin:P@ssw0rd123@db.internal.com:5432/maindb
2026-03-25 08:00:05 INFO [Auth] JWT secret: super_secret_jwt_key_2026_prod
2026-03-25 08:15:23 DEBUG Request: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4ifQ.sig
2026-03-25 08:15:24 DEBUG Cookie: session_id=a7b3c9d1e5f2g8h4i6j0k; auth_token=secure_token_abc123xyz789
2026-03-25 08:20:10 ERROR Authentication failed for user: admin from 203.0.113.45
2026-03-25 08:20:15 ERROR Authentication failed for user: admin from 203.0.113.45
2026-03-25 08:20:20 ERROR Authentication failed for user: root from 203.0.113.45
2026-03-25 08:20:25 ERROR Authentication failed for user: admin from 203.0.113.46
2026-03-25 08:20:30 ERROR Authentication failed for user: admin from 203.0.113.47
2026-03-25 08:25:00 ERROR [API] Exception in /api/users endpoint
Traceback (most recent call last):
  File "/var/www/app/routes/users.py", line 145, in get_user_data
    user = User.query.filter_by(id=user_id).first()
sqlalchemy.exc.OperationalError: could not connect to server
2026-03-25 08:30:16 ERROR [Payment] password=user_pass_2026, api_key=sk_live_EXAMPLE_KEY_FOR_TESTING_ONLY
2026-03-25 08:35:22 INFO [Cache] redis://:cache_password_xyz@cache.internal:6379/0
2026-03-25 08:40:00 ERROR [DB] SQL Error: You have an error in your SQL syntax near WHERE user_id
2026-03-25 08:45:10 DEBUG console.log() {user: 'admin', token: 'secret_admin_token_xyz'}
2026-03-25 09:00:00 INFO [Integration] GitHub PAT: ghp_1234567890abcdefghijklmnopqrstuvwxyz
2026-03-25 09:05:15 DEBUG [AWS] AKIAIOSFODNN7EXAMPLE
"""

# Test Case 2: Brute Force Attack Log
log_bruteforce = """2026-03-25 10:00:00 INFO Login attempt from 192.168.1.100
2026-03-25 10:00:05 ERROR Authentication failed for admin
2026-03-25 10:00:10 ERROR Authentication failed for admin
2026-03-25 10:00:15 ERROR Authentication failed for root
2026-03-25 10:00:20 ERROR Authentication failed for user
2026-03-25 10:00:25 ERROR Authentication failed for admin
2026-03-25 10:00:30 ERROR Authentication failed for admin
2026-03-25 10:00:35 ERROR Authentication failed for admin
2026-03-25 10:00:40 ERROR Authentication failed for admin
2026-03-25 10:00:45 ERROR Authentication failed for admin
2026-03-25 10:00:50 ERROR Authentication failed for admin
2026-03-25 10:00:55 ERROR Authentication failed from 192.168.1.101
2026-03-25 10:01:00 ERROR Authentication failed from 192.168.1.102
"""

# Test Case 3: Stack Traces and Debug Leaks
log_errors = """2026-03-25 11:00:00 INFO Application started
2026-03-25 11:05:00 ERROR Unhandled exception
Traceback (most recent call last):
  File "app.py", line 42, in process
    result = handler.execute()
Exception: NullPointerException at com.example.Handler.execute(Handler.java:123)
2026-03-25 11:10:00 DEBUG print() called with sensitive data
2026-03-25 11:15:00 TRACE Entering authentication module
2026-03-25 11:20:00 DEBUG var_dump($user_credentials)
Exception in thread "main" java.lang.NullPointerException
    at com.example.Main.run(Main.java:56)
    at com.example.Application.start(Application.java:89)
2026-03-25 11:25:00 ERROR Another exception raised in module
"""

# Test Case 4: Secrets and Credentials Leak
log_secrets = """2026-03-25 12:00:00 INFO Starting payment processor
2026-03-25 12:00:05 INFO GitHub token: ghp_abcdefghijklmnopqrstuvwxyz1234567890
2026-03-25 12:00:10 INFO AWS keys - Access: AKIAIOSFODNN7EXAMPLE, Secret: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
2026-03-25 12:00:15 INFO Stripe key: sk_live_EXAMPLE_KEY_FOR_TESTING
2026-03-25 12:00:20 INFO DB password: MyS3cr3tP@ssw0rd!2026
2026-03-25 12:00:25 INFO API key: api_key=live_key_abc123xyz789def456ghi
2026-03-25 12:00:30 INFO Bearer token logged: Bearer abc123def456ghi789jkl012mno345pqr678stu
2026-03-25 12:00:35 DEBUG Authorization: Basic dXNlcjpwYXNzd29yZA==
"""

# Test Case 5: Multiple IPs (Distributed Attack)
log_ips = """2026-03-25 13:00:00 INFO Request from 192.168.1.1
2026-03-25 13:00:05 INFO Request from 192.168.1.2
2026-03-25 13:00:10 INFO Request from 192.168.1.3
2026-03-25 13:00:15 INFO Request from 10.0.0.1
2026-03-25 13:00:20 INFO Request from 10.0.0.2
2026-03-25 13:00:25 INFO Request from 172.16.0.1
2026-03-25 13:00:30 INFO Request from 172.16.0.2
2026-03-25 13:00:35 INFO Request from 203.0.113.1
2026-03-25 13:00:40 INFO Request from 203.0.113.2
2026-03-25 13:00:45 INFO Request from 198.51.100.1
2026-03-25 13:00:50 INFO Request from 198.51.100.2
2026-03-25 13:00:55 INFO Request from 203.0.113.3
2026-03-25 13:01:00 INFO Request from 203.0.113.4
2026-03-25 13:01:05 INFO Request from 198.51.100.3
2026-03-25 13:01:10 INFO Request from 198.51.100.4
2026-03-25 13:01:15 INFO Request from 192.168.2.1
"""

if __name__ == "__main__":
    print("\n" + "="*80)
    print("LOG ANALYSIS COMPREHENSIVE TEST SUITE")
    print("Testing enhanced log-specific detection and behavioral analysis")
    print("="*80)

    # Test 1: Comprehensive Log
    test_log_analysis(
        "Comprehensive Production Log",
        log_comprehensive,
        [
            "PostgreSQL Connection",
            "JWT Token",
            "Authorization Header Leak",
            "Cookie with Secrets",
            "Repeated Failures",
            "Stack Trace",
            "Password",
            "Stripe Live Key",
            "GitHub PAT",
            "AWS Access Key",
            "Debug Log Leak",
            "SQL Error Leak"
        ]
    )

    # Test 2: Brute Force
    test_log_analysis(
        "Brute Force Attack Detection",
        log_bruteforce,
        [
            "Repeated Failures",
            "IP Address"
        ]
    )

    # Test 3: Errors and Stack Traces
    test_log_analysis(
        "Stack Traces and Debug Leaks",
        log_errors,
        [
            "Stack Trace Leak",
            "Debug Log Leak"
        ]
    )

    # Test 4: Secrets Leak
    test_log_analysis(
        "Credentials and Secrets Exposure",
        log_secrets,
        [
            "GitHub PAT",
            "AWS Access Key",
            "AWS Secret Key",
            "Stripe Live Key",
            "Password",
            "Generic API Key",
            "Bearer Token",
            "Authorization Header Leak"
        ]
    )

    # Test 5: Multiple IPs
    test_log_analysis(
        "Distributed Attack (Multiple IPs)",
        log_ips,
        [
            "IP Address",
            "Suspicious IP Activity"
        ]
    )

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)
