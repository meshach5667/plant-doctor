"""
Plant Doctor API - Main Application Entry Point

A production-ready FastAPI application for plant disease diagnosis.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from config import get_settings
from database import init_db
from routes import auth_router, farm_router, diagnosis_router, routines_router
from core.middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from core.handlers import register_exception_handlers
from core.security import SecurityConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

settings = get_settings()


def configure_security() -> None:
    """Initialize security configuration from settings."""
    SecurityConfig.configure(
        secret_key=settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )
    logger.info("Security configuration initialized")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    
    Handles startup and shutdown tasks including:
    - Database initialization
    - Security configuration
    - Directory creation
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize security
    configure_security()
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Create uploads directory
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    logger.info(f"Uploads directory ready: {uploads_dir}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}...")


# Create FastAPI application
app = FastAPI(
)

# Register exception handlers
register_exception_handlers(app)

# Add middleware (order matters - first added is outermost)
# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# Request logging
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths=["/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"]
)

# Rate limiting
if not settings.DEBUG:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        exclude_paths=["/health", "/docs", "/redoc", "/openapi.json"]
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time-Ms"],
)

# Mount static files for uploaded images
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include routers with versioned prefix
API_V1_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(farm_router, prefix=API_V1_PREFIX)
app.include_router(diagnosis_router, prefix=API_V1_PREFIX)
app.include_router(routines_router, prefix=API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns the current health status of the API and its dependencies.
    """
    from services import diagnosis_service
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "model_loaded": diagnosis_service.is_model_loaded,
    }


# Run with uvicorn when executed directly
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level="debug" if settings.DEBUG else "info",
    )
