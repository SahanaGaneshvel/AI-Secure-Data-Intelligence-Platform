"""
Cross-log correlation and temporal analysis engine
Detects patterns across multiple logs and time-based anomalies
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import re
from collections import defaultdict

class CorrelationEngine:
    """
    Analyzes patterns across multiple log entries and time windows
    """

    # Temporal thresholds
    RAPID_SUCCESSION_SECONDS = 5
    SUSPICIOUS_PATTERN_THRESHOLD = 3  # Number of occurrences to flag

    @staticmethod
    def parse_timestamp(line: str) -> Optional[datetime]:
        """
        Extract timestamp from log line
        Supports common log formats:
        - ISO 8601: 2024-01-15T10:30:45Z
        - Apache: [15/Jan/2024:10:30:45 +0000]
        - Syslog: Jan 15 10:30:45
        - Custom: 2024-01-15 10:30:45
        """
        # ISO 8601
        iso_pattern = r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})'
        match = re.search(iso_pattern, line)
        if match:
            try:
                return datetime.strptime(match.group(1).replace('T', ' '), '%Y-%m-%d %H:%M:%S')
            except:
                pass

        # Apache format
        apache_pattern = r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})'
        match = re.search(apache_pattern, line)
        if match:
            try:
                return datetime.strptime(match.group(1), '%d/%b/%Y:%H:%M:%S')
            except:
                pass

        # Syslog format (add current year)
        syslog_pattern = r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'
        match = re.search(syslog_pattern, line)
        if match:
            try:
                current_year = datetime.now().year
                return datetime.strptime(f"{match.group(1)} {current_year}", '%b %d %H:%M:%S %Y')
            except:
                pass

        return None

    @staticmethod
    def detect_rapid_succession(log_lines: List[str], keyword: str) -> List[Dict]:
        """
        Detect events happening in rapid succession
        Returns list of suspicious time windows
        """
        events = []

        for i, line in enumerate(log_lines):
            if keyword.lower() in line.lower():
                timestamp = CorrelationEngine.parse_timestamp(line)
                if timestamp:
                    events.append({
                        'line': i + 1,
                        'timestamp': timestamp,
                        'content': line.strip()
                    })

        # Find clusters of events within RAPID_SUCCESSION_SECONDS
        clusters = []
        if len(events) >= CorrelationEngine.SUSPICIOUS_PATTERN_THRESHOLD:
            for i in range(len(events) - 2):
                time_diff = (events[i + 2]['timestamp'] - events[i]['timestamp']).total_seconds()
                if time_diff <= CorrelationEngine.RAPID_SUCCESSION_SECONDS:
                    clusters.append({
                        'start_line': events[i]['line'],
                        'end_line': events[i + 2]['line'],
                        'event_count': 3,
                        'time_window_seconds': time_diff,
                        'pattern': keyword
                    })

        return clusters

    @staticmethod
    def detect_failed_login_attempts(log_lines: List[str]) -> Dict:
        """
        Detect multiple failed login attempts (potential brute force)
        """
        failed_patterns = [
            r'failed\s+login',
            r'authentication\s+failed',
            r'invalid\s+password',
            r'login\s+failed',
            r'failed\s+authentication'
        ]

        failed_events = []
        for i, line in enumerate(log_lines):
            for pattern in failed_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    timestamp = CorrelationEngine.parse_timestamp(line)
                    # Extract username/IP if present
                    user_match = re.search(r'user[=:\s]+([^\s,]+)', line, re.IGNORECASE)
                    ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)

                    failed_events.append({
                        'line': i + 1,
                        'timestamp': timestamp,
                        'user': user_match.group(1) if user_match else 'unknown',
                        'ip': ip_match.group(0) if ip_match else 'unknown',
                        'content': line.strip()
                    })
                    break

        # Analyze patterns
        analysis = {
            'total_failures': len(failed_events),
            'unique_users': len(set(e['user'] for e in failed_events)),
            'unique_ips': len(set(e['ip'] for e in failed_events)),
            'is_brute_force': False,
            'targeted_accounts': []
        }

        # Detect brute force patterns
        if len(failed_events) >= 5:
            analysis['is_brute_force'] = True

            # Find most targeted accounts
            user_counts = defaultdict(int)
            for event in failed_events:
                user_counts[event['user']] += 1

            analysis['targeted_accounts'] = [
                {'user': user, 'attempts': count}
                for user, count in sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
                if count >= 3
            ]

        return analysis

    @staticmethod
    def detect_privilege_escalation(log_lines: List[str]) -> List[Dict]:
        """
        Detect potential privilege escalation attempts
        """
        escalation_patterns = [
            r'sudo\s+',
            r'su\s+-',
            r'privilege.*escalat',
            r'root\s+access',
            r'admin\s+rights',
            r'elevation.*request'
        ]

        events = []
        for i, line in enumerate(log_lines):
            for pattern in escalation_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    timestamp = CorrelationEngine.parse_timestamp(line)
                    events.append({
                        'line': i + 1,
                        'timestamp': timestamp,
                        'pattern': pattern,
                        'content': line.strip()
                    })
                    break

        return events

    @staticmethod
    def detect_data_exfiltration(log_lines: List[str]) -> Dict:
        """
        Detect potential data exfiltration patterns
        """
        exfil_patterns = {
            'large_transfer': r'transfer.*(\d+)\s*(mb|gb)',
            'download': r'download.*file',
            'export': r'export.*data',
            'copy': r'copy.*to.*external'
        }

        events = []
        for i, line in enumerate(log_lines):
            for pattern_name, pattern in exfil_patterns.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    size_match = re.search(r'(\d+)\s*(kb|mb|gb)', line, re.IGNORECASE)
                    events.append({
                        'line': i + 1,
                        'type': pattern_name,
                        'size': size_match.group(0) if size_match else 'unknown',
                        'content': line.strip()
                    })

        return {
            'potential_exfiltration': len(events) > 0,
            'event_count': len(events),
            'events': events
        }

    @staticmethod
    def analyze_temporal_patterns(log_lines: List[str]) -> Dict:
        """
        Analyze time-based patterns across all logs
        """
        timestamps = []
        for line in log_lines:
            ts = CorrelationEngine.parse_timestamp(line)
            if ts:
                timestamps.append(ts)

        if not timestamps:
            return {'has_temporal_data': False}

        timestamps.sort()

        # Calculate time gaps
        gaps = []
        for i in range(1, len(timestamps)):
            gap = (timestamps[i] - timestamps[i-1]).total_seconds()
            gaps.append(gap)

        # Detect anomalies
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        unusual_gaps = [g for g in gaps if g > avg_gap * 3]  # 3x average is unusual

        return {
            'has_temporal_data': True,
            'total_entries': len(timestamps),
            'time_span_seconds': (timestamps[-1] - timestamps[0]).total_seconds(),
            'average_gap_seconds': avg_gap,
            'unusual_gaps_count': len(unusual_gaps),
            'first_event': timestamps[0].isoformat(),
            'last_event': timestamps[-1].isoformat()
        }

    @staticmethod
    def generate_insights(content: str, detections: List[Dict]) -> List[str]:
        """
        Generate cross-log correlation insights
        Main entry point for correlation analysis
        """
        log_lines = content.split('\n')
        insights = []

        # Temporal analysis
        temporal = CorrelationEngine.analyze_temporal_patterns(log_lines)
        if temporal.get('has_temporal_data'):
            insights.append(
                f"Analyzed {temporal['total_entries']} timestamped events spanning "
                f"{int(temporal['time_span_seconds'])} seconds"
            )
            if temporal['unusual_gaps_count'] > 0:
                insights.append(
                    f"Detected {temporal['unusual_gaps_count']} unusual time gaps (potential log tampering)"
                )

        # Failed login analysis
        login_analysis = CorrelationEngine.detect_failed_login_attempts(log_lines)
        if login_analysis['total_failures'] > 0:
            insights.append(
                f"Found {login_analysis['total_failures']} failed login attempts "
                f"across {login_analysis['unique_users']} users"
            )
            if login_analysis['is_brute_force']:
                insights.append("⚠️ Potential brute force attack detected")
                if login_analysis['targeted_accounts']:
                    top_target = login_analysis['targeted_accounts'][0]
                    insights.append(
                        f"Most targeted account: {top_target['user']} ({top_target['attempts']} attempts)"
                    )

        # Privilege escalation
        escalation_events = CorrelationEngine.detect_privilege_escalation(log_lines)
        if len(escalation_events) > 0:
            insights.append(
                f"Detected {len(escalation_events)} privilege escalation attempts"
            )

        # Data exfiltration
        exfil = CorrelationEngine.detect_data_exfiltration(log_lines)
        if exfil['potential_exfiltration']:
            insights.append(
                f"⚠️ Potential data exfiltration detected ({exfil['event_count']} suspicious events)"
            )

        # Rapid succession patterns for critical keywords
        critical_keywords = ['error', 'failed', 'denied', 'unauthorized']
        for keyword in critical_keywords:
            clusters = CorrelationEngine.detect_rapid_succession(log_lines, keyword)
            if clusters:
                insights.append(
                    f"Rapid succession of '{keyword}' events detected "
                    f"({len(clusters)} clusters within {CorrelationEngine.RAPID_SUCCESSION_SECONDS}s windows)"
                )

        return insights
