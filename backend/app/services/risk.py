"""
Risk calculation service
Deterministic scoring based on findings
"""
from app.config import RISK_WEIGHTS, get_risk_level, get_primary_action
from app.models import RiskDistribution, RiskScoreBreakdownItem

class RiskService:
    @staticmethod
    def calculate_score(detections: list) -> tuple[int, list[RiskScoreBreakdownItem]]:
        """
        Calculate overall risk score and breakdown
        Returns (total_score, breakdown_items)
        """
        breakdown = {}

        for detection in detections:
            finding_type = detection['type']
            weight = RISK_WEIGHTS.get(finding_type, 5)  # Default weight if not in config

            if finding_type in breakdown:
                breakdown[finding_type] += weight
            else:
                breakdown[finding_type] = weight

        # Convert to breakdown items
        breakdown_items = [
            RiskScoreBreakdownItem(finding=finding_type, contribution=score)
            for finding_type, score in breakdown.items()
        ]

        # Calculate total (capped at 100)
        total_score = min(100, sum(breakdown.values()))

        return total_score, breakdown_items

    @staticmethod
    def calculate_distribution(detections: list) -> RiskDistribution:
        """
        Calculate distribution of findings by risk level
        """
        distribution = RiskDistribution()

        for detection in detections:
            risk_level = detection['risk'].lower()
            if risk_level == "critical":
                distribution.critical += 1
            elif risk_level == "high":
                distribution.high += 1
            elif risk_level == "medium":
                distribution.medium += 1
            elif risk_level == "low":
                distribution.low += 1

        return distribution

    @staticmethod
    def get_vulnerabilities(detections: list) -> list[str]:
        """
        Extract critical vulnerabilities for AI panel
        """
        vulnerabilities = []

        for detection in detections:
            if detection['risk'] == "Critical":
                finding_type = detection['type']
                if finding_type == "GitHub PAT":
                    vulnerabilities.append(
                        "Detected an active GitHub Personal Access Token (PAT). "
                        "This token has been automatically masked in the output logs to prevent credential leakage."
                    )
                elif finding_type == "AWS Key":
                    vulnerabilities.append(
                        "Detected an AWS Access Key. This credential provides access to AWS resources "
                        "and should be rotated immediately."
                    )
                elif finding_type == "Private Key":
                    vulnerabilities.append(
                        "Detected a private cryptographic key. This should never be included in logs or transmitted."
                    )

        return list(set(vulnerabilities))  # Remove duplicates

    @staticmethod
    def get_anomalies(detections: list) -> list[str]:
        """
        Extract behavioral anomalies
        """
        anomalies = []

        for detection in detections:
            finding_type = detection['type']
            if finding_type == "SQL Injection":
                anomalies.append(
                    f"The query field contains a classic tautology (OR 1=1) "
                    f"strongly indicative of a SQL injection attempt."
                )

        return list(set(anomalies))

    @staticmethod
    def get_recommendations(detections: list, options: dict) -> list[str]:
        """
        Generate recommended actions based on findings
        """
        recommendations = []
        finding_types = {d['type'] for d in detections}

        if "GitHub PAT" in finding_types:
            recommendations.append("Rotate the exposed GitHub PAT immediately.")

        if "AWS Key" in finding_types:
            recommendations.append("Rotate the AWS credentials and review CloudTrail logs for unauthorized access.")

        if "SQL Injection" in finding_types:
            recommendations.append("Ensure parameterized queries are used on the backend handling this payload.")

        if "Private Key" in finding_types:
            recommendations.append("Revoke and regenerate the exposed private key. Audit all systems that may have been compromised.")

        if "Password" in finding_types:
            recommendations.append("Change the exposed password immediately and enable multi-factor authentication.")

        # Generic recommendations
        if len(detections) > 0 and options.get('mask'):
            recommendations.append("Continue using output masking to prevent future leakage in logs.")

        return recommendations
