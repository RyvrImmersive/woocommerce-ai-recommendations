#!/usr/bin/env python3
"""
Minimal test app to debug Railway deployment
"""
import os
from fastapi import FastAPI

# Create minimal FastAPI app
app = FastAPI(title="Test App", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Test app is working!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "port": os.getenv("PORT", "unknown")}

@app.get("/env")
async def check_env():
    """Check environment variables"""
    return {
        "has_openai": bool(os.getenv("OPENAI_API_KEY")),
        "has_astra_token": bool(os.getenv("ASTRA_DB_APPLICATION_TOKEN")),
        "has_astra_endpoint": bool(os.getenv("ASTRA_DB_API_ENDPOINT")),
        "port": os.getenv("PORT", "not_set")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
