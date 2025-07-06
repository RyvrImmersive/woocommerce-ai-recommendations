#!/usr/bin/env python3
"""
Simple FastAPI app for Railway debugging
"""
import os
from fastapi import FastAPI

app = FastAPI(title="Simple Test", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Simple app working!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": "2025-01-06"}

@app.get("/env-check")
async def env_check():
    return {
        "port": os.getenv("PORT", "not_set"),
        "has_openai": bool(os.getenv("OPENAI_API_KEY")),
        "python_version": os.getenv("PYTHON_VERSION", "not_set")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
