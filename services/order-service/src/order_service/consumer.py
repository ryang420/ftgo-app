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
from order_service.domain.models import InvalidOrderStatusTransitionError
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


async def handle_kitchen_ticket_accepted(message: IncomingMessage) -> None:
    async with message.process(requeue=False):
        envelope = json.loads(message.body.decode())
        payload = envelope["payload"]
        order_id_str = payload.get("order_id")
        if not order_id_str:
            logger.error("KitchenTicketAccepted missing order_id: %s", envelope)
            return
        try:
            order_id = UUID(order_id_str)
        except ValueError:
            logger.error("KitchenTicketAccepted has invalid order_id: %s", order_id_str)
            return
        session = SessionLocal()
        try:
            service = OrderLifecycleApplicationService(
                order_repository=SqlAlchemyOrderRepository(session),
                unit_of_work=SqlAlchemyUnitOfWork(session),
            )
            try:
                order = service.begin_preparing_order(order_id)
            except InvalidOrderStatusTransitionError as exc:
                logger.error("Cannot begin_preparing order %s: %s", order_id, exc)
                return
            if order is None:
                logger.warning(
                    "Order %s not found for KitchenTicketAccepted", order_id
                )
                return
            logger.info("Order %s transitioned to %s", order.id, order.status.value)
        finally:
            session.close()


async def handle_kitchen_ticket_rejected(message: IncomingMessage) -> None:
    async with message.process(requeue=False):
        envelope = json.loads(message.body.decode())
        payload = envelope["payload"]
        order_id_str = payload.get("order_id")
        if not order_id_str:
            logger.error("KitchenTicketRejected missing order_id: %s", envelope)
            return
        try:
            order_id = UUID(order_id_str)
        except ValueError:
            logger.error("KitchenTicketRejected has invalid order_id: %s", order_id_str)
            return
        session = SessionLocal()
        try:
            service = OrderLifecycleApplicationService(
                order_repository=SqlAlchemyOrderRepository(session),
                unit_of_work=SqlAlchemyUnitOfWork(session),
            )
            try:
                order = service.cancel_order(order_id)
            except InvalidOrderStatusTransitionError as exc:
                logger.error("Cannot cancel order %s: %s", order_id, exc)
                return
            if order is None:
                logger.warning(
                    "Order %s not found for KitchenTicketRejected", order_id
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

                # KitchenTicketCreated → approve order
                queue_created = await channel.declare_queue(
                    "order.kitchen-ticket-created", durable=True
                )
                await queue_created.bind(
                    exchange, routing_key="ftgo.KitchenTicket.KitchenTicketCreated"
                )
                await queue_created.consume(handle_message)

                # KitchenTicketAccepted → begin_preparing order
                queue_accepted = await channel.declare_queue(
                    "order.kitchen-ticket-accepted", durable=True
                )
                await queue_accepted.bind(
                    exchange, routing_key="ftgo.KitchenTicket.KitchenTicketAccepted"
                )
                await queue_accepted.consume(handle_kitchen_ticket_accepted)

                # KitchenTicketRejected → cancel order
                queue_rejected = await channel.declare_queue(
                    "order.kitchen-ticket-rejected", durable=True
                )
                await queue_rejected.bind(
                    exchange, routing_key="ftgo.KitchenTicket.KitchenTicketRejected"
                )
                await queue_rejected.consume(handle_kitchen_ticket_rejected)

                logger.info(
                    "Order consumer started (KitchenTicketCreated, "
                    "KitchenTicketAccepted, KitchenTicketRejected)"
                )

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
