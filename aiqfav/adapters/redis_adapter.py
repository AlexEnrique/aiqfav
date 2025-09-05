from datetime import timedelta
from typing import Any, Protocol

import redis.asyncio as redis

KeyT = bytes | str | memoryview
ResponseT = Any
EncodedT = bytes | bytearray | memoryview
DecodedT = str | int | float
EncodableT = EncodedT | DecodedT
ExpiryT = int | timedelta


class PipelineAsyncProtocol(Protocol):
    def set(
        self, name: KeyT, value: EncodableT, ex: ExpiryT | None = None
    ) -> ResponseT: ...

    async def execute(self) -> list[bool]: ...


class RedisAsyncProtocol(Protocol):
    async def get(self, key: KeyT) -> ResponseT | None: ...

    async def set(
        self,
        key: KeyT,
        value: EncodableT,
        ex: ExpiryT | None = None,
    ) -> ResponseT: ...

    async def delete(self, key: KeyT) -> int: ...

    def pipeline(self) -> PipelineAsyncProtocol: ...


class RedisAdapter:
    def __init__(self, client: redis.Redis):
        self.client = client

    async def get(self, key: KeyT) -> ResponseT | None:
        return await self.client.get(key)

    async def set(
        self, key: KeyT, value: EncodableT, ex: ExpiryT | None = None
    ) -> ResponseT:
        return await self.client.set(key, value, ex)

    async def delete(self, key: KeyT) -> ResponseT:
        return await self.client.delete(key)

    def pipeline(self) -> PipelineAsyncProtocol:
        return self.client.pipeline()
