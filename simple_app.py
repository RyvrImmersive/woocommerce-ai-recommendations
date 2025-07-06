#!/usr/bin/env python3
"""
Simple FastAPI app for Railway debugging
"""
import os
import logging
from fastapi import FastAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Test", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    port = os.getenv("PORT", "not_set")
    logger.info(f"App starting up on port: {port}")
    logger.info(f"Environment variables: PORT={port}")

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Simple app working!", "status": "ok"}

@app.get("/health")
async def health():
    logger.info("Health check called")
    port = os.getenv("PORT", "not_set")
    return {
        "status": "healthy", 
        "port": port,
        "message": "Health check successful"
    }

@app.get("/env-check")
async def env_check():
    return {
        "port": os.getenv("PORT", "not_set"),
        "has_openai": bool(os.getenv("OPENAI_API_KEY")),
        "python_version": os.getenv("PYTHON_VERSION", "not_set"),
        "all_env": dict(os.environ)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
