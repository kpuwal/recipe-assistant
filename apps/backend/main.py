from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from core.settings import settings

load_dotenv()

from utils.logger import logger
from routers.health import router as health_router
from routers.recipes import router as recipes_router
from routers.chat import router as chat_router
from routers.ingestion import router as ingestion_router
from routers.images import router as images_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Recipe Assistant started")

    yield

    logger.info("Recipe Assistant stopped")

app = FastAPI(
    title="Recipe Assistant API",
    version="1.0.0",
    description="Backend for Recipe Assistant mobile app",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Routers
app.include_router(health_router)
app.include_router(recipes_router)
app.include_router(chat_router)
app.include_router(ingestion_router)
app.include_router(images_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )