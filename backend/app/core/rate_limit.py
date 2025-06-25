"""
Rate limiting middleware for public API endpoints
"""
from typing import Dict, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from collections import defaultdict
import asyncio


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        self._cleanup_task = None
        
    async def __aenter__(self):
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._cleanup_task:
            self._cleanup_task.cancel()
            
    async def _cleanup_loop(self):
        """Periodically clean up old request records"""
        while True:
            await asyncio.sleep(60)  # Clean up every minute
            await self._cleanup()
            
    async def _cleanup(self):
        """Remove old request records"""
        cutoff = datetime.now() - timedelta(minutes=1)
        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                req_time for req_time in self.requests[ip]
                if req_time > cutoff
            ]
            if not self.requests[ip]:
                del self.requests[ip]
                
    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """Check if request is allowed"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Clean up old requests for this IP
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Check rate limit
        request_count = len(self.requests[client_ip])
        if request_count >= self.requests_per_minute:
            return False, self.requests_per_minute - request_count
            
        # Record new request
        self.requests[client_ip].append(now)
        return True, self.requests_per_minute - request_count - 1


# Global rate limiters for different endpoints
execute_rate_limiter = RateLimiter(requests_per_minute=100)  # 100 requests per minute for execute API
api_rate_limiter = RateLimiter(requests_per_minute=300)  # 300 requests per minute for general API


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Get client IP
    client_ip = request.client.host
    if forwarded_for := request.headers.get("X-Forwarded-For"):
        client_ip = forwarded_for.split(",")[0].strip()
        
    # Determine which rate limiter to use
    if request.url.path.startswith("/execute/"):
        rate_limiter = execute_rate_limiter
    else:
        rate_limiter = api_rate_limiter
        
    # Check rate limit
    allowed, remaining = rate_limiter.is_allowed(client_ip)
    
    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after": 60
            },
            headers={
                "X-RateLimit-Limit": str(rate_limiter.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int((datetime.now() + timedelta(minutes=1)).timestamp())),
                "Retry-After": "60"
            }
        )
        
    # Process request
    try:
        response = await call_next(request)
    except Exception:
        # Re-raise exception without modifying it
        raise
    
    # Add rate limit headers only if response is successful
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int((datetime.now() + timedelta(minutes=1)).timestamp()))
    
    return response