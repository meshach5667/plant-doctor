from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging
from config import get_settings
from database import init_db
from routes import auth_router, farm_router, diagnosis_router, routines_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Plant Doctor API...")
    init_db()
    logger.info("Database initialized")
    
    # Create uploads directory
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Plant Doctor API...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded images
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(farm_router, prefix="/api/v1")
app.include_router(diagnosis_router, prefix="/api/v1")
app.include_router(routines_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Hello, i am Plant Doctor ",
    
        }
    


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    from services import diagnosis_service
    
    return {
        "status": "healthy",
        "model_loaded": diagnosis_service.is_model_loaded,
        "version": settings.APP_VERSION
    }
