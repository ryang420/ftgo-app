from __future__ import annotations

from decimal import Decimal

from common.db import TimestampedModel
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RestaurantRecord(TimestampedModel):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    cuisine: Mapped[str] = mapped_column(String(120), nullable=False)

    menu_items: Mapped[list[MenuItemRecord]] = relationship(
        back_populates="restaurant",
        cascade="all, delete-orphan",
        order_by="MenuItemRecord.id",
    )


class MenuItemRecord(TimestampedModel):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    restaurant: Mapped[RestaurantRecord] = relationship(back_populates="menu_items")
