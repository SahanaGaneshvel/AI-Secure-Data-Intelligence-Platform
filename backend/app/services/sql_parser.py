"""
SQL parsing and analysis service
Detects dangerous patterns, injection attempts, and classifies queries
"""
import sqlparse
from typing import List, Dict
import re

class SQLParserService:
    """Parse and analyze SQL queries for security threats"""

    # Dangerous SQL keywords and patterns
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'EXEC',
        'EXECUTE', 'SCRIPT', 'SHUTDOWN', 'GRANT', 'REVOKE'
    ]

    INJECTION_PATTERNS = [
        r"('\s*OR\s+'?\d*'?\s*=\s*'?\d*)",  # OR 1=1
        r"('\s*OR\s+'[^']*'\s*=\s*'[^']*)",  # OR 'x'='x'
        r"(--|\#|\/\*)",  # SQL comments
        r"(;\s*DROP)",  # Statement chaining with DROP
        r"(UNION\s+SELECT)",  # UNION based injection
        r"(UNION\s+ALL\s+SELECT)",  # UNION ALL based injection
        r"(WAITFOR\s+DELAY)",  # Time-based blind injection
        r"(BENCHMARK\s*\()",  # MySQL benchmark function
        r"(SLEEP\s*\()",  # Sleep function
        r"(LOAD_FILE\s*\()",  # File system access
        r"(INTO\s+OUTFILE)",  # Write to file
        r"(xp_cmdshell)",  # Command execution (MSSQL)
    ]

    @staticmethod
    def parse_sql(content: str) -> List[Dict]:
        """
        Parse SQL content and detect security issues

        Returns list of analysis results
        """
        results = []

        try:
            # Parse SQL statements
            statements = sqlparse.split(content)

            for idx, statement in enumerate(statements, start=1):
                if not statement.strip():
                    continue

                # Parse the statement
                parsed = sqlparse.parse(statement)[0] if sqlparse.parse(statement) else None

                if parsed:
                    analysis = {
                        'statement_num': idx,
                        'statement': statement.strip(),
                        'type': SQLParserService._get_statement_type(parsed),
                        'dangerous': SQLParserService._is_dangerous(statement),
                        'injection_risk': SQLParserService._detect_injection(statement),
                        'findings': []
                    }

                    # Check for dangerous keywords
                    for keyword in SQLParserService.DANGEROUS_KEYWORDS:
                        if re.search(rf'\b{keyword}\b', statement, re.IGNORECASE):
                            analysis['findings'].append({
                                'type': 'Dangerous SQL Keyword',
                                'keyword': keyword,
                                'risk': 'High'
                            })

                    # Check for injection patterns
                    injection_patterns = SQLParserService._check_injection_patterns(statement)
                    analysis['findings'].extend(injection_patterns)

                    results.append(analysis)

        except Exception as e:
            # If parsing fails, still analyze as raw text
            results.append({
                'statement_num': 1,
                'statement': content[:500],
                'type': 'UNKNOWN',
                'dangerous': SQLParserService._is_dangerous(content),
                'injection_risk': SQLParserService._detect_injection(content),
                'findings': SQLParserService._check_injection_patterns(content),
                'parse_error': str(e)
            })

        return results

    @staticmethod
    def _get_statement_type(parsed) -> str:
        """Get SQL statement type (SELECT, INSERT, etc.)"""
        try:
            return parsed.get_type()
        except:
            # Fallback: check first keyword
            tokens = [t for t in parsed.tokens if not t.is_whitespace]
            if tokens:
                return str(tokens[0]).upper()
            return "UNKNOWN"

    @staticmethod
    def _is_dangerous(statement: str) -> bool:
        """Check if statement contains dangerous keywords"""
        for keyword in SQLParserService.DANGEROUS_KEYWORDS:
            if re.search(rf'\b{keyword}\b', statement, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def _detect_injection(statement: str) -> str:
        """Detect SQL injection risk level"""
        risk_score = 0

        for pattern in SQLParserService.INJECTION_PATTERNS:
            if re.search(pattern, statement, re.IGNORECASE):
                risk_score += 1

        if risk_score >= 3:
            return "Critical"
        elif risk_score >= 2:
            return "High"
        elif risk_score >= 1:
            return "Medium"
        else:
            return "Low"

    @staticmethod
    def _check_injection_patterns(statement: str) -> List[Dict]:
        """Check for specific injection patterns"""
        findings = []

        # OR 1=1 pattern
        if re.search(r"'\s*OR\s+'?\d*'?\s*=\s*'?\d*", statement, re.IGNORECASE):
            findings.append({
                'type': 'SQL Injection - Tautology',
                'pattern': "OR 1=1 or similar",
                'risk': 'Critical',
                'description': 'Classic authentication bypass pattern'
            })

        # UNION SELECT
        if re.search(r'UNION\s+(ALL\s+)?SELECT', statement, re.IGNORECASE):
            findings.append({
                'type': 'SQL Injection - UNION',
                'pattern': "UNION SELECT",
                'risk': 'High',
                'description': 'Attempt to combine queries and extract data'
            })

        # Comment-based injection
        if re.search(r'(--|\#|\/\*)', statement):
            findings.append({
                'type': 'SQL Injection - Comment',
                'pattern': "SQL comment markers",
                'risk': 'Medium',
                'description': 'Comment markers used to bypass query logic'
            })

        # Statement chaining
        if re.search(r';\s*\w+', statement):
            findings.append({
                'type': 'SQL Injection - Stacked Queries',
                'pattern': "Multiple statements",
                'risk': 'High',
                'description': 'Attempt to execute multiple SQL commands'
            })

        # Time-based blind injection
        if re.search(r'(WAITFOR|SLEEP|BENCHMARK)', statement, re.IGNORECASE):
            findings.append({
                'type': 'SQL Injection - Time-based Blind',
                'pattern': "SLEEP/WAITFOR/BENCHMARK",
                'risk': 'High',
                'description': 'Time-based blind SQL injection attempt'
            })

        return findings

    @staticmethod
    def generate_summary(results: List[Dict]) -> str:
        """Generate human-readable summary of SQL analysis"""
        if not results:
            return "No SQL statements detected"

        total_statements = len(results)
        dangerous_count = sum(1 for r in results if r.get('dangerous'))
        high_risk_count = sum(1 for r in results if r.get('injection_risk') in ['Critical', 'High'])

        summary_parts = [f"Analyzed {total_statements} SQL statement(s)"]

        if dangerous_count > 0:
            summary_parts.append(f"{dangerous_count} contain dangerous keywords (DROP, DELETE, etc.)")

        if high_risk_count > 0:
            summary_parts.append(f"{high_risk_count} show high injection risk")

        # Check for specific attack types
        attack_types = set()
        for result in results:
            for finding in result.get('findings', []):
                attack_types.add(finding['type'])

        if attack_types:
            summary_parts.append(f"Detected: {', '.join(attack_types)}")

        return ". ".join(summary_parts)
