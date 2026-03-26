"""
Rate limiting middleware for API endpoints
Protects against abuse and ensures fair resource allocation
"""
from fastapi import Request, HTTPException
from typing import Dict
import time
from collections import defaultdict
import asyncio

class RateLimiter:
    """
    Simple in-memory rate limiter
    For production, use Redis or similar distributed cache
    """

    def __init__(self):
        # Store: {ip_address: [(timestamp, endpoint), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_task = None

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check X-Forwarded-For header (for proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Fallback to direct client
        return request.client.host if request.client else "unknown"

    async def check_rate_limit(
        self,
        request: Request,
        max_requests: int = 10,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request is within rate limit
        Returns True if allowed, raises HTTPException if rate limited
        """
        client_ip = self.get_client_ip(request)
        endpoint = request.url.path
        current_time = time.time()

        # Get requests for this IP
        client_requests = self.requests[client_ip]

        # Filter out old requests outside the time window
        cutoff_time = current_time - window_seconds
        client_requests[:] = [
            (ts, ep) for ts, ep in client_requests
            if ts > cutoff_time
        ]

        # Count requests to this endpoint
        endpoint_requests = [
            ts for ts, ep in client_requests
            if ep == endpoint
        ]

        if len(endpoint_requests) >= max_requests:
            # Rate limit exceeded
            retry_after = int(window_seconds - (current_time - endpoint_requests[0]))
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Maximum {max_requests} requests per {window_seconds} seconds.",
                    "retry_after": retry_after,
                    "code": "RATE_LIMIT_EXCEEDED"
                },
                headers={"Retry-After": str(retry_after)}
            )

        # Add this request
        client_requests.append((current_time, endpoint))
        return True

    async def cleanup_old_entries(self):
        """
        Periodically clean up old entries to prevent memory bloat
        Run this as a background task
        """
        while True:
            await asyncio.sleep(300)  # Run every 5 minutes
            current_time = time.time()
            cutoff_time = current_time - 3600  # Keep last 1 hour

            # Clean up old entries
            for ip in list(self.requests.keys()):
                self.requests[ip][:] = [
                    (ts, ep) for ts, ep in self.requests[ip]
                    if ts > cutoff_time
                ]

                # Remove IP if no requests
                if not self.requests[ip]:
                    del self.requests[ip]

# Global rate limiter instance
rate_limiter = RateLimiter()
