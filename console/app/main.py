"""
Vacation Planner API - Main Entry Point
FastAPI application with LangChain agent for AI-powered vacation planning.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.config import settings
from app.database import init_db
from app.routers import plans, bookings
from app.utils.logger import logger

# === Lifespan Events ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Vacation Planner API...")
    init_db()
    logger.info("✅ Database initialized")
    
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Vacation Planner API...")

# === Create App ===
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# === CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Request Logging Middleware ===
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    
    return response

# === Include Routers ===
app.include_router(plans.router)
app.include_router(bookings.router)

# === Root Endpoints ===
@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "create_plan": "POST /api/v1/plan",
            "get_plan": "GET /api/v1/plan/{plan_id}",
            "confirm_booking": "POST /api/v1/plan/{plan_id}/confirm",
            "list_bookings": "GET /api/v1/bookings"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "llm_model": settings.LLM_MODEL,
        "llm_url": settings.LLM_BASE_URL
    }

# === Error Handlers ===
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again.",
            "detail": str(exc) if settings.DEBUG else None
        }
    )

# === Run with Uvicorn ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )