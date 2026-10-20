import threading
import time

from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Must run before core.settings is imported: Settings is built at import time
# and would otherwise read a half-populated environment.
load_dotenv()

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from core.settings import settings

from core.auth import require_api_key
from utils.logger import logger
from utils.exceptions import AppError
from core.dependencies import get_recipe_repository
from routers.health import router as health_router
from routers.recipes import router as recipes_router
from routers.chat import router as chat_router
from routers.ingestion import router as ingestion_router
from routers.images import router as images_router
from routers.history import router as history_router


def _warm_recipe_cache() -> None:
    try:
        started = time.time()
        recipes = get_recipe_repository().list()
        logger.info(
            "Warmed recipe cache with %d recipes in %.2fs",
            len(recipes),
            time.time() - started,
        )
    except Exception as e:
        logger.error("Recipe cache warmup failed: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.api_key:
        raise RuntimeError(
            "APP_API_KEY is not set. Refusing to start, because an API "
            "without a key would be readable and writable by anyone who "
            "knows the URL. Set APP_API_KEY in the environment."
        )

    logger.info("Recipe Assistant started")
    threading.Thread(
        target=_warm_recipe_cache,
        name="recipe-cache-warmup",
        daemon=True,
    ).start()
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

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


app.include_router(health_router)

# Everything else requires the shared API key. /health and /healthz stay open
# because Cloud Run probes them; /warmup is gated since it forces a full
# reload of every recipe from GCS and is a cheap DoS lever otherwise.
protected = [Depends(require_api_key)]
app.include_router(recipes_router, dependencies=protected)
app.include_router(chat_router, dependencies=protected)
app.include_router(ingestion_router, dependencies=protected)
app.include_router(images_router, dependencies=protected)
app.include_router(history_router, dependencies=protected)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
