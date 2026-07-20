from abc import ABC, abstractmethod
from typing import Dict


class RecipeStorage(ABC):

    @abstractmethod
    def save(self, recipe: Dict) -> None:
        """Save a recipe"""
        pass

    @abstractmethod
    def exists(self, recipe_id: str) -> bool:
        """Check if recipe already exists"""
        pass