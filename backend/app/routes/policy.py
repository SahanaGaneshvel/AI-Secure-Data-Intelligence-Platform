"""
Policy management endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.policy import PolicyEngine

router = APIRouter()

class PolicyUpdate(BaseModel):
    updates: Dict[str, Any]

@router.get("/policy")
async def get_policy():
    """
    Get current policy configuration
    """
    try:
        policy = PolicyEngine.get_policy()
        return {"policy": policy}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve policy",
                "message": str(e),
                "code": "SERVER_ERROR"
            }
        )

@router.put("/policy")
async def update_policy(update: PolicyUpdate):
    """
    Update policy configuration
    """
    try:
        updated_policy = PolicyEngine.update_policy(update.updates)
        return {
            "message": "Policy updated successfully",
            "policy": updated_policy
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to update policy",
                "message": str(e),
                "code": "SERVER_ERROR"
            }
        )

@router.post("/policy/reset")
async def reset_policy():
    """
    Reset policy to defaults
    """
    try:
        default_policy = PolicyEngine.reset_policy()
        return {
            "message": "Policy reset to defaults",
            "policy": default_policy
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to reset policy",
                "message": str(e),
                "code": "SERVER_ERROR"
            }
        )
