from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from common.messaging.publisher import MessagePublisher
from common.outbox.models import OutboxMessageRecord

logger = logging.getLogger(__name__)


class OutboxRelay:
    """Polls the outbox table and publishes events to RabbitMQ.

    Guarantees at-least-once delivery:
    - Messages are published first, then marked in DB.
    - If a crash occurs after publish but before commit, the message
      will be redelivered on the next poll. Downstream consumers
      must be idempotent (check message_id).
    """

    def __init__(
        self,
        database_url: str,
        amqp_url: str,
        *,
        poll_interval_seconds: float = 5.0,
        batch_size: int = 100,
    ):
        self.engine = create_engine(database_url, echo=False, future=True)
        self.session_factory = sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False
        )
        self.publisher = MessagePublisher(amqp_url)
        self.poll_interval = poll_interval_seconds
        self.batch_size = batch_size
        self._running = False

    async def run(self) -> None:
        await self.publisher.connect()
        self._running = True
        logger.info("Outbox relay started")

        try:
            while self._running:
                try:
                    count = await self._process_batch()
                    if count == 0:
                        await asyncio.sleep(self.poll_interval)
                except Exception:
                    logger.exception("Batch failed, retrying after interval")
                    await asyncio.sleep(self.poll_interval)
        finally:
            await self.publisher.disconnect()
            logger.info("Outbox relay stopped")

    def stop(self) -> None:
        self._running = False

    async def _process_batch(self) -> int:
        session = self.session_factory()
        try:
            # 1. Lock unprocessed rows to avoid competing relays
            stmt = (
                select(OutboxMessageRecord)
                .where(OutboxMessageRecord.published_at.is_(None))
                .order_by(OutboxMessageRecord.created_at)
                .limit(self.batch_size)
                .with_for_update(skip_locked=True)
            )
            messages = list(session.scalars(stmt).all())
            if not messages:
                return 0

            # 2. Publish messages one by one.
            #    If any publish fails we stop the batch so that
            #    successfully-published messages are still marked.
            successfully_published: list[OutboxMessageRecord] = []
            for msg in messages:
                try:
                    await self.publisher.publish(
                        exchange="ftgo.events",
                        routing_key=(
                            f"ftgo.{msg.aggregate_type}.{msg.event_type}"
                        ),
                        payload={
                            "event_type": msg.event_type,
                            "aggregate_type": msg.aggregate_type,
                            "aggregate_id": msg.aggregate_id,
                            "payload": msg.payload,
                            "occurred_at": msg.created_at.isoformat(),
                        },
                        message_id=str(msg.id),
                    )
                    successfully_published.append(msg)
                except Exception:
                    logger.exception(
                        "Failed to publish outbox message %s, "
                        "stopping batch. Successfully published "
                        "messages so far: %d",
                        msg.id,
                        len(successfully_published),
                    )
                    break

            # 3. Mark successfully published rows inside the same DB tx.
            now = datetime.now(timezone.utc)
            for msg in successfully_published:
                msg.published_at = now

            session.commit()
            logger.info(
                "Published %d/%d outbox messages",
                len(successfully_published),
                len(messages),
            )
            return len(successfully_published)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
