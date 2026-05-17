from restaurant_service.domain.models import MenuItem, Restaurant
from restaurant_service.infrastructure.db.models import MenuItemRecord, RestaurantRecord


def to_domain_menu_item(record: MenuItemRecord) -> MenuItem:
    return MenuItem(
        id=record.id,
        restaurant_id=record.restaurant_id,
        name=record.name,
        description=record.description,
        price=record.price,
    )


def to_domain_restaurant(record: RestaurantRecord) -> Restaurant:
    return Restaurant(
        id=record.id,
        name=record.name,
        slug=record.slug,
        cuisine=record.cuisine,
        menu_items=[to_domain_menu_item(item) for item in record.menu_items],
    )


def to_menu_item_record(menu_item: MenuItem) -> MenuItemRecord:
    return MenuItemRecord(
        id=menu_item.id,
        restaurant_id=menu_item.restaurant_id,
        name=menu_item.name,
        description=menu_item.description,
        price=menu_item.price,
    )


def to_restaurant_record(restaurant: Restaurant) -> RestaurantRecord:
    record = RestaurantRecord(
        id=restaurant.id,
        name=restaurant.name,
        slug=restaurant.slug,
        cuisine=restaurant.cuisine,
    )
    record.menu_items = [
        MenuItemRecord(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
        )
        for item in restaurant.menu_items
    ]
    return record
