"""
Telegram-Ecom-Bot-v2 — FastAPI Application Factory
====================================================
Main entry point for the bot server. Configures lifespan events,
middleware stack, and webhook route registration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.db.mongo import connect_mongo, close_mongo
from src.db.redis import connect_redis, close_redis
from src.api.routes.webhooks import router as webhook_router
from src.api.routes.health import router as health_router
from src.bot.setup import configure_bot
from src.utils.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup/shutdown lifecycle for DB connections and bot setup."""
    logger.info("Starting up Telegram-Ecom-Bot-v2...")

    # --- Startup ---
    app.state.mongo = await connect_mongo(settings.MONGO_URI, settings.MONGO_DB_NAME)
    app.state.redis = await connect_redis(settings.REDIS_URL)
    app.state.bot = await configure_bot(settings.BOT_TOKEN)

    logger.info(
        "Connected to MongoDB [%s] and Redis [%s]",
        settings.MONGO_DB_NAME,
        settings.REDIS_URL,
    )

    yield

    # --- Shutdown ---
    logger.info("Shutting down gracefully...")
    await close_redis(app.state.redis)
    await close_mongo(app.state.mongo)
    logger.info("All connections closed. Goodbye.")


def create_app() -> FastAPI:
    """Application factory — returns a fully configured FastAPI instance."""
    app = FastAPI(
        title="Telegram-Ecom-Bot-v2",
        description="Automated e-commerce sales bot for Telegram",
        version="2.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # --- Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Routes ---
    app.include_router(health_router, tags=["Health"])
    app.include_router(
        webhook_router,
        prefix="/api/v1/webhooks",
        tags=["Webhooks"],
    )

    return app


app = create_app()
