from app.application.commands import CreateMenuItemCommand, CreateRestaurantCommand
from app.domain.models import MenuItem, Restaurant
from app.domain.repositories import MenuItemRepository, RestaurantRepository


class RestaurantApplicationService:
    def __init__(
        self,
        restaurant_repository: RestaurantRepository,
        menu_item_repository: MenuItemRepository,
    ):
        self.restaurant_repository = restaurant_repository
        self.menu_item_repository = menu_item_repository

    def list_restaurants(self) -> list[Restaurant]:
        return self.restaurant_repository.list_restaurants()

    def create_restaurant(self, command: CreateRestaurantCommand) -> Restaurant:
        restaurant = Restaurant(
            name=command.name,
            slug=command.slug,
            cuisine=command.cuisine,
            menu_items=[
                MenuItem(
                    name=item.name,
                    description=item.description,
                    price=item.price,
                )
                for item in command.menu_items
            ],
        )
        return self.restaurant_repository.add(restaurant)

    def get_restaurant(self, restaurant_id: int) -> Restaurant | None:
        return self.restaurant_repository.get_restaurant(restaurant_id)

    def list_menu_items(self, restaurant_id: int) -> list[MenuItem]:
        return self.menu_item_repository.list_menu_items(restaurant_id)

    def create_menu_item(self, restaurant_id: int, command: CreateMenuItemCommand) -> MenuItem:
        menu_item = MenuItem(
            restaurant_id=restaurant_id,
            name=command.name,
            description=command.description,
            price=command.price,
        )
        return self.menu_item_repository.add(menu_item)

    def get_menu_item(self, restaurant_id: int, menu_item_id: int) -> MenuItem | None:
        return self.menu_item_repository.get_menu_item(restaurant_id, menu_item_id)
