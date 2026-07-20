from fastapi import APIRouter, Depends
from models.models import ChatRequest
from intent import detect_intent
from services.groq_service import groq_service
from services.search_service import SearchService
from core.dependencies import get_search_service
from utils.logger import logger

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
async def chat(
    request: ChatRequest,
    search_service: SearchService = Depends(get_search_service)
):
    intent = detect_intent(request.message)
    logger.info("Chat request - Intent: %s", intent)

    if intent == "search":
        recipes = search_service.search_recipes(query=request.message)
        logger.info("Search returned %d recipes", len(recipes))
        return {
            "answer": f"{len(recipes)} recepten gevonden.",
            "recipes": [
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    "image": recipe.image,
                    "time_minutes": recipe.time_minutes,
                    "source": recipe.source
                }
                for recipe in recipes
            ]
        }

    if intent == "knowledge" or intent == "substitution":
        prompt = f"Je bent een Nederlandse kookexpert.\n\nVraag:\n{request.message}"
        if intent == "substitution":
            prompt += "\n\nGeef drie goede vervangers."

        answer = groq_service.ask(prompt)
        return {"answer": answer, "recipes": []}

    if intent == "ai_recipe":
        recipes = groq_service.generate_recipes(request.message)
        logger.info("Generated %d AI recipes", len(recipes))
        return {
            "answer": f"Ik heb {len(recipes)} recepten bedacht.",
            "recipes": [
                {**recipe.model_dump(), "source": "ai"} for recipe in recipes
            ]
        }

    logger.warning("Unknown intent: %s", intent)
    return {"answer": "Geen antwoord gevonden.", "recipes": []}