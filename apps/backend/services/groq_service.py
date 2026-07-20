import json
import os
from groq import Groq
from pathlib import Path

from models.models import Recipe
from utils.logger import logger

PROMPT_PATH = Path("core/groq_prompt.txt")
PROMPT_TEMPLATE = PROMPT_PATH.read_text(encoding="utf-8")

class GroqService:
    def __init__(self):
        self.client = Groq( api_key=os.getenv("GROQ_API_KEY"))
        
    
    def ask(self, prompt: str):
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return (
                completion
                .choices[0]
                .message
                .content
            )
        except Exception as e:
            logger.error("Groq ask failed: %s", e)
            raise

    def generate_recipes(self, user_message: str, recipe_count: int = 3):
        prompt = PROMPT_TEMPLATE.format(
            recipe_count=recipe_count,
            user_message=user_message
        )
        
        try:
            logger.info("Generating AI recipes for query: %s", user_message[:100])

            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            content = completion.choices[0].message.content
            data = json.loads(content)

            recipes = []
            for recipe_data in data.get("recipes", []):
                recipe = Recipe.model_validate(recipe_data)
                recipes.append(recipe)

            logger.info("Successfully generated %d AI recipes", len(recipes))
            return recipes

        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI recipes JSON: %s", e)
            return []
        except Exception as e:
            logger.error("Groq generate_recipes failed: %s", e)
            return []


groq_service = GroqService()