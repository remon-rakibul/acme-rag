from fastapi import HTTPException, Header
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

VALID_API_KEY = os.getenv("API_KEY", "acme-ai-secret-key-2025")


async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key missing. Please provide X-API-Key header."
        )
    
    if x_api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key."
        )
    
    return x_api_key

