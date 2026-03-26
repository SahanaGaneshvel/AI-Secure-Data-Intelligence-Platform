"""
Masking service - replace sensitive values with masked versions
"""
import re

class MaskerService:
    @staticmethod
    def mask_value(value: str, finding_type: str) -> str:
        """
        Mask a detected value based on its type
        Keep first/last few chars for context
        """
        if not value:
            return value

        length = len(value)

        # GitHub PAT: ghp_****************************
        if finding_type == "GitHub PAT":
            return f"{value[:4]}{'*' * (length - 4)}"

        # AWS Key: AKIA****************
        if finding_type == "AWS Key":
            return f"{value[:4]}{'*' * (length - 4)}"

        # JWT: eyJ...***
        if finding_type == "JWT Token":
            return f"{value[:10]}...{'*' * 10}"

        # Email: j**@company.com
        if finding_type == "Email Address":
            parts = value.split('@')
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                masked_username = username[0] + '*' * (len(username) - 1) if len(username) > 1 else '*'
                return f"{masked_username}@{domain}"

        # Password: ********
        if finding_type == "Password":
            return '*' * 8

        # API Key: show first 4, mask rest
        if finding_type == "API Key":
            if length > 8:
                return f"{value[:4]}{'*' * (length - 4)}"
            return '*' * length

        # Bearer Token: Bearer ****
        if finding_type == "Bearer Token":
            if value.startswith("Bearer "):
                return "Bearer " + '*' * (length - 7)
            return '*' * length

        # Private Key: mask entirely
        if finding_type == "Private Key":
            return "*** PRIVATE KEY REDACTED ***"

        # Phone: mask middle digits
        if finding_type == "Phone Number":
            digits = re.sub(r'\D', '', value)
            if len(digits) >= 10:
                return f"({digits[:3]}) ***-{digits[-4:]}"
            return '*' * length

        # IP Address: mask last octet
        if finding_type == "IP Address":
            parts = value.split('.')
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.{parts[2]}.***"

        # Default: mask most of it
        if length <= 3:
            return '*' * length
        elif length <= 8:
            return value[0] + '*' * (length - 1)
        else:
            return value[:3] + '*' * (length - 6) + value[-3:]

    @staticmethod
    def mask_content(content: str, detections: list) -> list[str]:
        """
        Apply masking to content based on detections
        Returns list of masked lines
        """
        lines = content.split('\n')
        masked_lines = lines.copy()

        # Group detections by line
        detections_by_line = {}
        for detection in detections:
            line_num = detection['line']
            if line_num not in detections_by_line:
                detections_by_line[line_num] = []
            detections_by_line[line_num].append(detection)

        # Apply masks line by line (in reverse order to preserve positions)
        for line_num, line_detections in detections_by_line.items():
            line_idx = line_num - 1
            if line_idx >= len(masked_lines):
                continue

            line = masked_lines[line_idx]
            # Sort by start position in reverse
            sorted_detections = sorted(line_detections, key=lambda d: d['start'], reverse=True)

            for detection in sorted_detections:
                start = detection['start']
                end = detection['end']
                matched_text = detection['matched_text']
                finding_type = detection['type']

                masked_value = MaskerService.mask_value(matched_text, finding_type)
                line = line[:start] + masked_value + line[end:]

            masked_lines[line_idx] = line

        return masked_lines

    @staticmethod
    def create_preview(matched_text: str, finding_type: str, max_length: int = 50) -> str:
        """
        Create a preview string for findings table
        """
        masked = MaskerService.mask_value(matched_text, finding_type)
        if len(masked) > max_length:
            return masked[:max_length - 3] + "..."
        return masked
