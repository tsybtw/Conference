from typing import Dict, Tuple
import time
from fastapi import HTTPException, Request, status

from app.config import settings
from app.core.logging import logger

login_attempts: Dict[str, list] = {}

def check_login_rate_limit(request: Request, email: str) -> None:
    ip_address = request.client.host
    current_time = time.time()
    
    if ip_address in login_attempts:
        login_attempts[ip_address] = [
            attempt for attempt in login_attempts[ip_address]
            if current_time - attempt[0] < 60
        ]
    else:
        login_attempts[ip_address] = []
    
    recent_attempts = login_attempts[ip_address]
    if len(recent_attempts) >= settings.LOGIN_RATE_LIMIT:
        logger.warning(
            f"Rate limit exceeded for IP: {ip_address}, Email: {email}"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    login_attempts[ip_address].append((current_time, email)) 