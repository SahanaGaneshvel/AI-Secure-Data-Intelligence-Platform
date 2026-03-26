"""
Chat context engine - analyze multi-turn conversations for security risks
"""
import re
from typing import List, Dict
from datetime import datetime

class ChatMessage:
    """Represents a single chat message"""
    def __init__(self, content: str, speaker: str = "unknown", timestamp: str = None):
        self.content = content
        self.speaker = speaker
        self.timestamp = timestamp or datetime.now().isoformat()

class ChatContextEngine:
    """Analyze chat conversations for sensitive data leakage"""

    @staticmethod
    def parse_chat(content: str) -> List[ChatMessage]:
        """
        Parse chat content into individual messages

        Supports formats:
        - "Speaker: message"
        - "[Speaker] message"
        - "Speaker> message"
        - Plain multi-line (each line is a message)
        """
        messages = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            # Try to extract speaker
            speaker = "unknown"

            # Format: "Speaker: message"
            match = re.match(r'^([^:]+):\s*(.+)$', line)
            if match:
                speaker = match.group(1).strip()
                message_content = match.group(2).strip()
            # Format: "[Speaker] message"
            elif re.match(r'^\[([^\]]+)\]\s*(.+)$', line):
                match = re.match(r'^\[([^\]]+)\]\s*(.+)$', line)
                speaker = match.group(1).strip()
                message_content = match.group(2).strip()
            # Format: "Speaker> message"
            elif re.match(r'^([^>]+)>\s*(.+)$', line):
                match = re.match(r'^([^>]+)>\s*(.+)$', line)
                speaker = match.group(1).strip()
                message_content = match.group(2).strip()
            else:
                # Plain message
                message_content = line.strip()

            messages.append(ChatMessage(
                content=message_content,
                speaker=speaker,
                timestamp=f"line_{line_num}"
            ))

        return messages

    @staticmethod
    def analyze_conversation(messages: List[ChatMessage]) -> Dict:
        """
        Analyze entire conversation for security risks

        Returns:
            {
                'total_messages': int,
                'unique_speakers': int,
                'context_leaks': List[Dict],
                'progressive_disclosure': List[Dict],
                'summary': str
            }
        """
        if not messages:
            return {
                'total_messages': 0,
                'unique_speakers': 0,
                'context_leaks': [],
                'progressive_disclosure': [],
                'summary': 'No messages to analyze'
            }

        # Count unique speakers
        speakers = set(msg.speaker for msg in messages)

        # Detect context leaks (sensitive info mentioned in conversation)
        context_leaks = ChatContextEngine._detect_context_leaks(messages)

        # Detect progressive disclosure (info revealed across multiple messages)
        progressive_disclosure = ChatContextEngine._detect_progressive_disclosure(messages)

        # Generate summary
        summary = ChatContextEngine._generate_conversation_summary(
            messages, context_leaks, progressive_disclosure
        )

        return {
            'total_messages': len(messages),
            'unique_speakers': len(speakers),
            'speakers': list(speakers),
            'context_leaks': context_leaks,
            'progressive_disclosure': progressive_disclosure,
            'summary': summary
        }

    @staticmethod
    def _detect_context_leaks(messages: List[ChatMessage]) -> List[Dict]:
        """Detect sensitive information shared in conversation"""
        leaks = []

        # Patterns for sensitive data
        sensitive_patterns = {
            'password_mention': r'\b(password|pwd|pass)\b.*?[:\s]+([^\s]{6,})',
            'api_key_mention': r'\b(api[_\s]?key|token)\b.*?[:\s]+([a-zA-Z0-9_-]{20,})',
            'credential_sharing': r'\b(username|login|email)\b.*?[:\s]+([^\s@]+@[^\s]+)',
            'secret_sharing': r'\b(secret|private|confidential)\b.*?[:\s]+([^\s]{8,})',
        }

        for idx, msg in enumerate(messages):
            for pattern_name, pattern in sensitive_patterns.items():
                if re.search(pattern, msg.content, re.IGNORECASE):
                    leaks.append({
                        'message_index': idx,
                        'speaker': msg.speaker,
                        'leak_type': pattern_name,
                        'severity': 'High',
                        'excerpt': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content
                    })

        return leaks

    @staticmethod
    def _detect_progressive_disclosure(messages: List[ChatMessage]) -> List[Dict]:
        """
        Detect sensitive information revealed progressively across messages
        e.g., username in message 1, password in message 3
        """
        disclosures = []

        # Track what types of info have been mentioned
        mentioned_types = {}

        info_types = {
            'username': r'\b(username|user|login)\b',
            'password': r'\b(password|pwd|pass)\b',
            'email': r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'api_key': r'\b(api[_\s]?key|token)\b',
            'address': r'\b\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr)\b',
        }

        for idx, msg in enumerate(messages):
            for info_type, pattern in info_types.items():
                if re.search(pattern, msg.content, re.IGNORECASE):
                    if info_type not in mentioned_types:
                        mentioned_types[info_type] = []
                    mentioned_types[info_type].append({
                        'message_index': idx,
                        'speaker': msg.speaker
                    })

        # Check if multiple sensitive types mentioned across conversation
        if len(mentioned_types) >= 2:
            types_mentioned = list(mentioned_types.keys())
            disclosures.append({
                'type': 'Progressive Information Disclosure',
                'severity': 'Medium',
                'info_types': types_mentioned,
                'message_span': f"{min(min(v[0]['message_index'] for v in mentioned_types.values()))} - {max(max(v[0]['message_index'] for v in mentioned_types.values()))}",
                'description': f"Sensitive information of multiple types disclosed: {', '.join(types_mentioned)}"
            })

        return disclosures

    @staticmethod
    def _generate_conversation_summary(
        messages: List[ChatMessage],
        context_leaks: List[Dict],
        progressive_disclosure: List[Dict]
    ) -> str:
        """Generate summary of conversation analysis"""
        parts = []

        parts.append(f"Chat conversation with {len(messages)} message(s)")

        if context_leaks:
            parts.append(f"{len(context_leaks)} direct information leak(s) detected")

        if progressive_disclosure:
            parts.append(f"Progressive information disclosure across conversation")

        if not context_leaks and not progressive_disclosure:
            parts.append("no critical security issues detected in conversation")

        return ", ".join(parts)
