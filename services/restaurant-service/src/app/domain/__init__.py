"""Domain model for restaurant-service."""

from app.domain.models import MenuItem, Restaurant
from app.domain.repositories import MenuItemRepository, RestaurantRepository

__all__ = ["MenuItem", "MenuItemRepository", "Restaurant", "RestaurantRepository"]
