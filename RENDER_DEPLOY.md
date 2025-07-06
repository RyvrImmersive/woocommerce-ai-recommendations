# 🚀 Deploy to Render - Step by Step

## ✅ **Why Render?**
- **Free Tier**: 750 hours/month (more than Railway's 500 hours)
- **Better Python Support**: Optimized for Python apps
- **Auto-Deploy**: Deploys automatically from GitHub
- **Custom Domains**: Easy to add your own domain
- **Great Logs**: Better debugging interface

## 🚀 **Deployment Steps**

### Step 1: Go to Render
Visit: https://render.com

### Step 2: Sign Up/Login
- Click "Get Started for Free"
- Sign up with GitHub (recommended for easy integration)

### Step 3: Create New Web Service
1. Click "New +" button
2. Select "Web Service"
3. Connect your GitHub account if not already connected
4. Select repository: `RyvrImmersive/woocommerce-ai-recommendations`

### Step 4: Configure Service
**Fill in these settings:**
- **Name**: `woocommerce-ai-recommendations`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn langflow_integration:app --host 0.0.0.0 --port $PORT`
- **Plan**: `Free` (for now)

### Step 5: Set Environment Variables
In the "Environment Variables" section, add:

```
OPENAI_API_KEY=your_openai_api_key_here
ASTRA_DB_APPLICATION_TOKEN=your_astra_db_token_here
ASTRA_DB_API_ENDPOINT=your_astra_db_endpoint_here
ASTRA_DB_KEYSPACE=enablemart
WC_KEY=your_woocommerce_consumer_key
WC_SECRET=your_woocommerce_consumer_secret
WC_BASE_URL=your_woocommerce_store_url
PYTHON_VERSION=3.11.0
```

### Step 6: Deploy
1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your FastAPI app
   - Provide a public URL

### Step 7: Get Your Live URL
After deployment (~3-5 minutes), you'll get a URL like:
`https://woocommerce-ai-recommendations.onrender.com`

## ✅ **Test Your Deployed API**

```bash
# Test health endpoint
curl https://your-app.onrender.com/health

# Test intelligent search
curl -X POST https://your-app.onrender.com/api/intelligent-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "wheelchair for elderly parent",
    "session_id": "test123",
    "limit": 5
  }'
```

## 🔄 **Auto-Deploy Setup**
Once connected to GitHub, Render will automatically:
- Deploy when you push to `main` branch
- Show build logs in real-time
- Restart if the app crashes
- Scale automatically (on paid plans)

## 💰 **Pricing**
- **Free**: 750 hours/month, sleeps after 15 min inactivity
- **Starter ($7/month)**: Always on, custom domains, more resources
- **Pro ($25/month)**: More CPU/RAM, priority support

## 🎯 **Advantages over Railway**
- ✅ More free hours (750 vs 500)
- ✅ Better Python ecosystem support
- ✅ More detailed build logs
- ✅ Better free tier limits
- ✅ Easier environment variable management

---

## 🚀 **Ready to Deploy?**
1. Go to https://render.com
2. Sign up with GitHub
3. Create Web Service from your repository
4. Set environment variables
5. Deploy!

**Your API will be live in ~5 minutes!**
