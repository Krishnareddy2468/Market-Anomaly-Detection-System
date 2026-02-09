"""
FastAPI Application Entry Point
===============================
Main application factory with middleware, routes, and lifecycle management.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.routes import alerts, analytics, dashboard, feedback, investigations
from app.api.middleware import RequestLoggingMiddleware, ObservabilityMiddleware
from app.core.errors import AppException, register_exception_handlers
from app.core.logging import setup_logging, get_logger
from app.db.session import init_db, close_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    # Startup
    setup_logging()
    logger.info("Starting application", app_name=settings.APP_NAME, version=settings.APP_VERSION)
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")


def create_application() -> FastAPI:
    """Application factory function."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Enterprise-grade Market Anomaly & Fraud Detection API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom Middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ObservabilityMiddleware)
    
    # Exception Handlers
    register_exception_handlers(app)
    
    # API Routes
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
    app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
    app.include_router(investigations.router, prefix="/api/investigations", tags=["Investigations"])
    app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
    app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
    
    # Health Check
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for load balancers and monitoring."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """API root endpoint."""
        return {
            "message": "Market Anomaly & Fraud Detection API",
            "version": settings.APP_VERSION,
            "docs": "/docs" if settings.DEBUG else "Disabled in production",
        }
    
    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
    )
