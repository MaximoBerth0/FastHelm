import time
from .limiter import Decision

class TokenBucket:
    def __init__(self, storage, capacity, refill_rate):
        self._storage = storage
        self._capacity = capacity
        self._refill_rate = refill_rate

    async def check(self, key, cost=1): 
        now = time.monotonic() 

        async with self._storage.lock:
            state = await self._storage.get(key)

            if state is None:
                tokens = self._capacity
                last = now
            else:
                tokens, last = state 

            # lazy refill
            elapsed = now - last
            tokens = min(self._capacity, tokens + elapsed * self._refill_rate) 

            # decision
            if tokens >= cost:
                allowed = True
                tokens = tokens - cost
            else:
                allowed = False

            # numbers for headers
            reset_after = (self._capacity - tokens) / self._refill_rate
            retry_after = 0.0 if allowed else (cost - tokens) / self._refill_rate

            # saves and return the Desision
            await self._storage.set(key, (tokens, now))
        
        return Decision(
            allowed=allowed,    
            limit=self._capacity,
            remaining=int(tokens),
            reset_after=reset_after,
            retry_after=retry_after,
        )