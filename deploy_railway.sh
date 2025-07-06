#!/bin/bash

# Railway Deployment Script for Intelligent Recommendations API

echo "🚀 Deploying Intelligent Recommendations API to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (will open browser)
echo "🔐 Logging into Railway..."
railway login

# Initialize Railway project
echo "📦 Initializing Railway project..."
railway init

# Set environment variables
echo "🔧 Setting environment variables..."
echo "Please set these environment variables in Railway dashboard:"
echo "- OPENAI_API_KEY"
echo "- ASTRA_DB_APPLICATION_TOKEN" 
echo "- ASTRA_DB_API_ENDPOINT"
echo "- ASTRA_DB_KEYSPACE"
echo "- WC_KEY"
echo "- WC_SECRET"
echo "- WC_BASE_URL"
echo ""
echo "Opening Railway dashboard..."
railway open

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment initiated!"
echo "📋 Next steps:"
echo "1. Set environment variables in Railway dashboard"
echo "2. Wait for deployment to complete"
echo "3. Get your public URL from Railway dashboard"
echo "4. Update your frontend to use the new URL"
