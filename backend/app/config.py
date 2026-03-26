"""
Risk scoring configuration - LOCKED to match API_CONTRACT.md
"""

# Risk score contributions per finding type
RISK_WEIGHTS = {
    # Critical: Cloud & Service Keys
    "GitHub PAT": 40,
    "GitHub OAuth": 40,
    "AWS Access Key": 40,
    "AWS Secret Key": 45,
    # "Azure Token": 40,  # Disabled - too many false positives
    "GCP API Key": 40,
    "Stripe Live Key": 40,
    "Stripe Test Key": 25,

    # Critical: Private Keys
    "Private Key": 45,
    "SSH Private Key": 45,
    "PGP Private Key": 45,

    # High: Tokens & Credentials
    "JWT Token": 35,
    "Bearer Token": 30,
    "Generic API Key": 35,
    "MongoDB URI": 35,
    "PostgreSQL Connection": 35,
    "MySQL Connection": 35,
    "Slack Token": 30,
    "Slack Webhook": 25,
    "Password": 30,

    # High: Security Vulnerabilities
    "SQL Injection": 30,
    "XSS Pattern": 25,
    "Command Injection": 35,
    "Credit Card": 35,

    # High: Log Anomalies
    "Repeated Failures": 25,

    # Medium: Config Leaks
    ".env Leak": 20,
    "Stack Trace": 15,

    # Low: PII & Info
    "Email Address": 5,
    "Phone Number": 5,
    "Username": 10,
    "IP Address": 3,
    "Debug Log Leak": 5,

    # NEW: Log-specific patterns (HIGH WEIGHT for hackathon)
    "Session Token": 35,
    "Access Token in Log": 35,
    "Authorization Header Leak": 45,  # Critical
    "Cookie with Secrets": 30,
    "Database Password in Connection String": 45,  # Critical
    "Hardcoded Secret": 35,
    "Internal Path Disclosure": 10,
    "Error with User Data": 25,
    "Stack Trace Leak": 20,
    "Suspicious IP Activity": 20,
    "Sensitive Data in Error": 30,
    "SQL Error Leak": 25,
}

# Risk level thresholds
RISK_THRESHOLDS = {
    "Low": (0, 29),
    "Medium": (30, 59),
    "High": (60, 84),
    "Critical": (85, 100),
}

def get_risk_level(score: int) -> str:
    """Determine risk level from score"""
    for level, (min_score, max_score) in RISK_THRESHOLDS.items():
        if min_score <= score <= max_score:
            return level
    return "Critical"  # Fallback for scores > 100

def get_primary_action(score: int, mask: bool, block_high_risk: bool) -> str:
    """Determine primary action based on score and options"""
    if score >= 85 and mask:
        return "Masked & Flagged"
    elif score >= 85 and block_high_risk:
        return "Block"
    elif score >= 85:
        return "Mask"
    elif score >= 30 and mask:
        return "Mask"
    else:
        return "Allow"
