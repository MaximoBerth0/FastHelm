import math

from fastapi import HTTPException, status
from starlette.requests import Request
from starlette.responses import Response

from fasthelm.core.limiter import RateLimiter
from fasthelm.http.middleware import client_ip_key
from fasthelm.http.responses import rate_limit_headers


class RateLimit:
    """A configurable FastAPI dependency, reuse on many routes"""

    def __init__(self, limiter: RateLimiter, key_func=client_ip_key):
        self._limiter = limiter
        self._key_func = key_func

    async def __call__(self, request: Request, response: Response) -> None:
        key = self._key_func(request)
        decision = await self._limiter.check(key)

        if not decision.allowed:
            headers = rate_limit_headers(decision)
            headers["Retry-After"] = str(math.ceil(decision.retry_after))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers=headers,
            )

        response.headers.update(rate_limit_headers(decision))