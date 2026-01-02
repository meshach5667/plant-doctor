from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging
from config import get_settings
from database import init_db
from routes import auth_router, plants_router, diagnosis_router, routines_router

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
    description="""
    🌱 Plant Doctor API - Your AI-powered plant health assistant!
    
    ## Features
    
    * **🔍 Disease Diagnosis** - Upload plant images for AI-powered disease detection
    * **💊 Treatment Recommendations** - Get detailed treatment and prevention tips
    * **📅 Routine Checks** - Set up daily/weekly maintenance reminders
    * **🌿 Plant Management** - Track all your plants in one place
    
    ## How it works
    
    1. Register an account or use the diagnosis endpoint without auth for quick checks
    2. Upload a photo of your plant leaf
    3. Get instant AI diagnosis with confidence score
    4. Follow treatment recommendations
    5. Set up routine checks for ongoing plant care
    
    ## Supported Plants
    
    Currently supports diagnosis for:
    - 🍅 Tomato
    - 🥔 Potato  
    - 🌶️ Pepper (Bell)
    """,
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
app.include_router(plants_router, prefix="/api/v1")
app.include_router(diagnosis_router, prefix="/api/v1")
app.include_router(routines_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Plant Doctor API 🌱",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "plants": "/api/v1/plants",
            "diagnosis": "/api/v1/diagnosis",
            "routines": "/api/v1/routines"
        }
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
