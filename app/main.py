from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.core.scheduler import scheduler

# Import routers
from app.routers import auth, tenders, keywords, sources, fetch, notifications

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Tender Intel System...")

    #  ASYNC SAFE TABLE CREATION
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created/verified")

    # Start scheduler
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")

    yield

    # Shutdown
    logger.info("Shutting down Tender Intel System...")
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")

    await engine.dispose()



app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tenders.router, prefix="/api/tenders", tags=["Tenders"])
app.include_router(keywords.router, prefix="/api/keywords", tags=["Keywords"])
app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
app.include_router(fetch.router, prefix="/api/fetch", tags=["Fetch"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])


@app.get("/")
async def root():
    return {
        "message": "Tender Intel API",
        "version": settings.APP_VERSION,
        "status": "operational"
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "scheduler": "running" if scheduler.running else "stopped"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )