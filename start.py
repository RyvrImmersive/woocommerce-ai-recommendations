#!/usr/bin/env python3
"""
Startup script for Railway deployment
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'OPENAI_API_KEY',
        'ASTRA_DB_APPLICATION_TOKEN', 
        'ASTRA_DB_API_ENDPOINT',
        'ASTRA_DB_KEYSPACE'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        return False
    
    logger.info("All required environment variables are set")
    return True

def main():
    """Main startup function"""
    logger.info("Starting Intelligent Recommendations API...")
    
    # Check environment
    if not check_environment():
        logger.error("Environment check failed")
        sys.exit(1)
    
    # Import and start the app
    try:
        from langflow_integration import app
        logger.info("FastAPI app imported successfully")
        
        # Get port from environment
        port = int(os.getenv('PORT', 8001))
        
        # Start uvicorn
        import uvicorn
        logger.info(f"Starting uvicorn on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port, workers=1)
        
    except Exception as e:
        logger.error(f"Failed to start app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
