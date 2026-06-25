import asyncio


class MemoryStorage:
    def __init__(self):
        self._data = {}
        self.lock = asyncio.Lock()   

    async def get(self, key):
        return self._data.get(key)

    async def set(self, key, value):
        self._data[key] = value