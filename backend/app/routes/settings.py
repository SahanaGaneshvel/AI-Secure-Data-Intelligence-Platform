"""
Settings management endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import json
from pathlib import Path

router = APIRouter()

# Settings storage file
SETTINGS_PATH = Path(__file__).parent.parent.parent / "data" / "settings.json"

# Default settings matching frontend UserSettings type
DEFAULT_SETTINGS = {
    "theme": "dark",
    "timezone": "UTC",
    "language": "en",
    "notifications": {
        "email": True,
        "highRiskAlerts": True,
        "dailyDigest": False
    },
    "analysisDefaults": {
        "maskSensitiveData": True,
        "blockHighRiskContent": False,
        "advancedThreatDetection": True,
        "defaultInputType": "text"
    },
    "detectorConfig": {
        "regex": True,
        "heuristic": True,
        "nlp": True,
        "ai": True
    },
    "apiIntegration": {
        "apiKey": "",
        "webhookUrl": ""
    }
}


def _ensure_data_dir():
    """Ensure data directory exists"""
    SETTINGS_PATH.parent.mkdir(exist_ok=True)


def _load_settings() -> Dict[str, Any]:
    """Load settings from file, create defaults if not exists"""
    _ensure_data_dir()

    if not SETTINGS_PATH.exists():
        _save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
        # Merge with defaults to handle any missing fields
        return _merge_with_defaults(settings)
    except Exception:
        return DEFAULT_SETTINGS.copy()


def _save_settings(settings: Dict[str, Any]) -> bool:
    """Save settings to file"""
    _ensure_data_dir()

    try:
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False


def _merge_with_defaults(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user settings with defaults to fill any missing fields"""
    result = DEFAULT_SETTINGS.copy()

    for key, value in settings.items():
        if key in result:
            if isinstance(value, dict) and isinstance(result[key], dict):
                result[key] = {**result[key], **value}
            else:
                result[key] = value

    return result


class SettingsUpdate(BaseModel):
    updates: Dict[str, Any]


@router.get("/settings")
async def get_settings():
    """
    Get current user settings
    """
    try:
        settings = _load_settings()
        return {"settings": settings}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve settings",
                "message": str(e),
                "code": "SERVER_ERROR"
            }
        )


@router.put("/settings")
async def update_settings(update: SettingsUpdate):
    """
    Update user settings
    """
    try:
        current_settings = _load_settings()

        # Deep merge updates
        for key, value in update.updates.items():
            if key in current_settings:
                if isinstance(value, dict) and isinstance(current_settings[key], dict):
                    current_settings[key] = {**current_settings[key], **value}
                else:
                    current_settings[key] = value

        if not _save_settings(current_settings):
            raise Exception("Failed to persist settings")

        return {
            "message": "Settings updated successfully",
            "settings": current_settings
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to update settings",
                "message": str(e),
                "code": "SERVER_ERROR"
            }
        )


@router.post("/settings/reset")
async def reset_settings():
    """
    Reset settings to defaults
    """
    try:
        if not _save_settings(DEFAULT_SETTINGS):
            raise Exception("Failed to persist default settings")

        return {
            "message": "Settings reset to defaults",
            "settings": DEFAULT_SETTINGS
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to reset settings",
                "message": str(e),
                "code": "SERVER_ERROR"
            }
        )
