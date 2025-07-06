# 🚀 Railway Deployment Steps

## ✅ Preparation Complete
- ✅ Railway CLI installed
- ✅ Git repository initialized
- ✅ Code committed
- ✅ Configuration files ready

## 🔐 Step 1: Login to Railway
**Run this command in your terminal:**
```bash
cd /Users/jigeshshah/CascadeProjects/Langflow/woo-intelligent-recommendations
railway login
```
- This will open your browser
- Sign up/login with GitHub, Google, or email
- Return to terminal when done

## 📦 Step 2: Initialize Railway Project
```bash
railway init
```
- Choose "Create new project"
- Name it: `intelligent-recommendations-api`
- Select your team (or personal)

## 🚀 Step 3: Deploy
```bash
railway up
```
- This will build and deploy your API
- Wait for deployment to complete (~2-3 minutes)

## 🔧 Step 4: Set Environment Variables
**Run this to open Railway dashboard:**
```bash
railway open
```

**In the Railway dashboard, go to Variables tab and add:**
```
OPENAI_API_KEY=your_openai_api_key_here
ASTRA_DB_APPLICATION_TOKEN=your_astra_token_here
ASTRA_DB_API_ENDPOINT=your_astra_endpoint_here
ASTRA_DB_KEYSPACE=enablemart
WC_KEY=your_woocommerce_consumer_key
WC_SECRET=your_woocommerce_consumer_secret
WC_BASE_URL=your_woocommerce_store_url
```

## 🌐 Step 5: Get Your Public URL
After deployment, Railway will give you a URL like:
`https://intelligent-recommendations-api-production.up.railway.app`

## ✅ Step 6: Test Your Deployed API
```bash
# Test health endpoint
curl https://your-railway-url.railway.app/health

# Test intelligent search
curl -X POST https://your-railway-url.railway.app/api/intelligent-search \
  -H "Content-Type: application/json" \
  -d '{"query": "wheelchair for elderly", "limit": 5}'
```

## 🔄 Step 7: Update Your Frontend
Replace localhost URLs in your frontend with your new Railway URL:
```javascript
// Old
const API_URL = 'http://localhost:8001';

// New  
const API_URL = 'https://your-railway-url.railway.app';
```

---

## 🆘 Need Help?
If you encounter any issues:
1. Check Railway logs: `railway logs`
2. Check environment variables are set correctly
3. Verify your API keys are valid
4. Contact me for troubleshooting

**Your API will be live at: `https://your-railway-url.railway.app`**
