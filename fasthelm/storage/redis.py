from redis.asyncio import Redis

from fasthelm.core.limiter import Decision


class RedisTokenBucket:
    """Distributed token bucket limiter. fulfills the RateLimiter contract."""

    def __init__(self, redis: Redis, capacity: int, refill_rate: float):
        self._redis = redis
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._script = redis.register_script(LUA_SCRIPT)

    async def check(self, key: str, cost: int = 1) -> Decision:
        allowed_int, tokens_str = await self._script(
            keys=[key],
            args=[self._capacity, self._refill_rate, cost],
        )

        allowed = allowed_int == 1
        tokens = float(tokens_str)

        reset_after = (self._capacity - tokens) / self._refill_rate
        retry_after = 0.0 if allowed else (cost - tokens) / self._refill_rate

        return Decision(
            allowed=allowed,
            limit=self._capacity,
            remaining=int(tokens),
            reset_after=reset_after,
            retry_after=retry_after,
        )