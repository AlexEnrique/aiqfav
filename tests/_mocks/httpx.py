from unittest.mock import AsyncMock

import httpx


class HttpxAsyncClientMock:
    def __init__(self):
        self.get = AsyncMock(spec=httpx.AsyncClient.get)
        self.post = AsyncMock(spec=httpx.AsyncClient.post)
        self.put = AsyncMock(spec=httpx.AsyncClient.put)
        self.delete = AsyncMock(spec=httpx.AsyncClient.delete)
        self.patch = AsyncMock(spec=httpx.AsyncClient.patch)
        self.head = AsyncMock(spec=httpx.AsyncClient.head)
        self.options = AsyncMock(spec=httpx.AsyncClient.options)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    def __await__(self):
        async def _await():
            return self

        return _await().__await__()
