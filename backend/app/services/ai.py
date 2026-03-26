"""
AI service - summary and explanations only
NOT used for detection at this stage
ENHANCED for log analysis insights
NOW WITH LLM INTEGRATION (Phase 4)
"""
from typing import List, Dict
from app.services.llm_service import LLMService
import asyncio

class AIService:
    def __init__(self):
        self.llm_service = LLMService()

    async def generate_summary_async(self, input_type: str, content: str, findings_count: int, findings: List[Dict] = None) -> str:
        """
        Async version using LLM service with fallback
        """
        findings = findings or []
        return await self.llm_service.generate_summary(input_type, content, findings_count, findings)

    async def generate_explanation_async(self, finding_type: str, matched_text: str) -> str:
        """
        Async version using LLM service with fallback
        """
        return await self.llm_service.generate_explanation(finding_type, matched_text)
    @staticmethod
    def generate_summary(input_type: str, content: str, findings_count: int, findings: List[Dict] = None) -> str:
        """
        Generate context summary with enhanced log analysis
        For now: rule-based, can add LLM later
        """
        findings = findings or []

        if input_type == "log":
            # Enhanced log-specific summary
            has_credentials = any(f.get('type') in ['Password', 'API Key', 'Generic API Key', 'Session Token', 'Bearer Token'] for f in findings)
            has_errors = any(f.get('type') in ['Stack Trace Leak', 'SQL Error Leak', 'Sensitive Data in Error'] for f in findings)
            has_attacks = any(f.get('type') in ['Repeated Failures', 'Suspicious IP Activity', 'SQL Injection'] for f in findings)
            has_secrets = any(f.get('type') in ['GitHub PAT', 'AWS Access Key', 'Private Key', 'Authorization Header Leak'] for f in findings)

            summary_parts = []
            if has_secrets:
                summary_parts.append("CRITICAL: Hardcoded secrets and API keys detected in logs")
            if has_credentials:
                summary_parts.append("sensitive credentials exposed")
            if has_errors:
                summary_parts.append("system errors with internal details leaked")
            if has_attacks:
                summary_parts.append("suspicious activity patterns indicating potential attacks")

            if summary_parts:
                return "Log analysis reveals: " + ", ".join(summary_parts) + "."
            else:
                return "Log file analyzed - no critical security issues detected, but found sensitive data that should be masked."

        elif input_type == "text":
            if "user" in content.lower() and "email" in content.lower():
                return "The input appears to be a JSON payload likely intended for an authentication or user query endpoint."
            elif "{" in content and "}" in content:
                return "The input appears to be a JSON payload containing structured data."
            else:
                return "The input contains unstructured text data."

        elif input_type == "sql":
            return "SQL query detected. Analyzed for injection patterns and sensitive data exposure."

        elif input_type == "chat":
            return "Chat conversation analyzed for sensitive information disclosure."

        elif input_type == "file":
            return "File content analyzed for security vulnerabilities and sensitive data."

        return "Input analyzed for security threats and sensitive data."

    @staticmethod
    def generate_explanation(finding_type: str, matched_text: str) -> str:
        """
        Generate explanation for a finding (ENHANCED with log-specific types)
        """
        explanations = {
            # Existing patterns
            "GitHub PAT": "Detected an active GitHub Personal Access Token (PAT). This token has been automatically masked in the output logs to prevent credential leakage.",
            "AWS Access Key": "Detected an AWS Access Key ID. This credential should be rotated immediately and AWS CloudTrail logs should be reviewed.",
            "AWS Secret Key": "Detected an AWS Secret Access Key. CRITICAL: Rotate immediately, review CloudTrail for unauthorized access.",
            "Private Key": "Detected a private cryptographic key. This should never be included in logs or transmitted over insecure channels.",
            "JWT Token": "Detected a JSON Web Token (JWT). If exposed, this could allow session hijacking or unauthorized access.",
            "Bearer Token": "Detected a Bearer token used for authentication. This should be kept confidential and transmitted only over secure channels.",
            "Generic API Key": "Detected an API key. This credential provides programmatic access and should be rotated if exposed.",
            "SQL Injection": "The query field contains a classic tautology (OR 1=1) strongly indicative of a SQL injection attempt.",
            "Password": "Detected a password field with a plain-text value. Passwords should always be hashed and never logged.",
            "Email Address": "Email address detected and masked to prevent PII leakage.",
            "Phone Number": "Phone number detected. This is personally identifiable information (PII) and has been masked.",
            "Username": f"Username field detected with value '{matched_text[:20]}...'.",
            "IP Address": "IP address detected. This may be considered PII depending on context.",
            "XSS Pattern": "Detected potential cross-site scripting (XSS) pattern. User input should be sanitized.",

            # NEW: Log-specific patterns
            "Session Token": "Session token detected in logs. This could allow session hijacking if logs are compromised. Sessions should be invalidated.",
            "Access Token in Log": "Access token logged in plain text. This violates secure logging practices and could enable unauthorized access.",
            "Authorization Header Leak": "CRITICAL: Authorization header with credentials detected in logs. This exposes authentication tokens to anyone with log access.",
            "Cookie with Secrets": "Sensitive cookie data detected in logs. Cookies containing session/auth data should never be logged.",
            "Database Password in Connection String": "CRITICAL: Database password detected in connection string within logs. Rotate credentials immediately.",
            "Hardcoded Secret": "Hardcoded secret detected. Secrets should be stored in secure vaults (e.g., HashiCorp Vault, AWS Secrets Manager).",
            "Internal Path Disclosure": "Internal file system path disclosed. This reveals server architecture and could aid attackers in reconnaissance.",
            "Error with User Data": "Error message contains user data. This violates data privacy and could expose sensitive information.",

            # Behavioral/Heuristic patterns
            "Repeated Failures": "Multiple failure events detected. This could indicate a brute-force attack, credential stuffing, or system malfunction.",
            "Stack Trace Leak": "Stack trace detected in logs. This exposes internal application structure, dependencies, and code paths to potential attackers.",
            "Debug Log Leak": "Debug statements found in logs. Production systems should not log debug information as it may contain sensitive data.",
            "Suspicious IP Activity": "High volume of unique IP addresses detected. This could indicate scanning activity, DDoS preparation, or botnet behavior.",
            "Sensitive Data in Error": "Error messages contain sensitive data (passwords, tokens, etc). This is a severe logging misconfiguration.",
            "SQL Error Leak": "SQL error messages detected. These expose database schema, table names, and query structure to potential attackers.",
        }

        return explanations.get(finding_type, f"Detected {finding_type}. Review for security implications.")
