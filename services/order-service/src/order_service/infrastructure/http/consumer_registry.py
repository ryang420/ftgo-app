from uuid import UUID

import httpx

from order_service.application.errors import ConsumerNotFoundError
from order_service.application.ports import ConsumerRegistry


class HttpConsumerRegistry(ConsumerRegistry):
    def __init__(self, *, base_url: str, timeout_seconds: float):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout_seconds)

    async def ensure_consumer_exists(self, consumer_id: UUID) -> None:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/consumers/{consumer_id}")

        if response.status_code == 404:
            raise ConsumerNotFoundError(consumer_id)
        response.raise_for_status()
