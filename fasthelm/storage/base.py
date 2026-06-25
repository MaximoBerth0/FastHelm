from typing import Protocol
import asyncio


# contract
class Storage(Protocol):
    lock: asyncio.Lock

    async def get(self, key):
        ...

    async def set(self, key, value):
        ...