# 🐙 GitHub Integration Setup

## 📋 Step 1: Create GitHub Repository

1. **Go to GitHub**: https://github.com/new
2. **Repository name**: `intelligent-recommendations-api`
3. **Description**: `AI-powered WooCommerce product recommendations with Langflow and AstraDB`
4. **Visibility**: Public (or Private if you prefer)
5. **Initialize**: Don't check any boxes (we already have files)
6. **Click**: "Create repository"

## 📤 Step 2: Push Your Code to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Navigate to your project
cd /Users/jigeshshah/CascadeProjects/Langflow/woo-intelligent-recommendations

# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/intelligent-recommendations-api.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

## 🚀 Step 3: Deploy via Railway

1. **Go to Railway**: https://railway.app
2. **Sign up/Login** (use GitHub for easy integration)
3. **Click**: "New Project"
4. **Select**: "Deploy from GitHub repo"
5. **Choose**: `intelligent-recommendations-api`
6. **Railway will automatically**:
   - Detect it's a Python FastAPI app
   - Use the `railway.json` configuration
   - Start building and deploying

## 🔧 Step 4: Set Environment Variables

In Railway dashboard → **Variables** tab, add these:

```
OPENAI_API_KEY=your_openai_api_key_here
ASTRA_DB_APPLICATION_TOKEN=your_astra_db_token_here
ASTRA_DB_API_ENDPOINT=your_astra_db_endpoint_here
ASTRA_DB_KEYSPACE=enablemart
WC_KEY=your_woocommerce_consumer_key
WC_SECRET=your_woocommerce_consumer_secret
WC_BASE_URL=your_woocommerce_store_url
```

## 🌐 Step 5: Get Your Live URL

After deployment completes (~3-5 minutes), Railway will provide a URL like:
`https://intelligent-recommendations-api-production.up.railway.app`

## ✅ Step 6: Test Your Live API

```bash
# Replace with your actual Railway URL
curl https://your-railway-url.railway.app/health

# Test intelligent search
curl -X POST https://your-railway-url.railway.app/api/intelligent-search \
  -H "Content-Type: application/json" \
  -d '{"query": "wheelchair for elderly", "limit": 5}'
```

---

## 🎯 Ready to Start?

**Your next actions:**
1. ✅ Sign in to GitHub
2. ✅ Create repository: `intelligent-recommendations-api`  
3. ✅ Copy the git commands GitHub shows you
4. ✅ Run them in your terminal
5. ✅ Go to Railway and deploy from GitHub

**Need help with any step? Just ask!**
