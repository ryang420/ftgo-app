class RestaurantNotFoundError(Exception):
    def __init__(self, restaurant_id: int):
        self.restaurant_id = restaurant_id
        super().__init__(f"Restaurant {restaurant_id} was not found")


class MenuItemNotFoundError(Exception):
    def __init__(self, restaurant_id: int, menu_item_id: int):
        self.restaurant_id = restaurant_id
        self.menu_item_id = menu_item_id
        super().__init__(f"Menu item {menu_item_id} was not found for restaurant {restaurant_id}")
