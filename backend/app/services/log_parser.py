"""
Advanced log file parser and analyzer
Handles log-specific parsing, chunking, and contextual analysis
"""
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum

class LogLevel(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    CRITICAL = "CRITICAL"

class LogEntry:
    """Represents a parsed log entry with metadata"""
    def __init__(
        self,
        line_number: int,
        raw_line: str,
        timestamp: Optional[str] = None,
        level: Optional[str] = None,
        message: str = "",
        metadata: Optional[Dict] = None
    ):
        self.line_number = line_number
        self.raw_line = raw_line
        self.timestamp = timestamp
        self.level = level
        self.message = message
        self.metadata = metadata or {}
        self.risk_annotations = []
        self.findings = []

class LogParser:
    """Advanced log parser with support for multiple log formats"""

    # Common log timestamp patterns
    TIMESTAMP_PATTERNS = [
        # ISO 8601: 2026-03-10T10:00:01.123Z
        r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:?\d{2})?',
        # Common format: 2026-03-10 10:00:01
        r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',
        # Unix timestamp with brackets: [1678456801]
        r'\[\d{10,13}\]',
        # Human readable: Mar 10 10:00:01
        r'[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}',
        # Nginx/Apache: 10/Mar/2026:10:00:01 +0000
        r'\d{2}/[A-Z][a-z]{2}/\d{4}:\d{2}:\d{2}:\d{2}\s+[+-]\d{4}',
    ]

    # Log level patterns
    LEVEL_PATTERN = r'\b(TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\b'

    def __init__(self):
        self.timestamp_regex = re.compile('|'.join(f'({p})' for p in self.TIMESTAMP_PATTERNS))
        self.level_regex = re.compile(self.LEVEL_PATTERN, re.IGNORECASE)

    def parse_log_file(self, content: str, max_lines: Optional[int] = None) -> List[LogEntry]:
        """
        Parse log file content into structured LogEntry objects

        Args:
            content: Raw log file content
            max_lines: Maximum lines to parse (for large files)

        Returns:
            List of LogEntry objects
        """
        lines = content.split('\n')
        if max_lines:
            lines = lines[:max_lines]

        entries = []
        for line_num, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            entry = self._parse_line(line_num, line)
            entries.append(entry)

        return entries

    def _parse_line(self, line_number: int, line: str) -> LogEntry:
        """Parse a single log line into a LogEntry"""
        timestamp = None
        level = None
        message = line
        metadata = {}

        # Extract timestamp
        timestamp_match = self.timestamp_regex.search(line)
        if timestamp_match:
            timestamp = timestamp_match.group(0)
            metadata['timestamp_format'] = 'detected'

        # Extract log level
        level_match = self.level_regex.search(line)
        if level_match:
            level = level_match.group(0).upper()

        # Extract key-value pairs (common in structured logs)
        kv_pairs = self._extract_key_value_pairs(line)
        if kv_pairs:
            metadata['structured_data'] = kv_pairs

        # Detect common log formats
        log_format = self._detect_log_format(line)
        if log_format:
            metadata['format'] = log_format

        return LogEntry(
            line_number=line_number,
            raw_line=line,
            timestamp=timestamp,
            level=level,
            message=message,
            metadata=metadata
        )

    def _extract_key_value_pairs(self, line: str) -> Dict[str, str]:
        """Extract key=value or key:value pairs from log line"""
        kv_pairs = {}

        # Pattern: key=value or key="value" or key: value
        patterns = [
            r'(\w+)=(["\']?)([^"\'\s,;]+)\2',  # key=value or key="value"
            r'(\w+):\s*(["\']?)([^"\'\s,;]+)\2',  # key: value
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                key = match.group(1)
                value = match.group(3)
                kv_pairs[key] = value

        return kv_pairs

    def _detect_log_format(self, line: str) -> Optional[str]:
        """Detect common log formats"""
        # Apache/Nginx combined log format
        if re.match(r'^\d+\.\d+\.\d+\.\d+ - -', line):
            return 'apache_combined'

        # JSON log
        if line.strip().startswith('{') and '"' in line:
            return 'json'

        # Syslog format
        if re.match(r'^[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}', line):
            return 'syslog'

        # Windows Event Log
        if 'EventID' in line or 'Source:' in line:
            return 'windows_event'

        return None

    def chunk_large_log(self, content: str, chunk_size: int = 10000) -> List[Tuple[int, str]]:
        """
        Chunk large log files for processing

        Args:
            content: Full log content
            chunk_size: Number of lines per chunk

        Returns:
            List of (start_line_number, chunk_content) tuples
        """
        lines = content.split('\n')
        chunks = []

        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            chunks.append((i + 1, chunk_content))

        return chunks

    def extract_log_context(self, entries: List[LogEntry], target_line: int, context_lines: int = 3) -> List[LogEntry]:
        """Extract context around a specific log line"""
        start_idx = max(0, target_line - context_lines - 1)
        end_idx = min(len(entries), target_line + context_lines)
        return entries[start_idx:end_idx]

class LogAnalyzer:
    """Advanced log analysis with behavioral and pattern-based detection"""

    def __init__(self):
        self.parser = LogParser()

    def analyze_log_patterns(self, entries: List[LogEntry]) -> Dict:
        """
        Perform comprehensive log analysis

        Returns analysis summary with:
        - Error rate
        - Log level distribution
        - Temporal patterns
        - Anomalies
        """
        total_entries = len(entries)
        if total_entries == 0:
            return self._empty_analysis()

        # Log level distribution
        level_counts = {}
        error_count = 0
        warning_count = 0

        for entry in entries:
            if entry.level:
                level_counts[entry.level] = level_counts.get(entry.level, 0) + 1
                if entry.level in ['ERROR', 'FATAL', 'CRITICAL']:
                    error_count += 1
                elif entry.level in ['WARN', 'WARNING']:
                    warning_count += 1

        error_rate = (error_count / total_entries) * 100
        warning_rate = (warning_count / total_entries) * 100

        # Detect suspicious patterns
        suspicious_patterns = self._detect_suspicious_patterns(entries)

        # Temporal analysis
        temporal_info = self._analyze_temporal_patterns(entries)

        return {
            'total_lines': total_entries,
            'level_distribution': level_counts,
            'error_count': error_count,
            'warning_count': warning_count,
            'error_rate': round(error_rate, 2),
            'warning_rate': round(warning_rate, 2),
            'suspicious_patterns': suspicious_patterns,
            'temporal_analysis': temporal_info,
            'has_structured_data': any(entry.metadata.get('structured_data') for entry in entries),
            'detected_formats': list(set(
                entry.metadata.get('format')
                for entry in entries
                if entry.metadata.get('format')
            ))
        }

    def _detect_suspicious_patterns(self, entries: List[LogEntry]) -> List[Dict]:
        """Detect suspicious behavioral patterns in logs"""
        patterns = []

        # 1. Repeated failed authentication attempts
        auth_failures = [
            e for e in entries
            if any(keyword in e.raw_line.lower()
                   for keyword in ['failed login', 'authentication failed', 'invalid credentials', 'unauthorized'])
        ]
        if len(auth_failures) >= 3:
            patterns.append({
                'type': 'repeated_auth_failures',
                'severity': 'high',
                'count': len(auth_failures),
                'description': f'Detected {len(auth_failures)} failed authentication attempts',
                'first_occurrence': auth_failures[0].line_number if auth_failures else None
            })

        # 2. Rapid error spike
        error_entries = [e for e in entries if e.level in ['ERROR', 'FATAL', 'CRITICAL']]
        if len(error_entries) > len(entries) * 0.1:  # >10% errors
            patterns.append({
                'type': 'error_spike',
                'severity': 'medium',
                'count': len(error_entries),
                'description': f'High error rate: {len(error_entries)} errors in {len(entries)} lines',
                'percentage': round((len(error_entries) / len(entries)) * 100, 2)
            })

        # 3. Suspicious IP patterns (multiple IPs in short time)
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = set()
        for entry in entries:
            matches = re.findall(ip_pattern, entry.raw_line)
            ips.update(matches)

        if len(ips) > 10:
            patterns.append({
                'type': 'multiple_ips',
                'severity': 'low',
                'count': len(ips),
                'description': f'Detected {len(ips)} unique IP addresses',
            })

        # 4. Stack trace chains (multiple consecutive stack traces)
        stack_trace_lines = []
        in_stack_trace = False
        current_trace_start = None

        for entry in entries:
            if any(keyword in entry.raw_line.lower()
                   for keyword in ['traceback', 'exception', 'stack trace', 'at line']):
                if not in_stack_trace:
                    in_stack_trace = True
                    current_trace_start = entry.line_number
            elif in_stack_trace and entry.raw_line.strip() == '':
                in_stack_trace = False
                if current_trace_start:
                    stack_trace_lines.append(current_trace_start)

        if len(stack_trace_lines) >= 2:
            patterns.append({
                'type': 'multiple_stack_traces',
                'severity': 'medium',
                'count': len(stack_trace_lines),
                'description': f'Detected {len(stack_trace_lines)} stack traces indicating system instability',
            })

        return patterns

    def _analyze_temporal_patterns(self, entries: List[LogEntry]) -> Dict:
        """Analyze temporal patterns in logs"""
        timestamps = [e.timestamp for e in entries if e.timestamp]

        return {
            'has_timestamps': len(timestamps) > 0,
            'timestamp_coverage': round((len(timestamps) / len(entries)) * 100, 2) if entries else 0,
            'total_entries': len(entries),
        }

    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'total_lines': 0,
            'level_distribution': {},
            'error_count': 0,
            'warning_count': 0,
            'error_rate': 0,
            'warning_rate': 0,
            'suspicious_patterns': [],
            'temporal_analysis': {
                'has_timestamps': False,
                'timestamp_coverage': 0,
                'total_entries': 0
            },
            'has_structured_data': False,
            'detected_formats': []
        }

    def annotate_with_findings(self, entries: List[LogEntry], findings: List[Dict]) -> List[LogEntry]:
        """Annotate log entries with security findings"""
        # Create a mapping of line numbers to findings
        line_to_findings = {}
        for finding in findings:
            line_num = finding.get('line', 0)
            if line_num not in line_to_findings:
                line_to_findings[line_num] = []
            line_to_findings[line_num].append(finding)

        # Annotate entries
        for entry in entries:
            if entry.line_number in line_to_findings:
                entry.findings = line_to_findings[entry.line_number]
                entry.risk_annotations = [f.get('risk', 'Unknown') for f in entry.findings]

        return entries
