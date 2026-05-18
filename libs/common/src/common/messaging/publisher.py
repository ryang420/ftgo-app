import json
from typing import Any

import aio_pika
from aio_pika import DeliveryMode, ExchangeType


class MessagePublisher:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.RobustChannel | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self.amqp_url)
        self._channel = await self._connection.channel()

    async def disconnect(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def publish(
        self,
        exchange: str,
        routing_key: str,
        payload: dict[str, Any],
        message_id: str,
    ) -> None:
        if not self._channel:
            raise RuntimeError("Publisher not connected")

        ex = await self._channel.declare_exchange(
            exchange, ExchangeType.TOPIC, durable=True
        )

        await ex.publish(
            aio_pika.Message(
                body=json.dumps(payload, default=str).encode(),
                message_id=message_id,
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
