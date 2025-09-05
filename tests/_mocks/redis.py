from __future__ import annotations

import asyncio

from aiqfav.adapters.redis_adapter import EncodableT, ExpiryT, KeyT, ResponseT


class PipelineMock:
    """Mock para o pipeline do Redis assíncrono."""

    def __init__(self, client: RedisMock):
        self._cache = {}
        self._client = client

    def set(self, name: KeyT, value: EncodableT, ex: ExpiryT | None = None):
        """Mock do método set do pipeline do Redis."""
        self._cache[name] = value
        return True

    async def execute(self):
        """Mock do método execute do pipeline do Redis."""
        cache_length = len(self._cache)
        await asyncio.gather(
            *[
                self._client.set(key, value)
                for key, value in self._cache.items()
            ]
        )
        self._cache.clear()
        return [True] * cache_length


class RedisMock:
    """Mock para o Redis assíncrono que simula o comportamento dos métodos de cache."""

    def __init__(self):
        self._cache = {}
        self._pipeline = PipelineMock(self)

    async def get(self, key: KeyT) -> ResponseT | None:
        """Mock do método get do Redis."""
        return self._cache.get(key)

    async def set(
        self, key: KeyT, value: EncodableT, ex: ExpiryT | None = None
    ):
        """Mock do método set do Redis."""
        self._cache[key] = value
        return True

    async def delete(self, key: KeyT) -> ResponseT:
        """Mock do método delete do Redis."""
        if key in self._cache:
            del self._cache[key]
            return 1
        return 0

    def pipeline(self) -> PipelineMock:
        return self._pipeline
