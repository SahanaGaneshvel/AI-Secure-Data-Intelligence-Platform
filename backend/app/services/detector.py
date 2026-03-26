"""
Detection service - deterministic pattern matching
No AI/LLM at this stage - pure regex + heuristics
"""
import re
from typing import List, Dict, Optional

class DetectionPattern:
    def __init__(self, name: str, pattern: str, risk: str, detector: str):
        self.name = name
        self.pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self.risk = risk
        self.detector = detector

# Detection patterns - ordered by priority
PATTERNS = [
    # Critical: API Keys and Tokens
    DetectionPattern(
        "GitHub PAT",
        r"ghp_[a-zA-Z0-9]{36}",
        "Critical",
        "Regex"
    ),
    DetectionPattern(
        "GitHub OAuth",
        r"gho_[a-zA-Z0-9]{36}",
        "Critical",
        "Regex"
    ),
    DetectionPattern(
        "AWS Access Key",
        r"AKIA[0-9A-Z]{16}",
        "Critical",
        "Regex"
    ),
    DetectionPattern(
        "AWS Secret Key",
        r"aws_secret_access_key['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9/+=]{40})",
        "Critical",
        "Regex"
    ),
    # Azure Token pattern disabled - too many false positives
    # DetectionPattern(
    #     "Azure Token",
    #     r"[a-zA-Z0-9/+]{88}==",
    #     "Critical",
    #     "Regex"
    # ),
    DetectionPattern(
        "GCP API Key",
        r"AIza[0-9A-Za-z_-]{35}",
        "Critical",
        "Regex"
    ),
    DetectionPattern(
        "Stripe Live Key",
        r"sk_live_[0-9a-zA-Z]{24,}",
        "Critical",
        "Regex"
    ),
    DetectionPattern(
        "Stripe Test Key",
        r"sk_test_[0-9a-zA-Z]{24,}",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Private Key",
        r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        "Critical",
        "Regex"
    ),
    DetectionPattern(
        "SSH Private Key",
        r"-----BEGIN OPENSSH PRIVATE KEY-----",
        "Critical",
        "Regex"
    ),
    DetectionPattern(
        "PGP Private Key",
        r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
        "Critical",
        "Regex"
    ),

    # High: Tokens and Credentials
    DetectionPattern(
        "JWT Token",
        r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Bearer Token",
        r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Generic API Key",
        r"api[_-]?key['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "MongoDB URI",
        r"mongodb(\+srv)?://[^\s]+",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "PostgreSQL Connection",
        r"postgresql://[^\s]+",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "MySQL Connection",
        r"mysql://[^\s]+",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Slack Token",
        r"xox[baprs]-[0-9a-zA-Z]{10,48}",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Slack Webhook",
        r"https://hooks\.slack\.com/services/[A-Z0-9/]+",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Password",
        r"password['\"]?\s*[:=]\s*['\"]?([^\s'\"]{6,})",
        "High",
        "Regex"
    ),

    # High: Security Vulnerabilities
    DetectionPattern(
        "SQL Injection",
        r"(OR\s+1\s*=\s*1|UNION\s+SELECT|DROP\s+TABLE|DELETE\s+FROM|;--|\bEXEC\b|\bEXECUTE\b)",
        "High",
        "Heuristic"
    ),
    DetectionPattern(
        "XSS Pattern",
        r"<script[^>]*>.*?</script>|javascript:|onerror\s*=|onload\s*=",
        "High",
        "Heuristic"
    ),
    DetectionPattern(
        "Command Injection",
        r"[;&|]\s*(rm|curl|wget|bash|sh|nc|netcat|powershell)\s+",
        "High",
        "Heuristic"
    ),

    # Medium: Environment and Config
    DetectionPattern(
        ".env Leak",
        r"\.env|DATABASE_URL|SECRET_KEY|PRIVATE_KEY",
        "Medium",
        "Heuristic"
    ),

    # Low: PII and Basic Info
    DetectionPattern(
        "Email Address",
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "Low",
        "Regex"
    ),
    DetectionPattern(
        "Phone Number",
        r"(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "Low",
        "Regex"
    ),
    DetectionPattern(
        "Credit Card",
        r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Username",
        r"['\"]?user(name)?['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_-]{3,20})",
        "Low",
        "Heuristic"
    ),
    DetectionPattern(
        "IP Address",
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        "Low",
        "Regex"
    ),

    # Log-specific patterns (NEW)
    DetectionPattern(
        "Session Token",
        r"session[_-]?(id|token|key)['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{16,})",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Access Token in Log",
        r"access[_-]?token['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{20,})",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Authorization Header Leak",
        r"Authorization['\"]?\s*:\s*['\"]?(Bearer|Basic)\s+[a-zA-Z0-9_\-\.=]+",
        "Critical",
        "Regex"
    ),
    DetectionPattern(
        "Cookie with Secrets",
        r"Cookie['\"]?\s*:\s*['\"]?[^'\"]*(?:session|auth|token)=[a-zA-Z0-9_\-]{16,}",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Database Password in Connection String",
        r"password['\"]?\s*[:=]\s*['\"]?[^'\";\s]{3,}['\"]?\s*[;@]",
        "Critical",
        "Regex"
    ),
    DetectionPattern(
        "Hardcoded Secret",
        r"secret['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{12,})",
        "High",
        "Regex"
    ),
    DetectionPattern(
        "Internal Path Disclosure",
        r"(?:/var/www|/home|/usr/local|C:\\|D:\\)[/\\][\w/\\.-]+",
        "Low",
        "Heuristic"
    ),
    DetectionPattern(
        "Error with User Data",
        r"(?:error|exception|failed).*(?:user|email|password|token)",
        "Medium",
        "Heuristic"
    ),
]

