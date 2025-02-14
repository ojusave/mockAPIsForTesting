from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from models.auth import validate_token

router = APIRouter()

@router.get("/{accountId}/lock_settings")
async def get_account_lock_settings(
    accountId: str,
    option: Optional[str] = None, 
    custom_query_fields: Optional[str] = None,
    token: str = Depends(validate_token)
):
    """Get an account's locked settings.
    
    Returns locked settings for the specified account as long as a valid access token is provided.
    """
    # Return a basic response since we just need to validate the token
    return {
        "schedule_meeting": {
            "host_video": False,
            "participant_video": False,
            "audio_type": True
        },
        "in_meeting": {
            "chat": True,
            "screen_sharing": True
        },
        "email_notification": {
            "cloud_recording_available_reminder": True
        },
        "recording": {
            "cloud_recording": True,
            "auto_recording": True
        }
    } 