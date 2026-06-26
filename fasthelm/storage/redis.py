from redis.asyncio import Redis

from fasthelm.core.limiter import Decision


LUA_SCRIPT = """
local capacity    = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local cost        = tonumber(ARGV[3])

local t   = redis.call('TIME')
local now = tonumber(t[1]) + tonumber(t[2]) / 1000000

local state  = redis.call('HMGET', KEYS[1], 'tokens', 'ts')
local tokens = tonumber(state[1])
local last   = tonumber(state[2])

if tokens == nil then
    tokens = capacity
    last   = now
end

local elapsed = now - last
tokens = math.min(capacity, tokens + elapsed * refill_rate)

local allowed = 0
if tokens >= cost then
    allowed = 1
    tokens  = tokens - cost
end

redis.call('HSET', KEYS[1], 'tokens', tostring(tokens), 'ts', tostring(now))

local ttl = math.ceil(capacity / refill_rate) + 1
redis.call('EXPIRE', KEYS[1], ttl)

return { allowed, tostring(tokens) }
"""


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