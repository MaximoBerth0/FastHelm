from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fasthelm.core.limiter import RateLimiter
from fasthelm.http.responses import rate_limit_headers, too_many_requests


def client_ip_key(request: Request) -> str:
    # default keying: one bucket per client IP
    if request.client is None:
        return "anonymous"
    return request.client.host


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        limiter: RateLimiter,
        key_func: Callable[[Request], str] = client_ip_key,
    ):
        super().__init__(app)
        self._limiter = limiter
        self._key_func = key_func

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        key = self._key_func(request)
        decision = await self._limiter.check(key)

        if not decision.allowed:
            return too_many_requests(decision)

        response = await call_next(request)
        response.headers.update(rate_limit_headers(decision))
        return response