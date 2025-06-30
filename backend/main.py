from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import sys
from pathlib import Path
import os

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.deps import get_db
from app.db.session import engine, SessionLocal
from app.db.init_db import init_db
from app.api.api_v1.api import api_router

# Setup logging
logger = setup_logging()

app = FastAPI(
    title="Task Donegeon API",
    description="A gamified task management system API",
    version="1.0.0",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    try:
        # Log system information
        logger.info(f"""
System Information:
  - Python Version: {sys.version}
  - Environment: {settings.ENVIRONMENT}
  - Debug Mode: {settings.DEBUG}
  - API URL: {settings.API_V1_STR}
  - Database URL: {settings.DATABASE_URL}
""".strip())

        # Initialize database
        init_db(SessionLocal())
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed") 