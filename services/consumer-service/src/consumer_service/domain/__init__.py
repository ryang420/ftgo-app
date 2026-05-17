"""Domain model for consumer-service."""

from consumer_service.domain.models import ConsumerAddress, ConsumerProfile
from consumer_service.domain.repositories import ConsumerRepository

__all__ = ["ConsumerAddress", "ConsumerProfile", "ConsumerRepository"]
