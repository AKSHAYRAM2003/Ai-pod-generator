from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.core.exceptions import AppException


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up AI Podcast Generator API")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Podcast Generator API")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered podcast generation platform",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS - Must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Explicitly set origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


# Add custom middleware to log requests and add CORS headers
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    """Add CORS headers to all responses"""
    origin = request.headers.get("origin")
    
    # Handle preflight requests
    if request.method == "OPTIONS":
        response = JSONResponse(content={"ok": True})
        response.headers["Access-Control-Allow-Origin"] = origin or "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    
    # Process request
    response = await call_next(request)
    
    # Add CORS headers to response
    response.headers["Access-Control-Allow-Origin"] = origin or "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Global exception handler for custom application exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Mount static files for serving audio files
storage_path = os.path.join(os.path.dirname(__file__), "storage")
if os.path.exists(storage_path):
    app.mount("/storage", StaticFiles(directory=storage_path), name="storage")
    logger.info(f"Mounted storage directory: {storage_path}")
else:
    logger.warning(f"Storage directory not found: {storage_path}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
