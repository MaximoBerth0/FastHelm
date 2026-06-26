import math

from fastapi import status
from fastapi.responses import JSONResponse

from fasthelm.core.limiter import Decision


def rate_limit_headers(decision: Decision) -> dict[str, str]:
    """Los headers X-RateLimit-*, for every responses"""
    return {
        "X-RateLimit-Limit": str(decision.limit),
        "X-RateLimit-Remaining": str(max(0, decision.remaining)),
        "X-RateLimit-Reset": str(math.ceil(decision.reset_after)),
    }


def too_many_requests(decision: Decision) -> JSONResponse:
    """ response to return 429 too many requests """
    headers = rate_limit_headers(decision)
    headers["Retry-After"] = str(math.ceil(decision.retry_after))

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded"},
        headers=headers,
    )