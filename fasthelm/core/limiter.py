from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Decision:
    """The result of checking one request against a limit."""
    allowed: bool        # did this request pass? middleware branches on this
    limit: int           # bucket capacity      -> X-RateLimit-Limit
    remaining: int       # tokens left now      -> X-RateLimit-Remaining
    reset_after: float   # seconds until full   -> X-RateLimit-Reset
    retry_after: float   # seconds to wait      -> Retry-After (only when rejected)


class RateLimiter(Protocol):
    async def check(self, key: str, cost: int = 1) -> Decision:
        ...