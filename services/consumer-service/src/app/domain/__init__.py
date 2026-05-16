"""Domain model for consumer-service."""

from app.domain.models import ConsumerAddress, ConsumerProfile
from app.domain.repositories import ConsumerRepository

__all__ = ["ConsumerAddress", "ConsumerProfile", "ConsumerRepository"]
