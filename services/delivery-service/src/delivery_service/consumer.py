from __future__ import annotations

import asyncio
import json
import logging
import signal
from typing import Any
from uuid import UUID

import aio_pika
from aio_pika import ExchangeType, IncomingMessage

from delivery_service.application.deliveries import DeliveryApplicationService
from delivery_service.config import get_settings
from delivery_service.infrastructure.db import SessionLocal
from delivery_service.infrastructure.db.repositories import (
    SqlAlchemyDeliveryRepository,
    SqlAlchemyOutboxWriter,
    SqlAlchemyUnitOfWork,
)

logger = logging.getLogger(__name__)
settings = get_settings()
running = True


def build_delivery_payload(envelope: dict[str, Any]) -> dict[str, object]:
    try:
        payload = envelope["payload"]
        order_id = UUID(str(payload["order_id"]))
        delivery_address = str(payload["delivery_address"])
        restaurant_id = int(payload["restaurant_id"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Malformed KitchenTicketReadyForPickup payload") from exc
    if not delivery_address.strip():
        raise ValueError("delivery_address is required")
    return {
        "order_id": str(order_id),
        "restaurant_id": restaurant_id,
        "delivery_address": delivery_address,
    }


async def handle_kitchen_ticket_ready(message: IncomingMessage) -> None:
    async with message.process(requeue=False):
        envelope = json.loads(message.body.decode())
        try:
            payload = build_delivery_payload(envelope)
        except (KeyError, TypeError, ValueError) as exc:
            logger.error("Malformed KitchenTicketReadyForPickup payload: %s (%s)", envelope, exc)
            return

        session = SessionLocal()
        try:
            service = DeliveryApplicationService(
                delivery_repository=SqlAlchemyDeliveryRepository(session),
                outbox=SqlAlchemyOutboxWriter(session),
                unit_of_work=SqlAlchemyUnitOfWork(session),
            )
            delivery = service.create_delivery_for_ready_order(payload)
            logger.info(
                "Delivery %s is pending assignment for order %s from message %s",
                delivery.id,
                delivery.order_id,
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
                queue = await channel.declare_queue(
                    "delivery.kitchen-ticket-ready",
                    durable=True,
                )
                await queue.bind(
                    exchange,
                    routing_key="ftgo.KitchenTicket.KitchenTicketReadyForPickup",
                )
                await queue.consume(handle_kitchen_ticket_ready)
                logger.info("Delivery KitchenTicketReadyForPickup consumer started")

                while running:
                    await asyncio.sleep(1)
        except Exception:
            logger.exception("Delivery consumer failed, retrying")
            await asyncio.sleep(3)


def shutdown(sig: int, frame: object) -> None:
    global running
    logger.info("Received signal %s, shutting down delivery consumer...", sig)
    running = False


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level)
    asyncio.run(consume())
