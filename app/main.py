# import sys
# import asyncio
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from contextlib import asynccontextmanager
# import logging

# from app.core.config import settings
# from app.core.database import engine, Base
# from app.core.scheduler import scheduler
# # One-Drive
# from app.core.onedrivescheduler import OneDriveScheduler
# from app.core.logging_config import setup_logging

# # Import routers
# from app.routers import auth, tenders, keywords, sources, fetch, notifications, scrape_router, onedrive, powerbi


# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# setup_logging()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Starting Tender Intel System...")

#     #  ASYNC SAFE TABLE CREATION
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

#     logger.info("Database tables created/verified")

#     # Start scheduler
#     if not scheduler.running:
#         scheduler.start()
#         logger.info("Scheduler started")

#     yield

#     # Shutdown
#     logger.info("Shutting down Tender Intel System...")
#     if scheduler.running:
#         scheduler.shutdown()
#         logger.info("Scheduler stopped")

#     await engine.dispose()



# app = FastAPI(
#     title=settings.APP_NAME,
#     version=settings.APP_VERSION,
#     lifespan=lifespan,
#     docs_url="/docs",
#     redoc_url="/redoc"
# )

# # CORS Configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000", "http://localhost:5173"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include routers
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(tenders.router, prefix="/api/tenders", tags=["Tenders"])
# app.include_router(keywords.router, prefix="/api/keywords", tags=["Keywords"])
# app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
# app.include_router(fetch.router, prefix="/api/fetch", tags=["Fetch"])
# app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
# # Scarpe_Router
# app.include_router(scrape_router.router, prefix="/scrape", tags=["Scraping"])
# app.include_router(onedrive.router, prefix=settings.API_V1_PREFIX)

# @app.get("/")
# async def root():
#     return {
#         "message": "Tender Intel API",
#         "version": settings.APP_VERSION,
#         "status": "operational"
#     }


# @app.get("/api/health")
# async def health_check():
#     return {
#         "status": "healthy",
#         "database": "connected",
#         "scheduler": "running" if scheduler.running else "stopped"
#     }


# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     logger.error(f"Global exception: {str(exc)}", exc_info=True)
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "Internal server error occurred"}
#     )

# @app.on_event("startup")
# async def startup_event():
#     from app.core.scheduler import run_excel_ingestion
#     await run_excel_ingestion()

import sys
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base
from app.core.scheduler import scheduler, run_excel_ingestion
from app.core.logging_config import setup_logging

# Routers
from app.routers import (
    auth, tenders, keywords, sources,
    fetch, notifications, scrape_router,
    onedrive
)

# Windows async fix
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Tender Intel System...")

    #Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database ready")

    #Run Excel ingestion ONCE on startup
    try:
        logger.info("Running Excel ingestion...")
        await run_excel_ingestion()
        logger.info("Excel ingestion completed")
    except Exception as e:
        logger.error("Excel ingestion failed", exc_info=True)

    #Start scheduler
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")

    yield

    # Shutdown
    logger.info("Shutting down system...")
    if scheduler.running:
        scheduler.shutdown()
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tenders.router, prefix="/api/tenders", tags=["Tenders"])
app.include_router(keywords.router, prefix="/api/keywords", tags=["Keywords"])
app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
app.include_router(fetch.router, prefix="/api/fetch", tags=["Fetch"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(scrape_router.router, prefix="/scrape", tags=["Scraping"])
app.include_router(onedrive.router, prefix=settings.API_V1_PREFIX)

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
    logger.error("Global exception", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.on_event("startup")
async def startup_event():
    scheduler.start()