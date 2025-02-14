from fastapi import HTTPException, Header
from typing import Optional

async def validate_token(authorization: Optional[str] = Header(None)) -> str:
    """Validate the authorization token.
    
    Args:
        authorization: The authorization header containing the access token
        
    Returns:
        The validated token
        
    Raises:
        HTTPException: If no token is provided or token is invalid
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization token provided")
        
    # For mock API, just validate token exists
    # In real implementation, would verify JWT/OAuth token
    return authorization 