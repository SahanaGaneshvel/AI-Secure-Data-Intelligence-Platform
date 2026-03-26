"""
SQLite database for analysis persistence
Stores full analysis data for audit logs
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "data" / "analyses.db"

def init_database():
    """Initialize database schema"""
    DATABASE_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Analyses table - full schema for complete audit history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            input_type TEXT NOT NULL,
            overall_risk_score INTEGER NOT NULL,
            overall_risk_level TEXT NOT NULL,
            primary_action TEXT NOT NULL,
            total_findings INTEGER NOT NULL,
            findings_json TEXT NOT NULL,
            masked_output_json TEXT NOT NULL,
            ai_summary TEXT,
            risk_distribution_json TEXT NOT NULL,
            critical_vulnerabilities_json TEXT,
            behavioral_anomalies_json TEXT,
            recommended_actions_json TEXT,
            risk_score_breakdown_json TEXT,
            metadata_json TEXT
        )
    """)

    # Add new columns if they don't exist (for migrations)
    try:
        cursor.execute("ALTER TABLE analyses ADD COLUMN critical_vulnerabilities_json TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        cursor.execute("ALTER TABLE analyses ADD COLUMN behavioral_anomalies_json TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE analyses ADD COLUMN recommended_actions_json TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE analyses ADD COLUMN risk_score_breakdown_json TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE analyses ADD COLUMN metadata_json TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

def save_analysis(analysis_data: Dict) -> bool:
    """
    Save analysis to database
    Returns True if successful
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Handle findings - convert Pydantic models if necessary
        findings = analysis_data.get("findings", [])
        if findings and hasattr(findings[0], 'dict'):
            findings_json = json.dumps([f.dict() for f in findings])
        else:
            findings_json = json.dumps(findings)

        # Handle risk distribution
        risk_dist = analysis_data.get("riskDistribution", {})
        if hasattr(risk_dist, 'dict'):
            risk_dist_json = json.dumps(risk_dist.dict())
        else:
            risk_dist_json = json.dumps(risk_dist)

        # Handle risk score breakdown
        breakdown = analysis_data.get("riskScoreBreakdown", [])
        if breakdown and hasattr(breakdown[0], 'dict'):
            breakdown_json = json.dumps([b.dict() for b in breakdown])
        else:
            breakdown_json = json.dumps(breakdown)

        # Handle metadata
        metadata = analysis_data.get("metadata", {})
        if hasattr(metadata, 'dict'):
            metadata_json = json.dumps(metadata.dict())
        else:
            metadata_json = json.dumps(metadata)

        cursor.execute("""
            INSERT INTO analyses (
                id, timestamp, input_type,
                overall_risk_score, overall_risk_level, primary_action,
                total_findings, findings_json, masked_output_json,
                ai_summary, risk_distribution_json,
                critical_vulnerabilities_json, behavioral_anomalies_json,
                recommended_actions_json, risk_score_breakdown_json, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_data["id"],
            datetime.utcnow().isoformat(),
            analysis_data["inputType"],
            analysis_data["overallRiskScore"],
            analysis_data["overallRiskLevel"],
            analysis_data["primaryAction"],
            analysis_data["totalFindings"],
            findings_json,
            json.dumps(analysis_data.get("maskedOutput", [])),
            analysis_data.get("aiSummary", ""),
            risk_dist_json,
            json.dumps(analysis_data.get("criticalVulnerabilities", [])),
            json.dumps(analysis_data.get("behavioralAnomalies", [])),
            json.dumps(analysis_data.get("recommendedActions", [])),
            breakdown_json,
            metadata_json,
        ))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving analysis: {e}")
        return False

def get_analysis_by_id(analysis_id: str) -> Optional[Dict]:
    """
    Retrieve full analysis by ID
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        # Parse JSON fields with defaults for potentially missing columns
        def safe_json_loads(value, default):
            if value is None:
                return default
            try:
                return json.loads(value)
            except:
                return default

        return {
            "id": row["id"],
            "timestamp": row["timestamp"],
            "inputType": row["input_type"],
            "overallRiskScore": row["overall_risk_score"],
            "overallRiskLevel": row["overall_risk_level"],
            "primaryAction": row["primary_action"],
            "totalFindings": row["total_findings"],
            "findings": safe_json_loads(row["findings_json"], []),
            "maskedOutput": safe_json_loads(row["masked_output_json"], []),
            "aiSummary": row["ai_summary"] or "",
            "riskDistribution": safe_json_loads(row["risk_distribution_json"], {"low": 0, "medium": 0, "high": 0, "critical": 0}),
            "criticalVulnerabilities": safe_json_loads(row["critical_vulnerabilities_json"] if "critical_vulnerabilities_json" in row.keys() else None, []),
            "behavioralAnomalies": safe_json_loads(row["behavioral_anomalies_json"] if "behavioral_anomalies_json" in row.keys() else None, []),
            "recommendedActions": safe_json_loads(row["recommended_actions_json"] if "recommended_actions_json" in row.keys() else None, []),
            "riskScoreBreakdown": safe_json_loads(row["risk_score_breakdown_json"] if "risk_score_breakdown_json" in row.keys() else None, []),
            "metadata": safe_json_loads(row["metadata_json"] if "metadata_json" in row.keys() else None, {}),
        }
    except Exception as e:
        print(f"Error retrieving analysis: {e}")
        return None

def get_all_analyses(limit: int = 50, offset: int = 0) -> List[Dict]:
    """
    Retrieve all analyses (for audit logs page)
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id, timestamp, input_type,
                overall_risk_score, overall_risk_level,
                primary_action, total_findings
            FROM analyses
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row["id"],
                "timestamp": row["timestamp"],
                "inputType": row["input_type"],
                "overallRiskScore": row["overall_risk_score"],
                "overallRiskLevel": row["overall_risk_level"],
                "primaryAction": row["primary_action"],
                "totalFindings": row["total_findings"],
            }
            for row in rows
        ]
    except Exception as e:
        print(f"Error retrieving analyses: {e}")
        return []

def get_analysis_count() -> int:
    """Get total count of analyses"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM analyses")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except:
        return 0

# Initialize database on module import
init_database()
