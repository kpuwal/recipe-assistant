import re
from copy import deepcopy

from models.models import Recipe, Ingredient
from utils.logger import logger


class RecipeScaler:

    UNCHANGED = {
        "snufje",
        "snuf",
        "naar smaak",
        "peper",
        "zout",
    }

    def scale(
        self,
        recipe: Recipe,
        target_persons: int,
    ) -> Recipe:

        if not recipe.persons or recipe.persons <= 0:
            return recipe

        factor = target_persons / recipe.persons

        logger.info("Scaling recipe '%s' from %d to %d persons (factor=%.2f)", 
                   recipe.title, recipe.persons, target_persons, factor)

        scaled = deepcopy(recipe)
        scaled.persons = target_persons

        scaled.ingredients = [
            self.scale_ingredient(i, factor)
            for i in recipe.ingredients
        ]

        scaled.pantry_ingredients = [
            self.scale_ingredient(i, factor)
            for i in recipe.pantry_ingredients
        ]

        return scaled

    def scale_ingredient(
        self,
        ingredient: Ingredient,
        factor: float,
    ) -> Ingredient:

        ingredient = ingredient.model_copy(deep=True)

        if not ingredient.quantity:
            return ingredient

        quantity = ingredient.quantity.lower().strip()

        if quantity in self.UNCHANGED:
            return ingredient

        ingredient.quantity = self.scale_quantity(
            ingredient.quantity,
            factor,
        )

        return ingredient

    def scale_quantity(
        self,
        quantity: str,
        factor: float,
    ) -> str:

        quantity = quantity.strip()

        match = re.match(
            r"^(\d+(?:[.,]\d+)?)\s*(.*)$",
            quantity,
        )

        if not match:
            return quantity

        value = float(match.group(1).replace(",", "."))
        unit = match.group(2)

        value *= factor

        if value >= 10:
            value = round(value)
        elif value >= 1:
            value = round(value, 1)
        else:
            value = round(value, 2)

        if value.is_integer():
            value = int(value)

        if unit:
            return f"{value} {unit}"

        return str(value)


recipe_scaler = RecipeScaler()