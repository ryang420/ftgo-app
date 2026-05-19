from __future__ import annotations

import asyncio
import json
import logging
import signal
from typing import Any
from uuid import UUID

import aio_pika
from aio_pika import ExchangeType, IncomingMessage

from kitchen_service.application.commands import (
    CreateKitchenTicketCommand,
    CreateKitchenTicketLineItemCommand,
)
from kitchen_service.application.tickets import KitchenTicketApplicationService
from kitchen_service.config import get_settings
from kitchen_service.infrastructure.db import SessionLocal
from kitchen_service.infrastructure.db.repositories import SqlAlchemyKitchenTicketRepository

logger = logging.getLogger(__name__)
settings = get_settings()
running = True


def build_command(envelope: dict[str, Any]) -> CreateKitchenTicketCommand:
    payload = envelope["payload"]
    return CreateKitchenTicketCommand(
        order_id=UUID(payload["order_id"]),
        restaurant_id=int(payload["restaurant_id"]),
        line_items=[
            CreateKitchenTicketLineItemCommand(
                menu_item_id=int(item["menu_item_id"]),
                name=item["name"],
                quantity=int(item["quantity"]),
            )
            for item in payload["line_items"]
        ],
    )


async def handle_message(message: IncomingMessage) -> None:
    async with message.process(requeue=True):
        envelope = json.loads(message.body.decode())
        session = SessionLocal()
        try:
            service = KitchenTicketApplicationService(SqlAlchemyKitchenTicketRepository(session))
            ticket = service.create_ticket_for_order(build_command(envelope))
            logger.info(
                "Kitchen ticket %s is ready for order %s from message %s",
                ticket.id,
                ticket.order_id,
                message.message_id,
            )
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
                queue = await channel.declare_queue("kitchen.order-created", durable=True)
                await queue.bind(exchange, routing_key="ftgo.Order.OrderCreated")
                await queue.consume(handle_message)
                logger.info("Kitchen OrderCreated consumer started")

                while running:
                    await asyncio.sleep(1)
        except Exception:
            logger.exception("Kitchen consumer failed, retrying")
            await asyncio.sleep(3)


def shutdown(sig: int, frame: object) -> None:
    global running
    logger.info("Received signal %s, shutting down kitchen consumer...", sig)
    running = False


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    asyncio.run(consume())
