"""
Policy engine - simple rule-based policies
"""
from typing import Dict

# Default policy configuration
DEFAULT_POLICY = {
    "name": "default",
    "block_high_risk": False,
    "mask_all_secrets": True,
    "critical_threshold": 85,
    "high_threshold": 60,
    "auto_rotate_keys": False,
    "alert_on_critical": True,
    "enabled_detectors": "all",  # or list of specific detectors
}

# In-memory policy storage (can be moved to DB later)
_current_policy = DEFAULT_POLICY.copy()

class PolicyEngine:
    @staticmethod
    def get_policy() -> Dict:
        """Get current policy"""
        return _current_policy.copy()

    @staticmethod
    def update_policy(updates: Dict) -> Dict:
        """Update policy with new values"""
        _current_policy.update(updates)
        return _current_policy.copy()

    @staticmethod
    def reset_policy() -> Dict:
        """Reset to default policy"""
        global _current_policy
        _current_policy = DEFAULT_POLICY.copy()
        return _current_policy.copy()

    @staticmethod
    def evaluate_action(score: int, risk_level: str, options: Dict) -> str:
        """
        Evaluate what action to take based on policy and score
        """
        policy = PolicyEngine.get_policy()

        # Critical threshold
        if score >= policy["critical_threshold"]:
            if policy["block_high_risk"] and options.get("blockHighRisk"):
                return "Block"
            elif policy["mask_all_secrets"] and options.get("mask"):
                return "Masked & Flagged"
            else:
                return "Mask"

        # High threshold
        elif score >= policy["high_threshold"]:
            if policy["mask_all_secrets"] and options.get("mask"):
                return "Mask"
            else:
                return "Allow"

        # Below high threshold
        else:
            if options.get("mask") and score >= 30:
                return "Mask"
            else:
                return "Allow"

    @staticmethod
    def should_alert(score: int, risk_level: str) -> bool:
        """
        Determine if an alert should be sent
        """
        policy = PolicyEngine.get_policy()
        return policy["alert_on_critical"] and risk_level == "Critical"

    @staticmethod
    def is_detector_enabled(detector_name: str) -> bool:
        """
        Check if a specific detector is enabled
        """
        policy = PolicyEngine.get_policy()
        enabled = policy.get("enabled_detectors", "all")

        if enabled == "all":
            return True
        elif isinstance(enabled, list):
            return detector_name in enabled
        else:
            return False
