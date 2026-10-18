"""Cliente resiliente com retry, rate limit e logs."""

import asyncio
from collections import defaultdict
from time import monotonic
from typing import cast

import httpx
from loguru import logger
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from price_monitor.config import settings


class RateLimiter:
    """Garante intervalo minimo entre requisicoes ao mesmo dominio."""

    def __init__(self, rate_per_second: float) -> None:
        self._min_interval = 1.0 / rate_per_second
        self._last_call: dict[str, float] = defaultdict(float)
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def acquire(self, domain: str) -> None:
        """Aguarda ate que seja seguro fazer uma requisicao ao dominio."""
        async with self._locks[domain]:
            elapsed = monotonic() - self._last_call[domain]
            wait_time = self._min_interval - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self._last_call[domain] = monotonic()


class HttpClient:
    """Cliente HTTP com retry, rate limit e logs."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._limiter = RateLimiter(settings.rate_limit_per_second)

    async def __aenter__(self) -> "HttpClient":
        self._client = httpx.AsyncClient(
            timeout=settings.timeout_seconds,
            headers={
                "User-Agent": settings.user_agent,
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            },
            follow_redirects=True,
            http2=True,
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        if self._client:
            await self._client.aclose()

    async def _do_request(self, method: str, url: str) -> httpx.Response:
        assert self._client is not None, "Use dentro de 'async with HttpClient()'"

        for attempt in Retrying(
            stop=stop_after_attempt(settings.max_retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
            reraise=True,
        ):
            with attempt:
                response = await self._client.request(method, url)
                response.raise_for_status()
                return response

        raise RuntimeError("unreachable")

    async def get(self, url: str) -> httpx.Response:
        assert self._client is not None, "Use dentro de 'async with HttpClient()'"
        domain = httpx.URL(url).host
        await self._limiter.acquire(domain)
        logger.debug(f"GET {url}")
        return await self._do_request("GET", url)

    async def get_json(self, url: str) -> dict[str, object] | list[object]:
        response = await self.get(url)
        return cast(dict[str, object] | list[object], response.json())
