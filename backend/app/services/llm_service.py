"""
LLM Integration Service with fallback mechanism
Supports OpenAI and Anthropic with graceful degradation to rule-based system
"""
import os
from typing import Optional, Dict, List
import asyncio

# Optional imports - graceful fallback if not available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMService:
    """
    Hybrid AI system: LLM with fallback to rule-based analysis
    """

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.llm_enabled = (OPENAI_AVAILABLE and self.openai_api_key) or \
                          (ANTHROPIC_AVAILABLE and self.anthropic_api_key)

        if self.llm_enabled:
            if OPENAI_AVAILABLE and self.openai_api_key:
                openai.api_key = self.openai_api_key
                self.provider = 'openai'
            elif ANTHROPIC_AVAILABLE and self.anthropic_api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                self.provider = 'anthropic'
        else:
            self.provider = 'rule-based'

    async def generate_summary_llm(self, input_type: str, content: str, findings_count: int) -> str:
        """
        Generate AI summary using LLM with timeout and error handling
        """
        prompt = f"""Analyze this {input_type} content for security issues.
Found {findings_count} potential security findings.

Content (first 1000 chars):
{content[:1000]}

Provide a concise 2-3 sentence security summary focusing on:
1. Overall security posture
2. Most critical risks
3. Recommended immediate actions
"""

        try:
            if self.provider == 'openai':
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        openai.ChatCompletion.create,
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a security analysis expert."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200,
                        temperature=0.7
                    ),
                    timeout=5.0
                )
                return response.choices[0].message.content.strip()

            elif self.provider == 'anthropic':
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.anthropic_client.messages.create,
                        model="claude-3-haiku-20240307",
                        max_tokens=200,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    ),
                    timeout=5.0
                )
                return response.content[0].text.strip()

        except asyncio.TimeoutError:
            return None  # Fallback to rule-based
        except Exception as e:
            print(f"LLM error: {e}")
            return None  # Fallback to rule-based

    def generate_summary_rule_based(self, input_type: str, findings_count: int, detections: List[Dict]) -> str:
        """
        Fallback rule-based summary generation
        """
        if findings_count == 0:
            return f"No security issues detected in this {input_type}. Content appears clean."

        # Analyze risk distribution
        risk_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        for detection in detections:
            risk_counts[detection.get('risk', 'Low')] += 1

        # Build summary based on risk profile
        if risk_counts['Critical'] > 0:
            summary = f"⚠️ CRITICAL: Found {risk_counts['Critical']} critical security issues requiring immediate attention. "
        elif risk_counts['High'] > 0:
            summary = f"⚠️ HIGH RISK: Detected {risk_counts['High']} high-risk security findings. "
        elif risk_counts['Medium'] > 0:
            summary = f"Medium risk: Identified {risk_counts['Medium']} medium-risk security concerns. "
        else:
            summary = f"Low risk: Found {risk_counts['Low']} low-risk findings. "

        # Add input-type specific context
        if input_type == "log":
            summary += "Review logs for suspicious patterns and potential intrusion attempts. "
        elif input_type == "sql":
            summary += "Check for SQL injection vulnerabilities and malicious queries. "
        elif input_type == "chat":
            summary += "Monitor for context leaks and sensitive information disclosure. "
        else:
            summary += "Review all findings and apply recommended security measures. "

        summary += f"Total findings: {findings_count}."

        return summary

    async def generate_summary(self, input_type: str, content: str, findings_count: int, detections: List[Dict]) -> str:
        """
        Main entry point: Try LLM first, fallback to rule-based
        """
        if self.llm_enabled:
            llm_result = await self.generate_summary_llm(input_type, content, findings_count)
            if llm_result:
                return f"[{self.provider.upper()}] {llm_result}"

        # Fallback to rule-based
        return self.generate_summary_rule_based(input_type, findings_count, detections)

    async def generate_explanation_llm(self, finding_type: str, matched_text: str) -> Optional[str]:
        """
        Generate finding explanation using LLM
        """
        prompt = f"""Explain this security finding in one concise sentence:
Type: {finding_type}
Detected text: {matched_text[:100]}

Focus on: why this is a security concern and what threat it poses."""

        try:
            if self.provider == 'openai':
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        openai.ChatCompletion.create,
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a security expert. Provide concise explanations."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=100,
                        temperature=0.7
                    ),
                    timeout=3.0
                )
                return response.choices[0].message.content.strip()

            elif self.provider == 'anthropic':
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.anthropic_client.messages.create,
                        model="claude-3-haiku-20240307",
                        max_tokens=100,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    ),
                    timeout=3.0
                )
                return response.content[0].text.strip()

        except:
            return None  # Fallback to rule-based

    def generate_explanation_rule_based(self, finding_type: str) -> str:
        """
        Fallback rule-based explanation generation
        """
        explanations = {
            "API Key": "Exposed API key can lead to unauthorized access and service abuse.",
            "Credit Card": "Credit card data exposure violates PCI-DSS and risks financial fraud.",
            "Email": "Email addresses may be used for phishing or social engineering attacks.",
            "IP Address": "IP address exposure can reveal network topology and enable targeted attacks.",
            "Password": "Password exposure enables account takeover and unauthorized access.",
            "SSH Key": "SSH key exposure grants direct server access to attackers.",
            "JWT Token": "JWT token leak allows session hijacking and impersonation.",
            "AWS Key": "AWS credentials leak can lead to cloud resource compromise and data breaches.",
            "Database Connection": "Database credentials enable direct data access and potential exfiltration.",
            "Private Key": "Private key exposure compromises encryption and authentication security.",
            "SQL Injection": "SQL injection allows attackers to manipulate database queries and extract data.",
            "XSS": "Cross-site scripting enables execution of malicious scripts in user browsers.",
            "Command Injection": "Command injection allows attackers to execute arbitrary system commands.",
            "Path Traversal": "Path traversal enables unauthorized access to filesystem directories.",
            "Hardcoded Secret": "Hardcoded secrets in code create persistent security vulnerabilities."
        }

        return explanations.get(
            finding_type,
            f"{finding_type} represents a potential security risk requiring investigation."
        )

    async def generate_explanation(self, finding_type: str, matched_text: str) -> str:
        """
        Main entry point: Try LLM first, fallback to rule-based
        """
        if self.llm_enabled:
            llm_result = await self.generate_explanation_llm(finding_type, matched_text)
            if llm_result:
                return llm_result

        # Fallback to rule-based
        return self.generate_explanation_rule_based(finding_type)

    def get_provider_info(self) -> Dict:
        """
        Return information about current AI provider
        """
        return {
            'provider': self.provider,
            'llm_enabled': self.llm_enabled,
            'openai_available': OPENAI_AVAILABLE and bool(self.openai_api_key),
            'anthropic_available': ANTHROPIC_AVAILABLE and bool(self.anthropic_api_key)
        }
