import csv
import logging

from faker import Faker

logger = logging.getLogger(__name__)


class FoodTypeProvider(Faker):
    def cuisine(self):
        return self.random_element(elements=["Italian", "Chinese", "Indian", "Mexican", "Japanese"])

    def dish_type(self):
        dish_types = [
            "Pizza",
            "Burger",
            "Sushi",
            "Pasta",
            "Steak",
            "Salad",
            "Soup",
            "Tacos",
            "Curry",
            "Noodles",
            "Sandwich",
            "Rice Bowl",
            "Fried Chicken",
            "Ramen",
            "Pho",
            "Pad Thai",
            "Burrito",
            "Enchiladas",
            "Lasagna",
            "Paella",
            "Spaghetti",
            "Mac and Cheese",
            "Chicken Stir Fry",
            "Fish and Chips",
            "Pancakes",
            "Waffles",
            "Omelette",
            "Fruit Salad",
            "Yogurt Parfait",
        ]
        return self.random_element(elements=dish_types)

    def ingredient(self):
        return self.random_element(elements=["Chicken", "Beef", "Lamb", "Vegetable", "Seafood"])

    @staticmethod
    def _load_list_from_csv(filename):
        try:
            with open(filename, "r") as file:
                reader = csv.reader(file)
                data = list(reader)[0]  # Assuming only one row of data
            return data
        except FileNotFoundError:
            logger.error("Error: File %s not found.", filename)
            return None
