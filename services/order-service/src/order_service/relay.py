import asyncio
import logging
import signal
import sys

from common.outbox.relay import OutboxRelay

from order_service.config import OrderServiceSettings

settings = OrderServiceSettings()
relay = OutboxRelay(
    database_url=settings.database_url,
    amqp_url=settings.amqp_url,
    poll_interval_seconds=3.0,
)


def shutdown(sig: int, frame: object) -> None:
    logging.info("Received signal %s, shutting down...", sig)
    relay.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(relay.run())
