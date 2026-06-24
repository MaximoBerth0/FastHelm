import time
from .limiter import Decision

class TokenBucket:  # this satisfies the RateLimiter protocol
    def __init__(self, storage, capacity: int, refill_rate: float):
        self._storage = storage      # where per-key state lives
        self._capacity = capacity    # max tokens (the burst size)
        self._refill_rate = refill_rate  # tokens added per second

    async def check(self, key, cost=1):
        now = time.monotonic()
        state = await self._storage.get(key)

        if state is None:
            tokens = self._capacity 
            last = now
        else:
            tokens, last = state

        elapsed = now - last
        tokens = min(self._capacity, tokens + elapsed * self._refill_rate)

        if tokens >= cost:
            allowed = True
            tokens = tokens - cost  
        else:
            allowed = False   

        reset_after = (self._capacity - tokens) / self._refill_rate
        if allowed:
            retry_after = 0.0
        else:
            faltan = cost - tokens
            retry_after = faltan / self._refill_rate       

        await self._storage.set(key, (tokens, now))

        return Decision(
            allowed=allowed,
            limit=self._capacity,
            remaining=int(tokens),
            reset_after=reset_after,
            retry_after=retry_after,
        )