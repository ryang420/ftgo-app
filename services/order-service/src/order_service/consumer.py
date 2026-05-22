from __future__ import annotations

import asyncio
import json
import logging
import signal
from uuid import UUID

import aio_pika
from aio_pika import ExchangeType, IncomingMessage

from order_service.application.lifecycle import OrderLifecycleApplicationService
from order_service.config import OrderServiceSettings
from order_service.infrastructure.db import SessionLocal
from order_service.infrastructure.db.repositories import (
    SqlAlchemyOrderRepository,
    SqlAlchemyUnitOfWork,
)

logger = logging.getLogger(__name__)
settings = OrderServiceSettings()
running = True


async def handle_message(message: IncomingMessage) -> None:
    async with message.process(requeue=True):
        envelope = json.loads(message.body.decode())
        order_id = UUID(envelope["payload"]["order_id"])
        session = SessionLocal()
        try:
            service = OrderLifecycleApplicationService(
                order_repository=SqlAlchemyOrderRepository(session),
                unit_of_work=SqlAlchemyUnitOfWork(session),
            )
            order = service.approve_order(order_id)
            if order is None:
                logger.warning(
                    "Order %s was not found for message %s",
                    order_id,
                    message.message_id,
                )
                return
            logger.info("Order %s transitioned to %s", order.id, order.status.value)
        finally:
            session.close()


async def consume() -> None:
    while running:
        try:
            connection = await aio_pika.connect_robust(settings.amqp_url)
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=10)
                exchange = await channel.declare_exchange(
                    "ftgo.events",
                    ExchangeType.TOPIC,
                    durable=True,
                )
                queue = await channel.declare_queue("order.kitchen-ticket-created", durable=True)
                await queue.bind(exchange, routing_key="ftgo.KitchenTicket.KitchenTicketCreated")
                await queue.consume(handle_message)
                logger.info("Order KitchenTicketCreated consumer started")

                while running:
                    await asyncio.sleep(1)
        except Exception:
            logger.exception("Order consumer failed, retrying")
            await asyncio.sleep(3)


def shutdown(sig: int, frame: object) -> None:
    global running
    logger.info("Received signal %s, shutting down order consumer...", sig)
    running = False


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    asyncio.run(consume())
