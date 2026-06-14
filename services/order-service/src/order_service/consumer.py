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


def extract_order_id(envelope: dict[str, object], *, event_type: str) -> UUID:
    try:
        payload = envelope["payload"]
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        return UUID(str(payload["order_id"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{event_type} has missing or invalid order_id") from exc


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


async def handle_kitchen_ticket_preparing(message: IncomingMessage) -> None:
    async with message.process(requeue=False):
        envelope = json.loads(message.body.decode())
        payload = envelope["payload"]
        order_id_str = payload.get("order_id")
        if not order_id_str:
            logger.error("KitchenTicketPreparing missing order_id: %s", envelope)
            return
        try:
            order_id = UUID(order_id_str)
        except ValueError:
            logger.error("KitchenTicketPreparing has invalid order_id: %s", order_id_str)
            return
        session = SessionLocal()
        try:
            service = OrderLifecycleApplicationService(
                order_repository=SqlAlchemyOrderRepository(session),
                unit_of_work=SqlAlchemyUnitOfWork(session),
            )
            order = service.order_repository.get_order(order_id)
            if order is None:
                logger.warning("Order %s not found for KitchenTicketPreparing", order_id)
                return
            logger.info(
                "Order %s is %s (KitchenTicketPreparing received)",
                order.id,
                order.status.value,
            )
        finally:
            session.close()


async def handle_kitchen_ticket_ready(message: IncomingMessage) -> None:
    async with message.process(requeue=False):
        envelope = json.loads(message.body.decode())
        payload = envelope["payload"]
        order_id_str = payload.get("order_id")
        if not order_id_str:
            logger.error("KitchenTicketReadyForPickup missing order_id: %s", envelope)
            return
        try:
            order_id = UUID(order_id_str)
        except ValueError:
            logger.error(
                "KitchenTicketReadyForPickup has invalid order_id: %s", order_id_str
            )
            return
        session = SessionLocal()
        try:
            service = OrderLifecycleApplicationService(
                order_repository=SqlAlchemyOrderRepository(session),
                unit_of_work=SqlAlchemyUnitOfWork(session),
            )
            try:
                order = service.mark_ready_order(order_id)
            except InvalidOrderStatusTransitionError as exc:
                logger.error("Cannot mark_ready order %s: %s", order_id, exc)
                return
            if order is None:
                logger.warning(
                    "Order %s not found for KitchenTicketReadyForPickup", order_id
                )
                return
            logger.info("Order %s transitioned to %s", order.id, order.status.value)
        finally:
            session.close()


async def handle_delivery_created(message: IncomingMessage) -> None:
    async with message.process(requeue=False):
        envelope = json.loads(message.body.decode())
        try:
            order_id = extract_order_id(envelope, event_type="DeliveryCreated")
        except ValueError as exc:
            logger.error("%s: %s", exc, envelope)
            return
        session = SessionLocal()
        try:
            service = OrderLifecycleApplicationService(
                order_repository=SqlAlchemyOrderRepository(session),
                unit_of_work=SqlAlchemyUnitOfWork(session),
            )
            order = service.order_repository.get_order(order_id)
            if order is None:
                logger.warning("Order %s not found for DeliveryCreated", order_id)
                return
            logger.info(
                "Delivery created for order %s; order remains %s",
                order.id,
                order.status.value,
            )
        finally:
            session.close()


async def handle_delivery_assigned(message: IncomingMessage) -> None:
    async with message.process(requeue=False):
        envelope = json.loads(message.body.decode())
        try:
            order_id = extract_order_id(envelope, event_type="DeliveryAssigned")
        except ValueError as exc:
            logger.error("%s: %s", exc, envelope)
            return
        session = SessionLocal()
        try:
            service = OrderLifecycleApplicationService(
                order_repository=SqlAlchemyOrderRepository(session),
                unit_of_work=SqlAlchemyUnitOfWork(session),
            )
            try:
                order = service.mark_delivery_assigned_order(order_id)
            except InvalidOrderStatusTransitionError as exc:
                logger.error("Cannot mark_delivery_assigned order %s: %s", order_id, exc)
                return
            if order is None:
                logger.warning("Order %s not found for DeliveryAssigned", order_id)
                return
            logger.info("Order %s transitioned to %s", order.id, order.status.value)
        finally:
            session.close()


async def handle_delivery_picked_up(message: IncomingMessage) -> None:
    async with message.process(requeue=False):
        envelope = json.loads(message.body.decode())
        try:
            order_id = extract_order_id(envelope, event_type="DeliveryPickedUp")
        except ValueError as exc:
            logger.error("%s: %s", exc, envelope)
            return
        session = SessionLocal()
        try:
            service = OrderLifecycleApplicationService(
                order_repository=SqlAlchemyOrderRepository(session),
                unit_of_work=SqlAlchemyUnitOfWork(session),
            )
            try:
                order = service.mark_out_for_delivery_order(order_id)
            except InvalidOrderStatusTransitionError as exc:
                logger.error("Cannot mark_out_for_delivery order %s: %s", order_id, exc)
                return
            if order is None:
                logger.warning("Order %s not found for DeliveryPickedUp", order_id)
                return
            logger.info("Order %s transitioned to %s", order.id, order.status.value)
        finally:
            session.close()


async def handle_delivery_delivered(message: IncomingMessage) -> None:
    async with message.process(requeue=False):
        envelope = json.loads(message.body.decode())
        try:
            order_id = extract_order_id(envelope, event_type="DeliveryDelivered")
        except ValueError as exc:
            logger.error("%s: %s", exc, envelope)
            return
        session = SessionLocal()
        try:
            service = OrderLifecycleApplicationService(
                order_repository=SqlAlchemyOrderRepository(session),
                unit_of_work=SqlAlchemyUnitOfWork(session),
            )
            try:
                order = service.mark_delivered_order(order_id)
            except InvalidOrderStatusTransitionError as exc:
                logger.error("Cannot mark_delivered order %s: %s", order_id, exc)
                return
            if order is None:
                logger.warning("Order %s not found for DeliveryDelivered", order_id)
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

                # KitchenTicketPreparing → ack (order stays PREPARING)
                queue_preparing = await channel.declare_queue(
                    "order.kitchen-ticket-preparing", durable=True
                )
                await queue_preparing.bind(
                    exchange, routing_key="ftgo.KitchenTicket.KitchenTicketPreparing"
                )
                await queue_preparing.consume(handle_kitchen_ticket_preparing)

                # KitchenTicketReadyForPickup → mark_ready order
                queue_ready = await channel.declare_queue(
                    "order.kitchen-ticket-ready", durable=True
                )
                await queue_ready.bind(
                    exchange,
                    routing_key="ftgo.KitchenTicket.KitchenTicketReadyForPickup",
                )
                await queue_ready.consume(handle_kitchen_ticket_ready)

                # DeliveryCreated → delivery requested; order remains READY
                queue_delivery_created = await channel.declare_queue(
                    "order.delivery-created", durable=True
                )
                await queue_delivery_created.bind(
                    exchange,
                    routing_key="ftgo.Delivery.DeliveryCreated",
                )
                await queue_delivery_created.consume(handle_delivery_created)

                # DeliveryAssigned → mark delivery assigned
                queue_delivery_assigned = await channel.declare_queue(
                    "order.delivery-assigned", durable=True
                )
                await queue_delivery_assigned.bind(
                    exchange,
                    routing_key="ftgo.Delivery.DeliveryAssigned",
                )
                await queue_delivery_assigned.consume(handle_delivery_assigned)

                # DeliveryPickedUp → mark out for delivery
                queue_delivery_picked_up = await channel.declare_queue(
                    "order.delivery-picked-up", durable=True
                )
                await queue_delivery_picked_up.bind(
                    exchange,
                    routing_key="ftgo.Delivery.DeliveryPickedUp",
                )
                await queue_delivery_picked_up.consume(handle_delivery_picked_up)

                # DeliveryDelivered → mark delivered
                queue_delivery_delivered = await channel.declare_queue(
                    "order.delivery-delivered", durable=True
                )
                await queue_delivery_delivered.bind(
                    exchange,
                    routing_key="ftgo.Delivery.DeliveryDelivered",
                )
                await queue_delivery_delivered.consume(handle_delivery_delivered)

                logger.info(
                    "Order consumer started (KitchenTicketCreated, "
                    "KitchenTicketAccepted, KitchenTicketRejected, "
                    "KitchenTicketPreparing, KitchenTicketReadyForPickup, "
                    "DeliveryCreated, DeliveryAssigned, DeliveryPickedUp, "
                    "DeliveryDelivered)"
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
