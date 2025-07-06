#!/usr/bin/env python3
"""
🚀 Setup Script for Intelligent WooCommerce Recommendations
Automates the setup process for AstraDB, Langflow, and the recommendation service
"""

import os
import sys
import asyncio
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv

def print_banner():
    """Print setup banner"""
    banner = """
    🤖 INTELLIGENT WOOCOMMERCE RECOMMENDATIONS
    ==========================================
    Powered by Langflow + AstraDB + OpenAI
    
    This setup will configure:
    ✅ Python dependencies
    ✅ Environment variables
    ✅ AstraDB collections
    ✅ Product vectorization
    ✅ Langflow integration
    """
    print(banner)

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check if pip is available
    try:
        subprocess.run(["pip", "--version"], check=True, capture_output=True)
        print("✅ pip available")
    except subprocess.CalledProcessError:
        print("❌ pip not found")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            # Copy example to .env
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ Created .env file from template")
            print("⚠️  Please update .env with your actual credentials:")
            print("   - OPENAI_API_KEY")
            print("   - ASTRA_DB_APPLICATION_TOKEN") 
            print("   - ASTRA_DB_API_ENDPOINT")
            print("   - WC_KEY and WC_SECRET")
            
            return False  # Need manual configuration
        else:
            print("❌ No .env.example found")
            return False
    else:
        print("✅ .env file exists")
        return True

def validate_environment():
    """Validate environment variables"""
    print("🔍 Validating environment...")
    
    load_dotenv()
    
    required_vars = [
        "OPENAI_API_KEY",
        "ASTRA_DB_APPLICATION_TOKEN", 
        "ASTRA_DB_API_ENDPOINT",
        "WC_KEY",
        "WC_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables validated")
    return True

async def setup_astradb():
    """Setup AstraDB collections"""
    print("🗄️ Setting up AstraDB...")
    
    try:
        from astra_client import IntelligentAstraClient
        
        client = IntelligentAstraClient()
        await client.initialize()
        
        print("✅ AstraDB collections initialized")
        return True
        
    except Exception as e:
        print(f"❌ AstraDB setup failed: {e}")
        return False

async def vectorize_products():
    """Vectorize WooCommerce products"""
    print("🔄 Vectorizing products...")
    
    try:
        from product_vectorizer import ProductVectorizer
        
        vectorizer = ProductVectorizer()
        await vectorizer.sync_all_products()
        
        print("✅ Products vectorized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Product vectorization failed: {e}")
        print("   You can run this manually later with:")
        print("   python product_vectorizer.py --sync-all")
        return False

def setup_langflow():
    """Setup Langflow"""
    print("🔄 Setting up Langflow...")
    
    try:
        # Check if Langflow is installed
        result = subprocess.run(["langflow", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Langflow is installed")
        else:
            print("📦 Installing Langflow...")
            subprocess.run([sys.executable, "-m", "pip", "install", "langflow"], check=True)
            print("✅ Langflow installed")
        
        # Import the flow
        flow_file = Path("recommendation_flow.json")
        if flow_file.exists():
            print("✅ Recommendation flow configuration ready")
            print("   Import manually in Langflow UI or use the API")
        
        return True
        
    except Exception as e:
        print(f"❌ Langflow setup failed: {e}")
        return False

def create_startup_script():
    """Create startup script"""
    print("📝 Creating startup script...")
    
    startup_script = """#!/bin/bash
# 🚀 Intelligent Recommendations Startup Script

echo "Starting Intelligent WooCommerce Recommendations..."

# Start Langflow in background
echo "Starting Langflow..."
langflow run --host 0.0.0.0 --port 7860 &
LANGFLOW_PID=$!

# Wait for Langflow to start
sleep 10

# Start the recommendation service
echo "Starting Recommendation Service..."
python langflow_integration.py &
SERVICE_PID=$!

echo "Services started:"
echo "- Langflow: http://localhost:7860 (PID: $LANGFLOW_PID)"
echo "- Recommendation API: http://localhost:8001 (PID: $SERVICE_PID)"

# Wait for services
wait $LANGFLOW_PID $SERVICE_PID
"""
    
    with open("start_services.sh", "w") as f:
        f.write(startup_script)
    
    # Make executable
    os.chmod("start_services.sh", 0o755)
    
    print("✅ Startup script created: start_services.sh")

def print_next_steps():
    """Print next steps"""
    next_steps = """
    🎉 SETUP COMPLETE!
    
    Next Steps:
    1. Update .env with your credentials if not done already
    2. Run product vectorization: python product_vectorizer.py --sync-all
    3. Start services: ./start_services.sh
    4. Import recommendation_flow.json into Langflow UI
    5. Test the API: curl http://localhost:8001/health
    
    Integration with existing WooCommerce proxy:
    - Add intelligent search endpoint to your proxy
    - Update frontend to use new recommendation API
    - Implement session management for user context
    
    Documentation: README.md
    """
    print(next_steps)

async def main():
    """Main setup function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return
    
    # Setup environment
    env_ready = setup_environment()
    
    if not env_ready:
        print("⚠️  Please configure .env file and run setup again")
        return
    
    # Validate environment
    if not validate_environment():
        print("❌ Environment validation failed")
        return
    
    # Setup AstraDB
    if not await setup_astradb():
        print("❌ AstraDB setup failed")
        return
    
    # Setup Langflow
    if not setup_langflow():
        print("❌ Langflow setup failed")
        return
    
    # Create startup script
    create_startup_script()
    
    # Vectorize products (optional, can fail)
    await vectorize_products()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    asyncio.run(main())