class DetectorService:
    def __init__(self):
        self.patterns = PATTERNS

    def detect(self, content: str) -> List[Dict]:
        """
        Run all detection patterns on content
        Returns list of raw detections (before masking)
        """
        detections = []
        lines = content.split('\n')

        # Pattern-based detection
        for pattern_def in self.patterns:
            for line_num, line in enumerate(lines, start=1):
                matches = pattern_def.pattern.finditer(line)
                for match in matches:
                    matched_text = match.group(0)
                    detections.append({
                        "type": pattern_def.name,
                        "risk": pattern_def.risk,
                        "detector": pattern_def.detector,
                        "line": line_num,
                        "matched_text": matched_text,
                        "start": match.start(),
                        "end": match.end(),
                    })

        # Log intelligence - behavioral detection
        log_anomalies = self._detect_log_anomalies(lines)
        detections.extend(log_anomalies)

        return detections

    def _detect_log_anomalies(self, lines: List[str]) -> List[Dict]:
        """
        Detect behavioral anomalies in logs (ENHANCED for hackathon)
        """
        anomalies = []

        # 1. Repeated failures detection (brute-force indicator)
        failure_patterns = ["failed", "error", "denied", "unauthorized", "forbidden", "rejected", "invalid"]
        failure_lines = [(i+1, line) for i, line in enumerate(lines) if any(pattern in line.lower() for pattern in failure_patterns)]
        failure_count = len(failure_lines)

        if failure_count >= 5:
            # Check for rapid succession (potential brute-force)
            if failure_count >= 10:
                risk_level = "Critical"
                message = f"{failure_count} failures detected - possible brute-force attack"
            else:
                risk_level = "High"
                message = f"{failure_count} failure events detected"

            anomalies.append({
                "type": "Repeated Failures",
                "risk": risk_level,
                "detector": "Heuristic",
                "line": failure_lines[0][0],
                "matched_text": message,
                "start": 0,
                "end": len(failure_lines[0][1]) if failure_lines else 0,
            })

        # 2. Stack trace detection (multiple occurrences)
        stack_trace_indicators = ["traceback", "exception", "at line", "stacktrace", "raise ", "thrown", "at com.", "at java.", "at org."]
        stack_trace_lines = []
        for line_num, line in enumerate(lines, start=1):
            if any(indicator in line.lower() for indicator in stack_trace_indicators):
                stack_trace_lines.append((line_num, line))

        if stack_trace_lines:
            # Report first stack trace with count
            count = len(stack_trace_lines)
            risk = "High" if count >= 3 else "Medium"
            message = f"{count} stack trace(s) detected - system errors leaked" if count > 1 else "Stack trace detected - internal error exposed"

            anomalies.append({
                "type": "Stack Trace Leak",
                "risk": risk,
                "detector": "Heuristic",
                "line": stack_trace_lines[0][0],
                "matched_text": message,
                "start": 0,
                "end": len(stack_trace_lines[0][1]),
            })

        # 3. Debug/Trace log leak (production environment issue)
        debug_patterns = [r"\bDEBUG\b", r"\bTRACE\b", r"console\.log", r"print\(", r"var_dump", r"dd\(", r"dump\("]
        debug_count = 0
        first_debug_line = None

        for line_num, line in enumerate(lines, start=1):
            for pattern in debug_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    debug_count += 1
                    if first_debug_line is None:
                        first_debug_line = (line_num, line)
                    break

        if debug_count > 0:
            risk = "Medium" if debug_count >= 3 else "Low"
            message = f"{debug_count} debug statement(s) in logs - possible production misconfiguration"

            anomalies.append({
                "type": "Debug Log Leak",
                "risk": risk,
                "detector": "Heuristic",
                "line": first_debug_line[0],
                "matched_text": message,
                "start": 0,
                "end": len(first_debug_line[1]),
            })

        # 4. Multiple unique IPs (potential distributed attack or scanning)
        ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        unique_ips = set()
        for line in lines:
            ips = ip_pattern.findall(line)
            unique_ips.update(ips)

        if len(unique_ips) >= 15:
            # Find first line with IP
            for line_num, line in enumerate(lines, start=1):
                if ip_pattern.search(line):
                    anomalies.append({
                        "type": "Suspicious IP Activity",
                        "risk": "Medium",
                        "detector": "Heuristic",
                        "line": line_num,
                        "matched_text": f"{len(unique_ips)} unique IPs detected - potential scanning/distributed attack",
                        "start": 0,
                        "end": len(line),
                    })
                    break

        # 5. Sensitive data in error messages
        sensitive_in_error = []
        for line_num, line in enumerate(lines, start=1):
            line_lower = line.lower()
            if any(err in line_lower for err in ["error", "exception", "failed"]):
                # Check if line also contains sensitive patterns
                if any(sens in line_lower for sens in ["password", "token", "secret", "api_key", "credit_card"]):
                    sensitive_in_error.append((line_num, line))

        if sensitive_in_error:
            anomalies.append({
                "type": "Sensitive Data in Error",
                "risk": "High",
                "detector": "Heuristic",
                "line": sensitive_in_error[0][0],
                "matched_text": f"Sensitive data exposed in error messages ({len(sensitive_in_error)} occurrences)",
                "start": 0,
                "end": len(sensitive_in_error[0][1]),
            })

        # 6. SQL errors (potential injection attempts or DB issues)
        sql_error_keywords = ["sql syntax", "mysql error", "postgres error", "ora-", "sqlite error", "syntax error near"]
        sql_errors = []
        for line_num, line in enumerate(lines, start=1):
            if any(keyword in line.lower() for keyword in sql_error_keywords):
                sql_errors.append((line_num, line))

        if sql_errors:
            anomalies.append({
                "type": "SQL Error Leak",
                "risk": "High",
                "detector": "Heuristic",
                "line": sql_errors[0][0],
                "matched_text": f"{len(sql_errors)} SQL error(s) detected - database schema/structure leaked",
                "start": 0,
                "end": len(sql_errors[0][1]),
            })

        return anomalies

    def detect_lightweight(self, content: str) -> Dict[str, int]:
        """
        Lightweight detection for real-time preview
        Returns count by risk level (no line numbers)
        """
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for pattern_def in self.patterns:
            matches = pattern_def.pattern.findall(content)
            if matches:
                count = len(matches)
                risk_level = pattern_def.risk.lower()
                counts[risk_level] += count

        return counts
